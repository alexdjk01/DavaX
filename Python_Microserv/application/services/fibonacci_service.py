def calculate_fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Negative numbers! Fibonacci won't work!")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
