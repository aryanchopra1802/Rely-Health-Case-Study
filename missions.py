"""Space missions data analysis"""

import pandas as pd
from pathlib import Path

_df = None
_MAX_YEAR = 9999
_REQUIRED_COLUMNS = {
    'Company', 'Location', 'Date', 'Rocket', 'Mission', 'RocketStatus', 'MissionStatus',
}


# Validation helpers 

def _validate_company_name(companyName, func_name: str) -> str:
    if companyName is None:
        raise TypeError(f"{func_name}() requires a string for 'companyName', got None.")
    if not isinstance(companyName, str):
        raise TypeError(
            f"{func_name}() requires a string for 'companyName', "
            f"got {type(companyName).__name__!r} ({companyName!r})."
        )
    return companyName.strip()


def _validate_year(value, param_name: str, func_name: str) -> int:
    # bool is a subclass of int in Python, so check it first
    if isinstance(value, bool):
        raise TypeError(
            f"{func_name}() requires an integer for {param_name!r}, "
            f"got bool ({value!r})."
        )
    if not isinstance(value, int):
        raise TypeError(
            f"{func_name}() requires an integer for {param_name!r}, "
            f"got {type(value).__name__!r} ({value!r})."
        )
    if value < 1:
        raise ValueError(f"{func_name}(): {param_name!r} must be >= 1, got {value}.")
    if value > _MAX_YEAR:
        raise ValueError(f"{func_name}(): {param_name!r} must be <= {_MAX_YEAR}, got {value}.")
    return value


def _validate_date_string(value, param_name: str, func_name: str) -> pd.Timestamp:
    """Requires a non-empty string in strict YYYY-MM-DD format."""
    if value is None:
        raise TypeError(f"{func_name}() requires a string for {param_name!r}, got None.")
    if not isinstance(value, str):
        raise TypeError(
            f"{func_name}() requires a string for {param_name!r}, "
            f"got {type(value).__name__!r} ({value!r})."
        )
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{func_name}(): {param_name!r} must not be empty.")
    try:
        return pd.to_datetime(stripped, format="%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(
            f"{func_name}(): {param_name!r} must be 'YYYY-MM-DD', got {stripped!r}."
        )


def _validate_n(n, func_name: str) -> int:
    if isinstance(n, bool):
        raise TypeError(f"{func_name}() requires an integer for 'n', got bool ({n!r}).")
    if not isinstance(n, int):
        raise TypeError(
            f"{func_name}() requires an integer for 'n', "
            f"got {type(n).__name__!r} ({n!r})."
        )
    if n < 0:
        raise ValueError(f"{func_name}(): 'n' must be >= 0, got {n}.")
    return n


#  Data loading 

def _load_data(csv_path: str = "space_missions.csv") -> pd.DataFrame:
    """Load, clean, and cache the CSV. Returns a copy of the cached dataframe."""
    global _df

    if _df is not None:
        return _df.copy()

    path = Path(csv_path)
    if not path.exists():
        for alt in ["space_missions 123.csv", "space_missions (1) 2.csv",
                    "space_missions (1).csv", "space_missions.csv"]:
            if Path(alt).exists():
                path = Path(alt)
                break
        else:
            raise FileNotFoundError(f"Could not find CSV file: {csv_path!r}.")

    try:
        df = pd.read_csv(path, na_values=[''], keep_default_na=False, on_bad_lines='warn')
    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file {path!r} is empty.")

    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV missing required columns: {sorted(missing)}. "
            f"Found: {sorted(df.columns.tolist())}."
        )

    if 'Price' in df.columns:
        df['Price'] = df['Price'].replace('', pd.NA)
        df['Price'] = df['Price'].astype(str).str.replace('"', '').str.replace(',', '')
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year

    for col in _REQUIRED_COLUMNS - {'Date'}:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    _df = df
    return _df.copy()


#  Public functions 

def getMissionCountByCompany(companyName: str) -> int:
    """Returns total mission count for a company. Returns 0 if not found."""
    name = _validate_company_name(companyName, "getMissionCountByCompany")
    df = _load_data()
    return int(len(df[df['Company'] == name]))


