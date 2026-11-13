import sys
import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis import agency_summary, decade_summary, load_inventory


class DataTests(unittest.TestCase):
    def test_source_totals_and_unknown_years(self):
        data = load_inventory()
        self.assertEqual(len(data), 8862)
        self.assertEqual(data["year"].isna().sum(), 289)
        summary = agency_summary(data)
        self.assertEqual(summary["records"].sum(), 8862)
        self.assertAlmostEqual(summary["area"].sum(), data["area"].sum())
        hist = decade_summary(data, 1753, 2019)
        self.assertEqual(hist["records"].sum(), 8573)

    def test_decade_boundaries_and_empty_bins(self):
        data = pd.DataFrame({"year": [1989, 1990, 1999, 2010, None]})
        result = decade_summary(data, 1990, 2010)
        self.assertEqual(result["decade"].tolist(), [1990, 2000, 2010])
        self.assertEqual(result["records"].tolist(), [2, 0, 1])


class AppTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_default_and_metric_change(self):
        app = self.app()
        self.assertEqual(app.metric[0].value, "8,862")
        self.assertEqual(len(app.get("vega_lite_chart")), 2)
        before = app.get("vega_lite_chart")[0].proto.spec
        app.radio(key="measure").set_value("Inventory records").run()
        self.assertEqual(len(app.exception), 0)
        self.assertNotEqual(before, app.get("vega_lite_chart")[0].proto.spec)
        self.assertTrue(any("Department of Natural Resources ranks first with 3,223 records" in x.value for x in app.caption))

    def test_status_and_empty_selection(self):
        app = self.app()
        app.multiselect(key="statuses").set_value(["Abandon"]).run()
        self.assertEqual(app.metric[0].value, "226")
        app.multiselect(key="statuses").set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "0")
        self.assertEqual(len(app.info), 2)

    def test_agency_year_and_top_n(self):
        app = self.app()
        app.slider(key="top_n").set_value(5).run()
        app.selectbox(key="agency").set_value("University of Illinois").run()
        app.slider(key="years").set_value((1900, 1999)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "8,862")
        data = load_inventory()
        expected = int((data["agency"].eq("University of Illinois") & data["year"].between(1900, 1999)).sum())
        self.assertTrue(any(f"Current view: {expected:,} records;" in x.value for x in app.caption))
        app.slider(key="years").set_value((1753, 1753)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("No records" in x.value for x in app.info))


if __name__ == "__main__":
    unittest.main()
