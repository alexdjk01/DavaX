def calculate_factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Negative numbers! Factorial won't work!")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
