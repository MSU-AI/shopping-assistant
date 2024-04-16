from django.shortcuts import render, redirect
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
import pandas as pd
import os
import openai
from openai import OpenAI
from .task import *
from .amazon import *
from .chatbot import *

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

def search_form(request):
    return render(request, 'Landing.html')

def login(request):
    return render(request, 'Login.html')

def signup_view(request):
    if request.method == 'POST':
        # Process signup
        return redirect('login')
    return render(request, 'signup.html')

def add_product(request):


    search_term = request.GET.get('search_term', '')

    """   if search_term:
        output_csv_path = "C:\\Users\\anoos\\shopping-assistant-2\\web_project\\scraper\\output.csv"


    if os.path.exists(output_csv_path):
       os.remove(output_csv_path)
    """

    #api_call(search_term)
    results=get_product_data_csv("output.csv")
    #asins = [product[1] for product in results]
    #fetch_and_save_product_details.delay(asins)
    #combined_product_data = fetch_all_product_data()
    #another_function(combined_product_data)
    

    return render(request, 'Results.html', {'products': results})


from bson import json_util

def fetch_all_product_data():
    all_products = product.find()  # Fetch all documents in the 'scraper' collection

    # Initialize an empty list to hold all product details
    all_product_details = []

    for prod in all_products:
        print(f"Processing product: {prod.get('_id')}")
        # Serialize each product and append it to the list
        all_product_details.append(json.dumps(prod, default=json_util.default))

    # Combine all product details into a single string separated by newlines
    combined_product_details = ' '.join(all_product_details)

    return combined_product_details



def another_function(big_string):
    print(big_string)  