# pylint: disable=missing-docstring

import re
import json

from datetime import timedelta

import pandas as pd

from duration_rounder import DurationRounder
from calc import calc_rounded_hours

pd.set_option('max_rows', 999)
pd.set_option('max_colwidth', 80)

def create_dataframe(data, config):
    json_data = json.dumps(data)
    dataframe = pd.read_json(json_data, convert_dates=['start', 'end', 'updated'])

    dataframe['start_local'] = dataframe['start'].dt.tz_localize(None)
    dataframe['date'] = dataframe['start_local'].dt.to_period('D')
    dataframe['duration'] = dataframe['dur'].apply(lambda x: timedelta(milliseconds=x))

    dataframe = dataframe[['date', 'client', 'project', 'description', 'duration']]
    dataframe = dataframe.rename(columns={'description': 'task'})

    dataframe = dataframe.groupby(['date', 'client', 'project', 'task'], as_index=False).sum()
    dataframe = dataframe.sort_values(by=['date', 'client', 'project', 'task'])

    __map_descriptive_cols(dataframe, config)
    __perform_rounding(dataframe, config)

    return dataframe

def __map_descriptive_cols(dataframe, config):
    dataframe['client'] = dataframe['client'].apply(lambda x: __map_item(x, config.client_map()))
    dataframe['project'] = dataframe['project'].apply(lambda x: __map_item(x, config.project_map()))
    dataframe['task'] = dataframe['task'].apply(lambda x: __map_item(x, config.task_map()))
    return dataframe

def __perform_rounding(dataframe, config):
    duration_rounder = DurationRounder(config.round_to_minutes())
    dataframe['rounded_duration'] = dataframe['duration'].apply(duration_rounder.round)
    dataframe['rounded_hours'] = dataframe['rounded_duration'].apply(calc_rounded_hours)
    return dataframe

def __map_item(item, lookup_map):
    if lookup_map.get(item):
        return lookup_map[item]

    for key, value in lookup_map.items():
        if re.fullmatch(key, item):
            return value

    return item

def calculate_daily_totals(dataframe):
    daily_totals = dataframe.groupby('date', as_index=False).sum()
    return daily_totals[['date', 'duration', 'rounded_duration', 'rounded_hours']]

def calculate_totals(dataframe):
    return dataframe[['duration', 'rounded_duration', 'rounded_hours']].sum()

def combine_with_daily_totals(dataframe, daily_totals):
    combined_df = pd.concat([dataframe, daily_totals])
    combined_df = combined_df.sort_values(by=['date', 'client', 'project', 'task'], na_position='last')
    combined_df['client'] = combined_df['client'].fillna('')
    combined_df['project'] = combined_df['project'].fillna('')
    combined_df['task'] = combined_df['task'].fillna('')
    return combined_df
