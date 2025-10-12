from datetime import date
import unittest
import pandas as pd
from src.parse_table import parse_cdip_jdar_wind

class TestParseCdipJdarWind(unittest.TestCase):
    def setUp(self):
        # Column names expected from the function
        self.expected_cols = ["station", "date_utc", "time_utc", "wspd_m_s", "wdir_deg"]

    def test_single_valid_row_with_headers(self):
        # Input data with headers and a single valid row
        station = "123"
        headers = "year mo dy hr mn hs_m tp_sec dp_deg depth_m ta_sec pres_mb wspd_m_s wdir_deg tempair_c tempsea_c"
        header_descriptions = "      utc           m   sec  deg     m     sec    mb     m/s  deg air(c) sfc(c) mid(c) bot(c)"
        data_row = "2025 10 09 01 45  0.52  9.14         4.62  5.39          2.71 323              "
        input_text = f"{station} {headers}\n{header_descriptions}\n{data_row} "

        df = parse_cdip_jdar_wind(input_text)

        # Basic structural assertions
        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 1)

        # Station exact match
        self.assertEqual(df.loc[0, "station"], int(station))

        # Time parsing: timezone-aware UTC Timestamp and correct value
        ts = df.loc[0, "time_utc"]
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["time_utc"]))
        self.assertEqual(ts, pd.Timestamp("2025-10-09T01:45:00Z"))

        # date_utc equals date part
        self.assertEqual(df.loc[0, "date_utc"], date(2025, 10, 9))

        # Wind speed and direction
        self.assertAlmostEqual(df.loc[0, "wspd_m_s"], 2.71)
        self.assertEqual(df.loc[0, "wdir_deg"], 323)

    def test_empty_input(self):
        # Empty string should produce an empty DataFrame with the expected columns
        df = parse_cdip_jdar_wind("")
        # DataFrame shape: zero rows
        self.assertEqual(len(df), 0)
        # Columns still present and in expected order
        self.assertListEqual(list(df.columns), self.expected_cols)

    def test_non_string_input(self):
        # Passing a non-string (None) should raise a TypeError when StringIO is called
        with self.assertRaises(TypeError):
            parse_cdip_jdar_wind(None)

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
