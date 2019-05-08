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
import os, json, re, shutil, sys

# specify defaults

cfg = {
	"site": "https://botsin.space",
}

# scopes define what your bot has access to.
# a list of scopes is available here: https://docs.joinmastodon.org/api/permissions/
# to see what scopes you need for a particular action, check the relevant section in the Mastodon REST API docs.
# for example, if you want to see what you need to manage statuses, see https://docs.joinmastodon.org/api/rest/statuses/
# the permissions below allow you to read posts, see who's following you (and who you're following), post statuses, and view notifications (needed for replying to people).
scopes = ["read:statuses", "read:accounts", "write:statuses", "read:notifications"]

# try to read from the existing config.json. if it's not there, use the defaults to create a new one.
try:
	cfg.update(json.load(open('config.json', 'r')))
except:
	json.dump(cfg, open("config.json", "w+"))

# load meta information, which defines the bot name, source code URL, etc.
# note that it is mandatory to provide a source code link, as stated by the AGPLv3 license.
try:
	meta = json.load(open("meta.json", 'r'))
except OSError as e:
	print("Failed to load meta.json: {}".format(e.strerror))
	sys.exit(1)
except:
	raise

if "client" not in cfg:
	print("No application info -- registering {}} with {}".format(meta['bot_name'], cfg['site']))
	client_id, client_secret = Mastodon.create_app(meta['bot_name'],
		api_base_url=cfg['site'],
		scopes=scopes,
		website=meta['source_url'])

	# save application information
	cfg['client'] = {
		"id": client_id,
		"secret": client_secret
	}

if "secret" not in cfg:
	print("No user credentials -- logging in to {}".format(cfg['site']))
	client = Mastodon(client_id = cfg['client']['id'],
		client_secret = cfg['client']['secret'],
		api_base_url=cfg['site'])

	print("Open this URL and authenticate to give {} access to your bot's account: {}".format(meta['bot_name'], client.auth_request_url(scopes=scopes)))
	# log in and save the provided information
	cfg['secret'] = client.log_in(code=input("Secret: "), scopes=scopes)

# save the current configuration

json.dump(cfg, open("config.json", "w+"))

# test login information
client = Mastodon(
	client_id=cfg['client']['id'],
	client_secret = cfg['client']['secret'],
	access_token=cfg['secret'],
	api_base_url=cfg['site'])

me = client.account_verify_credentials()

print("Done!")
