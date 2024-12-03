import pandas as pd
import pyarrow.feather as feather
import argparse
import os
import time

def read_feather_file(filepath):
    return feather.read_feather(filepath)

def print_first_rows(df, title, rows=4):
    if not df.empty:
        print(f"\n{title} (First {rows} rows):\n{df.head(rows)}")
    else:
        print(f"\n{title} is empty.\n")

def save_to_feather(df, filepath):
    feather.write_feather(df, filepath)

def append_to_feather(df, filepath):
    if os.path.exists(filepath):
        existing_df = read_feather_file(filepath)
        df = pd.concat([existing_df, df], ignore_index=True)
    save_to_feather(df, filepath)

def process_data(year):
    feather_file = f'/projectnb/rcs-intern/Jiazheng/accounting/data/scc/{year}.feather'

    if not os.path.exists(feather_file):
        print(f"File {feather_file} does not exist.")
        return

    df = read_feather_file(feather_file)

    # Sort the DataFrame by 'ux_submission_time'
    df.sort_values(by='ux_submission_time', inplace=True)

    # Filter and select relevant columns
    df = df[['qname', 'hostname', 'owner', 'job_name', 'job_number', 'ux_submission_time', 'ux_start_time', 'ux_end_time', 'granted_pe', 'slots', 'task_number', 'options', 'pe_taskid', 'slots']]
    
    df.sort_values(by='job_number', inplace=True)
    print("DataFrame loaded from Feather file:\n", df.head())
    return 

    # print("\nChecking for NaN values in specific columns before filtering:\n",
    #       df[['ux_submission_time', 'ux_start_time', 'ux_end_time']].isna().sum())

    # Filter rows with non-null values in specified columns
    df_filtered = df.dropna(subset=['ux_submission_time', 'ux_start_time', 'ux_end_time'])
    # print_first_rows(df_filtered, "Filtered Data")

    # Convert columns to numeric, coercing errors to NaN to gracefully handle the non-numeric value when encounterd in later data analysis
    df_filtered[['ux_submission_time', 'ux_start_time']] = df_filtered[['ux_submission_time', 'ux_start_time']].apply(pd.to_numeric, errors='coerce')

    output_feather_file = f'/projectnb/rcs-intern/Jiazheng/accounting/data/scc/{year}-filtered.feather'
    save_to_feather(df_filtered, output_feather_file)
    print(f"Filtered data has been saved to {output_feather_file}.")

    df_verified = read_feather_file(output_feather_file)
    print_first_rows(df_verified, "Verified DataFrame from Feather file")

def filter_data_by_user(year):
    feather_file = f'/projectnb/rcs-intern/Jiazheng/accounting/data/scc/{year}-test.feather'

    if not os.path.exists(feather_file):
        print(f"File {feather_file} does not exist.")
        return

    df = pd.read_feather(feather_file)
    # Filter and select relevant columns
    df = df[['qname', 'hostname', 'owner', 'job_name', 'job_number', 'ux_submission_time', 'ux_start_time', 'ux_end_time', 'granted_pe', 'task_number', 'options', 'pe_taskid', 'slots']]
    # Filter rows with non-null values in specified columns
    df = df.dropna(subset=['ux_submission_time', 'ux_start_time', 'ux_end_time'])
    # Sort the DataFrame by 'ux_submission_time'
    df.sort_values(by='ux_submission_time', inplace=True)
    df.sort_values(by='job_number', inplace=True)
    print("DataFrame loaded from Feather file:\n", df.head())
    return 


    
    print("start getting new data")
    
    output_feather_file = f'/projectnb/rcs-intern/Jiazheng/accounting/data/scc/{year}-filtered.feather'
    
    # Initialize a mask with False values, with the same index as the DataFrame
    # filtered_mask = pd.Series([False] * len(df), index=df.index)

    # for owner, group in df.groupby('owner'):
    #     prev_latest_end_time = 0

    #     for index, row in group.iterrows():
    #         submission_time = row['ux_submission_time']
    #         start_time = row['ux_start_time']
    #         end_time = row['ux_end_time']

    #         if prev_latest_end_time is not None and submission_time > prev_latest_end_time: # find a 'first' job for current user
    #             filtered_mask.at[index] = True

    #         if end_time > prev_latest_end_time: # update the latest end time
    #             prev_latest_end_time = end_time

    # # Apply the mask to the DataFrame and save the filtered data
    # filtered_df = df[filtered_mask]
    filtered_df = df
    filtered_df = filtered_df.sort_values(by='ux_submission_time', ascending=True)
    filtered_df.reset_index(drop=True, inplace=True) # Reset index to avoid issues with duplicate indices
    filtered_df.to_feather(output_feather_file)

    print(f"Filtered data has been saved to {output_feather_file}.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process accounting data.')
    parser.add_argument('year', type=int, help='Year of the data to process')
    args = parser.parse_args()

    start_time = time.time()
    # process_data(args.year)
    filter_data_by_user(args.year)
    end_time = time.time()
    running_time = end_time - start_time

    print(f"Running time: {running_time} seconds")