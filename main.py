#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 09:27:21 2020

@author: vlad
"""
import os
from dotenv import load_dotenv, find_dotenv
from scraper import scraper

load_dotenv(find_dotenv())

GD_USERNAME = os.environ.get("GD_USERNAME")
GD_PASSWORD = os.environ.get("GD_PASSWORD")

def main():
    print('Glassdoor Job Scraper.')
    job_title = input('Job search input: ')
    location = input('Location: ')
    while True:
        outcome = scraper(job_title, location, GD_USERNAME, GD_PASSWORD)
        if outcome:
            break

if __name__ == "__main__": 
    main()