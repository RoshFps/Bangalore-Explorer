"""Builds the trip-recommendation query.

Only identifiers from the fixed ``CATEGORIES`` table below ever reach the SQL
text; everything the user types (budget, location) is passed as a bound
parameter. This closes the SQL injection in the original string-built query.
"""

from __future__ import annotations

from dataclasses import dataclass

# Rupees kept aside for bus fares when matching a budget.
TRANSPORT_RESERVE = 75
MAX_RESULTS = 200


@dataclass(frozen=True)
class Category:
    label: str
    table: str
    name_col: str
    place_col: str
    price_col: str


CATEGORIES: dict[str, Category] = {
    "Restaurants": Category("Restaurants", "HOTELS", "NAME", "LOCATION", "AVG_PRICE"),
    "Games": Category("Games", "GAMES", "NAME", "PLACE", "PRICE"),
    "Malls": Category("Malls", "MALLS", "NAME", "PLACE", "AVG_PRICE"),
    "Hangouts": Category("Hangouts", "HANGOUTS", "NAME", "PLACE", "PRICE"),
}


class PlannerInputError(ValueError):
    pass


@dataclass(frozen=True)
class TripQuery:
    sql: str
    params: tuple
    columns: list[str]


def parse_budget(min_text: str, max_text: str) -> tuple[int, int]:
    try:
        low = int(str(min_text).strip() or 0)
        high = int(str(max_text).strip())
    except ValueError:
        raise PlannerInputError("Budgets must be whole numbers of rupees.") from None
    if low < 0 or high <= 0:
        raise PlannerInputError("Budgets must be positive.")
    if low >= high:
        raise PlannerInputError("Minimum budget must be less than the maximum.")
    if high <= TRANSPORT_RESERVE:
        raise PlannerInputError(f"Maximum budget must be more than ₹{TRANSPORT_RESERVE} (kept for bus fare).")
    return low, high


def build_trip_query(selected: list[str], min_budget: int, max_budget: int, location: str = "") -> TripQuery:
    unknown = [s for s in selected if s not in CATEGORIES]
    if unknown:
        raise PlannerInputError(f"Unknown category: {', '.join(unknown)}")
    if not selected:
        raise PlannerInputError("Pick at least one kind of place.")

    cats = [CATEGORIES[s] for s in selected]
    aliases = [f"t{i}" for i in range(len(cats))]

    select_cols, columns, prices = [], [], []
    for alias, c in zip(aliases, cats):
        select_cols += [f"{alias}.{c.name_col}", f"{alias}.{c.place_col}", f"{alias}.{c.price_col}"]
        columns += [c.label, f"{c.label} area", f"{c.label} price (₹)"]
        prices.append(f"{alias}.{c.price_col}")

    total = " + ".join(prices)
    from_clause = " CROSS JOIN ".join(f"{c.table} {a}" for a, c in zip(aliases, cats))

    where, params = [f"({total}) > %s", f"({total}) < %s"], [min_budget, max_budget - TRANSPORT_RESERVE]
    first_place = f"{aliases[0]}.{cats[0].place_col}"
    for alias, c in zip(aliases[1:], cats[1:]):
        where.append(f"{alias}.{c.place_col} = {first_place}")
    if location.strip():
        where.append(f"{first_place} LIKE %s")
        params.append(f"%{location.strip()}%")

    sql = (
        f"SELECT {', '.join(select_cols)}, ({total}) AS total_price "
        f"FROM {from_clause} WHERE {' AND '.join(where)} "
        f"ORDER BY total_price LIMIT {MAX_RESULTS}"
    )
    columns.append("Total (₹)")
    return TripQuery(sql=sql, params=tuple(params), columns=columns)


BUS_QUERY = "SELECT DISTINCT bus_no FROM bus WHERE stops LIKE %s ORDER BY bus_no LIMIT 20"
