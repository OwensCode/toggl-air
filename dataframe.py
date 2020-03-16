# pylint: disable=missing-docstring

import json

from datetime import timedelta

import pandas as pd
import numpy as np

from duration_rounder import DurationRounder
from calc import calc_rounded_hours

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

    duration_rounder = DurationRounder(config.round_to_minutes())

    dataframe['rounded_duration'] = dataframe['duration'].apply(duration_rounder.round)
    dataframe['rounded_hours'] = dataframe['rounded_duration'].apply(calc_rounded_hours)

    return dataframe

def map_client(dataframe, client_map):
    pass

def calculate_daily_totals(dataframe):
    daily_totals = dataframe.groupby('date', as_index=False).sum()
    daily_totals['client'] = np.nan
    daily_totals['project'] = np.nan
    daily_totals['task'] = np.nan
    return daily_totals

def combine_with_daily_totals(dataframe, daily_totals):
    combined_df = pd.concat([dataframe, daily_totals])
    combined_df = combined_df.sort_values(by=['date', 'client', 'project', 'task'], na_position='last')
    combined_df['client'] = combined_df['client'].fillna('')
    combined_df['project'] = combined_df['project'].fillna('')
    combined_df['task'] = combined_df['task'].fillna('')
    return combined_df
