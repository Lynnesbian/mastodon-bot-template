#!/usr/bin/env python3
# https://github.com/Lynnesbian/fediverse-bot-template
# Copyright (C) 2019 Lynne (@lynnesbian@fedi.lynnesbian.space)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# import Mastodon.py and other modules
from mastodon import Mastodon
import json, random

try:
	cfg = json.load(open('config.json', 'r'))
except:
	print("Couldn't load config.json. Make sure you run main.py first!\n-----")
	raise
meta = json.load(open('meta.json', 'r'))

# log in
client = Mastodon(
	client_id=cfg['client']['id'],
	client_secret=cfg['client']['secret'],
	access_token=cfg['secret'],
	api_base_url=cfg['site'])

# make a post!
client.status_post("Hi! Your random number is: {}".format(random.randint(0,10000))
