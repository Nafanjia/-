# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def org_url(url):
    result = f'https://hh.ru{url[0]}'
    return result

def clear_salary(salary):
    result = ''
    result = result.join(salary).replace(u'\xa0', u' ')
    return result

class AvitoparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HHItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    salary = scrapy.Field(output_processor=clear_salary)
    skills = scrapy.Field()
    organization = scrapy.Field(output_processor=TakeFirst())
    org_url = scrapy.Field(output_processor=org_url)
    logo_url = scrapy.Field(output_processor=TakeFirst())