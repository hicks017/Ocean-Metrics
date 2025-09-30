CREATE TABLE IF NOT EXISTS wind (
    id {id_def},
    Station INTEGER NOT NULL,
    Date_utc TEXT NOT NULL,
    Time_utc TEXT NOT NULL,
    Wspd_m_s REAL,
    Wdir_deg REAL
);
