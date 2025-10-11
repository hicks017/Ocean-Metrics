## Overview

Step-by-step plan to support both SQLite and PostgreSQL initializations and to convert pandas columns dynamically before writes. Each step includes the change, why it’s needed, and a minimal code example or template you can drop into your project.

## 1. Add Postgres-specific DDL files

- Change: Create Postgres versions of your four SQL init files in project/sql, e.g.:
    - sql/init_table_swell.sqlite.sql (existing) — SQLite-friendly (TEXT for dates)
    - sql/init_table_swell.postgres.sql — Postgres-friendly (DATE / TIMESTAMP)
- Why: Keep both schemas side-by-side so init_db can choose the correct one without ad-hoc string edits.
- Example Postgres template (swell):

```sql
CREATE TABLE IF NOT EXISTS swell (
    id {id_def},
    station INTEGER NOT NULL,
    date_utc DATE NOT NULL,
    time_utc TIME NOT NULL,
    hs_m REAL,
    tp_s REAL,
    dp_deg REAL,
    ta_s REAL,
    UNIQUE(date_utc, station)
);
```

- Note: Use consistent lowercase names across DBs (station, date_utc, time_utc) to avoid reflection mismatches.

## 2. Update load_ddl to pick file by dialect

- Change: Modify storage.load_ddl to accept dialect or detect USE_POSTGRES and load the correct SQL file name.
- Why: Centralize selection logic; keep existing files unchanged.
- Code sketch (replace load_ddl in storage.py):

```python
def load_ddl(table_name: str, dialect: str) -> str:
    """
    Reads the external SQL file for a table and dialect.
    Expect files named init_table_<table>.<dialect>.sql under project/sql/.
    dialect: 'sqlite' or 'postgres'
    """
    filename = f"init_table_{table_name}.postgres.sql" if dialect == "postgres" else f"init_table_{table_name}.sqlite.sql"
    sql_file = ROOT / "sql" / filename
    if not sql_file.exists():
        raise FileNotFoundError(f"DDL not found: {sql_file}")
    return sql_file.read_text()
```

- Integrate with init_db by detecting dialect: `dialect = "postgres" if USE_POSTGRES else "sqlite"`.

## 3. Make init_db call the dialect-aware loader and create indexes with correct column names

- Change: Pass dialect into load_ddl and normalize index column names to match the schema (use lowercase names).
- Why: Avoid casing issues and mismatched columns when creating indexes.
- Key edits in init_db:

```python
dialect = "postgres" if USE_POSTGRES else "sqlite"
ddl = load_ddl(table, dialect).format(id_def=id_def)
conn.execute(text(ddl))
# Index creation: use 'date_utc' and 'station' (lowercase)
for col in ["date_utc", "station"]:
    idx = f"idx_{table}_{col}"
    sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
    conn.execute(text(sql))
```

## 4. Add a small helper module for dtype/format conversion

- Change: New module src/db_utils.py with functions that:
    - Detect dialect from SQLAlchemy engine.
    - Convert pandas DataFrame columns to appropriate Python types for the target DB.
    - Convert single scalar values used in duplicate checks.
- Why: Keep conversion logic centralized and reused by fetch/insert code.
- Minimal db_utils.py:

