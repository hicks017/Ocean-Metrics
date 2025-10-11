from io import StringIO
import pandas as pd
import re

def parse_cdip_pre_mp(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from 'mp: bulk parameters from
        spectral processing'.
    """
    if not isinstance(pre_text, str):
        raise TypeError("pre_text must be a str")

    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # station
        (4, 18),  # time_utc
        (20, 24), # hs_m
        (25, 30), # tp_s
        (31, 34), # dp_deg
        (35, 40), # ta_s
    ]
    col_names = ["station", "time_utc", "hs_m", "tp_s", "dp_deg", "ta_s"]

    # Format data frame
    buffer = StringIO(pre_text)
    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert time stamp column
    df['time_utc'] = pd.to_datetime(
        df['time_utc'],
        format='%Y%m%d%H%M%S',
        utc=True,
        errors='coerce'
    )

    # Extract date from time stamp
    df.insert(1, 'date_utc', df['time_utc'].dt.date)
    return df

def parse_cdip_pre_9c(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from '9c: 9-band combined energy
        and direction.
    """
    if not isinstance(pre_text, str):
        raise TypeError("pre_text must be a str")
        
    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # station
        (4, 16),  # time_utc
        (20, 23), # band_22s_plus_cm2
        (24, 27), # band_22s_plus_dir
        (31, 34), # band_22_18s_cm2
        (35, 38), # band_22_18s_dir
        (42, 45), # band_18_16s_cm2
        (46, 49), # band_18_16s_dir
        (53, 56), # band_16_14s_cm2
        (57, 60), # band_16_14s_dir
        (64, 67), # band_14_12s_cm2
        (68, 71), # band_14_12s_dir
        (75, 78), # band_12_10s_cm2
        (79, 82), # band_12_10s_dir
        (86, 89), # band_10_8s_cm2
        (90, 93), # band_10_8s_dir
        (97, 100), # band_8_6s_cm2
        (101, 104), # band_8_6s_dir
        (107, 111), # band_6_2s_cm2
        (112, 115), # band_6_2s_dir
    ]
    col_names = [
        "station",
        "time_utc",
        "band_22s_plus_cm2",
        "band_22s_plus_dir",
        "band_22_18s_cm2",
        "band_22_18s_dir",
        "band_18_16s_cm2",
        "band_18_16s_dir",
        "band_16_14s_cm2",
        "band_16_14s_dir",
        "band_14_12s_cm2",
        "band_14_12s_dir",
        "band_12_10s_cm2",
        "band_12_10s_dir",
        "band_10_8s_cm2",
        "band_10_8s_dir",
        "band_8_6s_cm2",
        "band_8_6s_dir",
        "band_6_2s_cm2",
        "band_6_2s_dir"
    ]

    # Format data frame
    buffer = StringIO(pre_text)
    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert time stamp column
    df['time_utc'] = pd.to_datetime(
        df['time_utc'],
        format='%Y%m%d%H%M',
        utc=True,
        errors='coerce'
    )

    # Extract date from time stamp
    df.insert(1, 'date_utc', df['time_utc'].dt.date)
    return df

def parse_cdip_pre_te(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from 'mp: bulk parameters from
        spectral processing'.
    """
    if not isinstance(pre_text, str):
        raise TypeError("pre_text must be a str")

    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # station
        (4, 18),  # time_utc
        (19, 24), # sst_c
        (26, 31), # sst_f
    ]
    col_names = ["station", "time_utc", "sst_c", "sst_f"]

    # Format data frame
    buffer = StringIO(pre_text)
    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert time stamp column
    df['time_utc'] = pd.to_datetime(
        df['time_utc'],
        format='%Y%m%d%H%M%S',
        utc=True,
        errors='coerce'
    )
    
    # Extract date from time stamp
    df.insert(1, 'date_utc', df['time_utc'].dt.date)
    return df

def parse_cdip_jdar_wind(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects a specific table header.
    """
    if not isinstance(pre_text, str):
        raise TypeError("pre_text must be a str")

    # Handle empty input
    if not pre_text.strip():
        return pd.DataFrame(columns=["station", "date_utc", "time_utc", "wspd_m_s", "wdir_deg"])

    # Capture station ID
    STATION = int(pre_text.split()[0])

    # Remove headers and header descriptions
    first_data_row = re.search(r'(?m)^20\d{2}', pre_text)
    if not first_data_row:
        pre_text_stripped = ''
    else:
        pre_text_stripped = pre_text[first_data_row.start():]

    # Remove leading/trailing blank lines
    lines = [ln.strip() for ln in pre_text_stripped.splitlines() if ln.strip() != ""]

    # Join lines into a single string for processing
    txt = "\n".join(lines)
    buffer = StringIO(txt)

    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 4), (5, 7), (8, 10), (11, 13), (14, 16),  # year, mo, dy, hr, mn
        (18, 22), (24, 28), (29, 32), (35, 40), (43, 47),  # hs_m, tp_sec, dp_deg, depth_m, ta_sec
        (47, 57), (57, 61), (62, 65), (65, 74), (74, 78)   # pres_mb, wspd_m_s, wdir_deg, tempair_c, tempsea_c
    ]

    col_names = [
        "year", "mo", "dy", "hr", "mn",
        "hs_m", "tp_sec", "dp_deg", "depth_m", "ta_sec",
        "pres_mb", "wspd_m_s", "wdir_deg",
        "tempair_c", "tempsea_c"
    ]

    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert all columns to numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # Create a single datetime column
    df['Time_utc'] = pd.to_datetime(
        {
            'year':   df['year'],
            'month':  df['mo'],
            'day':    df['dy'],
            'hour':   df['hr'],
            'minute': df['mn']
        },
        utc=True,
        errors='coerce'
    )
    
    # Extract date from time stamp
    df.insert(1, 'date_utc', df['time_utc'].dt.date)

    # Create column to indicate station
    df['station'] = STATION

    # Select columns
    df = df[['station', 'date_utc', 'time_utc', 'wspd_m_s', 'wdir_deg']]

    # Return the latest record
    return df.tail(1)
