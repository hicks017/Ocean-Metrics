import unittest
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, Timeout
from src.fetch_data import fetch_pre_text  


class TestFetchPreText(unittest.TestCase):
    def setUp(self):
        # URL with station “ABC” (between '?' and first '+')
        self.url = "http://example.com/data?ABC+rest"
        self.user_agent = (
            "python-requests/table_download "
            "(+https://github.com/hicks017/Ocean-Metrics)"
        )

    @patch("src.fetch_data.requests.get")
    def test_successful_fetch_and_parse_first_pre_only(self, mock_get):
        """Mock 200 response with HTML having multiple <pre>; only first used."""
        html = "<html><body>" \
               "<pre>first line</pre>" \
               "<pre>second line</pre>" \
               "</body></html>"

        resp = Mock()
        resp.status_code = 200
        resp.text = html
        resp.raise_for_status = Mock(return_value=None)
        mock_get.return_value = resp

        result = fetch_pre_text(self.url)
        # Should prefix station and pick only the first <pre> text
        self.assertEqual(result, "ABC first line")

    @patch("src.fetch_data.requests.get")
    def test_missing_pre_block_raises_runtime_error(self, mock_get):
        """HTML with no <pre> or find("pre") → RuntimeError."""
        html = "<html><body><div>No pre here</div></body></html>"

        resp = Mock()
        resp.status_code = 200
        resp.text = html
        resp.raise_for_status = Mock(return_value=None)
        mock_get.return_value = resp

        with self.assertRaises(RuntimeError) as ctx:
            fetch_pre_text(self.url)

        self.assertIn("No <pre> block", str(ctx.exception))

    @patch("src.fetch_data.requests.get")
    def test_empty_pre_text_treated_as_no_content(self, mock_get):
        """A <pre> whose get_text() returns '' should raise RuntimeError."""
        html = "<html><body><pre>   </pre></body></html>"
        # Note: BeautifulSoup.get_text() would return whitespace → strip to empty
        resp = Mock()
        resp.status_code = 200
        resp.text = html
        resp.raise_for_status = Mock(return_value=None)
        mock_get.return_value = resp

        with self.assertRaises(RuntimeError):
            fetch_pre_text(self.url)

    @patch("src.fetch_data.requests.get")
    def test_http_error_bubbles_up(self, mock_get):
        """Simulate non-200 status → raise_for_status raises HTTPError."""
        resp = Mock()
        resp.raise_for_status = Mock(side_effect=HTTPError("404 Not Found"))
        mock_get.return_value = resp

        with self.assertRaises(HTTPError):
            fetch_pre_text(self.url)

    @patch("src.fetch_data.requests.get")
    def test_timeout_propagation_and_header(self, mock_get):
        """Ensure Timeout is propagated and headers & timeout args are correct."""
        # Prepare the side_effect to raise on call
        mock_get.side_effect = Timeout("timed out")

        # Default timeout
        with self.assertRaises(Timeout):
            fetch_pre_text(self.url)
        mock_get.assert_called_with(
            self.url,
            headers={"User-Agent": self.user_agent},
            timeout=10
        )

        mock_get.reset_mock()

        # Custom timeout
        with self.assertRaises(Timeout):
            fetch_pre_text(self.url, timeout=1)
        mock_get.assert_called_with(
            self.url,
            headers={"User-Agent": self.user_agent},
            timeout=1
        )


if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
