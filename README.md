# MLB-ML-DataFetcher

**MLB-ML-DataFetcher** is a Python-based AWS Lambda function designed to fetch MLB player statistics and pitcher starter information. This data is then uploaded to Amazon S3 for further machine learning analysis or other purposes. The function is containerized using Docker and deployable via AWS CDK.

## Features
- Fetches daily MLB statistics such as FB data, HH data, and pitcher matchups.
- Automates data collection for machine learning models.
- Uses Chrome headless for web scraping.
- Uploads the scraped data to Amazon S3 for storage and further processing.
- Deployed as a Lambda function using Docker with dependencies.
