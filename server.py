# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 rmad17 <souravbasu17@gmail.com>
#
# Distributed under terms of the MIT license.

import json

import os

import cherrypy

from jinja2 import Environment, FileSystemLoader

import redis

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(CUR_DIR), trim_blocks=True)


class Index:

    def __init__(self):
        self.redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_redis_data(self, date_str):
        raw_data = self.redis_con.get('bhavcopy')
        raw_data = json.loads(raw_data.decode('utf-8'))
        return raw_data[date_str]

    def search_by_name(self, name='', date_str='200418'):
        context = []
        for i, ds in enumerate(self.get_redis_data(date_str)):
            print(name, ds['name'])
            if ds['name'].strip() == name.strip():
                if float(ds['close']) > float(ds['open']):
                    ds['fontcolor'] = "font-white bg-success"
                else:
                    ds['fontcolor'] = "font-white bg-danger"
                context.append(ds)
                break
        return context

    def get_data(self, date_str='200418'):
        context = []
        for i, ds in enumerate(self.get_redis_data(date_str)):
            if i > 9:
                break
            if float(ds['close']) > float(ds['open']):
                ds['fontcolor'] = "font-green"
            else:
                ds['fontcolor'] = "font-orange"
            context.append(ds)
        return context

    @cherrypy.expose()
    def index(self):
        template = env.get_template('stocks.html')
        context = {'stocks': self.get_data()}
        return template.render(**context)

    @cherrypy.expose()
    def search(self, name=''):
        template = env.get_template('stocks.html')
        context = {'stocks': self.search_by_name(name)}
        return template.render(**context)


cherrypy.quickstart(Index(), '/')
