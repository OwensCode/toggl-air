# pylint: disable=missing-docstring

import sys
import json
import collections

from json import JSONDecodeError

Filters = collections.namedtuple('Filters', ['client'], defaults=[None])

class Config:
    def __init__(self, config_file):
        self.config = Config.__read_config(config_file)

    def round_to_minutes(self):
        return self.config.get('round_to_minutes', 5)

    def rounding_boundary(self):
        round_mins = self.round_to_minutes()
        return self.config.get('rounding_boundary', round_mins / 2.3)

    def client_map(self):
        return self.config.get('client_map', {})

    def project_map(self):
        return self.config.get('project_map', {})

    def task_map(self):
        return self.config.get('task_map', {})

    @staticmethod
    def __read_config(config_file):
        try:
            with open(config_file) as file:
                return json.load(file)
        except FileNotFoundError:
            print(f'Error: Configuration file "{config_file}" not found')
            sys.exit(1)
        except JSONDecodeError as error:
            print(f'Error reading JSON settings file: {error}')
            sys.exit(1)
