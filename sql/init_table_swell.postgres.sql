CREATE TABLE IF NOT EXISTS swell (
    id SERIAL PRIMARY KEY,
    station INTEGER NOT NULL,
    date_utc DATE NOT NULL,
    time_utc TIMESTAMPZ NOT NULL,
    hs_m REAL,
    tp_s REAL,
    dp_deg REAL,
    ta_s REAL
);
