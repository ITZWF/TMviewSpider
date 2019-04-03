# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TmviewItem(scrapy.Item):

    # 这个是搜索的关键字
    kw = scrapy.Field()
    # 列表页的所有信息
    rows = scrapy.Field()
    # 当前多少页的数据
    page = scrapy.Field()
    # 总的条数
    records = scrapy.Field()
    # 总页数
    total = scrapy.Field()


class TmDetailItem(scrapy.Item):

    # 这是解析详情页的字段
    # 做一个标记
    wd = scrapy.Field()
    # 商标下面的所有信息
    trade_mark = scrapy.Field()
    # Nice分类下面的所有内容
    goods_services = scrapy.Field()
    # 拥有者信息
    owner = scrapy.Field()
    # 代理人信息
    representative = scrapy.Field()
    # 通信地址
    correspondence_address = scrapy.Field()
    # 资历
    seniority = scrapy.Field()
    # Exhibition priority
    exhibition_priority = scrapy.Field()
    # Priority
    priority = scrapy.Field()
    # International registration transformation
    irt = scrapy.Field()
    # Publication
    publication = scrapy.Field()
    # Opposition
    opposition = scrapy.Field()
    # Recordals
    recordals = scrapy.Field()
    # Cancellation
    cancellation = scrapy.Field()
    # Appeals
    appeals = scrapy.Field()
    # Renewals
    renewals = scrapy.Field()


class TmImgItem(scrapy.Item):
    # 标记量   相当于ID
    wd = scrapy.Field()

    # 图片保存的路径
    img_path = scrapy.Field()

    # 保存图片的名称
    img_name = scrapy.Field()
