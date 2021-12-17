import time, datetime
from flask.typing import TeardownCallable
from data import data
from flask import Flask, request
from flask.templating import render_template
from covid_data_handler import schedule_covid_updates
from covid_news_handling import news_API_request

'''

Script responsible for running and rendering webpage on localhost
Copyright | 2021 | Miles Edwards

'''

config_data = data.config_data
app = Flask(__name__)


def handle_requests(requests_dict: dict):
    update_label = requests_dict.get('two')
    update_time = requests_dict.get('update')
    dt = datetime.datetime.now()
    x = time.strptime(update_time,'%H:%M')
    y = time.strptime(datetime.datetime.now().strftime('%H:%M'),'%H:%M')
    then_seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    now_seconds = datetime.timedelta(hours=y.tm_hour,minutes=y.tm_min,seconds=y.tm_sec).total_seconds()
    if then_seconds < now_seconds:
        update_time = then_seconds + ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
    else:
        update_time = then_seconds - now_seconds
    repeat = requests_dict.get('repeat')
    
    if requests_dict.get('covid-data'):
        schedule_covid_updates(update_time, update_label)




@app.route('/index')
def main():

    if request.args.to_dict():
        handle_requests(request.args.to_dict())

    data.scheduled_updates.run(blocking=False)
    return render_template('index.html', **config_data['covid'])


def on_close(f: TeardownCallable):
    data.dump()
    print('Data saved locally...\nShutting Down...')


if __name__ == '__main__':
    app.run(debug=True)
