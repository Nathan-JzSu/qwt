import pandas as pd
import numpy as np
import time
import argparse
from tqdm import tqdm
from helpers import (determine_job_type, determine_job_type, GPU_1_queue_time, GPU_1_queue_time_by_month, GPU_all_queue_time, GPU_queue_time_by_month, MPI_shared_queues_time, MPI_shared_queue_separately, calculate_statistics)
import datetime


def calculate_waiting_time_from_feather_per_user(input_file_name, output_file_name):
    # Read data from the Feather file
    df = pd.read_feather(input_file_name)

    # filter cols we need
    df = df[['qname', 'hostname', 'owner', 'job_number', 'ux_submission_time', 'ux_start_time', 'ux_end_time', 'granted_pe', 'slots', 'task_number', 'options', 'pe_taskid']]
    
    # Apply the function to create the job_type column
    # df['job_type'] = df.apply(determine_job_type, axis=1)
    # print(df.head())
    # return

    # Ensure the time columns are integers
    df['ux_submission_time'] = df['ux_submission_time'].astype(int)
    df['ux_start_time'] = df['ux_start_time'].astype(int)
    df['ux_end_time'] = df['ux_end_time'].astype(int)
    
    # Initialize a dictionary to store waiting times for each owner
    owner_waiting_times = {}

    # Sort by submission time for each owner
    df = df.sort_values(by=['owner', 'ux_submission_time'])
    
    for owner, group in df.groupby('owner'):
        waiting_time = 0
        prev_latest_end_time = 0
        # count = 1

        for index, row in group.iterrows():
            submission_time = row['ux_submission_time']
            start_time = row['ux_start_time']
            end_time = row['ux_end_time']

            if prev_latest_end_time is not None and submission_time > prev_latest_end_time: # find a 'first' job for current user
                waiting_time += (start_time - submission_time)
                # count += 1

            if end_time > prev_latest_end_time: # update the latest end time
                prev_latest_end_time = end_time

        # Calculate the average waiting time for the current owner
        # avg_waiting_time = waiting_time / count
        owner_waiting_times[owner] = waiting_time
    
    # Convert the results to a DataFrame
    result_df = pd.DataFrame(list(owner_waiting_times.items()), columns=['owner', 'first_job_waiting_time'])
    
    # Sort the DataFrame by average_waiting_time in ascending order
    result_df = result_df.sort_values(by='first_job_waiting_time', ascending=True)

    # Save the results to a CSV file
    # Calculate the min, max, mean, and median of first_job_waiting_time
    min_waiting_time = result_df['first_job_waiting_time'].min()
    max_waiting_time = result_df['first_job_waiting_time'].max()
    mean_waiting_time = result_df['first_job_waiting_time'].mean()
    median_waiting_time = result_df['first_job_waiting_time'].median()

    # Create a new row with the desired values
    statistics = [
        {'owner': 'Min', 'first_job_waiting_time': min_waiting_time},
        {'owner': 'Max', 'first_job_waiting_time': max_waiting_time},
        {'owner': 'Mean', 'first_job_waiting_time': mean_waiting_time},
        {'owner': 'Median', 'first_job_waiting_time': median_waiting_time}
    ]

    # Insert the new rows at the beginning of the DataFrame
    result_df = pd.concat([pd.DataFrame(statistics), result_df], ignore_index=True)


    # Save the results to a CSV file
    result_df.to_csv(output_file_name, index=False, chunksize=100000)

# Example usage
input_file_name = './data/scc/2013-aggregated.feather'
output_file_name = 'waiting_times_2013_per_user.csv'
# start_time = time.time()
# calculate_waiting_time_from_feather_per_user(input_file_name, output_file_name)
# end_time = time.time()

# running_time = end_time - start_time

# print(f"First job waiting times per user saved to {output_file_name}")
# print(f"Running time: {running_time} seconds")




