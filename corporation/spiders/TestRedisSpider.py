# encoding: utf-8
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request

from ..item.CorpItem import CorpItem
from ..model.CorpParseModel import CorpParseModel


class CorpSpider(CrawlSpider):
    name = "test2"
    allowed_domains = ["www.zhiqiye.com"]
    start_urls = [
        "http://www.zhiqiye.com/r-new/0049003100140000_1.html",
    ]

    rules = (
        Rule(LinkExtractor(allow=r"/r-new/0049003100140000_1"),
             callback="parse_page", follow=True),
    )

    def __init__(self):
        self.url_prefix = 'http://www.zhiqiye.com'
        super(CorpSpider, self).__init__()

    """
    分析页面数据, 一共有以下几种情况：
        1. 省份 -- 选择省份（除全国外）
        2. 城市 -- 选择城市
        3. 区域 -- 选择区域
        4. 企业列表 -- 选择企业
        5. 分页 -- 获取下一页数据
        6. 内容 -- 进入内容详情
    """

    def parse_page(self, response):
        province = response.meta.get('province', '')
        city = response.meta.get('city', '')
        area = response.meta.get('area', '')
        corp = CorpParseModel()
        ar_corp = corp.get_corp_list(response)
        for corp_url in ar_corp:
            corp_id = corp.get_corp_id_by_url(corp_url)
            yield Request("%s%s" % (self.url_prefix, corp_url),
                          meta={"province": province,
                                "city": city,
                                "area": area,
                                "corp_id": corp_id}, callback=self.parse_corp)

    """
    分析企业详情
    """
    def parse_corp(self, response):
        print "parse corp"
        item = CorpItem()
        item["province"] = response.meta.get('province', '')
        item["city"] = response.meta.get('city', '')
        item["area"] = response.meta.get('area', '')
        item["corp_id"] = response.meta.get('corp_id', '')
        corp = CorpParseModel()
        corp.get_corp_tips(response, item)
        corp.get_contact(response, item)
        corp.get_corp_info(response, item)
        corp.get_relate_corp(response, item)
        return item
