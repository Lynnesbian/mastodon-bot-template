#!/usr/bin/env python3
# Copyright (C) 2019 Lynne (@lynnesbian@fedi.lynnesbian.space)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

from mastodon import Mastodon, StreamListener
from bs4 import BeautifulSoup

# use multiprocessing to run multiple reply listener threads at once
# this means we can handle more than one reply at a time!
from multiprocessing import Pool
import os, random, re, json, re, sys

try:
	cfg = json.load(open('config.json', 'r'))
except:
	print("Couldn't load config.json. Make sure you run main.py first!\n-----")
	raise
meta = json.load(open('meta.json', 'r'))

print("Logging in...")

client = Mastodon(
	client_id=cfg['client']['id'],
	client_secret=cfg['client']['secret'],
	access_token=cfg['secret'],
	api_base_url=cfg['site'])

# extract the handle (the @username@instance part)
handle = "@{}@{}".format(client.account_verify_credentials()['username'], re.match("https://([^/]*)/?", cfg['site']).group(1)).lower()

# convert the text of the status to plain text
# this part's a bit of a mess!!
def extract_toot(toot):
	toot = toot.replace("&apos;", "'") #convert HTML stuff to normal stuff
	toot = toot.replace("&quot;", '"') #ditto
	soup = BeautifulSoup(toot, "html.parser")
	for lb in soup.select("br"): #replace <br> with linebreak
		lb.insert_after("\n")
		lb.decompose()

	for p in soup.select("p"): #ditto for <p>
		p.insert_after("\n")
		p.unwrap()

	for ht in soup.select("a.hashtag"): #make hashtags no longer links, just text
		ht.unwrap()

	for link in soup.select("a"): #ocnvert <a href='https://example.com>example.com</a> to just https://example.com
		link.insert_after(link["href"])
		link.decompose()

	text = soup.get_text()
	text = re.sub("https://([^/]+)/(@[^ ]+)", r"\2@\1", text) #put mastodon-style mentions back in
	text = re.sub("https://([^/]+)/users/([^ ]+)", r"@\2@\1", text) #put pleroma-style mentions back in
	text = text.rstrip("\n") #remove trailing newline
	# text = re.sub(r"^@[^@]+@[^ ]+\s*", r"", text) #remove the initial mention
	text = text.lower() #treat text as lowercase for easier keyword matching
	return text

# handle error messages
def error(message, acct, post_id, visibility):
	print("error: {}".format(message))
	temp_client = Mastodon(
		client_id=cfg['client']['id'],
		client_secret=cfg['client']['secret'],
		access_token=cfg['secret'],
		api_base_url=cfg['site'])
	temp_client.status_post("{}\n{}\nContact the admin ({}) for assistance.".format(acct, message, meta['admin']), post_id, visibility = visibility, spoiler_text = "Error")

# handle replies
def process_mention(client, notification):
	acct = "@" + notification['account']['acct'] #get the account's @
	print("mention detected")
	post = notification['status']
	mention_text = extract_toot(post['content'])

	# copy the visibility setting of the mention, but replace public with unlisted
	visibility = post['visibility']
	if visibility == "public":
		visibility = "unlisted"

	# create the toot you want to reply with here.
	toot = "Hello there! Thanks for mentioning me!"

	# replace any @'s in the post with "fake" ones.
	# unicode character 200B is the zero width space, which functions as a regular space, but it's invisible.
	# this means that the mention still looks like a real one, but it doesn't actually mention the person in question.
	# this prevents your bot from accidentally mentioning people.
	toot = toot.replace("@", "@\u200B")

	# finally, add the handle of the person who mentioned your bot and caused it to reply.
	toot = acct + toot # prepend the @

	# if something goes wrong, you should call the error function, and then return.
	# this lets the person who mentioned the bot know that something has failed.
	# for example:
	catastrophic_error = False
	if catastrophic_error:
		error("Something terrible has happened!!", acct, post['id'], visibility)
		return

	# finally, send the post!
	client.status_post(
		status = toot, # the toot you'd like to send
		in_reply_to_id = post['id'], # the post you're replying to
		visibility=visibility # whether the toot is public/unlisted/etc
	)

class ReplyListener(StreamListener):
	def __init__(self):
		self.pool = Pool(8) # listen on 8 threads at once

	def on_notification(self, notification): #listen for notifications
		if notification['type'] == 'mention': #if we're mentioned:
			self.pool.apply_async(process_mention, args=(client, notification))

# create a new instance of our ReplyListener class
rl = ReplyListener()
client.stream_user(rl) #go!
