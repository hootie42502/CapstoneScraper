import logging
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_driver(path=None, headless=True):
    """Initializes and returns a Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-accelerated-2d-canvas")
    options.add_argument("--disable-accelerated-video-decode")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    
    if headless:
        options.add_argument("--headless")

    return webdriver.Chrome(options=options) #, service=Service(path)) if path else webdriver.Chrome(options=options)

def scrape_articles(driver, site_url, article_xpath, title_xpath, url_xpath, timestamp_xpath):
    """Scrapes articles from the given site URL."""
    logging.info(f"Scraping {site_url} ...")
    driver.get(site_url)

    WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, article_xpath))
    )
    
    articles = driver.find_elements(By.XPATH, article_xpath)
    article_data = []

    for article in articles:
        try:
            title = article.find_element(By.XPATH, title_xpath).text
            url = article.find_element(By.XPATH, url_xpath).get_attribute('href')
            timestamp = article.find_element(By.XPATH, timestamp_xpath).text
            article_data.append({'title': title, 'url': url, 'timestamp' : timestamp})
        except Exception as e:
            logging.error(f"Error scraping article: {e}")
    
    return article_data

def display_articles(articles, site_name):
    """Displays the scraped articles."""
    logging.info(f"Displaying articles from {site_name}:")
    for i, article in enumerate(articles, start=1):
        logging.info(f"ARTICLE {i}: {article['title']} \nURL: {article['url']}  \nTIME: {article['timestamp']}\n")

def scrape_site(driver, search_term):
    """Scrapes multiple sites for the given search term."""
    search_sites = [
        {
            'name': 'CNBC',
            'url': f"https://www.cnbc.com/quotes/{search_term}?tab=news",
            'article_xpath': '//*[@class="LatestNews-item\"]',
            'title_xpath': './/*[@class="LatestNews-headline\"]',
            'url_xpath': './/*[@class="LatestNews-headline\"]',
            'timestamp_xpath': './/*[@class="LatestNews-timestamp\"]'
        },
        {
            'name': 'Yahoo Finance',
            'url': f"https://finance.yahoo.com/quote/{search_term}/news",
            'article_xpath': '//*[@class="stream-item story-item yf-1usaaz9\"]',
            'title_xpath': './/*[@class="clamp  yf-y1ahm5\"]',
            'url_xpath': './/*[@class="subtle-link fin-size-small titles noUnderline yf-1e4diqp\"]',
            'timestamp_xpath': './/*[@class="publishing yf-1weyqlp\"]'
        },
        {
            'name': 'Business Insider',
            'url': f"https://markets.businessinsider.com/news/{search_term}-stock",
            'article_xpath': '//*[@class="latest-news__story\"]',
            'title_xpath': './/*[@class="news-link\"]',
            'url_xpath': './/*[@class="news-link\"]' ,
            'timestamp_xpath': './/*[@class="latest-news__date\"]'
        }, 
        {
            'name': 'Seeking Alpha',
            'url': f"https://seekingalpha.com/symbol/{search_term}/news",
            'article_xpath': '//*[@data-test-id="post-list-item\"]',
            'title_xpath': './/*[@data-test-id="post-list-item-title\"]',
            'url_xpath': './/*[@data-test-id="post-list-item-title\"]' ,
            'timestamp_xpath': './/*[@data-test-id="post-list-date\"]'
        }

    ]
    
    all_articles = []
    for site in search_sites:
        articles = scrape_articles(driver, site['url'], site['article_xpath'], site['title_xpath'], site['url_xpath'], site['timestamp_xpath'])
        if articles:
            all_articles.append({site['name']: articles})
        display_articles(articles, site['name'])

    return all_articles

def save_to_json(data, search_term):
    """Saves the scraped article data to a JSON file."""
    filename= f"{search_term}_scraped_articles.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Saved scraped articles to {filename}")

def main(search_term, driver_path=None):
    """Main function to initialize scraping."""
    driver = init_driver(driver_path,False)
    
    try:
        all_articles = scrape_site(driver, search_term)
        if all_articles:
            save_to_json(all_articles, search_term)
    finally:
        driver.quit()

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 testModularScraper.py <STOCK_TICKER>")
        sys.exit(1)

    search_term = sys.argv[1]  # Get stock ticker from command line

    driver_path = r"C:\Users\eric0\OneDrive\Documents\ChromeDriver\chromedriver-win64\chromedriver-win64\chromedriver"
    main(search_term, driver_path)
