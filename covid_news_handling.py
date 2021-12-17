from sched import Event
from data import data
import requests

'''
Module responsible for handling COVID news requested from a generic news api
Copyright | 2021 | Miles Edwards

'''

def news_API_request(covid_terms: str = 'Covid COVID-19 coronavirus') -> list[dict]:
    api_key = data.config_data['user']['apiKey']
    url = 'https://newsapi.org/v2/everything?q={}&sortBy=popularity&apiKey={}'.format(covid_terms, api_key)
    response = requests.get(url)
    articles = response.json()['articles']
    return [{'title': a['title'], 'content': a['content']} for a in articles]


def update_news(update_interval: int, update_name: str) -> Event:
    return data.update_scheduler.enter(delay=update_interval, priority=1, action=update_news)


def update_news():
    articles: list[dict] = news_API_request()                
    filtered_articles: list[dict] = \
        list(filter((lambda a: a['title'] not in  \
            data.config_data['dashboard']['rejected_news_articles']), articles))
    data.config_data['dashboard']['news_articles'] = filtered_articles