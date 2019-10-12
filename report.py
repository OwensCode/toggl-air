# pylint: disable=missing-docstring

import os
import re

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import requests

from dotenv import load_dotenv
from texttable import Texttable

from duration_rounder import DurationRounder
from errors import RequestError
from settings_rn import CLIENT_MAP, PROJECT_MAP, TASK_MAP, ROUND_TO_MINUTES

REPORT_DETAIL_URL = 'https://toggl.com/reports/api/v2/details'

EMPTY_TABLE_ROW = [''] * 4 + ['--------', '--------', '-----']

def get_auth():
    return (os.environ['TOGGL_API_TOKEN'], 'api_token')

def get_request_params():
    return {
        'user_agent': os.environ['TOGGL_USER_AGENT'],
        'workspace_id': os.environ['TOGGL_WORKSPACE_ID']
    }

def map_item(item, lookup_map):
    if lookup_map.get(item):
        return lookup_map[item]

    for key, value in lookup_map.items():
        if re.fullmatch(key, item):
            return value

    return item

def map_client(client):
    return map_item(client, CLIENT_MAP)

def map_project(project):
    return map_item(project, PROJECT_MAP)

def map_task(task):
    return map_item(task, TASK_MAP)

def report_summary(summary):
    table = Texttable(max_width=0)
    table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
    table.set_precision(2)
    table.header(['Date', 'Client', 'Project', 'Task', 'Duration', 'Rounded', 'Hours'])

    duration_rounder = DurationRounder(ROUND_TO_MINUTES)

    previous_day = ''
    daily_duration = total_duration = timedelta(0)
    daily_rounded_duration = total_rounded_duration = timedelta(0)
    daily_rounded_hours = total_rounded_hours = Decimal('0.0')

    for key in sorted(summary):
        duration = timedelta(milliseconds=summary[key])
        rounded_duration = duration_rounder.round(duration)
        rounded_hours = Decimal.from_float(rounded_duration.total_seconds()) / 60 / 60
        rounded_hours = rounded_hours.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        total_duration += duration
        total_rounded_duration += rounded_duration
        total_rounded_hours += rounded_hours

        if previous_day and key[0] != previous_day:
            display_daily_total(table, daily_duration, daily_rounded_duration, daily_rounded_hours)

            daily_duration = duration
            daily_rounded_duration = rounded_duration
            daily_rounded_hours = rounded_hours
        else:
            daily_duration += duration
            daily_rounded_duration += rounded_duration
            daily_rounded_hours += rounded_hours

        previous_day = key[0]

        values = []
        for value in key:
            if value:
                values.append(value)

        table.add_row([key[0], key[1], key[2], key[3], duration, rounded_duration, rounded_hours])

    display_daily_total(table, daily_duration, daily_rounded_duration, daily_rounded_hours)

    display_weekly_total(table, total_duration, total_rounded_duration, total_rounded_hours)

    return table.draw()

def display_daily_total(table, daily_duration, daily_rounded_duration, daily_rounded_hours):
    table.add_row(EMPTY_TABLE_ROW)
    table.add_row([''] * 4 + [
        daily_duration,
        daily_rounded_duration,
        daily_rounded_hours
        ])
    table.add_row(EMPTY_TABLE_ROW)

def display_weekly_total(table, total_duration, total_rounded_duration, total_rounded_hours):
    table.add_row([''] * 4 + [
        duration_to_str(total_duration),
        duration_to_str(total_rounded_duration),
        total_rounded_hours])

def duration_to_str(duration):
    total_seconds = duration.days * (24 * 60 * 60) + duration.seconds
    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def run_detail_report():
    response = requests.get(REPORT_DETAIL_URL, params=get_request_params(), auth=get_auth())

    if not response.ok:
        raise RequestError.create(response)

    summary = {}

    for item in response.json()['data']:
        start_date = item['start'][:10]
        client = map_client(item['client'])
        project = map_project(item['project'])
        task = map_task(item['description'])
        duration = item['dur']

        key = (start_date, client, project, task)

        summary[key] = summary.get(key, 0) + duration

    print(report_summary(summary))

if __name__ == '__main__':
    load_dotenv(verbose=False)
    run_detail_report()
