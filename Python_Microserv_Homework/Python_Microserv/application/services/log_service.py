import math

def calculate_log(number: float) -> float:
    if number <= 0:
        raise ValueError("Logarithm is only defined for positive numbers.")
    return math.log(number)
