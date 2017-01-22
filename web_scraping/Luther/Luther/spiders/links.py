import scrapy

class TeamLinksSpider(scrapy.Spider):
    name = 'teamlinks'
    start_urls = [
        'http://www.basketball-reference.com/leagues/NBA_2016.html'
    ]
    
    def parse(self, response):
        for i in response.xpath('//div[contains(@id, "all_confs_standings")]//a/@href').extract():
            print 'http://www.basketball-reference.com' + i