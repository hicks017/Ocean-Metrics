import pandas as pd
from datetime import date, datetime
from sqlalchemy.engine import Engine

def dialect_name(engine: Engine) -> str:
    return engine.dialect.name  # 'sqlite' or 'postgresql'

def prepare_df_for_db(df: pd.DataFrame, engine: Engine) -> pd.DataFrame:
    dname = dialect_name(engine)
    df = df.copy()

    # ensure station column type
    if "station" in df.columns:
        df["station"] = pd.to_numeric(df["station"], errors="coerce").astype("Int64")

    # date/datetime handling
    if "date_utc" in df.columns:
        dt = pd.to_datetime(df["date_utc"], errors="coerce")
        if dname == "sqlite":
            df["date_utc"] = dt.dt.date.astype("object").astype(str)
        else:  # postgresql
            df["date_utc"] = dt.dt.date  # python date objects
    if "time_utc" in df.columns:
        tt = pd.to_datetime(df["time_utc"], errors="coerce", utc=True)
        if dname == "sqlite":
            df["time_utc"] = tt.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:  # postgresql
            df["time_utc"] = tt
    return df

def scalar_for_db(val, engine: Engine, kind: str="date"):
    dname = dialect_name(engine)
    if pd.isna(val):
        return None
    if kind == "date":
        ts = pd.to_datetime(val, errors="coerce")
        if pd.isna(ts):
            return None
        if dname == "sqlite":
            return ts.date().isoformat()
        else:
            return ts.date().to_pydatetime().date()
    if kind in c("datetime", "timestamp", "ts"):
        ts = pd.to_datetime(val, utc=True, errors="coerce")
        if pd.isna(ts):
            return None
        if dname == "sqlite":
            return ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(ts, pd.Timestamp) else ts.isoformat()
        else:
            return ts.time().to_pydatetime()
