"""核对交换资料的客户编号、时序和关联条件。"""
import json
from pathlib import Path
import unittest


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def rows(name):
    content = (SAMPLES / f"{name}.ndjson").read_text(encoding="utf-8")
    return [json.loads(line) for line in content.splitlines()]


class ExchangeSampleTest(unittest.TestCase):
    def test_records_are_json_objects(self):
        files = sorted(SAMPLES.glob("*.ndjson"))
        self.assertEqual(len(files), 5)
        for path in files:
            with self.subTest(path=path.name):
                records = rows(path.stem)
                self.assertTrue(records)
                self.assertTrue(all(isinstance(row, dict) for row in records))

    def test_related_records_preserve_source_evidence(self):
        self.assertFalse(set(rows("shops")[0]) < {"shop", "scope"})
        tills = rows("tills")
        lake = [row for row in tills if row["scope"] == "t-lake"]
        self.assertGreater(lake[1]["seq"], lake[0]["through"] + 1)
        self.assertEqual(lake[1]["seq"], lake[3]["seq"])
        self.assertNotEqual(lake[1]["message"], lake[3]["message"])
        self.assertGreater(lake[4]["through"], lake[5]["through"])
        picks = rows("handling")
        self.assertEqual(picks[0], picks[1])
        self.assertLess(picks[0]["occurred_at"], lake[4]["as_of"])
        self.assertGreater(picks[2]["occurred_at"], lake[4]["as_of"])
        self.assertIn(picks[0]["basket"], {row["basket"] for row in rows("baskets")})
