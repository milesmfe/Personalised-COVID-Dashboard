import time, datetime
from data import data
from flask import Flask, request
from flask.typing import TeardownCallable
from flask.templating import render_template
from covid_data_handler import schedule_covid_updates, update_covid_data
from covid_news_handling import remove_news, schedule_news_updates, update_news

'''
Script responsible for running and rendering webpage on localhost:5000 (default port)
Copyright | 2021 | Miles Edwards

'''

config_data = data.config_data
app = Flask(__name__)


@app.route('/index')
def main():
    data.update_scheduler.run(blocking=False)

    notif = request.args.get('notif')
    update_item = request.args.get('update_item')

    if notif:
        remove_news(notif)
        update_news()

    if update_item:
        data.remove_update(update_item)

    update_time = request.args.get('update')
    update_label = request.args.get('two')
    covid = request.args.get('covid-data')
    news = request.args.get('news')
    repeat = request.args.get('repeat')

    if update_time:
        raw_update_time = update_time
        dt = datetime.datetime.now()
        x = time.strptime(update_time,'%H:%M')
        y = time.strptime(datetime.datetime.now().strftime('%H:%M'),'%H:%M')
        then_seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
        now_seconds = datetime.timedelta(hours=y.tm_hour,minutes=y.tm_min,seconds=y.tm_sec).total_seconds()
        if then_seconds < now_seconds:
            update_time = then_seconds + ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
        else:
            update_time = then_seconds - now_seconds

    if update_time and update_label and covid:
        update = {
            'title': update_label,
            'content': 'Scheduled to update COVID data at, ' + raw_update_time
        }
        data.config_data['dashboard']['updates'].append(update)
        data.update_events[update_label] = {
            'event': schedule_covid_updates(update_time, update_label),
            'repeat': False if not repeat else True,
            'time': update_time
            }

    if update_time and update_label and news:
        update = {
            'title': update_label,
            'content': 'Scheduled to update news at, ' + raw_update_time
        }
        data.config_data['dashboard']['updates'].append(update)
        data.update_events[update_label] = data.update_events[update_label] = {
            'event': schedule_covid_updates(update_time, update_label),
            'repeat': False if not repeat else True,
            'time': update_time
            }
    
    return render_template('index.html', **config_data.get('dashboard'))

@app.route('/save')
def save():
    data.dump()
    return 'Data saved locally...\nYou may now close the browser window...'


if __name__ == '__main__':
    update_covid_data()
    update_news()
    app.run()