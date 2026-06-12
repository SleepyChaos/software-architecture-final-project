import pybreaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitBreakerError(Exception):
    pass


def _make_state_change_listener(name: str) -> type:
    """创建带日志的断路器状态变更监听器类"""

    class _Listener(pybreaker.CircuitBreakerListener):
        def state_change(self, cb, old_state, new_state):
            logger.info(
                f"{name} circuit breaker changed from {old_state} to {new_state}"
            )

    return _Listener


def circuit_breaker_decorator(
    max_failures: int = 5,
    reset_timeout: int = 30,
    name: str = None
):
    def decorator(func):
        breaker_name = name or func.__name__
        breaker = pybreaker.CircuitBreaker(
            fail_max=max_failures,
            reset_timeout=reset_timeout,
            name=breaker_name,
        )

        breaker.add_listener(_make_state_change_listener(breaker_name)())

        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


redis_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    name="redis_breaker",
)

redis_breaker.add_listener(_make_state_change_listener("Redis")())


elasticsearch_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=60,
    name="elasticsearch_breaker",
)

elasticsearch_breaker.add_listener(_make_state_change_listener("Elasticsearch")())


rabbitmq_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=45,
    name="rabbitmq_breaker",
)

rabbitmq_breaker.add_listener(_make_state_change_listener("RabbitMQ")())


def get_circuit_breaker_state(name: str) -> str:
    breakers = {
        "redis": redis_breaker,
        "elasticsearch": elasticsearch_breaker,
        "rabbitmq": rabbitmq_breaker,
    }
    breaker = breakers.get(name)
    if breaker:
        return breaker.state.name
    return "unknown"


def get_all_circuit_breaker_states() -> dict:
    return {
        "redis": redis_breaker.state.name,
        "elasticsearch": elasticsearch_breaker.state.name,
        "rabbitmq": rabbitmq_breaker.state.name,
    }
