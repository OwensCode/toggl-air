# Toggl Report

Export Toggl reports into a text format that can be copied and pasted into a company timesheet.

```
usage: report.py [-h] [-s START] [-e END] [--client CLIENT] config

positional arguments:
  config                configuration file in JSON format

options:
  -h, --help            show this help message and exit
  -s START, --start START
                        start date, default is most recent Saturday
  -e END, --end END     end date, default is today
  --client CLIENT       only include time for this client
```

## Toggl Credentials

See `.env-example` for Toggl configuration settings. Copy the file to `.env` and edit it to update
the values with your personal settings, as per the comments in the file.

## Configuration

Round and group values with different settings, in case you need to report time into different
timesheet systems with different requirements.

Example configuration, as shown in `example_configuration.json`:

```json
{
  "round_to_minutes" : 15,
  "rounding_boundary": 6.5,
  "client_map" : {
    "RN-.*" : "RN",
    "HS2-.*" : "Bounteous",
    "B8-Admin": "Admin"
  },
  "project_map" : {
    "Tech": "Technology"
  },
  "task_map" : {
    "Onboarding": "Project Ramp-up"
  }
}
```

- `round_to_minutes` - round the task times to this number of minutes, either going up or down,
  depending on the boundary. The default is `5`.
- `rounding_boundary` - the boundary as to whether the rounding goes up or down. In the example
  shown, anything more than 6.5 minutes over the threshold will be rounded up, and anything below
  will be rounded down. The default is `round_to_minutes / 2.3`. You might need to play with this to
  make it fair, depending on whether you typically have a lot of short tasks per day compared to a
  small number of long tasks. If the setting is "unfair" you could end up looking like you worked a
  lot more time than you actually did, or sometimes less than you actually did. The more tasks you
  have in a day, the larger the bigger the discrepancy can be.
- `client_map` - used for renaming clients. Can be useful if you need to enter time into multiple
  systems, or for report formatting.
- `project_map` - same intention as for renaming clients
- `task_map` - same intention as renaming clients and projects, but possibly less useful if you have
  the same task name repeated over different projects or clients
