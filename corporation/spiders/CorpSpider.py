# encoding: utf-8
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request, FormRequest
from scrapy.shell import inspect_response
import time
import traceback
import logging
import requests

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
        #Rule(LinkExtractor(allow=r"/company/[\d\w]+/index\.html$"),
        #     callback="parse_start", follow=True),

    )

    def __init__(self):
        self.url_prefix = 'http://www.zhiqiye.com'
        self.user_name = 'test3'
        self.password = 'qwer1234'
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

    # 首先定位到登陆页面
    def start_requests(self):
        logging.info("start to login ...")
        return [Request("http://www.zhiqiye.com/index.html",
                    callback=self.post_login)]

    def post_login(self, response, re_login=False):
        logging.info("post login ...")
        old_url = ""
        old_meta = {}
        if re_login:
            old_url = response.url
            old_meta = response.meta
            new_url = "http://www.zhiqiye.com/index.html"
            new_response = requests.get(new_url)
            response = response.replace(url=new_url, body=new_response.content)
        current = int(time.time() * 1000)
        return [FormRequest.from_response(response,
                                        url="http://www.zhiqiye.com/account/login/",
                                        method="POST",
                                        formdata={
                                            'time': "%s" % current,
                                            'username': self.user_name,
                                            'pass': self.password,
                                            'f': 'true'
                                        },
                                        meta={
                                            "old_url": old_url,
                                            "old_meta": old_meta,
                                            "is_retry": True
                                        },
                                        dont_filter=True,
                                        callback=self.after_login)]

    """
    登陆后重新进行规则匹配
    """
    def after_login(self, response):
        old_url = response.meta.get('old_url')
        if old_url:
            logging.info("after login again, and call old url again ...%s" % old_url)
            new_response = requests.get(old_url)
            response = response.replace(url=old_url, body=new_response.content)
            meta = response.meta.get('old_meta')
            yield Request(old_url,
                          meta=meta,
                          callback=self.parse_corp)
        else:
            for url in self.start_urls :
                yield Request(url=url, callback=self.parse_province)

    """
    分析省份详情
    """
    def parse_province(self, response):
        self.log("--------start parse province-----")
        corp = CorpParseModel()
        ar_province = corp.get_city_list(response)
        for province in ar_province:
            self.log("--------start parse province----- url is %s" % province[0])
            yield Request("%s%s" % (self.url_prefix, province[0]),
                          meta={"province": province[1]},
                          callback=self.parse_city)

    """
    分析城市详情
    """
    def parse_city(self, response):
        self.log("parse city ...")
        province = response.meta.get('province', '')
        corp = CorpParseModel()
        ar_city = corp.get_city_list(response, '20')
        if len(ar_city) > 0:
            for city in ar_city:
                yield Request("%s%s" % (self.url_prefix, city[0]),
                              meta={"province": province,
                                    "city": city[1]}, callback=self.parse_area)
        else:
            ar_area = corp.get_city_list(response, '30')
            for area in ar_area:
                yield Request("%s%s" % (self.url_prefix, area[0]),
                              meta={"province": province,
                                    "city": "",
                                    "area": area[1]}, callback=self.parse_page)

    """
    分析区域详情
    """
    def parse_area(self, response):
        self.log("parse area ...")
        province = response.meta.get('province', '')
        city = response.meta.get('city', '')
        corp = CorpParseModel()
        ar_area = corp.get_city_list(response, '30')
        for area in ar_area:
            yield Request("%s%s" % (self.url_prefix, area[0]),
                          meta={"province": province,
                                "city": city,
                                "area": area[1]}, callback=self.parse_page)

    """
    分析页面上企业名单, 如果有下一页， 则在下一页继续执行本方法
    """
    def parse_page(self, response):
        self.log("parse page ...")
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
        # 将下一页加入到爬取队列
        next_page = corp.get_next_page_url(response)
        if next_page:
            yield Request("%s%s" % (self.url_prefix, next_page),
                          meta={"province": province,
                                "city": city,
                                "area": area}, callback=self.parse_page)


    """
    分析企业详情
    """
    def parse_corp(self, response, meta=False):
        #inspect_response(response, self)
        if meta:
            response_meta = meta
        else:
            response_meta = response.meta
        item = CorpItem()
        item["province"] = response_meta.get('province', '')
        item["city"] = response_meta.get('city', '')
        item["area"] = response_meta.get('area', '')
        item["corp_id"] = response_meta.get('corp_id', '')
        is_retry = response_meta.get('is_retry', False)
        try:
            corp = CorpParseModel()
            corp.get_corp_tips(response, item)
            corp.get_contact(response, item)
            corp.get_commercial(response, item)
            corp.get_corp_info(response, item)
            corp.get_relate_corp(response, item)
            return item
        except IndexError:
            self.log("------------- start to login again -------------")
            if is_retry:
                self.log("------ retry login and fails ------")
            else:
                return self.post_login(response, True)
        except Exception:
            self.log(traceback.format_exc(), logging.ERROR)
