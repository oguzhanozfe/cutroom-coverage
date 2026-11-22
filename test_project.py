import json
from pathlib import Path
import unittest

from project import analyze


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class ProjectTests(unittest.TestCase):
    def test_pickups_include_short_and_missing(self):
        report = analyze(example())
        self.assertEqual([r["Status"] for r in report["rows"]], ["Covered", "Too short", "Covered", "Missing"])
        self.assertEqual(report["rows"][1]["Seconds short"], 0.9)

    def test_disjoint_short_clips_do_not_add_up(self):
        data = {"shot_list": [{"shot": "A", "tags": ["Red"], "seconds": 2}],
                "footage": [{"id": s, "tags": ["red"], "in": 0, "out": 1} for s in ["b", "a"]]}
        self.assertEqual(analyze(data)["rows"][0]["Best clip"], "a")
        self.assertEqual(analyze(data)["rows"][0]["Status"], "Too short")

    def test_empty_bin(self):
        data = example()
        data["footage"] = []
        self.assertEqual(analyze(data)["metrics"]["Covered"], 0)

    def test_exact_decimal_duration(self):
        data = {"shot_list": [{"shot": "dial", "tags": ["macro"], "seconds": 0.2}],
                "footage": [{"id": "A", "in": 0.1, "out": 0.3, "tags": ["macro"]}]}
        self.assertEqual(analyze(data)["rows"][0]["Status"], "Covered")

    def test_invalid_time_range(self):
        data = example()
        data["footage"][0]["out"] = 0
        with self.assertRaises(ValueError):
            analyze(data)


if __name__ == "__main__":
    unittest.main()
