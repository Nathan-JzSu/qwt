from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent

# Create an empty list to hold the dataframes
dataframes = []

# Loop through the years and read the CSV files into the list
for year in range(2013, 2025):
    file_path = app_dir / f"../../waiting_times_{year}_per_job_type.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Concatenate all the dataframes into a single dataframe
dataset = pd.concat(dataframes, ignore_index=True)