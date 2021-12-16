import csv, json
import sched, time
from datetime import datetime
from typing import Tuple
from uk_covid19 import Cov19API

'''

Module responsible for loading and processing COVID data from csv files and cvoid api json data
Copyright | 2021 | Miles Edwards

'''

def parse_csv_data(csv_filename: str) -> list[str]:
    with open(csv_filename, 'r', newline = '',) as csv_file:
        return [row.strip() for row in csv_file]


def process_covid_csv_data(covid_csv_data: list[str]) -> Tuple[int, int, int]:
    last7days_cases = sum(int(row.split(',')[-1]) for row in remove_empty_buffer(covid_csv_data, -1)[1:][1:8])
    currnt_hospital_cases = int(remove_empty_buffer(covid_csv_data, -2)[1].split(',')[-2])
    total_deaths = int(remove_empty_buffer(covid_csv_data, -3)[1].split(',')[-3])
    return last7days_cases, currnt_hospital_cases, total_deaths


def remove_empty_buffer(aList: list[str], row_number: int) -> list[str]:
    headers = aList[0]
    content = aList[1:]
    i = 0
    for row in content:
        if row.split(',')[row_number] == ' ' or row.split(',')[row_number] == '':
            i += 1
        else:
            return [headers] + content[i:]


def covid_API_request(location: str = 'Exeter', location_type: str = 'Itla') -> dict:
    api = Cov19API(
        filters = [
            'areaType=' + location_type,
            'areaName=' + location
        ],
        structure = {
            "date": "date",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
            "hospitalCases": "hospitalCases",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate"
        }
    )    
    try:
        return api.get_json()
    except:
        return None


def process_covid_json_data(covid_json_data: dict, structure: list[str] = ['newCasesBySpecimenDate', 'hospitalCases', 'cumDailyNsoDeathsByDeathDate']) -> dict:
    try:
        return {
            'lastUpdate': covid_json_data['lastUpdate'],
            'length': covid_json_data['length'],
            'data': {i['date']: {j: i[j] for j in structure} for i in covid_json_data['data']}
        }
    except:
        return {
            'lastUpdate': None,
            'length': 0,
            'data': None
        }


def schedule_covid_updates(update_interval: int, update_name: str) -> bool:
    s = sched.scheduler(time.time, time.sleep)
    s.enter(update_interval, 1, lambda: save_covid_json_data(update_name))
    try:
        s.run()
        return True
    except:
        return False


def save_covid_json_data(update_name: str):
    with open('covid_data.json', 'w') as covid_data:
        local = process_covid_json_data(covid_API_request())
        nation = process_covid_json_data(covid_API_request(location='England', location_type='nation'))
        json.dump({'update_name': update_name, 'nation': nation, 'local': local}, covid_data)
        covid_data.close()