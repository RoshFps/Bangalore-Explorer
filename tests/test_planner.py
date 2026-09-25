import unittest

from explorer.planner import TRANSPORT_RESERVE, PlannerInputError, build_trip_query, parse_budget


class BudgetTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_budget("100", "1000"), (100, 1000))
        self.assertEqual(parse_budget("", "500"), (0, 500))

    def test_rejects_bad_input(self):
        for low, high in [("a", "100"), ("10", "1; DROP TABLE users"), ("500", "100"), ("0", "50"), ("-1", "500")]:
            with self.assertRaises(PlannerInputError):
                parse_budget(low, high)


class QueryTests(unittest.TestCase):
    def test_single_category(self):
        q = build_trip_query(["Restaurants"], 0, 1000)
        self.assertIn("FROM HOTELS t0", q.sql)
        self.assertEqual(q.params, (0, 1000 - TRANSPORT_RESERVE))
        self.assertEqual(len(q.columns), 4)

    def test_multi_category_joins_on_area(self):
        q = build_trip_query(["Restaurants", "Games"], 0, 1000)
        self.assertIn("t1.PLACE = t0.LOCATION", q.sql)
        self.assertIn("(t0.AVG_PRICE + t1.PRICE)", q.sql)

    def test_user_text_is_never_in_sql(self):
        evil = "x' OR '1'='1"
        q = build_trip_query(["Malls"], 0, 1000, location=evil)
        self.assertNotIn(evil, q.sql)
        self.assertIn(f"%{evil}%", q.params)
        self.assertEqual(q.sql.count("%s"), len(q.params))

    def test_unknown_category_rejected(self):
        with self.assertRaises(PlannerInputError):
            build_trip_query(["USERS; --"], 0, 1000)
        with self.assertRaises(PlannerInputError):
            build_trip_query([], 0, 1000)


if __name__ == "__main__":
    unittest.main()
