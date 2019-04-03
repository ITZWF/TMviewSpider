# -*- coding: utf-8 -*-
import json
import redis
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError, logger
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from TMview.items import TmDetailItem

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
                wd = self.connect.blpop(keyword_key, timeout=60)[1].decode('utf-8').strip()
                print(wd)
                first_url = 'https://www.tmdn.org/tmview/get-detail?st13=%s' % wd

                yield scrapy.Request(url=first_url, callback=self.parse_detail, cookies=self.cookie,
                                     meta={'wd': wd}, errback=self.errback_twisted)

        except TypeError:
            pass

    def parse_detail(self, response):

        wd = response.meta['wd']
        item = TmDetailItem()
        item['wd'] = wd

        tables = response.xpath('//div[@class="detail_right_content"]/table[@cellspacing="0"]')

        all_title = {'trade_mark', 'goods_services', 'owner', 'representative', 'correspondence_address',
                     'seniority', 'exhibition_priority', 'priority', 'irt', 'publication', 'opposition',
                     'recordals', 'cancellation', 'appeals', 'renewals'}
        title_set = set()

        for table in tables:
            title = table.xpath('./thead/tr/th/span').extract_first()

            if 'Trade mark' in title:
                item['trade_mark'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('trade_mark')

            elif 'List of goods and services' in title:
                item['goods_services'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('goods_services')

            elif 'Owner' in title:
                item['owner'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('owner')

            elif 'Representative' in title:
                item['representative'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('representative')

            elif 'Correspondence address' in title:
                item['correspondence_address'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('correspondence_address')

            elif 'Seniority' in title:
                item['seniority'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('seniority')

            elif 'Exhibition priority' in title:
                item['exhibition_priority'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('exhibition_priority')

            elif 'Priority' in title:
                item['priority'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('priority')

            elif 'International registration transformation' in title:
                item['irt'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('irt')

            elif 'Publication' in title:
                item['publication'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('publication')

            elif 'Opposition' in title:
                item['opposition'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('opposition')

            elif 'Recordals' in title:
                item['recordals'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('recordals')

            elif 'Cancellation' in title:
                item['cancellation'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('cancellation')

            elif 'Appeals' in title:
                item['appeals'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('appeals')

            elif 'Renewals' in title:
                item['renewals'] = table.xpath('./tbody/tr/td').extract_first()
                title_set.add('renewals')

        null_title = all_title - title_set

        for nt in null_title:
            item[nt] = empty_word

        yield item
