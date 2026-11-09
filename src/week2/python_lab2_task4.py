PRICES = [12.5, 9.9, 15.0, 22.3, 5.0]
QUANTITIES = [2, 5, 1, 3, 4]


# ---------- Part A: functional style ----------


def item_totals(prices: list[float], quantities: list[int]) -> list[float]:
    """Return price * quantity for each item, using map() and a lambda."""
    return list(map(lambda p, q: p * q, prices, quantities))


def filter_above(totals: list[float], threshold: float = 30) -> list[float]:
    """Return totals greater than threshold, using filter() and a lambda."""
    return list(filter(lambda x: x > threshold, totals))


def pair_up(prices: list[float], quantities: list[int]) -> list[tuple]:
    """Return a list of (price, quantity) tuples, using zip()."""
    return list(zip(prices, quantities))


# ---------- Part B: list comprehensions ----------


def item_totals_comp(prices: list[float], quantities: list[int]) -> list[float]:
    """Same as item_totals(), but with a list comprehension."""
    return [p * q for p, q in zip(prices, quantities)]


def filter_above_comp(totals: list[float], threshold: float = 30) -> list[float]:
    """Same as filter_above(), but with a list comprehension."""
    return [x for x in totals if x > threshold]


if __name__ == "__main__":
    totals = item_totals(PRICES, QUANTITIES)

    print("Totals:", totals)
    print("Totals > 30:", filter_above(totals))
    print("Price-quantity pairs:", pair_up(PRICES, QUANTITIES))
    print("Totals (comprehension):", item_totals_comp(PRICES, QUANTITIES))
    print("Totals > 30 (comprehension):", filter_above_comp(totals))

    print("I find list comprehensions easier to read.")
