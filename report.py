# pylint: disable=missing-docstring

import os
import argparse

from datetime import date, timedelta

import requests

from dotenv import load_dotenv
from texttable import Texttable
import pandas as pd

import dataframe as df

from config import Config
from errors import RequestError

REPORT_DETAIL_URL = 'https://toggl.com/reports/api/v2/details'

EMPTY_TABLE_ROW = [''] * 4 + ['--------', '--------', '-----']

ONE_DAY = timedelta(days=1)

def valid_date(date_str):
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        msg = f'Not a valid date: "{date_str}". Must be in format yyyy-mm-dd.'
        raise argparse.ArgumentTypeError(msg)

def previous_monday(end_date):
    prev_date = end_date - ONE_DAY
    while prev_date.isoweekday() != 1:
        prev_date = prev_date - ONE_DAY
    return prev_date

def run_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', help='start date, default is most recent Monday', type=valid_date)
    parser.add_argument('-e', '--end', help='end date, default is today', type=valid_date)
    parser.add_argument('config', help='configuration file in JSON format')
    args = parser.parse_args()

    if args.end is None:
        args.end = date.today()

    if args.start is None:
        args.start = previous_monday(args.end)

    assert args.start <= args.end, 'End date cannot be before start date'

    return args

def get_auth():
    return (os.environ['TOGGL_API_TOKEN'], 'api_token')

def get_request_params(start_date, end_date):
    return {
        'user_agent': os.environ['TOGGL_USER_AGENT'],
        'workspace_id': os.environ['TOGGL_WORKSPACE_ID'],
        'since': start_date,
        'until': end_date
    }

def duration_to_str(duration):
    total_seconds = duration.days * (24 * 60 * 60) + duration.seconds
    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def create_report(dataframe, totals):
    df.fill_na(dataframe)

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

def run_detail_report(config, report_date):
    request_params = get_request_params(report_date, report_date)
    response = requests.get(REPORT_DETAIL_URL, params=request_params, auth=get_auth())

    if not response.ok:
        raise RequestError.create(response)

    data = response.json()['data']
    if len(data):
        dataframe = df.create_dataframe(data, config)
        daily_totals = df.calculate_daily_totals(dataframe)
        dataframe = df.combine_with_daily_totals(dataframe, daily_totals)
        return dataframe

def main():
    load_dotenv(verbose=False)
    args = run_args()
    config = Config(args.config)

    dataframe = None

    report_date = args.start
    while report_date <= args.end:
        dayframe = run_detail_report(config, report_date)
        if dataframe is not None:
            dataframe = pd.concat([dataframe, dayframe]);
        else:
            dataframe = dayframe
        report_date = report_date + ONE_DAY

    totals = df.calculate_totals(dataframe)
    print(create_report(dataframe, totals))

if __name__ == '__main__':
    main()
