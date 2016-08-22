# coding=utf-8
from ..misc.store import corpDB, confRedis
import logging


class CorpPipeline(object):
    def process_item(self, item, spider):
        if spider.name != 'corp': return item
        if item.get("corp_id", None) is None: return item
        spec = {"corp_id": item["corp_id"]}
        corpDB.corp.update(spec, {'$set': dict(item)}, upsert=True)
        # store corp_id in redis
        confRedis.sadd('corp_id', item["corp_id"])
        return None
