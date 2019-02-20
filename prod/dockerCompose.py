import os
import uuid
import logging
import re
from time import sleep
import dockerBot
import pandas as pd


if __name__ == '__main__':
	project_id = os.environ['project_id']
	destination_table = os.environ['destination_table']
	username = os.environ['username']
	password = os.environ['password']
	pages = os.environ['pages']
	hashtag_list = os.environ['hashtag_list']

	instagram_bot = dockerBot.InstagramBot(username=username, password=password)
	# First login to the website
	login_webdriver = instagram_bot.login()

	# unfollow_df = instagram_bot.unfollow_users(webdriver=login_webdriver)
	# unfollow_df.to_gbq(project_id=project_id,
	# 							 private_key="scarlet-labs.json",
	# 							 destination_table="instagram.{}".format("unfollows"),
	# 							 if_exists="append",
	# 							 chunksize=100,
	# 							 verbose=True)


	if bool(re.search(string=hashtag_list.lower(), pattern="[.]csv")):
		hashtag_list = [x[1:].strip()
	        for x in pd.read_csv(hashtag_list, header=None)[0].values if len(x) > 0]
	else:
		hashtag_list = hashtag_list.split(" ")

	for hashtag in hashtag_list:
		print(hashtag)
		try:
			df = instagram_bot.follow_hashtag(webdriver=login_webdriver, hashtag=hashtag, pages=pages)
			df.to_gbq(project_id=project_id,
										 private_key="scarlet-labs.json",
										 destination_table="instagram.{}".format(destination_table),
										 if_exists="append",
										 chunksize=100,
										 verbose=True)

		except Exception as e:
			print(e)
			logging.debug(e)
			continue
