import unittest
from urllib.parse import quote_plus
from src.fetch_data import build_url

class TestBuildUrl(unittest.TestCase):

    def test_default_station_table_and_days_zero(self):
        """Verify default station/table and days=0 → c0 with default source ndar."""
        url = build_url(station="ABC", table="XYZ")
        self.assertTrue(
            url.startswith("https://cdip.ucsd.edu/data_access/ndar?"),
            f"URL should start with ndar source, got: {url}"
        )
        self.assertIn(
            "?ABC+XYZ+c0",
            url,
            f"Query should contain 'ABC+XYZ+c0', got: {url}"
        )

    def test_days_positive_and_zero(self):
        """Test that positive days appear verbatim and zero becomes c0."""
        cases = [
            (5, "?ABC+XYZ+5"),
            (0, "?ABC+XYZ+c0"),
        ]
        for days, expected in cases:
            with self.subTest(days=days):
                url = build_url(station="ABC", table="XYZ", days=days)
                self.assertIn(
                    expected,
                    url,
                    f"For days={days}, expected segment '{expected}' in URL {url}"
                )

    def test_justdar_flag_logic(self):
        """Check justdar flag behavior for days=0 and days>0."""
        # justdar=False, days=0 → ndar, c0
        url1 = build_url(station="S", table="T", days=0, justdar=False)
        self.assertIn("/ndar?", url1)
        self.assertIn("?S+T+c0", url1)

        # justdar=True, days=0 → justdar.cdip, days forced to 1
        url2 = build_url(station="S", table="T", days=0, justdar=True)
        self.assertIn("/justdar.cdip", url2)
        self.assertIn("?S+T+1", url2)

        # justdar=True, days>0 → justdar.cdip, days unchanged
        url3 = build_url(station="S", table="T", days=7, justdar=True)
        self.assertIn("/justdar.cdip", url3)
        self.assertIn("?S+T+7", url3)

    def test_custom_base_url_and_single_slash(self):
        """Ensure custom base URL works and only one slash joins URL and source."""
        for base in ("http://example.com", "http://example.com/"):
            with self.subTest(base=base):
                url = build_url(station="A", table="B", url=base)
                # must start with base + '/ndar?'
                self.assertTrue(
                    url.startswith("http://example.com/ndar?"),
                    f"URL should start with 'http://example.com/ndar?', got: {url}"
                )
                # ensure no double slash before 'ndar'
                self.assertNotIn("//ndar", url)

    def test_query_encoding_special_characters(self):
        """Station/table with spaces/punctuation must be quote_plus-encoded."""
        station = "st#1"
        table = "ta ble"
        url = build_url(station=station, table=table)
        raw_query = f"{station} {table} c0"
        expected = quote_plus(raw_query)

        self.assertTrue(
            url.endswith(expected),
            f"URL should end with encoded query '{expected}', got: {url}"
        )
        # spot-check that '#' is percent-encoded and spaces become '+'
        self.assertIn("%23", url)
        self.assertIn("+", url)


if __name__ == "__main__":
    unittest.main()

# Created with AI assistance.
