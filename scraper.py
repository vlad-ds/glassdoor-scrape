#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 09:06:32 2020

@author: vlad
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import json

def scraper(job_title, location, username, password):
    print("Accessing GD...")
    #start the driver
    driver = webdriver.Firefox()
    driver.implicitly_wait(60)
    actions = ActionChains(driver)
    
    #access glassdoor and sign in
    url = "http://www.glassdoor.com/"
    driver.get(url)
    
    #accept cookies
    try:
        sleep(5)
        driver.find_element_by_id('onetrust-accept-btn-handler').click()
    except:
        pass
    
    sign_in_start = driver.find_element_by_class_name('sign-in')
    sign_in_start.click()
    
    try:
        sign_in_div = driver.find_element_by_class_name('fullContent')
    except:
        sign_in_div = driver.find_element_by_class_name('gdUserLogin')
    
    
    email_input = sign_in_div.find_element_by_id('userEmail')
    password_input = sign_in_div.find_element_by_id('userPassword')
    sign_in_button = sign_in_div.find_element_by_class_name('gd-ui-button')
    
    email_input.send_keys(username)
    password_input.send_keys(password)
    
    try:
        sign_in_button.click()
    except:
        print("Could not sign in.")
        return False
    
    sleep(5)
    
    #initiate search
    job_title_input = driver.find_element_by_id('sc.keyword')
    location_input = driver.find_element_by_id('sc.location')
    search_button = driver.find_element_by_class_name('gd-ui-button')
    
    attempts = 5
    
    while attempts:
        try:
            job_title_input.clear()
            location_input.clear()
            location_input.send_keys(location)
            job_title_input.send_keys(job_title)
            search_button.click()
            break
        except:
            attempts -= 1
            
    if attempts == 0:
        print('Could not execute job search.')    
        return False
    
    #accept cookies
    try:
        sleep(5)
        driver.find_element_by_id('onetrust-accept-btn-handler').click()
    except:
        pass
    
    #acquire job data
    jobs = []
    
    #instantiate page counter
    page = 1
    
    #get base url (to which we'll add page number)
    url = driver.current_url
    
    #start pages loop
    while True:
        
        #every page lists 30 jobs. we open each in turn and collect the data
        job_elements = driver.find_elements_by_class_name('jl')
        
        if not job_elements:
            print(f'Done. {len(jobs)} total jobs found.')
            break
        
        print('Extracting jobs...')
        
        for i, e in enumerate(job_elements): 
            sleep(5)
            
            try:
                #open the job. try clicking until we open a new window (5 attempts)
                attempts = 5
                while attempts:
                    e.click()
                    sleep(5)
                    if len(driver.window_handles) > 1:
                        break
                    else:
                        attempts -= 1
                
                #if out of attempts, throw exception and move on to next job
                if not attempts: 
                    1/0
                    
                #switch driver to the second tab
                driver.switch_to.window(driver.window_handles[1])
                sleep(5)
                
                position, company, description, job_url = None, None, None, None
                
                try:
                    position = driver.find_element_by_class_name('css-17x2pwl').text
                except: 
                    pass
                
                try:
                    company = driver.find_element_by_class_name('css-16nw49e').text
                except:
                    pass
            
                try:
                    description = driver.find_element_by_class_name('css-58vpdc').text
                except: 
                    pass
                
                job_url = driver.current_url
                
                job = {'position': position,
                       'company': company,
                       'description': description, 
                       'url': job_url}
                
                #print(job['position'], job['company'])
                
                jobs.append(job)
                
                #close job tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print('Element extraction failed')
                #TODO: close every tab except the first?
                driver.switch_to.window(driver.window_handles[0])
                pass
        
        #get to next page (hacky solution... navigation buttons don't work atm!)
        page += 1
        print(f'Found {len(jobs)} jobs. Turning to page {page}...')
        next_page = url.split('.htm')[0] + '_IP' + str(page) + '.htm'
        driver.get(next_page)
        sleep(5)
        
    #export findings
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    
    filename = f'{job_title} {location}'.replace(' ', '_') + '_' + today + '.json'
    save_location = 'output/' + filename
    
    with open(save_location, 'w') as file:
        json.dump(jobs, file)
        print(f'Saved to {save_location}.')
        return True