def getSuccessRate(companyName: str) -> float:
    """Returns success rate (0–100) for a company, rounded to 2 decimal places."""
    name = _validate_company_name(companyName, "getSuccessRate")
    df = _load_data()
    missions = df[df['Company'] == name]
    if len(missions) == 0:
        return 0.0
    success_count = int((missions['MissionStatus'] == 'Success').sum())
    return round(success_count / len(missions) * 100, 2)


def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    """Returns mission names between startDate and endDate (YYYY-MM-DD), sorted chronologically."""
    start = _validate_date_string(startDate, "startDate", "getMissionsByDateRange")
    end   = _validate_date_string(endDate,   "endDate",   "getMissionsByDateRange")
    if start > end:
        raise ValueError(
            f"getMissionsByDateRange(): startDate ({startDate!r}) must not be after endDate ({endDate!r})."
        )
    df = _load_data()
    filtered = df[(df['Date'] >= start) & (df['Date'] <= end)].sort_values('Date')
    return filtered['Mission'].tolist()


def getTopCompaniesByMissionCount(n: int) -> list:
    """Returns top N companies as [(name, count), ...], sorted by count desc then name asc."""
    n = _validate_n(n, "getTopCompaniesByMissionCount")
    if n == 0:
        return []
    df = _load_data()
    counts = df['Company'].value_counts()
    company_counts = pd.DataFrame({'Company': counts.index, 'Count': counts.values})
    company_counts = company_counts.sort_values(by=['Count', 'Company'], ascending=[False, True])
    top_n = company_counts.head(n)
    return list(zip(top_n['Company'], top_n['Count']))


def getMissionStatusCount() -> dict:
    """Returns mission counts by status. All four expected keys are always present."""
    df = _load_data()
    raw = df['MissionStatus'].value_counts().to_dict()
    expected = ["Success", "Failure", "Partial Failure", "Prelaunch Failure"]
    return {status: int(raw.get(status, 0)) for status in expected}


def getMissionsByYear(year: int) -> int:
    """Returns total missions launched in a given year. Returns 0 if none found."""
    year = _validate_year(year, "year", "getMissionsByYear")
    df = _load_data()
    return int(len(df[df['Year'] == year]))


def getMostUsedRocket() -> str:
    """Returns the most frequently used rocket name. Alphabetical tie-break."""
    df = _load_data()
    rockets = df['Rocket'].replace('', pd.NA).dropna()
    if rockets.empty:
        return ""
    counts = rockets.value_counts()
    tied = counts[counts == counts.max()]
    return sorted(tied.index.tolist())[0]


def getAverageMissionsPerYear(startYear: int, endYear: int) -> float:
    """Returns average missions per year over the given range, rounded to 2 decimal places."""
    startYear = _validate_year(startYear, "startYear", "getAverageMissionsPerYear")
    endYear   = _validate_year(endYear,   "endYear",   "getAverageMissionsPerYear")
    if startYear > endYear:
        raise ValueError(
            f"getAverageMissionsPerYear(): startYear ({startYear}) must not exceed endYear ({endYear})."
        )
    df = _load_data()
    total = int(((df['Year'] >= startYear) & (df['Year'] <= endYear)).sum())
    return round(total / (endYear - startYear + 1), 2)


def reload_data(csv_path: str = "space_missions.csv"):
    """Force a fresh reload of the CSV (clears the cache)."""
    global _df
    _df = None
    return _load_data(csv_path)


if __name__ == "__main__":
    print("Testing space missions functions...\n")
    try:
        print(f"SpaceX missions:        {getMissionCountByCompany('SpaceX')}")
        print(f"SpaceX success rate:    {getSuccessRate('SpaceX')}%")
        print(f"Missions Jan 2020:      {len(getMissionsByDateRange('2020-01-01', '2020-01-31'))}")
        print(f"Top 3 companies:        {getTopCompaniesByMissionCount(3)}")
        print(f"Status counts:          {getMissionStatusCount()}")
        print(f"Missions in 2020:       {getMissionsByYear(2020)}")
        print(f"Most used rocket:       {getMostUsedRocket()}")
        print(f"Avg missions 2010-2020: {getAverageMissionsPerYear(2010, 2020)}")
        print("\nAll tests passed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
