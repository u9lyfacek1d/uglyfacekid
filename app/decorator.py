import time
import tracemalloc
from functools import wraps

def measure_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.perf_counter()

        result = await func(*args, **kwargs)

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"{func.__name__} завершилась за {end_time - start_time:.4f} секунд")
        print(f"Память: текущая = {current / 10**6:.3f} MB; пик = {peak / 10**6:.3f} MB")

        return result
    return wrapper
