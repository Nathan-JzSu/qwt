import pandas as pd
import numpy as np
import datetime

def determine_job_type(row):
    qname = row['qname']
    if qname is not None and qname in ['academic', 'academic-gpu', 'academic-gpu-pub', 'academic-pub', 'aclabgroup', 'aclabgroup-pub',
        'afgen', 'afgen-pub', 'anderssongroup', 'anderssongroup-pub', 'anl', 'anl-long', 'anl-pub',
        'apolkovnikov', 'apolkovnikov-pub', 'b', 'b-long', 'batcomputer', 'batcomputer-pub', 'bil-koo',
        'bil-koo-gpu', 'bil-koo-gpu-pub', 'bil-koo-pub', 'bioinfo', 'bioinfo-pub', 'biophys-gpu', 
        'biophys-gpu-pub', 'boas', 'boas-pub', 'bpnlab', 'bpnlab-pub', 'bravaya', 'bravaya-pub', 
        'bstats', 'bstats-pub', 'c', 'casaq', 'casaq-gpu', 'casaq-gpu-pub', 'casaq-mpi', 'casaq-pub', 
        'cbm.q', 'cbm.q-pub', 'cbms', 'cbms-pub', 'ccs', 'ccs-pub', 'cds', 'cds-gpu', 'cds-gpu-pub', 
        'cds-m1024', 'cds-m1024-pub', 'cds-pub', 'chapmangroup', 'chapmangroup-gpu', 'chapmangroup-gpu-pub', 
        'chapmangroup-pub', 'chem-pub', 'chem1', 'chem2', 'chem3', 'chem4', 'crem', 'crem-pub', 'csdata', 
        'csdata-pub', 'csgpu', 'csgpu-pub', 'cui', 'cui-pub', 'cuigpu', 'cuigpu-pub', 'cupples', 
        'cupples-pub', 'cyberteam', 'cyberteam-pub', 'czcb-buyin', 'czcb-buyin-pub', 'darpa', 'darpa-pub', 
        'devorlab', 'devorlab-pub', 'dm', 'dm-pub', 'download', 'e8', 'ece', 'ece-pub', 'ecoggroup', 
        'ecoggroup-pub', 'econ', 'econ-pub', 'engineering', 'engineering-pub', 'f', 'fhs', 'fhs-pub', 
        'geo', 'geo-int', 'geo-mpi2', 'hasselmo', 'hasselmo-pub', 'huggins', 'huggins-pub', 'ilya', 'ilya-pub', 
        'iris', 'iris-gpu', 'iris-gpu-pub', 'iris-long', 'iris-pub', 'iris-wef', 'iris28', 'iris32', 
        'ivcbuyin', 'ivcbuyin-int', 'ivcbuyin-long', 'ivcbuyin-pub', 'jchengroup', 'jchengroup-pub', 
        'jjgroup', 'jjgroup-pub', 'johnsonlab.q', 'johnsonlab.q-pub', 'joshigroup', 'joshigroup-gpu', 
        'joshigroup-gpu-pub', 'joshigroup-pub', 'k40', 'katia', 'knl', 'kolaczyk', 'kolaczyk-pub', 
        'korolevgroup', 'korolevgroup-gpu', 'korolevgroup-gpu-pub', 'korolevgroup-pub', 'kulisgpu', 
        'kulisgpu-pub', 'l40s', 'labcigroup', 'labcigroup-gpu', 'labcigroup-gpu-pub', 'labcigroup-pub', 
        'lagakosgroup', 'lagakosgroup-pub', 'laumann', 'laumann-pub', 'lbi', 'lbi-pub', 'lejeunelab', 
        'lejeunelab-pub', 'li-rbsp', 'li-rbsp-gpu', 'li-rbsp-gpu-pub', 'li-rbsp-pub', 'linga', 
        'marschergroup', 'marschergroup-pub', 'mcdaniel-pub', 'mem1024', 'mem384', 'mem512', 'mnemosyne',
        'mnemosyne-pub', 'montilab', 'montilab-pub', 'muirheadgroup', 'muirheadgroup-pub', 'neuro', 
        'neuro-autonomy', 'neuro-autonomy-pub', 'neuro-pub', 'neuromorphics-16', 'neuromorphics-pub', 
        'onrcc-gpu', 'onrcc-gpu-pub', 'onrcc-m1024', 'onrcc-m1024-pub', 'onrcc-m256', 'onrcc-m512', 
        'onrcc-m512-pub', 'onrcc-pub', 'onrcc-vgl', 'opa', 'p', 'p-int', 'p-long', 'p100', 'p16', 
        'p8', 'park', 'park-pub', 'peloso', 'peloso-pub', 'pulmonarygroup', 'pulmonarygroup-pub', 
        'qonos', 'qonos-pub', 'qphys', 'qphys-pub', 'rd-compute', 'rd-compute-pub', 'rnaseq', 
        'rnaseq-pub', 'ryanlab-pub', 'ryanlab1', 'ryanlab2', 'ryanlab3', 'saimath', 'saimath-pub', 
        'sandvik', 'sandvik-pub', 'sebas', 'sebas-pub', 'sgrace', 'sgrace-pub', 'siggers', 'siggers-pub', 
        'sorenson', 'sorenson-pub', 'spl', 'spl-pub', 'straub', 'straub-mpi', 'straub-pub', 'tcn', 
        'tcn-pub', 'thinfilament', 'thinfilament-gpu', 'thinfilament-gpu-pub', 'thinfilament-pub', 
        'tsourakakisgroup', 'tsourakakisgroup-pub', 'v100', 'virtualgl', 'w', 'w-long', 'w28', 
        'wise', 'wise-pub', 'withers01', 'withers01-pub', 'wys-text', 'wys-text-pub', 'linga', 'geo', 'neuromorphics']:
        return 'removed'
    elif row['options'] and 'gpus=' in row['options']:
        return 'GPU'
    elif qname is not None and qname in ['u','z', '4', 'a', 'as', 'budge', 'a128']:
        return 'MPI'
    elif row['slots'] == 1:
        return '1-p'
    else:
        return 'omp'
    

