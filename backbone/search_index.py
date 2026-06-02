import os
from typing import Any

try:
    from elasticsearch import Elasticsearch, helpers
except ImportError:  # pragma: no cover - 依赖缺失时自动降级
    Elasticsearch = None
    helpers = None

from mock_data import BOOKS, DEFAULT_SUGGESTIONS

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://127.0.0.1:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "library-books")

_es_client = None


def get_elasticsearch_client():
    global _es_client

    if Elasticsearch is None:
        return None

    if _es_client is not None:
        return _es_client

    try:
        client = Elasticsearch(ELASTICSEARCH_URL, request_timeout=2, max_retries=0)
        if not client.ping():
            return None
        _es_client = client
        return _es_client
    except Exception:
        return None


def _book_document(book: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": book["id"],
        "isbn": book["isbn"],
        "title": book["title"],
        "author": book["author"],
        "publisher": book["publisher"],
        "publishYear": book["publishYear"],
        "category": book["category"],
        "coverImageUrl": book["coverImageUrl"],
        "location": book["location"],
        "totalCopies": book["totalCopies"],
        "availableCopies": book["availableCopies"],
        "barcodes": book["barcodes"],
        "description": book["description"],
    }


def ensure_index() -> bool:
    client = get_elasticsearch_client()
    if client is None:
        return False

    if not client.indices.exists(index=ELASTICSEARCH_INDEX):
        client.indices.create(
            index=ELASTICSEARCH_INDEX,
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "isbn": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "author": {"type": "text"},
                    "publisher": {"type": "text"},
                    "publishYear": {"type": "integer"},
                    "category": {"type": "keyword"},
                    "coverImageUrl": {"type": "keyword"},
                    "location": {"type": "text"},
                    "totalCopies": {"type": "integer"},
                    "availableCopies": {"type": "integer"},
                    "barcodes": {"type": "keyword"},
                    "description": {"type": "text"},
                }
            },
        )

    if helpers is None:
        return False

    actions = [
        {
            "_index": ELASTICSEARCH_INDEX,
            "_id": book["id"],
            "_source": _book_document(book),
        }
        for book in BOOKS
    ]
    helpers.bulk(client, actions, refresh=True)
    return True


def _fallback_search(query: str, category: str | None, only_available: bool, limit: int) -> list[dict[str, Any]]:
    normalized_query = query.strip().lower()
    results = []

    for book in BOOKS:
        if category and book["category"] != category:
            continue
        if only_available and book["availableCopies"] <= 0:
            continue

        if normalized_query:
            haystack = " ".join(
                str(book[field]) for field in ("title", "author", "isbn", "description", "category")
            ).lower()
            if normalized_query not in haystack:
                continue

        results.append(book)

    results.sort(key=lambda item: (item["availableCopies"], item["publishYear"]), reverse=True)
    return results[:limit]


def search_books(query: str, category: str | None = None, only_available: bool = False, limit: int = 12):
    client = get_elasticsearch_client()
    normalized_query = query.strip()

    if client is None:
        return _fallback_search(query, category, only_available, limit)

    filters: list[dict[str, Any]] = []
    if category:
        filters.append({"term": {"category": category}})
    if only_available:
        filters.append({"range": {"availableCopies": {"gt": 0}}})

    must_clause: list[dict[str, Any]]
    if normalized_query:
        must_clause = [
            {
                "multi_match": {
                    "query": normalized_query,
                    "fields": ["title^4", "author^2", "isbn^3", "description"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        ]
    else:
        must_clause = [{"match_all": {}}]

    try:
        response = client.search(
            index=ELASTICSEARCH_INDEX,
            size=limit,
            query={
                "bool": {
                    "must": must_clause,
                    "filter": filters,
                }
            },
            sort=["_score", {"availableCopies": "desc"}, {"publishYear": "desc"}],
        )
        hits = response["hits"]["hits"]
        return [hit["_source"] for hit in hits]
    except Exception:
        return _fallback_search(query, category, only_available, limit)


def suggest_books(query: str, limit: int = 6) -> list[str]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return DEFAULT_SUGGESTIONS[:limit]

    client = get_elasticsearch_client()
    suggestions: list[str] = []

    if client is not None:
        try:
            response = client.search(
                index=ELASTICSEARCH_INDEX,
                size=limit,
                query={
                    "multi_match": {
                        "query": normalized_query,
                        "fields": ["title^5", "author^2", "isbn", "description"],
                        "type": "bool_prefix",
                    }
                },
            )
            suggestions.extend(hit["_source"]["title"] for hit in response["hits"]["hits"])
        except Exception:
            suggestions = []

    if not suggestions:
        for book in BOOKS:
            candidates = [book["title"], book["author"], book["isbn"]]
            if any(normalized_query in str(item).lower() for item in candidates):
                suggestions.append(book["title"])

    suggestions.extend(item for item in DEFAULT_SUGGESTIONS if normalized_query in item.lower())

    deduplicated: list[str] = []
    for item in suggestions:
        if item not in deduplicated:
            deduplicated.append(item)

    return deduplicated[:limit]
