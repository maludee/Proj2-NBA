## Bball Ref
## Purpose: Scrape Basketball Player Data from Web

## TODO
# Figure out how/when to close csv files when finished
# Scrape wins and losses as separate function 

## Notes
# I was able to get the teamstats data by pulling everything out of the loop
# But after I ran the whole thing only 2016 results are showing 
# Were other years showing before?

# If you want to figure out why something isn't working, run without "try" to see traceback
# Also try running without for loop

# Load Libraries
import scrapy
import time
from selenium import webdriver
import os
import csv

# Set up the environment
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

# Open CSV files to prepare for output
a = open('playertotals.csv','wb')
writer_a = csv.writer(a)
b = open('salaries.csv','wb')
writer_b = csv.writer(b)
c = open('advanced.csv','wb')
writer_c = csv.writer(c)
d = open('teamstats.csv','wb')
writer_d = csv.writer(d)
e = open('teammisc.csv','wb')
writer_e = csv.writer(e)

# New instance of class scrapy.Spider
class nbaref(scrapy.Spider):
    name = "nbaref"

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
        years = ['2016','2015','2014','2013','2012','2011']
        base_url = 'http://www.basketball-reference.com/leagues/NBA_{}.html'
        urls = [base_url.format(x) for x in years]
        for url in urls:
            season = url.split('_')[-1].split('.')[0]
            # hang onto season tag so that you can use it later
            yield scrapy.Request(url = url, callback = self.team_links, meta = {'season':season})
  
    # Gets URLs for all of the team links from the initial league table!
    def team_links(self, response):
        year = response.request.meta['season']
        team_urls = response.xpath('//div[contains(@id, "all_divs_standings")]//tbody//tr')
        #yr = response.request.meta['season']
        for i in team_urls:
            try:
                name = i.xpath('.//a/text()').extract()[0]
                wins = i.xpath('.//td[@data-stat="wins"]/text()').extract()[0]
                losses = i.xpath('.//td[@data-stat="losses"]/text()').extract()[0]
                url_stub = i.xpath('.//a/@href').extract()[0]
                url = 'http://www.basketball-reference.com'+ url_stub
                print url
                yield scrapy.Request(url = url, callback = self.get_totals, meta = {'team':name,'season':year, 'wins':wins, 'losses':losses})
                # yield scrapy.Request(url = 'http://www.basketball-reference.com/teams/TOR/2013.html', callback = self.get_totals, meta = {'team':name, 'season':year, 'wins':wins, 'losses':losses})
            except:
                continue     

   # # Gets URLs for all of the team links from the initial league table FOR 2016
   #  def team_links(self, response):
   #      year = response.request.meta['season']
   #      team_urls = response.xpath('//div[contains(@id, "all_confs_standings")]//tbody//tr')
   #      #yr = response.request.meta['season']
   #      for i in team_urls:
   #          name = i.xpath('.//a/text()').extract()[0]
   #          wins = i.xpath('.//td[@data-stat="wins"]/text()').extract()[0]
   #          losses = i.xpath('.//td[@data-stat="losses"]/text()').extract()[0]
   #          url_stub = i.xpath('.//a/@href').extract()[0]
   #          url = 'http://www.basketball-reference.com'+ url_stub
   #          print url
   #          # yield scrapy.Request(url = url, callback = self.get_totals, meta = {'team':name,'season':year, 'wins':wins, 'losses':losses})
   #          yield scrapy.Request(url = 'http://www.basketball-reference.com/teams/TOR/2013.html', callback = self.get_totals, meta = {'team':name, 'season':year, 'wins':wins, 'losses':losses})
 

    # Gets actual player stats         
    def get_totals(self, response):
        team = response.request.meta['team']
        season = response.request.meta['season']
        wins = response.request.meta['wins']
        losses = response.request.meta['losses']
        player_list = []
        salary_list = []
        advanced_list = []
        team_list = []
        misc_list = []
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
                field_goals = i.find_element_by_xpath('.//td[@data-stat="fg"]').text
                # create a tuple for each player, append to list
                playertotals = (player_name, team, season, minutes_played, games_played, games_started, points, field_goals, wins, losses)
                player_list.append(playertotals)
            except:
                continue
        
        # Find salary table and loop through each row by player to get salary stats 
        for i in self.driver.find_elements_by_xpath('//table[@id="salaries"]//tbody//tr'):
            try:
                player_name = i.find_element_by_xpath('.//td[@data-stat="player"]').text
                salary =  i.find_element_by_xpath('.//td[@data-stat="salary"]').text
                # create a tuple for each player's salary, append to list
                salaries = (player_name, team, season, salary)
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
                advanced = (player_name, team, season, age, per)
                advanced_list.append(advanced)
            except:
                continue

        # Find team table and loop through each row for team and opponent stats
        try:
            games = self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="g"]').text
            tm3pct =  self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="fg3_pct"]').text
            tmfgallow = self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="fga"]').text
            opp3pct = self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="opp_fg3_pct"]').text
            oppfgpct = self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="opp_fg_pct"]').text
            oppfgall = self.driver.find_element_by_xpath('//table[@id="team_and_opponent"]//tbody//tr//td[@data-stat="opp_fga"]').text
            teamstats = (team, games, season, tm3pct, tmfgallow, opp3pct, oppfgpct, oppfgall)
            team_list.append(teamstats)
        except:
            pass
        # for i in self.driver.find_elements_by_xpath('//table[@id="team_and_opponent"]//tbody//tr'):
        #     try:
        #     games = i.find_element_by_xpath('.//td[@data-stat="g"]').text
        #     tm3pct =  i.find_element_by_xpath('.//td[@data-stat="fg3_pct"]').text
        #     tmfgallow = i.find_element_by_xpath('.//td[@data-stat="fga"]').text
        #     opp3pct = i.find_element_by_xpath('.//td[@data-stat="opp_fg3_pct"]').text
        #     oppfgpct = i.find_element_by_xpath('.//td[@data-stat="opp_fg_pct"]').text
        #     oppfgall = i.find_element_by_xpath('.//td[@data-stat="opp_fga"]').text
        #     # # create a tuple for each player's advanced stats, append to list
        #     teamstats = (team, games, season, tm3pct, tmfgallow, opp3pct, oppfgpct, oppfgall)
        #     team_list.append(teamstats)
        #     except:
        #         continue

        # Find misc table and loop through each row for team and opponent stats
        for i in self.driver.find_elements_by_xpath('//table[@id="team_misc"]//tbody//tr[@data-row="1"]'):
            try:
                pace = i.find_element_by_xpath('.//td[@data-stat="pace"]').text
                # create a tuple for each team's misc stats, append to list
                teammisc = (team, season, pace)
                misc_list.append(teammisc)
            except:
                continue

        # Write results to file
        writer_a.writerows(player_list)
        writer_b.writerows(salary_list)
        writer_c.writerows(advanced_list)
        writer_d.writerows(team_list)
        writer_e.writerows(misc_list)


