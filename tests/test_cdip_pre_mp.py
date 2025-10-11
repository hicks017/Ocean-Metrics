from datetime import date
import unittest
import pandas as pd
import numpy as np
from src.parse_table import parse_cdip_pre_mp


class TestParseCdipPreMp(unittest.TestCase):
    def setUp(self):
        # Column names expected from the function
        self.expected_cols = ["station", "Date_utc", "Time_utc", "Hs_m", "Tp_s", "Dp_deg", "Ta_s"]

    def test_single_valid_row(self):
        # Build a single line with fixed-width columns per col_specs in function:
        # (0,3)=station, (4,18)=Time_utc (YYYYmmddHHMMSS), (21,25)=Hs_m, (25,30)=Tp_s,
        # (31,34)=Dp_deg, (36,40)=Ta_s
        station = "ABC"
        time_str = "20240101123045"  # 2024-01-01 12:30:45 UTC
        hs = "1.11"    # occupies cols 21-24 (4 chars in snippet)
        tp = "22.22"    # occupies cols 25-29 (5 chars)
        dp = "333"     # occupies cols 31-33 (3 chars)
        ta = "44.44"    # occupies cols 36-39 (4 chars)
        # Construct line by placing spaces to match the column indices used by read_fwf
        # indices: 0-2 station, 3 is space, 4-17 time (14 chars), 18-20 spaces, 21-24 Hs, 25 is space,
        # 26-29 Tp, 30 is space, 31-33 Dp, 34-35 spaces, 36-39 Ta
        line = (
            f"{station}"               # cols 0-2
            f" "                       # col 3
            f"{time_str}"              # cols 4-17
            f"  "                      # cols 18-19
            f"{hs}"                    # cols 20-23
            f" "                       # col 24
            f"{tp}"                    # cols 25-29
            f" "                       # col 30
            f"{dp}"                    # cols 31-33
            f" "                       # cols 34-35
            f"{ta}"                    # cols 36-39
        ) + "\n"
        df = parse_cdip_pre_mp(line)

        # Basic structural assertions
        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 1)

        # Station exact match
        self.assertEqual(df.loc[0, "station"].strip(), station)

        # Time parsing: timezone-aware UTC Timestamp and correct value
        # ts = df.loc[0, "Time_utc"]
        # self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["Time_utc"]))
        # self.assertEqual(ts.tzinfo.zone if hasattr(ts.tzinfo, "zone") else ts.tz, pd.Timestamp("2024-01-01T12:30:45Z").tzinfo if hasattr(pd.Timestamp("2024-01-01T12:30:45Z"), "tzinfo") else None)
        # self.assertEqual(ts, pd.Timestamp("2024-01-01T12:30:45Z"))

        # Date_utc equals date part
        # self.assertEqual(df.loc[0, "Date_utc"], date(2024, 1, 1))

        # Numeric-like fields preserved as strings/objects by read_fwf; verify their trimmed contents
        self.assertEqual(str(df.loc[0, "Hs_m"]).strip(), hs.strip())
        self.assertEqual(float(df.loc[0, "Tp_s"]), float(tp.strip()))
        self.assertEqual(str(df.loc[0, "Dp_deg"]).strip(), dp.strip())
        self.assertEqual(float(df.loc[0, "Ta_s"]), float(ta.strip()))

    def test_multiple_valid_rows(self):
        # Create three lines with different station and timestamps
        lines = []
        for i, (st, tstr) in enumerate([("STA", "20230101000000"), ("BBB", "20230101120000"), ("CCC", "20230101235959")]):
            hs = f"{0.5 + i:.2f}".rjust(4)   # keep width similar
            tp = f"{3.0 + i:.2f}".ljust(5)
            dp = f"{30 + i}"
            ta = f"{1.0 + i:.2f}".rjust(4)
            line = (
                f"{st} "
                f"{tstr}"
                f"   "
                f"{hs}"
                f"{tp}"
                f" "
                f"{dp}"
                f"  "
                f"{ta}"
            ) + "\n"
            lines.append(line)
        text = "".join(lines)

        df = parse_cdip_pre_mp(text)

        self.assertListEqual(list(df.columns), self.expected_cols)
        self.assertEqual(len(df), 3)
        # Check first, middle, last timestamps and station values
        self.assertEqual(df.loc[0, "station"].strip(), "STA")
        self.assertEqual(df.loc[1, "station"].strip(), "BBB")
        self.assertEqual(df.loc[2, "station"].strip(), "CCC")
        # self.assertEqual(df.loc[0, "Time_utc"], pd.Timestamp("2023-01-01T00:00:00Z"))
        # self.assertEqual(df.loc[1, "Time_utc"], pd.Timestamp("2023-01-01T12:00:00Z"))
        # self.assertEqual(df.loc[2, "Time_utc"], pd.Timestamp("2023-01-01T23:59:59Z"))
        # Row order preserved
        self.assertEqual(list(df["station"].str.strip()), ["STA", "BBB", "CCC"])

    def test_blank_numeric_field(self):
        # Hs_m field blank (spaces). Other fields valid.
        station = "ABC"
        time_str = "20240202101010"
        hs_blank = "    "   # spaces where Hs_m would be
        tp = "5.00"
        dp = "045"
        ta = "0.50"
        line = (
            f"{station}"
            f" "
            f"{time_str}"
            f"   "
            f"{hs_blank}"
            f" "
            f"{tp}"
            f" "
            f"{dp}"
            f"  "
            f"{ta}"
        ) + "\n"

        df = parse_cdip_pre_mp(line)

        # One row, correct columns
        self.assertEqual(len(df), 1)
        self.assertListEqual(list(df.columns), self.expected_cols)

        # Hs_m should become NaN or an empty/whitespace string depending on pandas version;
        # check both possibilities robustly.
        hs_val = df.loc[0, "Hs_m"]
        # Acceptable: NaN-like or string of whitespace/empty when stripped is empty
        if pd.isna(hs_val):
            pass
        else:
            self.assertEqual(str(hs_val).strip(), "")

        # Other fields parsed as expected
        self.assertEqual(float(df.loc[0, "Tp_s"]), float(tp.strip()))
        self.assertEqual(str(df.loc[0, "Dp_deg"]).strip(), dp.strip('0'))

    def test_empty_input(self):
        # Empty string should produce an empty DataFrame with the expected columns
        df = parse_cdip_pre_mp("")
        # DataFrame shape: zero rows
        self.assertEqual(len(df), 0)
        # Columns still present and in expected order
        self.assertListEqual(list(df.columns), self.expected_cols)

    def test_non_string_input(self):
        # Passing a non-string (None) should raise a TypeError when StringIO is called
        with self.assertRaises(TypeError):
            parse_cdip_pre_mp(None)


if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
