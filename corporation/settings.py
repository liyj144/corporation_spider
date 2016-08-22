# -*- coding: utf-8 -*-

BOT_NAME = 'corporation'

SPIDER_MODULES = ['corporation.spiders']
NEWSPIDER_MODULE = 'corporation.spiders'
ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'corporation.misc.middlewares.IgnoreHttpRequestMiddleware': 1,
    'corporation.misc.middlewares.CustomUserAgentMiddleware': 401,
    'corporation.misc.middlewares.CustomCookieMiddleware': 701,
    'corporation.misc.middlewares.CustomHeadersMiddleware': 551,
}
ITEM_PIPELINES = {
    'corporation.pipelines.CorpPipeline.CorpPipeline': 1,
}
# 广度优先, 默认是深度遍历
# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
# SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"
# 调试时，将深度调整为一级
# DEPTH_LIMIT = 1

# 重复性过滤采用布隆过滤的方式
DUPEFILTER_CLASS = "corporation.misc.bloomfilter.BLOOMDupeFilter"

WEBSERVICE_ENABLED = False
TELNETCONSOLE_ENABLED = False
LOG_LEVEL = "DEBUG"