# filter GPU jobs by months:
def GPU_queue_time_by_month(df):    # input is GPU job in one year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    latest_end_times = {month: 0 for month in months}
    waiting_times = {month: [] for month in months}

    for index, row in df.iterrows():
        submission_time = row['ux_submission_time']
        start_time = row['ux_start_time']
        end_time = row['ux_end_time']
        month = datetime.datetime.fromtimestamp(submission_time).strftime('%b')

        if submission_time > latest_end_times[month]:
            current_waiting_time = start_time - submission_time
            waiting_times[month].append(current_waiting_time)

        if end_time > latest_end_times[month]:
            latest_end_times[month] = end_time

    total_waiting_times = [sum(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    min_waiting_times = [min(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    max_waiting_times = [max(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    mean_waiting_times = [sum(waiting_times[month]) / len(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    median_waiting_times = [sorted(waiting_times[month])[len(waiting_times[month]) // 2] if waiting_times[month] else 0 for month in months]

    return months, total_waiting_times, min_waiting_times, max_waiting_times, mean_waiting_times, median_waiting_times

# calculate the queue waiting time for 1GPU job per month
def GPU_1_queue_time_by_month(df):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    latest_end_times = {month: 0 for month in months}
    waiting_times = {month: [] for month in months}

    for index, row in df.iterrows():
        if 'gpus=1' in row['options']:
            submission_time = row['ux_submission_time']
            start_time = row['ux_start_time']
            end_time = row['ux_end_time']
            month = datetime.datetime.fromtimestamp(submission_time).strftime('%b')

            if submission_time > latest_end_times[month]:
                current_waiting_time = start_time - submission_time
                waiting_times[month].append(current_waiting_time)

            if end_time > latest_end_times[month]:
                latest_end_times[month] = end_time

    total_waiting_times = [sum(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    min_waiting_times = [min(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    max_waiting_times = [max(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    mean_waiting_times = [sum(waiting_times[month]) / len(waiting_times[month]) if waiting_times[month] else 0 for month in months]
    median_waiting_times = [sorted(waiting_times[month])[len(waiting_times[month]) // 2] if waiting_times[month] else 0 for month in months]

    return months, total_waiting_times, min_waiting_times, max_waiting_times, mean_waiting_times, median_waiting_times

# calculate the queue waiting time for GPU job use no more than 1 GPU
def GPU_1_queue_time(df):  
    waiting_time = 0
    prev_latest_end_time = 0
    waiting_times = []

    for index, row in df.iterrows():
        if 'options' in row and row['options'] and 'gpus=1' in row['options']:
            submission_time = row['ux_submission_time']
            start_time = row['ux_start_time']
            end_time = row['ux_end_time']

            if prev_latest_end_time is not None and submission_time > prev_latest_end_time:
                current_waiting_time = (start_time - submission_time)
                waiting_time += current_waiting_time
                waiting_times.append(current_waiting_time)

            if end_time > prev_latest_end_time:
                prev_latest_end_time = end_time

    if waiting_times:
        min_waiting_time = min(waiting_times)
        max_waiting_time = max(waiting_times)
        mean_waiting_time = sum(waiting_times) / len(waiting_times)
        median_waiting_time = sorted(waiting_times)[len(waiting_times) // 2]
    else:
        min_waiting_time = max_waiting_time = mean_waiting_time = median_waiting_time = 0
    
    return waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time

# calculate the queue waiting time for all GPU jobs
def GPU_all_queue_time(df):
    waiting_time = 0
    prev_latest_end_time = 0
    waiting_times = []

    for index, row in df.iterrows():
        # if 'options' in row and row['options'] and 'gpus=' in row['options']:
        submission_time = row['ux_submission_time']
        start_time = row['ux_start_time']
        end_time = row['ux_end_time']

        if prev_latest_end_time is not None and submission_time > prev_latest_end_time:
            current_waiting_time = (start_time - submission_time)
            waiting_time += current_waiting_time
            waiting_times.append(current_waiting_time)

        if end_time > prev_latest_end_time:
            prev_latest_end_time = end_time

    if waiting_times:
        min_waiting_time = min(waiting_times)
        max_waiting_time = max(waiting_times)
        mean_waiting_time = sum(waiting_times) / len(waiting_times)
        median_waiting_time = sorted(waiting_times)[len(waiting_times) // 2]
    else:
        min_waiting_time = max_waiting_time = mean_waiting_time = median_waiting_time = 0
    
    return waiting_time, min_waiting_time, max_waiting_time, mean_waiting_time, median_waiting_time

#calculate the queue waiting time for MPI shared jobs
def MPI_shared_queues_time(df):
    queues = {
        'u': [],
        'z': [],
        '4': [],
        'a': [],
        'as': [],
        'budge': [],
        'total': []
    }
    latest_end_times = {
        'u': 0,
        'z': 0,
        '4': 0,
        'a': 0,
        'as': 0,
        'budge': 0,
        'total': 0
    }

    for index, row in df.iterrows():
        qname = row['qname']
        submission_time = row['ux_submission_time']
        start_time = row['ux_start_time']
        end_time = row['ux_end_time']

        
        key = qname
        if qname == 'a128':
            key = 'a'

        if submission_time > latest_end_times[key]:
            current_waiting_time = (start_time - submission_time)
            queues[key].append(current_waiting_time)
            queues['total'].append(current_waiting_time)

        if end_time > latest_end_times[key]:
            latest_end_times[key] = end_time
            latest_end_times['total'] = end_time

    results = {
        'u': calculate_statistics(queues['u']),
        'z': calculate_statistics(queues['z']),
        '4': calculate_statistics(queues['4']),
        'a': calculate_statistics(queues['a']),
        'as': calculate_statistics(queues['as']),
        'budge': calculate_statistics(queues['budge']),
        'u_z_4_a_as_budge': calculate_statistics(queues['total'])
    }

    return results

#calculate waiting time for each shared MPI queue separately. consider a and a128 as the same queue. call it as 'a'
def MPI_shared_queue_separately(df):
    waiting_times = {}
    prev_latest_end_times = {}

    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        # Get the first character of the queue name to group them
        qname_group = row['qname'][0]

        # Initialize waiting time and previous end time for new queue groups
        if qname_group not in waiting_times:
            waiting_times[qname_group] = 0
            prev_latest_end_times[qname_group] = 0

        submission_time = row['ux_submission_time']
        start_time = row['ux_start_time']
        end_time = row['ux_end_time']

        # Calculate waiting time for the current queue group
        if prev_latest_end_times[qname_group] is not None and submission_time > prev_latest_end_times[qname_group]:
            waiting_times[qname_group] += (start_time - submission_time)

        # Update the latest end time for the current queue group
        if end_time > prev_latest_end_times[qname_group]:
            prev_latest_end_times[qname_group] = end_time

    return waiting_times

def calculate_statistics(queue):
        if not queue:
            return [0, 0, 0, 0, 0]
            
        total_sum = max(sum(queue), 0)
        minimum = max(min(queue), 0)
        maximum = max(max(queue), 0)
        mean = max(sum(queue) / len(queue), 0)
        median = max(np.median(queue), 0)
        
        return [total_sum, minimum, maximum, mean, median]
