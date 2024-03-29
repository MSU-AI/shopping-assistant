from django.shortcuts import render
from .models import product
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import csv
import time
from concurrent.futures import ThreadPoolExecutor
import requests
import datetime
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "X-Amzn-Trace-Id": "Root=1-65c58daf-3a2c6c3a7adb35726b652acb"
}

'''
AMAZON
'''

def get_product_links_amazon(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    a_tag = soup.find_all('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
    
    product_link_list = []
    for tag in a_tag:
        href = tag.get('href', '')
        # Check if href is a complete URL or a relative path
        if href.startswith('http'):
            product_link_list.append(href)
        else:
            # Ensure it's a relative path and prepend the base URL
            product_link_list.append('https://www.amazon.com' + href)
            
    return product_link_list


def get_product_data_amazon(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find(id='productTitle').get_text().strip() if soup.find(id='productTitle') else 'N/A'
    price = soup.find('span', class_='a-offscreen').get_text().strip() if soup.find('span', class_='a-offscreen') else 'N/A'
    rating = soup.find('span', id='acrCustomerReviewText').get_text().strip() if soup.find('span', id='acrCustomerReviewText') else 'N/A'
    score = soup.find('span', class_='a-icon-alt').get_text().strip() if soup.find('span', class_='a-icon-alt') else 'N/A'
    review_summary = soup.find(id='product-summary').get_text().strip() if soup.find(id='product-summary') else 'N/A'

    return [url, title, price, rating, score, review_summary]

"""
WALMART
"""

def get_product_links_walmart(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    a_tags = soup.find_all('a', class_='absolute w-100 h-100 z-1 hide-sibling-opacity')
    
    links = [a['href'] for a in a_tags if 'href' in a.attrs and not a['href'].startswith('https')]

    base_url = 'https://www.walmart.com'
    full_links = [base_url + link for link in links]
    
    return full_links

def get_product_details_walmart(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find(id="main-title").text
    price = soup.find('span', itemprop='price').text
    rating = soup.find('a', itemprop='ratingCount').text if soup.find('a', itemprop='ratingCount') else 'N/A'
    score = soup.find('span', class_='f7 rating-number').text if soup.find('span', class_='f7 rating-number') else 'N/A'
    image = soup.find('img', class_=['noselect', 'db'])['src']
    return [title,price,rating,score,image]


"""
BEST BUY
"""

def get_product_links_bestbuy(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    h4_elements = soup.find_all('h4', class_='sku-title')
    links = []
    for h4 in h4_elements:
        a_tag = h4.find('a', href=True)
        if a_tag:
            link = 'https://www.bestbuy.com' + a_tag['href'] 
            links.append(link)
    
    return links

def get_product_details_bestbuy(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find('h1',class_='heading-5 v-fw-regular').text
    price_div = soup.find('div', {'data-testid': 'customer-price'})
    price = price_div.find('span', {'aria-hidden': 'true'}).text
    rating = soup.find('span',class_='c-reviews order-2').text
    score = soup.find('span',class_="ugc-c-review-average font-weight-medium order-1").text
    image = soup.find('img',class_='primary-image')['src']
    return [title,price,rating,score,image]

"""
TARGET (using selenium)
"""

def get_product_links_target(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    
    # wait for page to load before finding links to products
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[@data-test="product-title"]'))
    )
    
    product_elements = driver.find_elements(By.XPATH, '//a[@data-test="product-title"]')
    product_link_list = [element.get_attribute('href') for element in product_elements]    
    driver.quit()
    return product_link_list

def get_product_details_target(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    products_info = []

    driver.get(url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-title"]'))
    )
    
    title = driver.find_element(By.CSS_SELECTOR, '[data-test="product-title"]').text
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-price"]'))
    )
    price = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]').text
    
    try:
        rating_elements = driver.find_element(By.CSS_SELECTOR, '[data-test="ratings"]').text
    except:
        rating_elements = "No rating"

    parts = rating_elements.split(' ')
    score = f"{parts[0]}/{parts[3]}"
    rating = parts[-2] + " ratings"

    image_element = driver.find_element(By.CSS_SELECTOR, 'img[alt^="Logitech M240 Wireless Mouse"]')
    image = image_element.get_attribute('src')
    
    products_info.append((title, price, rating, image))
    
    driver.quit()
    return products_info

def index(request):
    return HttpResponse("<h1>App is running</h1>")


def add_product_data_to_db(data):
    # Assuming your Product model has fields corresponding to the data list items
    # e.g., URL, Title, Price, Ratings, Score, Review Summary
    # Adapt field names based on your actual model definition
    records = {
        "url": str(data[0]),
        "title" : str(data[1]),
        "price " : str(data[2]),
        "ratings": str(data[3]),
        "score" : str(data[4]),
        "review_summary" : str(data[5])
    }
    product.insert_one(records)

def add_product(request):
    link = 'https://www.amazon.com/s?k=razer+mouse'
    product_links = get_product_links_amazon(link)

    # Using ThreadPoolExecutor to concurrently fetch product data
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_product_data_amazon, product_links))

    # Now, iterate through the results and add them to the database
    #for data in results:
        #add_product_data_to_db(data)
    
    # Instead of returning an HttpResponse, render the template with the results
    return render(request, 'add_products.html', {'products': results})
    

def get_all_product(request):
    products = product.find()
    return(products)

