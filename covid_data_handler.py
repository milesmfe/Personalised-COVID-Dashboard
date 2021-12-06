import csv
import sched, time
import flask
from uk_covid19 import Cov19API

# -------- Covid Data Handling Module -------- #
# ----- Copyright | 2021 | Miles Edwards ----- #

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

    # Look at the first 7 rows in the data set ignoring empty values and the first of the last 7 days
    # Sum up all the values in the last column of each of these rows
    last7days_cases = sum(int(row.split(',')[-1]) for row in remove_empty_buffer(covid_csv_data, -1)[1:][1:8])

    # Set currnt_hospital_cases to the value in the 2nd to last column of the first value row in the data set
    currnt_hospital_cases = int(remove_empty_buffer(covid_csv_data, -2)[1].split(',')[-2])

    # Look for the first total deaths
    total_deaths = int(remove_empty_buffer(covid_csv_data, -3)[1].split(',')[-3])

    return last7days_cases, currnt_hospital_cases, total_deaths

def remove_empty_buffer(aList, row_number):
    headers = aList[0]
    content = aList[1:]
    i = 0
    for row in content:
        if row.split(',')[row_number] == ' ':
            i += 1
        else:
            return [headers] + content[i:]


def covid_API_request(location = 'England', location_type = 'nation'):
    GETfilter = [
        'areaType={}'.format(location_type),
        'areaName={}'.format(location)
    ]
    GETStructure = {
        "areaCode": "areaCode",
        "areaName": "areaName",
        "areaType": "areaType",
        "date": "date",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }
    api = Cov19API(filters=GETfilter, structure=GETStructure)
    csv = api.get_csv().split('\n')

    return(csv)

def schedule_covid_updates(update_interval, update_name):
    pass

print(covid_API_request())