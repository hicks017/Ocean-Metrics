CREATE TABLE IF NOT EXISTS swell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station INTEGER NOT NULL,
    date_utc TEXT NOT NULL,
    time_utc TEXT NOT NULL,
    hs_m REAL,
    tp_s REAL,
    dp_deg REAL,
    ta_s REAL
);
