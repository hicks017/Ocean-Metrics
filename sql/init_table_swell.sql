CREATE TABLE IF NOT EXISTS swell (
    id {id_def},
    Station INTEGER NOT NULL,
    Date_utc TEXT NOT NULL,
    Time_utc TEXT NOT NULL,
    Hs_m REAL,
    Tp_s REAL,
    Dp_deg REAL,
    Ta_s REAL,
    UNIQUE(Date_utc, Station)
);
