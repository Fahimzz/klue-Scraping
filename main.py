import datetime
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import InvalidArgumentException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

main_url = "https://klue.com/product/integrations"

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
# options.add_argument('--headless')  # Optional: run headless if you don't want the browser window to show up
driver = webdriver.Chrome(options=options)
# Open the webpage
try:
    driver.get(main_url)
    driver.maximize_window()
except InvalidArgumentException as e:
    print("Invalid URL:", e)


# Function to write data to CSV file
def write_to_csv(data):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    with open('klue_data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ListingName', 'Category 1', 'ListingIcon', 'Overview', 'ListingScrapeDate', 'ListingRank', 'ListingSellerName'])
        # Check if file is empty, if so, write the header
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'ListingName': data['title'],
            'Category 1': data['tab_name'],
            'ListingIcon': data['image_url'],
            'Overview': data['description'],
            'ListingScrapeDate': today,
            'ListingRank': data['tab_name'] + ' - ' + str(data['rank']),
            'ListingSellerName': ''
        })

tabs = driver.find_elements(By.CSS_SELECTOR, 'ul.cardfilter li a')
for tab in tabs:
    tab_name = tab.text
    # Check if the tab is selected
    if "selected" in tab.get_attribute("class"):
        # Clicking on a selected tab doesn't change anything, so we skip it
        continue
    else:
        tab.click()  # Click on the tab to load its content
        time.sleep(2)  # Wait for the content to load (you may need to adjust this)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Here you can write your code to extract data from the current tab using BeautifulSoup
        cards = soup.find_all('div', class_='card')

        # Iterate over each card and extract category and description
        rank = 0
        for card in cards:
            # Check if the card is visible
            if card['style'] != 'display: none;':
                rank += 1
                category_span = card.find('p', class_='tags').find('span', class_='tag')
                if category_span:
                    category = category_span.text.strip()  # Extract category name
                else:
                    category = "Unknown"

                title = card.find('h3').text.strip()  # Extract title
                image_url = card.find('div', class_='icon').img['data-src']  # Extract image URL
                description = card.find('div', class_='text').text.strip()  # Extract description
                print("Category:", category)
                print("Description:", description)
                data = {
                    'title': title,
                    'tab_name': tab_name,
                    'image_url': image_url,
                    'description': description,
                    'rank': rank
                }
                write_to_csv(data)
        # For demonstration, let's print the tab name and the HTML content
        print("Tab:", tab_name)
        # print("HTML Content:", soup.prettify())
time.sleep(2)
driver.quit()
