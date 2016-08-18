# encoding: utf-8
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.shell import inspect_response
from scrapy import Request, crawler, settings

from ..item.CorpItem import CorpItem
from ..model.CorpParseModel import CorpParseModel


class CorpSpider(CrawlSpider):
    name = "corp"
    allowed_domains = ["www.zhiqiye.com"]
    start_urls = ["http://www.zhiqiye.com/r-new/0049000000000000_1.html"]

    rules = (
        Rule(LinkExtractor(allow=r"/r-new/0049000000000000_1"),
             callback="parse_province", follow=True),
        #Rule(LinkExtractor(allow=r"/r-new/0049(\d{4}(?<!0000))\d{8}_1"),
             #callback="parse_area", follow=True),
        Rule(LinkExtractor(allow=r"/compony/[\d\w]+/index\.html$"),
             callback="parse_corp", follow=True),

    )

    """
    分析页面数据, 一共有以下几种情况：
        1. 省份 -- 选择省份（除全国外）
        2. 城市 -- 选择城市
        3. 区域 -- 选择区域
        4. 企业列表 -- 选择企业
        5. 分页 -- 获取下一页数据
        6. 内容 -- 进入内容详情
    """

    """
    分析省份详情
    """
    def parse_province(self, response):
        self.log("--------start parse province-----")
        corp = CorpParseModel()
        ar_province = corp.get_city_list(response)
        for province in ar_province:
            self.log("--------start parse province----- url is %s" % province[0])
            yield Request("%s%s" % ('http://www.zhiqiye.com', province[0]),
                          meta={"province": province[1]},
                          callback=self.parse_city)

    """
    分析城市详情
    """
    def parse_city(self, response):
        province = response.meta.get('province', '')
        corp = CorpParseModel()
        ar_city = corp.get_city_list(response, '20')
        if len(ar_city):
            for city in ar_city:
                yield Request("%s%s" % ('http://www.zhiqiye.com', city[0]),
                              meta={"province": province,
                                    "city": city[1]}, callback=self.parse_area)
        else:
            yield Request(response.url,
                          meta={"province": province,
                                "city": ''}, callback=self.parse_area)

    """
    分析区域详情
    """
    def parse_area(self, response):
        province = response.meta.get('province', '')
        city = response.meta.get('city', '')
        corp = CorpParseModel()
        ar_area = corp.get_city_list(response, '30')
        for area in ar_area:
            yield Request("%s%s" % ('http://www.zhiqiye.com', area[0]),
                          meta={"province": province,
                                "city": city,
                                "area": area[1]}, callback=self.parse_page)

    """
    分析页面上企业名单, 如果有下一页， 则在下一页继续执行本方法
    """
    def parse_page(self, response):
        province = response.meta.get('province', '')
        city = response.meta.get('city', '')
        area = response.meta.get('area', '')
        corp = CorpParseModel()
        ar_corp = corp.get_corp_list(response)
        for corp_url in ar_corp:
            yield Request("%s%s" % ('http://www.zhiqiye.com', corp_url),
                          meta={"province": province,
                                "city": city,
                                "area": area}, callback=self.parse_corp)
        # todo 模拟下一页
        next_page = corp.get_next_page_url(response)
        if next_page:
            yield Request("%s%s" % ('http://www.zhiqiye.com', next_page),
                          meta={"province": province,
                                "city": city,
                                "area": area}, callback=self.parse_page)

    """
    分析企业详情
    """
    def parse_corp(self, response):
        item = CorpItem()
        item["province"] = response.meta.get('province', '')
        item["city"] = response.meta.get('city', '')
        item["area"] = response.meta.get('area', '')
        corp = CorpParseModel()
        item["corp_id"] = corp.get_corp_id(response)
        corp.get_corp_tips(response, item)
        corp.get_contact(response, item)
        corp.get_corp_info(response, item)
        corp.get_relate_corp(response, item)
        return item