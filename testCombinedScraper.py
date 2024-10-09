from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # Import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # Import Keys here

# Example usage
search_term = "AAPL"  # Change this to whatever you want to search for

path = r"C:\Users\eric0\OneDrive\Documents\ChromeDriver\chromedriver-win64\chromedriver-win64\chromedriver"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--headless")
options.add_argument("--disable-gpu")  # Disable GPU usage
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-accelerated-2d-canvas")
options.add_argument("--disable-accelerated-video-decode")
options.add_argument("--log-level=3")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

num_article = 1

#SCRAPE CNBC
site = "https://www.cnbc.com/quotes/" + search_term + "?tab=news"

driver.get(site)
driver.implicitly_wait(0.5)
wait = WebDriverWait(driver, 30)
driver.implicitly_wait(0.5)

articles = driver.find_elements(By.XPATH, '//*[@class="LatestNews-item\"]')
article_title = []

for article in articles:
    title = article.find_element(By.XPATH, './/*[@class="LatestNews-headline\"]').get_attribute('title')
    url = article.find_element(By.XPATH, './/*[@class="LatestNews-headline\"]').get_attribute('href')

    article_title.append(title)
    print (f"ARTICLE: {num_article}")
    print (f"TITLE: {title}")
    print ("URL:" + url + "\n\n")

    num_article += 1



#SCRAPE YAHOO
site = "https://finance.yahoo.com/quote/" + search_term + "/news"

driver.get(site)
driver.implicitly_wait(0.5)
wait = WebDriverWait(driver, 30)
driver.implicitly_wait(0.5)

articles = driver.find_elements(By.XPATH, '//*[@class="stream-item story-item yf-1usaaz9\"]')
article_title = []

for article in articles:
    title = article.find_element(By.XPATH, './/*[@class="clamp  yf-1sxfjua\"]').text
    url = article.find_element(By.XPATH, './/*[@class="subtle-link fin-size-small titles noUnderline yf-1e4diqp\"]').get_attribute('href')

    article_title.append(title)
    print (f"ARTICLE: {num_article}")
    print (f"TITLE: {title}")
    print ("URL:" + url + "\n\n")
    num_article += 1

#SCRAPE BI
site = "https://markets.businessinsider.com/news/" + search_term + "-stock"

driver.get(site)
driver.implicitly_wait(0.5)
wait = WebDriverWait(driver, 30)
driver.implicitly_wait(0.5)

articles = driver.find_elements(By.XPATH, '//*[@class="latest-news__story\"]')
article_title = []

for article in articles:
    title = article.find_element(By.XPATH, './/*[@class="news-link\"]').text
    url = article.find_element(By.XPATH, './/*[@class="news-link\"]').get_attribute('href')

    article_title.append(title)
    print (f"ARTICLE: {num_article}")
    print (f"TITLE: {title}")
    print ("URL:" + url + "\n\n")
    num_article += 1
