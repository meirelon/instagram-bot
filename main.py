import argparse
import bot


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
	parser.add_argument('--file_path',
	                    dest='file_path',
	                    default = None,
	                    help='File Path')
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

	hashtag_list = args.hashtag_list.split(" ")
	for hashtag in hashtag_list:
		print(hashtag)
		try:
			instagram_bot.follow_hashtag(webdriver=login_webdriver, hashtag=hashtag, pages=args.pages)
		except:
			continue

if __name__ == '__main__':
	main()
