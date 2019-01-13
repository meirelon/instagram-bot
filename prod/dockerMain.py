import os
import logging
import argparse
import re
from time import sleep
import dockerBot
import pandas as pd

from gcloud import bigquery

def async_query(query, project_id, dataset_id, dest_table):
    client = bigquery.Client.from_service_account_json("scarlet-labs.json")
    query_job = client.run_async_query(str(uuid.uuid4()), query)
    query_job.use_legacy_sql = False
    dataset = bigquery.Dataset(dataset_id, client)
    table = bigquery.Table(dest_table, dataset)
    query_job.destination = table
    query_job.create_disposition = "CREATE_IF_NEEDED"
    query_job.write_disposition = "WRITE_TRUNCATE"
    query_job.begin()
    return True


def main(argv=None):
	parser = argparse.ArgumentParser()
	parser.add_argument('--project_id',
	                    dest='project_id',
	                    default = "scarlet-labs",
	                    help='This is the GCP project you wish to send the data')
	parser.add_argument('--destination_table',
	                    dest='destination_table',
	                    default = "followed_master_table",
	                    help='This is the GCP project you wish to send the data')
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
	                    default = int(20),
	                    help='Number of pages to scan')
	parser.add_argument('--hashtag_list',
	                    dest='hashtag_list',
	                    default = "travelblog travelblogger traveler",
	                    help='total hashtags to scan')

	args, _ = parser.parse_known_args(argv)

	instagram_bot = dockerBot.InstagramBot(username=args.username, password=args.password)
	# First login to the website
	login_webdriver = instagram_bot.login()


	final_table_query = """select *
							from `scarlet-labs.instagram.latest_run`
							union all(
							select * from `scarlet-labs.instagram.followed_master_table`)""".format(destination_table=args.destination_table)


	if bool(re.search(string=args.hashtag_list.lower(), pattern="[.]csv")):
		hashtag_list = [x[1:].strip()
            for x in pd.read_csv(args.hashtag_list, header=None)[0].values if len(x) > 0]
	else:
		hashtag_list = args.hashtag_list.split(" ")

	for hashtag in hashtag_list:
		print(hashtag)
		try:
			df = instagram_bot.follow_hashtag(webdriver=login_webdriver, hashtag=hashtag, pages=args.pages)
			df.to_gbq(project_id=args.project_id,
										 private_key="scarlet-labs.json",
										 destination_table="instagram.latest_run",
										 if_exists="replace",
										 chunksize=100,
										 verbose=True)

			sleep(2)
			async_query(query=final_table_query,
						project_id=args.project_id,
						dataset_id="instagram",
						dest_table=args.destination_table)
		except Exception as e:
			print(e)
			logging.debug(e)
			continue


if __name__ == '__main__':
	main()
