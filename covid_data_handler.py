import csv
from uk_covid19 import Cov19API

# Covid Data Handling Module
# Copyright | 2021 | Miles Edwards

# Reads Data from CSV File
def parse_csv_data(csv_filename):
    rows = []
    with open(csv_filename, 'r', newline= '',) as csv_file: # Open a data read stream between the code and the csv file
        reader = csv.reader(csv_file) # Generate a list using the csv reader method
        for row in reader:
            rows.append(', '.join(row)) # Populate the rows list, separating each row with a comma
        csv_file.close()
    return rows

# Processes Data read from CSV File
def process_covid_csv_data(covid_csv_data):
    
    # Look at the first 7 rows in the data set ignoring the current day and the first of the last 7 days
    # Sum up all the values in the last column of each of these rows
    last7days_cases = sum(int(row.split(',')[-1]) for row in covid_csv_data[1:][2:9])
    
    # Set currnt_hospital_cases to the value in the 2nd to last column of the first value row in the data set
    currnt_hospital_cases = int(covid_csv_data[1].split(',')[-2])

    for row in covid_csv_data[1:]: # Iterate through each row in the data set
        if row.split(',')[-3] != ' ': # Check if the value in the 3rd to last column is ' '
            total_deaths = int(row.split(',')[-3]) # If so, set total_deaths to this value
            break

    return last7days_cases, currnt_hospital_cases, total_deaths

def covid_API_request(location = 'Exeter', location_type = 'Itla'):
    pass