def calculate_waiting_time_for_each_job_type(input_file_name, output_file_name, year):
    # Read data from the Feather file
    df = pd.read_feather(input_file_name)

    # filter cols we need
    df = df[['ux_submission_time', 'ux_start_time', 'ux_end_time', 'granted_pe', 'slots', 'options', 'pe_taskid', 'qname']]
    
    # Apply the function to create the job_type column
    df['job_type'] = df.apply(determine_job_type, axis=1)
    
    # Ensure the time columns are integers
    df['ux_submission_time'] = df['ux_submission_time'].astype(int)
    df['ux_start_time'] = df['ux_start_time'].astype(int)
    df['ux_end_time'] = df['ux_end_time'].astype(int)

    df['year'] = year

    job_type_waiting_times = {}
    # job_type_waiting_times['GPU=1'] = 0     # new job type: GPU jobs use no more than 1 GPU

    # for job_type, group in df.groupby('job_type'):
    for job_type, group in tqdm(df.groupby('job_type'), desc="Processing job types"):
        waiting_time = 0
        prev_latest_end_time = 0
        waiting_times = []
        if job_type == 'removed':
            continue
        if job_type == 'GPU':
            # group.to_csv('GPU_group.csv', index=False)
            # print("GPU group saved")
            new_waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time = GPU_1_queue_time(group)
            # job_type_waiting_times['GPU=1'] = new_waiting_time
            job_type_waiting_times['GPU = 1'] = [new_waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time]
            # print(job_type_waiting_times)
            months, total_waiting_times, min_waiting_times, max_waiting_times, mean_waiting_times, median_waiting_times = GPU_1_queue_time_by_month(group)
            for i, month in enumerate(months):
                total_value = total_waiting_times[i]
                min_value = min_waiting_times[i]
                max_value = max_waiting_times[i]
                mean_value = mean_waiting_times[i]
                median_value = median_waiting_times[i]

                job_type_waiting_times[f'GPU=1 job in: {month}'] = [total_value, min_value, max_value, mean_value, median_value]

            
            new_waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time = GPU_all_queue_time(group)
            job_type_waiting_times['GPU >= 1'] = [new_waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time]
            
            months, total_waiting_times, min_waiting_times, max_waiting_times, mean_waiting_times, median_waiting_times = GPU_queue_time_by_month(group)
            for i, month in enumerate(months):
                total_value = total_waiting_times[i]
                min_value = min_waiting_times[i]
                max_value = max_waiting_times[i]
                mean_value = mean_waiting_times[i]
                median_value = median_waiting_times[i]

                job_type_waiting_times[f'GPU job in: {month}'] = [total_value, min_value, max_value, mean_value, median_value]            

        elif job_type == 'MPI':
            # job_type_waiting_times['all_shared_MPI_queue'] 
            all_shared_MPI_queues = MPI_shared_queues_time(group)
            for queue, waiting_time_stats in all_shared_MPI_queues.items():
                job_type_waiting_times[f'shared MPI queue: {queue}'] = waiting_time_stats
                
            # shared_MPI_queue_separately = MPI_shared_queue_separately(group)
            # for queue, waiting_time in shared_MPI_queue_separately.items():
            #     job_type_waiting_times[f'each_shared_MPI_queue: {queue}'] = waiting_time
        else:
            for index, row in group.iterrows():
                submission_time = row['ux_submission_time']
                start_time = row['ux_start_time']
                end_time = row['ux_end_time']

                if prev_latest_end_time is not None and submission_time > prev_latest_end_time:
                    current_waiting_time = (start_time - submission_time)
                    waiting_time += current_waiting_time
                    waiting_times.append(current_waiting_time)

                if end_time > prev_latest_end_time:
                    prev_latest_end_time = end_time

            min_waiting_time = max(min(waiting_times), 0)
            max_waiting_time = max(max(waiting_times), 0)
            mean_waiting_time = max(sum(waiting_times) / len(waiting_times), 0)
            median_waiting_time = max(sorted(waiting_times)[len(waiting_times) // 2], 0)

            job_type_waiting_times[job_type] = [waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time]

    # Convert the results to a DataFrame
    job_type_waiting_df = pd.DataFrame.from_dict(job_type_waiting_times, orient='index',
                                             columns=['first_job_waiting_time', 'min_waiting_time', 'max_waiting_time', 'mean_waiting_time', 'median_waiting_time'])
    # Reset the index to get 'job_type' as a column
    job_type_waiting_df.reset_index(inplace=True)
    job_type_waiting_df.rename(columns={'index': 'job_type'}, inplace=True)

    # Add the 'year' column
    job_type_waiting_df['year'] = df['year'].iloc[0]

    # Save the results to a CSV file
    job_type_waiting_df.to_csv(output_file_name, index=False, chunksize=100000)


def waiting_time_per_job_type(input_file_name, output_file_name, year):
    # Read data from the Feather file
    df = pd.read_feather(input_file_name)

    # filter cols we need
    df = df[['ux_submission_time', 'ux_start_time', 'ux_end_time', 'granted_pe', 'slots', 'options', 'pe_taskid', 'qname', 'job_number', 'owner', 'job_name', 'task_number']]
    
    # Apply the function to create the job_type column
    df['job_type'] = df.apply(determine_job_type, axis=1)
    
    # Ensure the time columns are integers
    df['ux_submission_time'] = df['ux_submission_time'].astype(int)
    df['ux_start_time'] = df['ux_start_time'].astype(int)
    df['ux_end_time'] = df['ux_end_time'].astype(int)

    df['year'] = year

    job_type_waiting_times = []
    
    for job_type, group in tqdm(df.groupby('job_type'), desc="Processing job types"):
        if job_type == 'removed':
            continue

        if job_type == 'GPU':
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            latest_end_times = {month: 0 for month in months}
            gpu_waiting_times = {month: [] for month in months}  # All GPU jobs
            gpu_1_latest_end_times = {month: 0 for month in months}
            gpu_1_waiting_times = {month: [] for month in months}  # GPU = 1 jobs
            for index, row in group.iterrows():
                submission_time = row['ux_submission_time']
                start_time = row['ux_start_time']
                end_time = row['ux_end_time']
                initialYear = datetime.datetime.fromtimestamp(submission_time).year
                if initialYear == year:
                    month = datetime.datetime.fromtimestamp(submission_time).strftime('%b')
                    if submission_time > latest_end_times[month]:
                        current_waiting_time = start_time - submission_time
                        job_type_waiting_times.append([job_type, current_waiting_time, month, year, row['job_number'], row['slots']])

                    if end_time > latest_end_times[month]:
                        latest_end_times[month] = end_time
                    
                    if 'gpus=1' in row['options']:
                        if submission_time > gpu_1_latest_end_times[month]:
                            current_waiting_time = start_time - submission_time
                            job_type_waiting_times.append(['GPU = 1', current_waiting_time, month, year, row['job_number'], row['slots']])

                        if end_time > gpu_1_latest_end_times[month]:
                            gpu_1_latest_end_times[month] = end_time

        elif job_type == 'MPI':
            qnames = ['z', 'u', '4', 'a', 'as', 'budge', 'a128']
            latest_end_times = {qname: 0 for qname in qnames}
            for index, row in group.iterrows():
                submission_time = row['ux_submission_time']
                start_time = row['ux_start_time']
                end_time = row['ux_end_time']
                initialYear = datetime.datetime.fromtimestamp(submission_time).year
                if initialYear == year:
                    month = datetime.datetime.fromtimestamp(submission_time).strftime('%b')
                    qname = row['qname']
                    if qname == 'a128':
                        qname = 'a'
                    if submission_time > latest_end_times[qname]:
                        current_waiting_time = start_time - submission_time
                        job_type_waiting_times.append([f'MPI job {qname}', current_waiting_time, month, year, row['job_number'], row['slots']])

                    if end_time > latest_end_times[qname]:
                        latest_end_times[qname] = end_time

        else:
            latest_end_times = 0
            for index, row in group.iterrows():
                submission_time = row['ux_submission_time']
                start_time = row['ux_start_time']
                end_time = row['ux_end_time']
                initialYear = datetime.datetime.fromtimestamp(submission_time).year
                if initialYear == year:
                    month = datetime.datetime.fromtimestamp(submission_time).strftime('%b')
                    if submission_time > latest_end_times:
                        current_waiting_time = start_time - submission_time
                        job_type_waiting_times.append([job_type, current_waiting_time, month, year, row['job_number'], row['slots']])
                    if end_time > latest_end_times:
                        latest_end_times = end_time

    # Convert the results to a DataFrame
    job_type_waiting_df = pd.DataFrame(job_type_waiting_times, columns=['job_type', 'first_job_waiting_time', 'month', 'year', 'job_number', 'slots'])

    # Save the results to a CSV file
    job_type_waiting_df.to_csv(output_file_name, index=False, chunksize=100000)



# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process accounting data.')
    parser.add_argument('year', type=int, help='Year of the data to process')
    args = parser.parse_args()

    year = args.year
    input_file_name = f'/projectnb/rcs-intern/Jiazheng/accounting/data/scc/{year}-filtered.feather'
    output_file_name = f'/projectnb/rcs-intern/Jiazheng/accounting/waiting_times_{year}_per_job_type.csv'

    start_time = time.time()
    waiting_time_per_job_type(input_file_name, output_file_name, year)
    end_time = time.time()

    running_time = end_time - start_time

    print(f"First job waiting times per job type saved to {output_file_name}")
    print(f"Running time: {running_time} seconds")