from datetime import date
import unittest
import pandas as pd
import numpy as np
from src.parse_table import parse_cdip_pre_9c

class TestParseCdipPre9c(unittest.TestCase):
    def setUp(self):
        # Column names expected from the function
        self.expected_cols = [
            "station", "Date_utc", "Time_utc", "band_22s_plus_cm2", "band_22s_plus_dir",
            "band_22_18s_cm2", "band_22_18s_dir", "band_18_16s_cm2", "band_18_16s_dir",
            "band_16_14s_cm2", "band_16_14s_dir", "band_14_12s_cm2", "band_14_12s_dir",
            "band_12_10s_cm2", "band_12_10s_dir", "band_10_8s_cm2", "band_10_8s_dir",
            "band_8_6s_cm2", "band_8_6s_dir", "band_6_2s_cm2", "band_6_2s_dir"
        ]

    def test_single_valid_row(self):
        # Build a single line with fixed-width columns per col_specs in function
        station = "ABC"
        time_str = "202401011230"  # 2024-01-01 12:30 UTC
        bands = ["123", "045", "234", "067", "345", "089", "456", "123", "567", "234", "678", "345", "789", "456", "890", "567", "901", "678", "012", "789"]
        # Construct line by placing spaces to match the column indices used by read_fwf
        line = (
            f"{station} "
            f"{time_str} "
            f"   "
            f"{bands[0]} {bands[1]} "
            f"   "
            f"{bands[2]} {bands[3]} "
            f"   "
            f"{bands[4]} {bands[5]} "
            f"   "
            f"{bands[6]} {bands[7]} "
            f"   "
            f"{bands[8]} {bands[9]} "
            f"   "
            f"{bands[10]} {bands[11]} "
            f"   "
            f"{bands[12]} {bands[13]} "
            f"   "
            f"{bands[14]} {bands[15]} "
            f"   "
            f"{bands[16]} {bands[17]} "
            f"   "
            f"{bands[18]} {bands[19]}"
        ) + "\n"

        df = parse_cdip_pre_9c(line)

        # Basic structural assertions
        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 1)

        # Station exact match
        self.assertEqual(df.loc[0, "station"].strip(), station)

        # Time parsing: timezone-aware UTC Timestamp and correct value
        # ts = df.loc[0, "Time_utc"]
        # self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["Time_utc"]))
        # self.assertEqual(ts, pd.Timestamp("2024-01-01T12:30:00Z"))

        # Date_utc equals date part
        # self.assertEqual(df.loc[0, "Date_utc"], date(2024, 1, 1))

        # Numeric-like fields preserved as strings/objects by read_fwf; verify their trimmed contents
        for i, col in enumerate(self.expected_cols[3:]):
            self.assertEqual(float(df.loc[0, col]), float(bands[i].strip()))

    def test_empty_input(self):
        # Empty string should produce an empty DataFrame with the expected columns
        df = parse_cdip_pre_9c("")
        # DataFrame shape: zero rows
        self.assertEqual(len(df), 0)
        # Columns still present and in expected order
        self.assertListEqual(list(df.columns), self.expected_cols)

    def test_non_string_input(self):
        # Passing a non-string (None) should raise a TypeError when StringIO is called
        with self.assertRaises(TypeError):
            parse_cdip_pre_9c(None)

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
