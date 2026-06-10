import pybreaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitBreakerError(Exception):
    pass


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
            on_state_change=lambda cb, old_state, new_state: logger.info(
                f"Circuit breaker {cb.name} changed from {old_state} to {new_state}"
            )
        )

        @breaker
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Circuit breaker {breaker_name} caught exception: {e}")
                raise

        return wrapper

    return decorator


redis_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    name="redis_breaker",
    on_state_change=lambda cb, old_state, new_state: logger.info(
        f"Redis circuit breaker changed from {old_state} to {new_state}"
    )
)

elasticsearch_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=60,
    name="elasticsearch_breaker",
    on_state_change=lambda cb, old_state, new_state: logger.info(
        f"Elasticsearch circuit breaker changed from {old_state} to {new_state}"
    )
)

rabbitmq_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=45,
    name="rabbitmq_breaker",
    on_state_change=lambda cb, old_state, new_state: logger.info(
        f"RabbitMQ circuit breaker changed from {old_state} to {new_state}"
    )
)


def get_circuit_breaker_state(name: str) -> str:
    breakers = {
        "redis": redis_breaker,
        "elasticsearch": elasticsearch_breaker,
        "rabbitmq": rabbitmq_breaker,
    }
    breaker = breakers.get(name)
    if breaker:
        return str(breaker.state)
    return "unknown"


def get_all_circuit_breaker_states() -> dict:
    return {
        "redis": str(redis_breaker.state),
        "elasticsearch": str(elasticsearch_breaker.state),
        "rabbitmq": str(rabbitmq_breaker.state),
    }
