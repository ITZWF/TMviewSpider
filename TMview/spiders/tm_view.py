# -*- coding: utf-8 -*-
import json
import time
import redis
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError, logger
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from TMview.items import TmviewItem

ip_cookie_key = 'ip_cookie_key'


class TmViewSpider(RedisSpider):
    name = 'tm_view'
    allowed_domains = ['tmdn.org']
    redis_key = 'tm_view:start_urls'
    start_urls = ['https://www.baidu.com']

    def __init__(self, *args, **kwargs):
        super(TmViewSpider, self).__init__(*args, **kwargs)
        self.connect = redis.Redis(host='127.0.0.1', port=6379, db=15)
        try:
            self.cookie = json.loads(list(eval(self.connect.lindex(ip_cookie_key, 0).decode('utf-8')))[1])
        except Exception as e:
            print(e)
            from TEST.get_tm_cookies import IPCookie
            IPCookie().get_cookies()
            self.cookie = json.loads(list(eval(self.connect.lindex(ip_cookie_key, 0).decode('utf-8')))[1])

    def errback_twisted(self, failure):
        if failure.check(TimeoutError, TCPTimedOutError, DNSLookupError):
            while True:
                self.connect.blpop(ip_cookie_key, 1)
                if self.connect.llen(ip_cookie_key) == 0:
                    break

            from TEST.get_tm_cookies import IPCookie
            IPCookie().get_cookies()
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            while True:
                self.connect.blpop(ip_cookie_key, 1)
                if self.connect.llen(ip_cookie_key) == 0:
                    break
            from TEST.get_tm_cookies import IPCookie
            IPCookie().get_cookies()

            response = failure.response
            logger.error('HttpError on %s', response.url)

    def parse(self, response):

        # wd_ls = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
        #          's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        # 这个仅仅是为了测试
        wd_ls = ['a']

        for wd in wd_ls:
            url = 'https://www.tmdn.org/tmview/search-tmv?_search=false&nd={}&rows=100&page=1&sidx=oc&' \
                  'sord=asc&q=tmsort%3A{}*&fq=%5B%5D&pageSize=100&facetQueryType=2&selectedRowRefNumber=null&provider' \
                  'List=null&expandedOffices=null'.format(str(int(time.time() * 1000)), wd)

            yield scrapy.Request(url=url, callback=self.parse_first_page, cookies=self.cookie,
                                 errback=self.errback_twisted, meta={'wd': wd})

    def parse_first_page(self, response):

        wd = response.meta['wd']
        json_text = json.loads(response.text, encoding='utf-8')

        item = TmviewItem()
        item['kw'] = wd
        item['page'] = str(json_text['page'])
        item['records'] = str(json_text['records'])
        item['total'] = str(json_text['total'])
        item['rows'] = str(json_text['rows'])

        yield item

        # for i in range(2, int(int(json_text['total']) + 1)):
        for i in range(2, 4):
            new_url = 'https://www.tmdn.org/tmview/search-tmv?_search=false&nd={}&rows=100&page={}&sidx=oc&' \
                      'sord=asc&q=tmsort%3A{}*&fq=%5B%5D&pageSize=100&facetQueryType=2&selectedRowRefNumber=null&provider' \
                      'List=null&expandedOffices=null'.format(str(int(time.time() * 1000)), str(i), wd)
            yield scrapy.Request(url=new_url, callback=self.parse_other_page, errback=self.errback_twisted,
                                 cookies=self.cookie, meta={'wd': wd})

    def parse_other_page(self, response):
        wd = response.meta['wd']
        json_text = json.loads(response.text, encoding='utf-8')

        item = TmviewItem()
        item['kw'] = wd
        item['page'] = str(json_text['page'])
        item['records'] = str(json_text['records'])
        item['total'] = str(json_text['total'])
        item['rows'] = str(json_text['rows'])

        yield item
