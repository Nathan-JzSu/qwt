#!/bin/bash

# Loop through the years 2013 to 2024
for year in {2013..2024}
do
    echo "Processing year: $year"
    python3 GetQueueTime.py "$year"
done

echo "All years processed."
