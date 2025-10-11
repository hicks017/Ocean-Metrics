CREATE TABLE IF NOT EXISTS temps (
    id {id_def},
    Station INTEGER NOT NULL,
    Date_utc TEXT NOT NULL,
    Time_utc TEXT NOT NULL,
    SST_C REAL,
    SST_F REAL,
    UNIQUE(Date_utc, Station)
);
