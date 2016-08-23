# coding=utf-8
from scrapy.spiders import CrawlSpider
from scrapy.shell import inspect_response
import re



class TestSpider(CrawlSpider):
    name = "test"
    start_urls = [
        #"http://www.zhiqiye.com/company/7A3577A29D3C4598A9089329BD32D8B4/index.html",
        #"http://www.zhiqiye.com/company/6A0C9366B8D44604B5E1DCA6B502D4C4/index.html",
        #"http://www.zhiqiye.com/company/17651AD021624542AC6D062513B2960F/index.html",
        "http://www.zhiqiye.com/r-new/0049000000000000_1.html"
    ]

    def parse(self, response):
        #next_page = response.css(".pag-numble").xpath(u"//a[contains(@title,'下一页')]").re(re.compile(ur'href="(.*?)".*>(?:.*)</a>'))
        #if next_page:
        #    print next_page[0]
        print response.css(".pag-numble").xpath(u"//a[@title='下一页']/@href").extract()[0]
        inspect_response(response, self)


