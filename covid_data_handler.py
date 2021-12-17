from sched import Event
from typing import Tuple
from uk_covid19 import Cov19API
from covid_news_handling import update_news
from data import data

'''

Module responsible for loading and processing COVID data using the nhs covid data api.
Also contains functionality for loading and processing covid data from local csv files.
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
        return {
            'lastUpdate': '',
            'length': 0,
            'data': []
        }


def process_covid_json_data(covid_json_data: dict, structure: list[str] = [
        'newCasesBySpecimenDate', 'hospitalCases', 'cumDailyNsoDeathsByDeathDate']) -> dict:

    '''
    Use this function to process data recieved from the api.
    Data returned from this function follows the following structure:
        {
            'lastUpdate': (The data's timestamp),
            'length': (The number of data entries),
            'data': {
                ...
                (Covid data corresponding to the *structure* argument)
                ...
            }
        }

    '''

    try:
        return {
            'lastUpdate': covid_json_data['lastUpdate'],
            'length': covid_json_data['length'],
            'data': {i['date']: {j: i[j] for j in structure} for i in covid_json_data['data']}
        }
    except:
        return {
            'lastUpdate': '',
            'length': 0,
            'data': {}
        }


def schedule_covid_updates(update_interval: int, update_name: str) -> Event:
    return data.update_scheduler.enter(delay=update_interval, priority=1, action=lambda: update_covid_data(update_name))


def update_covid_data(update_name: str = None):
    local: list = covid_API_request(
        location=data.config_data['dashboard']['location'], location_type='Itla').get('data')
    try:
        data.config_data['dashboard']['local_7day_infections'] = \
        sum(list(filter(None, [x['newCasesBySpecimenDate'] for x in local[1:]]))[0:7])
    except:
        data.config_data['dashboard']['local_7day_infections'] = 'N/A'

    national: list = covid_API_request(
        location=data.config_data['dashboard']['nation_location'], location_type='nation').get('data')
    try:
        data.config_data['dashboard']['national_7day_infections'] = \
        sum(list(filter(None, [x['newCasesBySpecimenDate'] for x in national[1:]]))[0:7])
    except:
        data.config_data['dashboard']['national_7day_infections'] = 'N/A'
    try:
        data.config_data['dashboard']['hospital_cases'] = \
        list(filter(None, [x['hospitalCases'] for x in national]))[0]
    except:
        data.config_data['dashboard']['hospital_cases'] = 'N/A'
    try:
        data.config_data['dashboard']['deaths_total'] = \
        list(filter(None, [x['cumDailyNsoDeathsByDeathDate'] for x in national]))[0]
    except:
        data.config_data['dashboard']['deaths_total'] = 'N/A'

    if update_name:
        if data.update_events[update_name].get('repeat'):
            schedule_covid_updates(data.update_events[update_name].get('time'),
                data.update_events[update_name].get('title'))
        else:
            data.remove_update(update_title=update_name)