```python
import pandas as pd
from datetime import date, datetime
from sqlalchemy.engine import Engine

def dialect_name(engine: Engine) -> str:
    return engine.dialect.name  # 'sqlite' or 'postgresql'

def prepare_df_for_db(df: pd.DataFrame, engine: Engine) -> pd.DataFrame:
    dname = dialect_name(engine)
    df = df.copy()
    # normalize column names to lowercase snake_case expected by DDL
    col_map = {c: c.lower() for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    # ensure station column type
    if "station" in df.columns:
        df["station"] = df["station"].apply(lambda v: int(v) if pd.notna(v) else None)

    # date/datetime handling
    if "date_utc" in df.columns:
        dt = pd.to_datetime(df["date_utc"], errors="coerce")
        if dname == "sqlite":
            df["date_utc"] = dt.dt.date.astype("object").astype(str)
        else:  # postgresql
            df["date_utc"] = dt.dt.date  # python date objects
    if "time_utc" in df.columns:
        tt = pd.to_datetime(df["time_utc"], errors="coerce")
        if dname == "sqlite":
            df["time_utc"] = tt.dt.time.astype("object").astype(str)
        else:
            # For Postgres TIME, keep as Python time objects
            # NOTE that I actually want to retain date and time into a date+time object, not a time object. Do the same for all occurences of time_utc.
            df["time_utc"] = tt.dt.time
    # handle combined datetime column if present
    if "datetime_utc" in df.columns and ("date_utc" not in df.columns or "time_utc" not in df.columns):
        full = pd.to_datetime(df["datetime_utc"], errors="coerce", utc=True)
        if dname == "sqlite":
            df["date_utc"] = full.dt.date.astype(str)
            df["time_utc"] = full.dt.time.astype(str)
        else:
            df["date_utc"] = full.dt.date
            df["time_utc"] = full.dt.time
    return df

def scalar_for_db(val, engine: Engine, kind: str="date"):
    dname = dialect_name(engine)
    if pd.isna(val):
        return None
    if kind == "date":
        ts = pd.to_datetime(val, errors="coerce")
        if dname == "sqlite":
            return ts.date().isoformat() if not pd.isna(ts) else None
        else:
            return ts.date().to_pydatetime().date() if not pd.isna(ts) else None
    if kind == "time":
        ts = pd.to_datetime(val, errors="coerce")
        if dname == "sqlite":
            return ts.time().isoformat(timespec="seconds") if not pd.isna(ts) else None
        else:
            return ts.time().to_pydatetime().time() if not pd.isna(ts) else None
```

- Note: adjust timezone handling for Postgres TIMESTAMP WITH TIME ZONE: convert to UTC before .to_pydatetime().

## 5. Wire conversion into fetch_parse_store (tasks.py)

- Change: Call prepare_df_for_db before doing the duplicate check and prior to df.to_sql.
- Why: Duplicate check must compare like-for-like types; df.to_sql should receive correctly typed values.
- Key patch inside fetch_parse_store before reflection/check:

```python
engine = get_connection()
# convert dataframe to match target DB types/names
from src.db_utils import prepare_df_for_db, scalar_for_db
df = prepare_df_for_db(df, engine)

metadata = MetaData()
table_obj = Table(table_name, metadata, autoload_with=engine)

# use lower-case column names in checks
row_date = scalar_for_db(df["date_utc"].iloc[0], engine, kind="date")
row_station = int(df["station"].iloc[0])

check_stmt = select(func.count()).select_from(table_obj).where(
    and_(
        table_obj.c.date_utc == row_date,
        table_obj.c.station == row_station
    )
)
```

- After check, call df.to_sql(table_name, engine, if_exists="append", index=False).
- Ensure the SQL table columns are lowercase to match df.rename behavior.

## 6. Testing and CI checklist

- For SQLite:
    - Run init_db with USE_POSTGRES=False and verify the SQLite file is created and tables exist.
    - Run one fetch_parse_store cycle; confirm strings inserted and duplicates detected.
- For Postgres:
    - Run init_db with USE_POSTGRES=True against a test Postgres (Docker or test server).
    - Confirm tables use DATE/TIME/TIMESTAMP types and that inserts use Python date/datetime objects (no string coercion).
    - Test timezone handling: convert datetimes to UTC before insert when using TIMESTAMP WITH TIME ZONE.
- Extra tests:
    - Use a small sample DataFrame to simulate parsed output with datetime, date, and combined datetime to ensure normalization works.
    - Add unit tests for db_utils.prepare_df_for_db and scalar_for_db for both dialects.

## Optional improvements

- Use SQLAlchemy Table metadata definitions (one central model) to avoid reflection at runtime and to guarantee consistent types for Postgres.
- Use Alembic for Postgres migrations if schema will evolve.
- Add logging around conversions (debug level) to make it easier to inspect the exact values used for duplicate checks.

## Final notes

- Keep column names consistent and lowercase across SQL files and your DataFrame renaming logic to avoid reflection mismatches.
- Treat SQLite as storing strings (ISO 8601), and Postgres as storing native DATE/TIMESTAMP types; use the helper functions to convert automatically based on engine.dialect.name