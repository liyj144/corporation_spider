# coding=utf-8
from scrapy.spiders import CrawlSpider
from scrapy.shell import inspect_response
import re

class TestSpider(CrawlSpider):
    name = "test"
    start_urls = [
        #"http://www.zhiqiye.com/company/7A3577A29D3C4598A9089329BD32D8B4/index.html",
        "http://www.zhiqiye.com/r-new/0049000000000000_1.html"
    ]

    def parse(self, response):
        next_page = response.css(".pag-numble").xpath(u"//a[contains(@title,'下一页')]").re(re.compile(ur'href="(.*?)".*>(?:.*)</a>'))
        if next_page:
            print next_page[0]
        inspect_response(response, self)


