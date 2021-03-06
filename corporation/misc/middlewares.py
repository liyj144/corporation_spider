# coding=utf-8
from random import choice
from helper import gen_bids
from scrapy.exceptions import IgnoreRequest
from ..misc.store import confRedis
import logging


class IgnoreHttpRequestMiddleware(object):
    # 公司重复性过滤
    def process_response(self, request, response, spider):
        corp_id = request.meta.get('corp_id')
        # 获取上海的企业
        #province = request.meta.get('province')
        #area = request.meta.get('area')
        #if province and province in [u'河北', u'湖南', u'浙江', u'安徽', u'江苏']:
        #    logging.debug("%s already scrapy, skipped" % province)
        #    raise IgnoreRequest("%s no in such province" % province)
        #if province and province not in [u'上海', u'北京']:
        #    logging.debug("%s no in such province, skipped" % province)
        #    raise IgnoreRequest("%s no in such province" % province)
        #if area and area not in [u'黄浦区']:
        #    logging.debug("%s no in such area, skipped" % area)
        #    raise IgnoreRequest("%s no in such area" % area)
        if confRedis.sismember('corp_id', corp_id):
            logging.debug("corp_id " + corp_id + ",already get, skipped ")
            raise IgnoreRequest("corp_id " + corp_id + ",already get, skipped ")
        else:
            return response


class CustomCookieMiddleware(object):
    def __init__(self):
        self.bids = gen_bids()

    def process_request(self, request, spider):
        request.headers["Cookie"] = 'bid="%s"' % choice(self.bids)


class CustomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ug = "Baiduspider"
        request.headers["User-Agent"] = ug


class CustomHeadersMiddleware(object):
    def process_request(self, request, spider):
        request.headers["Accept-Language"] = "zh-CN,zh"