from datetime import date
import unittest
import pandas as pd
from src.parse_table import parse_cdip_jdar_wind

class TestParseCdipJdarWind(unittest.TestCase):
    def setUp(self):
        # Column names expected from the function
        self.expected_cols = ["station", "Date_utc", "Time_utc", "Wspd_m_s", "Wdir_deg"]

    def test_single_valid_row_with_headers(self):
        # Input data with headers and a single valid row
        station = "123"
        headers = "YEAR MO DY HR MN Hs_m Tp_sec Dp_deg Depth_m Ta_sec Pres_mB Wspd_m_s Wdir_deg TempAir_C TempSea_C"
        header_descriptions = "      UTC           m   sec  deg     m     sec    mB     m/s  deg Air(C) Sfc(C) Mid(C) Bot(C)"
        data_row = "2025 10 09 01 45  0.52  9.14         4.62  5.39          2.71 323              "
        input_text = f"{station} {headers}\n{header_descriptions}\n{data_row} "

        df = parse_cdip_jdar_wind(input_text)

        # Basic structural assertions
        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 1)

        # Station exact match
        self.assertEqual(df.loc[0, "station"], int(station))

        # Time parsing: timezone-aware UTC Timestamp and correct value
        ts = df.loc[0, "Time_utc"]
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["Time_utc"]))
        self.assertEqual(ts, pd.Timestamp("2025-10-09T01:45:00Z"))

        # Date_utc equals date part
        self.assertEqual(df.loc[0, "Date_utc"], date(2025, 10, 9))

        # Wind speed and direction
        self.assertAlmostEqual(df.loc[0, "Wspd_m_s"], 2.71)
        self.assertEqual(df.loc[0, "Wdir_deg"], 323)

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
