import os
import time
import boto3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from tempfile import mkdtemp

# Initialize an S3 client using Boto3
s3_client = boto3.client('s3')

# Main function triggered by AWS Lambda

def lambda_handler(event, context):

    # Extract the stock ticker symbol from the event input
    search_term = event.get('stock-ticker', "")

    # Configure Chrome options for headless browsing
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    # Set up ChromeDriver service
    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log"
    )

    # Initialize WebDriver with Chrome options and service
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    # Initialize a list to store all articles from multiple sites
    all_articles = []

   

    #SCRAPE CNBC
    site = "https://www.cnbc.com/quotes/" + search_term + "?tab=news"

    driver.get(site)
    driver.implicitly_wait(0.5)
    driver.implicitly_wait(0.5)

    articles = driver.find_elements(By.XPATH, '//*[@class="LatestNews-item\"]')
    
    # Loop through each article and extract the title, URL, and timestamp
    for article in articles:
        title = article.find_element(By.XPATH, './/*[@class="LatestNews-headline\"]').get_attribute('title')
        url = article.find_element(By.XPATH, './/*[@class="LatestNews-headline\"]').get_attribute('href')
        timestamp = article.find_element(By.XPATH, './/*[@class="LatestNews-timestamp"]').text

        # Append each article's details as a dictionary to the list
        all_articles.append({'title': title, 'url': url, 'timestamp' : timestamp})
        

    #SCRAPE BI
    site = "https://markets.businessinsider.com/news/" + search_term + "-stock"

    driver.get(site)
    driver.implicitly_wait(0.5)
    
    driver.implicitly_wait(0.5)

    articles = driver.find_elements(By.XPATH, '//*[@class="latest-news__story\"]')

    # Loop through each article and extract the title, URL, and timestamp
    for article in articles:
       title = article.find_element(By.XPATH, './/*[@class="news-link\"]').text
       url = article.find_element(By.XPATH, './/*[@class="news-link\"]').get_attribute('href')
       timestamp = article.find_element(By.XPATH, './/*[@class="latest-news__date\"]').text

       # Append each article's details as a dictionary to the list
       all_articles.append({'title': title, 'url': url, 'timestamp' : timestamp})
    

    # Convert all collected articles to JSON format
    articles_json = json.dumps(all_articles)
        
    # Close the WebDriver
    driver.quit()

    # Define the S3 bucket and object key (file name)
    bucket_name = 'nick-boltons-stock-news'  # Replace with target S3 bucket name
    object_key = f'{search_term}_articles.json'  # The object key in S3

    # Upload the JSON to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=articles_json,
        ContentType='application/json'
    )

    # Return a response with status and details of the uploaded object
    return {
        'statusCode': 200,
        'message': f'Successfully uploaded {object_key} to {bucket_name}',
        'articles': all_articles,
        'event': event
    }