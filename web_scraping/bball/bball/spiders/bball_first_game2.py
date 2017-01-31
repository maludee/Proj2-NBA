## First games
## Purpose: Scrape First Game Data from a list of players from the web
## Plz don't ban

## TODO
# Figure out how/when to close csv files when finished


# Load Libraries
import scrapy
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
a = open('firstgames1.csv','wb')
writer_a = csv.writer(a)
b = open('firstgames2.csv','wb')
writer_b = csv.writer(b)

# New instance of class scrapy.Spider
class first_game2(scrapy.Spider):
    name = "first_game2"

    # Required so that our requests to website are spaced out
    custom_settings = {
        "DOWNLOAD_DELAY" : 3,
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
        years = ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016']
        base_url = 'http://www.basketball-reference.com/leagues/NBA_{}_games.html'
        urls = [base_url.format(x) for x in years]
        # Test case on 1 URL    
        # urls = ['http://www.basketball-reference.com/leagues/NBA_2014_games.html']
        
        for url in urls:
            # Right now it's getting games.html and I need it to get the year (2014 in the above example)
            season = url.split('_')[-2].split('_')[0]
            print season
            print url
            yield scrapy.Request(url = url, callback = self.season_links, meta = {'season':season})
 

    def season_links(self, response):
        season_urls = response.xpath('//div[contains(@id, "div_schedule")]//tbody//tr')
        # print season_urls
        season = response.request.meta['season']
        for i in season_urls:
            try:
                url_stub = i.xpath('.//td[@data-stat="box_score_text"]//a/@href').extract()[0]
                url = 'http://www.basketball-reference.com'+ url_stub
                print url
                team1 = i.xpath('.//td[@data-stat="visitor_team_name"]//a/@href').extract()[0]
                team1 = team1.split('/')[-2].split('/')[0]
                team1 = team1.lower()
                team2 = i.xpath('.//td[@data-stat="home_team_name"]//a/@href').extract()[0]
                team2 = team2.split('/')[-2].split('/')[0]
                team2 = team2.lower()
                
                yield scrapy.Request(url = url, callback = self.get_firsts, meta = {'season':season, 'team1':team1, 'team2':team2})
                # yield scrapy.Request(url = 'http://www.basketball-reference.com/teams/TOR/2013.html', callback = self.get_totals, meta = {'team':name, 'season':year, 'wins':wins, 'losses':losses})
            except:
                continue     

    # Gets actual first games stats        
    def get_firsts(self, response):
        season = response.request.meta['season']
        team1 = response.request.meta['team1']
        team2 = response.request.meta['team2']
        
        team1_list = []
        team2_list = []

        #first_games = response.xpath('//div[contains(@id, "all_pgl_basic")]//tbody//tr[@data-row="0"]')
        # Feed URL to selenium
        self.driver.get(response.url)
        # Maximize selenium window (means process has started)
        self.driver.maximize_window()
        # Give time for page to load
        time.sleep(3)
        # Find totals table and loop through each row by player to get stats 


        ## TEAM 1: VISITING TEAM ##
        team1path = '//table[@id="box_' + team1 + '_basic"]//tbody//tr'
        print(team1)
        for i in self.driver.find_elements_by_xpath(team1path):
            try:
                fg = i.find_element_by_xpath('.//td[@data-stat="fg"]').text 
                fga = i.find_element_by_xpath('.//td[@data-stat="fga"]').text 
                fg_pct = i.find_element_by_xpath('.//td[@data-stat="fg_pct"]').text
                fg3_pct = i.find_element_by_xpath('.//td[@data-stat="fg3_pct"]').text
                pts = i.find_element_by_xpath('.//td[@data-stat="pts"]').text
                mp = i.find_element_by_xpath('.//td[@data-stat="mp"]').text
                playername = i.find_element_by_xpath('.//th[@data-stat="player"]').text
                firstgames1 = (season, team1, team2, playername, fg, fga, fg_pct, fg3_pct, pts, mp)
                team1_list.append(firstgames1)
            except:
                continue

        ## TEAM 2: HOME TEAM ##
        team2path = '//table[@id="box_' + team2 + '_basic"]//tbody//tr'
        print(team2)
        for i in self.driver.find_elements_by_xpath(team2path):
            try:
                fg = i.find_element_by_xpath('.//td[@data-stat="fg"]').text 
                fga = i.find_element_by_xpath('.//td[@data-stat="fga"]').text 
                fg_pct = i.find_element_by_xpath('.//td[@data-stat="fg_pct"]').text
                fg3_pct = i.find_element_by_xpath('.//td[@data-stat="fg3_pct"]').text
                pts = i.find_element_by_xpath('.//td[@data-stat="pts"]').text
                mp = i.find_element_by_xpath('.//td[@data-stat="mp"]').text
                playername = i.find_element_by_xpath('.//th[@data-stat="player"]').text
                firstgames2 = (season, team2, team1, playername, fg, fga, fg_pct, fg3_pct, pts, mp)
                team2_list.append(firstgames2)
            except:
                continue

        

        # Write results to file
        writer_a.writerows(team1_list)
        writer_b.writerows(team2_list)
    
       


