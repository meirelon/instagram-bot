import argparse
import re
import bot
import pandas as pd


def main(argv=None):
	parser = argparse.ArgumentParser()

	parser.add_argument('--chromedriver_path',
	                    dest='chromedriver_path',
	                    default = None,
	                    help='Chromedriver Path')
	parser.add_argument('--username',
	                    dest='username',
	                    default = None,
	                    help='Username')
	parser.add_argument('--password',
	                    dest='password',
	                    default = None,
	                    help='Password')
	parser.add_argument('--pages',
	                    dest='pages',
	                    default = int(200),
	                    help='This is the GCP project you wish to send the data')
	parser.add_argument('--hashtag_list',
	                    dest='hashtag_list',
	                    default = "travelblog travelblogger traveler",
	                    help='This is the GCP project you wish to send the data')

	args, _ = parser.parse_known_args(argv)

	instagram_bot = bot.InstagramBot(chromedriver_path=args.chromedriver_path,
									username=args.username,
									password=args.password)
	# First login to the website
	login_webdriver = instagram_bot.login()


	if bool(re.search(string=args.hashtag_list.lower(), pattern="[.]csv")):
		hashtag_list = [x[1:].strip()
            for x in pd.read_csv(args.hashtag_list, header=None)[0].values]
	else:
		hashtag_list = args.hashtag_list.split(" ")

	for hashtag in hashtag_list:
		print(hashtag)
		try:
			df = instagram_bot.follow_hashtag(webdriver=login_webdriver, hashtag=hashtag, pages=args.pages)
			df.to_gbq(project_id="scarlet-labs",
										 private_key="scarlet-labs.json",
										 destination_table="instagram.followed_master_table",
										 if_exists="append",
										 chunksize=100,
										 verbose=True)
		except:
			continue


if __name__ == '__main__':
	main()
