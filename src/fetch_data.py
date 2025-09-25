from urllib.parse import quote_plus

def build_url(station: str, table:str, days: int = 0, url: str = "https://cdip.ucsd.edu/data_access/ndar") -> str:
    """
    Build the URL with a custom query string.
    The site expects something such as '?100+mp+1'.
    Days = 0 will fetch most recent record.
    """
    if days == 0:
        days = "c0"
    query = f"{station} {table} {days}"
    return f"{url}?{quote_plus(query)}"
