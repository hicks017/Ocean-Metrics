CREATE TABLE IF NOT EXISTS wind (
    id SERIAL PRIMARY KEY,
    station INTEGER NOT NULL,
    date_utc DATE NOT NULL,
    time_utc TIMESTAMPZ NOT NULL,
    wspd_m_s REAL,
    wdir_deg REAL
);
