from redis_client import redis_client


def increment_task_count(user_id: int):
    redis_client.incr(f"user:{user_id}:task_count")


def decrement_task_count(user_id: int):
    redis_client.decr(f"user:{user_id}:task_count")


def increment_completed_count(user_id: int):
    redis_client.incr(f"user:{user_id}:task_completed")


def decrement_completed_count(user_id: int):
    redis_client.decr(f"user:{user_id}:task_completed")


def get_task_count(user_id: int) -> int:
    count = redis_client.get(f"user:{user_id}:task_count")
    return int(count) if count else 0

def get_completed_task_count(user_id: int) -> int:
    count = redis_client.get(f"user:{user_id}:task_completed")
    return int(count) if count else 0