#!/usr/bin/env python3

import json
import sys
import argparse
import time
import requests
import singer
import backoff
import copy

from datetime import date, datetime, timedelta

base_url = 'https://api.stringee.com/v1/call/log'

logger = singer.get_logger()
session = requests.Session()

schema = {'type': 'object',
            'properties':
            {
                "uuid": {'type': ['null', 'string']},
                "id": {'type': ['null', 'string']},
                "to_alias": {'type': ['null', 'string']},
                "from_number": {'type': ['null', 'string']},
                "day": {'type': ['null', 'string']},
                "participants": {'type': ['null', 'string']},
                "to_number": {'type': ['null', 'string']},
                "object_type": {'type': ['null', 'string']},
                "from_alias": {'type': ['null', 'string']},
                "start_time_datetime": {'type': ['null', 'string']},
                "stop_time_datetime": {'type': ['null', 'string']},
                "created_datetime": {'type': ['null', 'string']},
                "project_name": {'type': ['null', 'string']},
                "from_user_id": {'type': ['null', 'string']},
                "record_path": {'type': ['null', 'string']},
                "answer_time": {'type': ['null', 'integer']},
                "stop_time": {'type': ['null', 'integer']},
                "first_answer_time": {'type': ['null', 'integer']},
                "answer_duration": {'type': ['null', 'integer']},
                "from_internal": {'type': ['null', 'integer']},
                "number_tts_character": {'type': ['null', 'integer']},
                "project_id": {'type': ['null', 'integer']},
                "to_internal": {'type': ['null', 'integer']},
                "amount": {'type': ['null', 'number']},
                "created": {'type': ['null', 'integer']},
                "video_call": {'type': ['null', 'integer']},
                "recorded": {'type': ['null', 'integer']},
                "start_time": {'type': ['null', 'integer']},
                "account_id": {'type': ['null', 'integer']},
                "answer_duration_minutes": {'type': ['null', 'integer']},
                "answer_time_datetime": {'type': ['null', 'string']}
            }
        }

def giveup(error):
    logger.error(error.response.text)
    response = error.response
    return not (response.status_code == 429 or
                response.status_code >= 500)

@backoff.on_exception(backoff.constant,
                      (requests.exceptions.RequestException),
                      jitter=backoff.random_jitter,
                      max_tries=5,
                      giveup=giveup,
                      interval=30)
def request(url, headers):
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    return response
    
def do_sync(JWT):
    state = {'start_date': start_date}
    next_date = start_date
    prev_schema = {}
    
    try:
        response = request(base_url, headers=
        {
            'Content-Type': 'application/json',
            'X-STRINGEE-AUTH': JWT
        })
        payload = response.json()

        singer.write_schema('stringee_call_logs', schema, 'date')

        # if payload['date'] == next_date:
        for r in payload['data']['calls']:
            r['answer_time_datetime'] = str(r['answer_time_datetime'])
            singer.write_records('stringee_call_logs', [r])

    except requests.exceptions.RequestException as e:
        logger.fatal('Error on ' + e.request.url +
                     '; received status ' + str(e.response.status_code) +
                     ': ' + e.response.text)
        singer.write_state(state)
        sys.exit(-1)

    singer.write_state(state)
    logger.info('Tap exiting normally')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config', help='Config file', required=False)
    parser.add_argument(
        '-s', '--state', help='State file', required=False)

    args = parser.parse_args()

    if args.config:
        with open(args.config) as file:
            config = json.load(file)
    else:
        config = {}

    if args.state:
        with open(args.state) as file:
            state = json.load(file)
    else:
        state = {}
    do_sync(config.get('JWT'))


if __name__ == '__main__':
    main()