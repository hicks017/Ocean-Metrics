import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def build_url(station: str, table: str, days: int = 0, url: str = "https://cdip.ucsd.edu/data_access", justdar: bool = False) -> str:
    """
    Build the URL with a custom query string.
    The site expects something such as '?100+mp+1'.
    Days = 0 will fetch most recent record.
    """
    base = url.rstrip("/")

    if days == 0:
        days = "c0"
    if justdar:
        source = "justdar.cdip"
        if days == "c0":
            days = 1
    else:
        source = "ndar"
    query = f"{station} {table} {days}"
    return f"{base}/{source}?{quote_plus(query)}"

def fetch_pre_text(url: str, timeout: int = 10) -> str:
    """
    Download the page and return the text contents of the first <pre> block.
    Raises RunetimeError if something goes wrong.
    """
    # Extract station ID from the URL query string, expected like '?100+mp+1'
    # Station is the characters between '?' and the first '+'
    qstart = url.index('?') + 1
    qend = url.index('+', qstart)
    station = url[qstart:qend]

    headers = {"User-Agent": "python-requests/table_download (+https://github.com/hicks017/Ocean-Metrics)"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    pre_tag = soup.find("pre")
    if pre_tag is None:
        raise RuntimeError("No <pre> block found on page; page layout may have changed.")

    pre_text = pre_tag.get_text()
    if not pre_text.strip():
        raise RuntimeError("Empty <pre> block found on page; data may not exist for the query")
    
    data = f'{station} {pre_text}'
    return data
