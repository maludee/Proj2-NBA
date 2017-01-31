## First games
## Purpose: Scrape First Game Data from a list of players from the web

## TODO
# Figure out how/when to close csv files when finished


# Load Libraries
import scrapy
import time
from selenium import webdriver
import os
import csv
import pandas as pd
import pickle
from string import ascii_lowercase


# Set up the environment
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

# Open the pickle file so that I can read out of the dataframe
with open("firsts.pkl", 'rb') as picklefile:
   firsts = pickle.load(picklefile)

# Open CSV files to prepare for output
a = open('firstgames.csv','wb')
writer_a = csv.writer(a)

# New instance of class scrapy.Spider
class first_game_ref(scrapy.Spider):
    name = "first_game_ref"

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
        # base_url = 'http://www.basketball-reference.com/players/{}/'
        # urls = [base_url.format(x) for x in ascii_lowercase]
        urls = ['http://www.basketball-reference.com/players/q/']
        for url in urls:
            # so far url is the bballref.player/letter
            print url
            yield scrapy.Request(url = url, callback = self.player_links)
  
    # Gets URLs for all of the players that we are searching for
    def player_links(self, response):
        player_urls = response.xpath('//div[contains(@id, "all_players")]//tbody//tr')
        #yr = response.request.meta['season']
        for i in player_urls:
            try:
                name = i.xpath('.//a/text()').extract()[0]
                url_stub = i.xpath('.//a/@href').extract()[0]
                url = 'http://www.basketball-reference.com'+ url_stub
                yield scrapy.Request(url = url, callback = self.season_links, meta = {'name':name})
            except:
                continue     

    def season_links(self, response):
        season_urls = response.xpath('//div[contains(@id, "all_per_game")]//tbody//tr')
        # print season_urls
        name = response.request.meta['name']
        for i in season_urls:
            try:
                season = i.xpath('.//a/text()').extract()[0]
                url_stub = i.xpath('.//a/@href').extract()[0]
                url = 'http://www.basketball-reference.com'+ url_stub
                yield scrapy.Request(url = url, callback = self.get_firsts, meta = {'name':name, 'season':season})
                # yield scrapy.Request(url = 'http://www.basketball-reference.com/teams/TOR/2013.html', callback = self.get_totals, meta = {'team':name, 'season':year, 'wins':wins, 'losses':losses})
            except:
                continue     

    # Gets actual first games stats        
    def get_firsts(self, response):

        #first_games = response.xpath('//div[contains(@id, "all_pgl_basic")]//tbody//tr[@data-row="0"]')
        # Feed URL to selenium
        self.driver.get(response.url)
        # Maximize selenium window (means process has started)
        self.driver.maximize_window()
        # Give time for page to load
        time.sleep(3)
        # Find totals table and loop through each row by player to get stats 
        name = response.request.meta['name']
        print name
        season = response.request.meta['season']
        print season
        first_game_list = []


        for i in self.driver.find_elements_by_xpath('//table[@id="all_pgl_basic"]//tbody//tr[@data-row="0"]'):
            # try:
            team_id = i.find_element_by_xpath('.//td[@data-stat="team_id"]').text
            # opp_id = i.xpath('.//td[@data-stat="opp_id"]').text
            # age = i.xpath('.//td[@data-stat="age"]').text
            # games_started = i.xpath('.//td[@data-stat="gs"]').text
            # field_goals = i.xpath('.//td[@data-stat="fg"]').text
            # fg_att = i.xpath('.//td[@data-stat="fga"]').text
            # fg_pct = i.xpath('.//td[@data-stat="fg_pct"]').text
            # fg3_pct = i.xpath('.//td[@data-stat="fg3_pct"]').text
            # points = i.xpath('.//td[@data-stat="pts"]').text
         
        # for i in first_games:
        #     # try:
        #     team_id = i.xpath('.//td[@data-stat="team_id"]').text
        #     opp_id = i.xpath('.//td[@data-stat="opp_id"]').text
        #     age = i.xpath('.//td[@data-stat="age"]').text
        #     games_started = i.xpath('.//td[@data-stat="gs"]').text
        #     field_goals = i.xpath('.//td[@data-stat="fg"]').text
        #     fg_att = i.xpath('.//td[@data-stat="fga"]').text
        #     fg_pct = i.xpath('.//td[@data-stat="fg_pct"]').text
        #     fg3_pct = i.xpath('.//td[@data-stat="fg3_pct"]').text
        #     points = i.xpath('.//td[@data-stat="pts"]').text
                
                
                # create a tuple for each player, append to list
            firstgames = (name, season, team_id)
            # firstgames = (name, season, team_id, opp_id, age, 
            #                     games_started, field_goals, fg_att, fg_pct, fg3_pct, 
            #                     points)
            first_game_list.append(firstgames)
            # except:
                # continue
        

        # Write results to file
        writer_a.writerows(first_game_list)
    
       


