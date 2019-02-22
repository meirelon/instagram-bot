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
	private_key = os.environ["private_key"]

	instagram_bot = dockerBot.InstagramBot(username=username, password=password)
	# First login to the website
	login_webdriver = instagram_bot.login()

	# unfollow_df = instagram_bot.unfollow_users(webdriver=login_webdriver)
	# unfollow_df.to_gbq(project_id=project_id,
	# 							 private_key="scarlet-labs.json",
	# 							 destination_table="instagram.{}".format("unfollows"),
	# 							 if_exists="append",
	# 							 chunksize=100)


	if hashtag_list.lower() == "bq":
		q = """select distinct hashtag
				from `{project_id}.instagram.hashtag_list`
				where r = extract(dayofweek from current_date())""".format(project_id=project_id)
		hashtag_df = pd.read_gbq(query=q, project_id=project_id, dialect="standard", private_key=private_key)
		hashtag_list = [x.replace("#", "") for x in hashtag_df["hashtag"].values if len(x) > 0]
	else:
		hashtag_list = hashtag_list.split(" ")

	for hashtag in hashtag_list:
		print(hashtag)
		try:
			df = instagram_bot.follow_hashtag(webdriver=login_webdriver, hashtag=hashtag, pages=pages)
			df.to_gbq(project_id=project_id,
										 private_key=private_key,
										 destination_table="instagram.{}".format(destination_table),
										 if_exists="append",
										 chunksize=100)

		except Exception as e:
			print(e)
			logging.debug(e)
			continue
