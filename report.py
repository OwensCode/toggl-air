# pylint: disable=missing-docstring

import os
import argparse

import requests

from dotenv import load_dotenv
from texttable import Texttable

import dataframe as df

from config import Config
from errors import RequestError

REPORT_DETAIL_URL = 'https://toggl.com/reports/api/v2/details'

EMPTY_TABLE_ROW = [''] * 4 + ['--------', '--------', '-----']

def run_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file in JSON format')
    return parser.parse_args()

def get_auth():
    return (os.environ['TOGGL_API_TOKEN'], 'api_token')

def get_request_params():
    return {
        'user_agent': os.environ['TOGGL_USER_AGENT'],
        'workspace_id': os.environ['TOGGL_WORKSPACE_ID']
    }

def duration_to_str(duration):
    total_seconds = duration.days * (24 * 60 * 60) + duration.seconds
    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def create_report(dataframe, totals):
    table = Texttable(max_width=0)
    table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
    table.set_precision(2)
    table.header(['Date', 'Client', 'Project', 'Task', 'Duration', 'Rounded', 'Hours'])

    report = dataframe.copy(deep=True)
    report['duration'] = report['duration'].apply(duration_to_str)
    report['rounded_duration'] = report['rounded_duration'].apply(duration_to_str)

    table.add_rows(report.values.tolist(), header=False)

    table.add_row(EMPTY_TABLE_ROW)

    table.add_row([
        '', '', '', '',
        duration_to_str(totals.get('duration')),
        duration_to_str(totals.get('rounded_duration')),
        totals.get('rounded_hours')
    ])

    return table.draw()

def run_detail_report(config):
    response = requests.get(REPORT_DETAIL_URL, params=get_request_params(), auth=get_auth())

    if not response.ok:
        raise RequestError.create(response)

    dataframe = df.create_dataframe(response.json()['data'], config)
    daily_totals = df.calculate_daily_totals(dataframe)
    totals = df.calculate_totals(dataframe)
    dataframe = df.combine_with_daily_totals(dataframe, daily_totals)
    print(create_report(dataframe, totals))

def main():
    load_dotenv(verbose=False)
    args = run_args()
    config = Config(args.config)
    run_detail_report(config)

if __name__ == '__main__':
    main()
