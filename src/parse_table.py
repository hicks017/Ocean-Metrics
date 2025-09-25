from io import StringIO
import pandas as pd

def parse_cdip_pre_mp(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from 'mp: bulk parameters from
        spectral processing'.
    """
    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # Station
        (4, 18),  # Time_utc
        (21, 25), # Hs_m
        (25, 30), # Tp_s
        (31, 34), # Dp_deg
        (36, 40), # Ta_s
    ]
    col_names = ["Station", "Time_utc", "Hs_m", "Tp_s", "Dp_deg", "Ta_s"]

    # Format data frame
    buffer = StringIO(pre_text)
    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert time stamp column
    df['Time_utc'] = pd.to_datetime(
        df['Time_utc'],
        format='%Y%m%d%H%M%S',
        utc=True
    )
    return df

def parse_cdip_pre_9c(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from '9c: 9-band combined energy
        and direction.
    """
    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # Station
        (4, 16),  # Time_utc
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
        "Station",
        "Time_utc",
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
    df['Time_utc'] = pd.to_datetime(
        df['Time_utc'],
        format='%Y%m%d%H%M',
        utc=True
    )
    return df

def parse_cdip_pre_te(pre_text: str) -> pd.DataFrame:
    """
    Parse the whitespace-formatted text into a DataFrame.
    This function expects the table headers from 'mp: bulk parameters from
        spectral processing'.
    """
    # Use fixed-width format to ensure proper column alignment
    col_specs = [
        (0, 3),   # Station
        (4, 18),  # Time_utc
        (19, 24), # SST_C
        (26, 31), # SST_F
    ]
    col_names = ["Station", "Time_utc", "SST_C", "SST_F"]

    # Format data frame
    buffer = StringIO(pre_text)
    df = pd.read_fwf(buffer, colspecs=col_specs, header=None, names=col_names)

    # Convert time stamp column
    df['Time_utc'] = pd.to_datetime(
        df['Time_utc'],
        format='%Y%m%d%H%M%S',
        utc=True
    )
    return df
