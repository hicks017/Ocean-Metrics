from datetime import date
import unittest
import pandas as pd
from src.parse_table import parse_cdip_pre_te

class TestParseCdipPreTe(unittest.TestCase):
    def setUp(self):
        # Column names expected from the function
        self.expected_cols = ["station", "date_utc", "time_utc", "sst_c", "sst_f"]

    def test_single_valid_row(self):
        # Build a single line with fixed-width columns per col_specs in function
        station = 123
        time_str = "20240101123045"  # 2024-01-01 12:30:45 UTC
        sst_c = "12.34"  # occupies cols 19-23 (5 chars)
        sst_f = "54.32"  # occupies cols 26-30 (5 chars)
        # Construct line by placing spaces to match the column indices used by read_fwf
        line = (
            f"{station} "
            f"{time_str} "
            f"{sst_c} "
            f" "
            f"{sst_f}"
        ) + "\n"

        df = parse_cdip_pre_te(line)

        # Basic structural assertions
        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 1)

        # Station exact match
        self.assertEqual(df.loc[0, "station"], station)

        # Time parsing: timezone-aware UTC Timestamp and correct value
        ts = df.loc[0, "time_utc"]
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["time_utc"]))
        self.assertEqual(ts, pd.Timestamp("2024-01-01T12:30:45Z"))

        # date_utc equals date part
        self.assertEqual(df.loc[0, "date_utc"], date(2024, 1, 1))

        # Numeric-like fields preserved as strings/objects by read_fwf; verify their trimmed contents
        self.assertEqual(str(df.loc[0, "sst_c"]).strip(), sst_c.strip())
        self.assertEqual(str(df.loc[0, "sst_f"]).strip(), sst_f.strip())

    def test_empty_input(self):
        # Empty string should produce an empty DataFrame with the expected columns
        df = parse_cdip_pre_te("")
        # DataFrame shape: zero rows
        self.assertEqual(len(df), 0)
        # Columns still present and in expected order
        self.assertListEqual(list(df.columns), self.expected_cols)

    def test_non_string_input(self):
        # Passing a non-string (None) should raise a TypeError when StringIO is called
        with self.assertRaises(TypeError):
            parse_cdip_pre_te(None)

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
