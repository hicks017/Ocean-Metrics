CREATE TABLE IF NOT EXISTS temps (
    id SERIAL PRIMARY KEY,
    station INTEGER NOT NULL,
    date_utc DATE NOT NULL,
    time_utc TIMESTAMPZ NOT NULL,
    sst_c REAL,
    sst_f REAL
);
