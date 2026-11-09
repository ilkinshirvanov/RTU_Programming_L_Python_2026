NUMBERS = [3, 8, -2, 7, 0, -5, 10]


def squares(numbers: list[int]) -> list[int]:
    """Return a list with the square of each number."""
    return [x**2 for x in numbers]


def positives(numbers: list[int]) -> list[int]:
    """Return only the numbers greater than 0."""
    return [x for x in numbers if x > 0]


def even_squares(numbers: list[int]) -> set[int]:
    """Return a set of the squares of the even numbers."""
    return {x**2 for x in numbers if x % 2 == 0}


def cubes(numbers: list[int]) -> dict[int, int]:
    """Return a dict mapping each number to its cube."""
    return {x: x**3 for x in numbers}


if __name__ == "__main__":
    print("Squares:", squares(NUMBERS))
    print("Positives:", positives(NUMBERS))
    print("Even squares:", even_squares(NUMBERS))
    print("Cubes:", cubes(NUMBERS))
