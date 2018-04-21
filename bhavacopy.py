#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 rmad17 <souravbasu17@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Get a zipped copy of bhavacopy published by BSE and extract the csv. Once done
parse the csv data.
"""
import csv
import io

from datetime import datetime, timedelta

from zipfile import ZipFile

import redis

import requests


def get_date_string():
    """
    To get the bhav copy url we need to generate the correct url.
    Here an assumption is made that bhav copy is updated few hours post closure
    of trading. Hence fetch bhav copy for the same day only after 7PM.
    """
    today = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)
    today_close = today.replace(hour=19, minute=0, second=0, microsecond=0)
    week_day = today.weekday()

    # Monday
    if week_day == 0:
        if today <= today_close:
            valid_date = today - timedelta(days=3)
        else:
            valid_date = today

    # Tuesday - Friday
    if week_day in range(1, 5):
        if today <= today_close:
            valid_date = yesterday
        else:
            valid_date = today

    # Saturday
    if week_day == 5:
            valid_date = yesterday

    # Sunday
    if week_day == 6:
            valid_date = today - datetime.timedelta(days=2)

    return valid_date.strftime('%d%m%y')


def parse_csv(date_str):
    """
    Parses csv and returns a dict consisting of rows of data
    :param: datestring used in url
    :rtype: dict
    """
    dataset = []
    with open('EQ{}.CSV'.format(date_str), 'r') as f:
        cr = csv.reader(f)
        for index, r in enumerate(cr):
            if index == 0:
                continue
            row_data = {}
            row_data['code'] = r[0]
            row_data['name'] = r[1]
            row_data['open'] = r[4]
            row_data['high'] = r[5]
            row_data['low'] = r[6]
            row_data['close'] = r[7]
            dataset.append(row_data)
    return str(dataset)


def update_to_redis(date_str, data):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(date_str, data)


def process():
    """
    main aggregator function
    """
    date_str = get_date_string()
    url = (
        'http://www.bseindia.com/download/BhavCopy/Equity/EQ{}_CSV.ZIP'.format(
            date_str))
    response = requests.get(url)
    z = ZipFile(io.BytesIO(response.content))
    z.extractall()
    data = parse_csv(date_str)
    update_to_redis(date_str, data)


if __name__ == '__main__':
    process()
