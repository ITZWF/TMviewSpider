# -*- coding: utf-8 -*-
import json
import os

import redis
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError, logger
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from TMview.items import TmImgItem

ip_cookie_key = 'ip_cookie_key'
keyword_key = 'keyword_key'
empty_word = 'null'


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
        try:

            while True:
                info = self.connect.blpop(keyword_key, timeout=60)[1].decode('utf-8').strip()
                [wd, img_url] = info.split('\t')
                print(wd)

                yield scrapy.Request(url=img_url, callback=self.parse_img, cookies=self.cookie, meta={'wd': wd},
                                     errback=self.errback_twisted)

        except TypeError:
            pass

    def parse_img(self, response):
        item = TmImgItem()

        wd = response.meta['wd']
        print(wd)
        if not os.path.exists('./TM_IMG/'):
            os.makedirs('./TM_IMG/')

        with open('./TM_IMG/' + wd + '.png', mode='wb+') as fw:
            fw.write(response.body)

        img_path = './TM_IMG/' + wd + '.png'
        img_name = wd + '.png'

        item['wd'] = wd
        item['img_path'] = img_path
        item['img_name'] = img_name
        yield item
