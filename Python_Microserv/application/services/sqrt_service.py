import math

def calculate_sqrt(number: float) -> float:
    if number < 0:
        raise ValueError("Square root is not defined for negative numbers.")
    return math.sqrt(number)
