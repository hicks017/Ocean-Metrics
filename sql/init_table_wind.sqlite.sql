CREATE TABLE IF NOT EXISTS wind (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station INTEGER NOT NULL,
    date_utc TEXT NOT NULL,
    time_utc TEXT NOT NULL,
    wspd_m_s REAL,
    wdir_deg REAL
);
