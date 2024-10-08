import json
import os
import sys
import pytz
import time
# Add the parent directory to the system path to find utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Remove from tmp directory
# Delete existing files from /tmp before writing new data
if os.path.exists('/tmp/today_iso_data.csv'):
    os.remove('/tmp/today_iso_data.csv')

if os.path.exists('/tmp/today_hh_data.csv'):
    os.remove('/tmp/today_hh_data.csv')

if os.path.exists('/tmp/today_fb_data.csv'):
    os.remove('/tmp/today_fb_data.csv')

if os.path.exists('/tmp/today_pitcher_data.csv'):
    os.remove('/tmp/today_pitcher_data.csv')

from utils.today_statcast_hh_data_fetcher import FangraphsStatcastScraper
from utils.today_dashboard_ISO_fetcher import FangraphsDashboardScraper
from utils.today_pitcher_starter_fetcher import PitcherScraperAPI
from utils.today_stats_fb_fetcher import FangraphsStatsScraper
from utils.s3_uploader import upload_to_s3
from utils.s3_uploader import delete_from_s3

from datetime import datetime, timedelta

BUCKET_NAME = 'timjimmymlbdata'

def lambda_handler(event, context):
    # Delete existing files from S3 first
    delete_from_s3(BUCKET_NAME, 'today_iso_data.csv');
    delete_from_s3(BUCKET_NAME, 'today_hh_data.csv');
    delete_from_s3(BUCKET_NAME, 'today_pitcher_data.csv');
    delete_from_s3(BUCKET_NAME, 'today_fb_data.csv');



    # Get today's date and get today's hh and iso data
    # Define the EST timezone
    est = pytz.timezone('America/New_York')

    # Get today's date in EST
    today = datetime.now(est).strftime('%Y-%m-%d')
    start_date = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=15)).strftime('%Y-%m-%d')
    # Save csv to /tmp as well
    FangraphsDashboardScraper.get_batter_iso_for_date(start_date, file_path="/tmp/today_iso_data.csv")
    time.sleep(10)  # Sleep for 10 seconds
    FangraphsStatcastScraper.get_batter_hh_for_date(start_date, file_path="/tmp/today_hh_data.csv")
    time.sleep(10)  # Sleep for 10 seconds
    FangraphsStatsScraper.get_batter_fb_for_date(start_date, file_path="/tmp/today_fb_data.csv")
    time.sleep(10)  # Sleep for 10 seconds
    PitcherScraperAPI.scrape_data(str(today), file_path="/tmp/today_pitcher_data.csv")
    time.sleep(2)  # Sleep for 10 seconds

    # Write to /tmp directory for Lambda environment 
    today_iso_data_path = '/tmp/today_iso_data.csv'
    today_hh_data_path = '/tmp/today_hh_data.csv'
    today_fb_data_path = '/tmp/today_fb_data.csv'
    today_pitcher_data_path = '/tmp/today_pitcher_data.csv'


    # Upload to S3
    upload_to_s3(today_iso_data_path, BUCKET_NAME, 'today_iso_data.csv')
    upload_to_s3(today_hh_data_path, BUCKET_NAME, 'today_hh_data.csv')
    upload_to_s3(today_pitcher_data_path, BUCKET_NAME, 'today_pitcher_data.csv')
    upload_to_s3(today_fb_data_path, BUCKET_NAME, 'today_fb_data.csv')
    return {
        'statusCode': 200,
        'body': json.dumps('Data fetched and saved successfully')
    }

