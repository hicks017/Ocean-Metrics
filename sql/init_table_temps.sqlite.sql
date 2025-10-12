CREATE TABLE IF NOT EXISTS temps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station INTEGER NOT NULL,
    date_utc TEXT NOT NULL,
    time_utc TEXT NOT NULL,
    sst_c REAL,
    sst_f REAL
);
