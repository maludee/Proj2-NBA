## Bball Ref
## Purpose: Scrape Basketball Player Data from Web

## TODO
# Figure out how/when to close csv files when finished
# Scrape wins and losses as separate function 

# Load Libraries
import scrapy
import time
from selenium import webdriver
import os
# import json
import csv

# Set up the environment
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

# Open CSV files to prepare for output
a = open('players.csv','wb')
writer_a = csv.writer(a)
b = open('salaries.csv','wb')
writer_b = csv.writer(b)
c = open('advanced.csv','wb')
writer_c = csv.writer(c)

# New instance of class scrapy.Spider
class bball(scrapy.Spider):
    name = "bballref"

    # Required so that our requests to website are spaced out
    custom_settings = {
        "DOWNLOAD_DELAY" : 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN" : 2
        }

    # Below two are scrapy convention to initialize and close 
    # Also driver so that you can refer to that instead of typing out webdriver.Chrome
    def __init__(self):
        self.driver = webdriver.Chrome(chromedriver)
        scrapy.Spider.__init__(self)
    
    # Close after last reference to spider
    def __del__(self):
        scrapy.Spider.__del__(self)
    
    # starting point URL for spider. start_requests is the method called to open the spider for scraping
    # callback passes instance to the next thing.
    def start_requests(self):
        url = 'http://www.basketball-reference.com/leagues/NBA_2016.html'
        yield scrapy.Request(url = url, callback = self.team_links)
        
    # Gets URLs for all of the team links from the initial league table
    def team_links(self, response):
        team_urls = response.xpath('//div[contains(@id, "all_confs_standings")]//a')
        for i in team_urls:
            name = i.xpath('./text()').extract()[0]
            print name
            url_stub = i.xpath('./@href').extract()[0]
            url = 'http://www.basketball-reference.com'+ url_stub
            yield scrapy.Request(url = url, callback = self.get_totals, meta = {'team':name})
            # yield scrapy.Request(url = 'http://www.basketball-reference.com/teams/TOR/2016.html', callback = self.get_totals, meta = {'team':name})
    
    # Gets actual player stats         
    def get_totals(self, response):
        team = response.request.meta['team']
        player_list = []
        salary_list = []
        advanced_list = []
        # Feed URL to selenium
        self.driver.get(response.url)
        # Maximize selenium window (means process has started)
        self.driver.maximize_window()
        # Give time for page to load
        time.sleep(3)
        # Find totals table and loop through each row by player to get stats 
        for i in self.driver.find_elements_by_xpath('//table[@id="totals"]//tbody//tr'):
            try:
                player_name = i.find_element_by_xpath('.//td[@data-stat="player"]').text
                minutes_played =  i.find_element_by_xpath('.//td[@data-stat="mp"]').text
                games_played = i.find_element_by_xpath('.//td[@data-stat="g"]').text
                games_started = i.find_element_by_xpath('.//td[@data-stat="gs"]').text
                points = i.find_element_by_xpath('.//td[@data-stat="pts"]').text
                # create a tuple for each player, append to list
                player = (player_name, team, minutes_played, games_played, games_started, points)
                player_list.append(player)
            except:
                continue
        
        # Find salary table and loop through each row by player to get salary stats 
        for i in self.driver.find_elements_by_xpath('//table[@id="salaries"]//tbody//tr'):
            try:
                player_name = i.find_element_by_xpath('.//td[@data-stat="player"]').text
                salary =  i.find_element_by_xpath('.//td[@data-stat="salary"]').text
                # create a tuple for each player's salary, append to list
                salaries = (player_name, team, salary)
                salary_list.append(salaries)
            except:
                continue

        # Find advanced table and loop through each row by player to get PER stats 
        for i in self.driver.find_elements_by_xpath('//table[@id="advanced"]//tbody//tr'):
            try:
                player_name = i.find_element_by_xpath('.//td[@data-stat="player"]').text
                age =  i.find_element_by_xpath('.//td[@data-stat="age"]').text
                per =  i.find_element_by_xpath('.//td[@data-stat="per"]').text
                # create a tuple for each player's advanced stats, append to list
                stats = (player_name, team, age, per)
                advanced_list.append(stats)
            except:
                continue

        # Write results to file
        writer_a.writerows(player_list)
        writer_b.writerows(salary_list)
        writer_c.writerows(advanced_list)

        