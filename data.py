import json, sched
from time import sleep, time

'''
Module responsible for parsing config data to and from local storage
Object also has key attribute: update_scheduler, which is used to unify all scheduled events
Copyright | 2021 | Miles Edwards

'''

class data:

    '''
    This static class acts as a hub for any data that needs to be accessed throughout the entire program.
    The majority of this data will be configuration data.

    The data object also contains an instance of sched.scheduler, which is declared here because:
        Only one instance is therefore required,
        Eliminates the need for multi-threading,
        Easy to reference (data.update_scheduler can be called from any other module).

    '''

    update_scheduler = sched.scheduler(time, sleep)
    update_events = {}
    
    '''
    When python processes this object (when the module is imported),
    the program attempts to open the configuration file.

    If no such file exists, the program writes it using the template below.

    '''

    template = {
        'dashboard': {
            'favicon': 'nhs.png',
            'image': 'nhs.png',
            'title': 'Covid Dashboard',
            'updates': [],
            'news_articles': [],
            'rejected_news_articles': [],
            'location': 'Exeter',
            'nation_location': 'England',
            'local_7day_infections': None,
            'national_7day_infections': None,
            'hospital_cases': None,
            'deaths_total': None
        },
        'user': {
            'apiKey': None
        }   
    }

    try:
        with open('config.json', 'r') as config_file:
            config_data: dict = json.load(config_file)
            config_file.close()
    except:
        with open('config.json', 'w') as config_file:
            config_data = template
            json.dump(config_data, config_file)
            config_file.close()    


    @staticmethod
    def remove_update(update_title: str):
        updated_list = []
        for x in data.config_data['dashboard']['updates']:
            if x['title'] != update_title:
                updated_list.append(x)
            else:
                removed_update = x['title']
        data.config_data['dashboard']['updates'] = updated_list
        data.update_scheduler.cancel(data.update_events.get(removed_update)['event'])
        del(data.update_events[removed_update])


    @staticmethod
    def dump():
        '''
        This static method handles saving configuration data to local storage.
        The pre-existing file is overritten with an updated version that the program has used.

        '''
        with open('config.json', 'w') as config_file:
            json.dump(data.config_data, config_file)
            config_file.close()


if '__name__' == '__main__':
    data()