# encoding: utf-8
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest, HtmlResponse, cookies
from scrapy.shell import inspect_response
import time
import traceback
import logging
import requests

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

    """
    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
        "Referer": "https://www.zhiqiye.com/",
    }
    """

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

    # 首先定位到登陆页面
    def start_requests(self):
        logging.info("start to login ...")
        return [Request("http://www.zhiqiye.com/index.html",
                        callback=self.post_login)]

    def re_login(self):
        logging.info("re login ...")
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
            #inspect_response(response, self)
            response = response.replace(url=new_url, body=new_response.content)
        current = int(time.time() * 1000)
        return [FormRequest.from_response(response,
                                        url="http://www.zhiqiye.com/account/login/",
                                        method="POST",
                                        #headers=self.post_headers,
                                        formdata={
                                            'time': "%s" % current,
                                            'username': 'test2',
                                            'pass': 'qwer1234',
                                            'f': 'false'
                                        },
                                        meta={
                                            "old_url": old_url,
                                            "old_meta": old_meta,
                                            "is_retry": True
                                        },
                                        dont_filter=True,
                                        callback=self.after_login)]

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
                yield Request(url=url,
                              callback=self.parse_page)

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
    def parse_corp(self, response, meta=False):
        #inspect_response(response, self)
        print "parse corp"
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
        if is_retry:
            inspect_response(response, self)
        print "retry here is ", is_retry
        try:
            corp = CorpParseModel()
            corp.get_corp_tips(response, item)
            corp.get_contact(response, item)
            corp.get_commercial(response, item)
            corp.get_corp_info(response, item)
            corp.get_relate_corp(response, item)
            corp.get_artificial_info(response)
            return item
        except IndexError:
            self.log("------ start to login again ------")
            if is_retry:
                self.log("------ retry login and fails ------")
            else:
                return self.post_login(response, True)
        except Exception:
            self.log(traceback.format_exc(), logging.ERROR)
