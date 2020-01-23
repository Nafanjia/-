# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from avitoparse.items import HHItem


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&clusters=true&enable_snippets=true&specialization=7.222&from=cluster_specialization&showClusters=true']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//div[@data-qa="pager-block"]/a[contains(@class, "HH-Pager-Controls-Next")]/@href').extract_first()
        yield response.follow(next_page, callback=self.parse)
        urls = response.xpath('//div[@data-qa="vacancy-serp__results"]//div[contains(@class, "vacancy-serp-item")]//a[@data-qa="vacancy-serp__vacancy-title"]/@href').extract()
        for url in urls:
            yield response.follow(url, callback=self.vac_parse)
        pass


    def vac_parse(self, response: HtmlResponse):
        item = ItemLoader(HHItem(), response)
        if response.xpath('//h1[@class="header"]/span/text()').extract_first() == None:
            item.add_xpath('title', '//h1[@class="header"]/text()')
        else:
            item.add_xpath('title', '//h1[@class="header"]/span/text()')
        item.add_value('url', response.url)
        item.add_xpath('salary', '//div[contains(@class, "vacancy-title")]/p[@class="vacancy-salary"]/text()')
        item.add_xpath('skills', '//div[@class="vacancy-section"]//span[@data-qa="bloko-tag__text"]/text()')
        if response.xpath('//a[@class="vacancy-company-name"]/span[@itemprop="name"]/text()').extract_first() == None:
            item.add_xpath('organization', '//a[@class="vacancy-company-name"]/span[@itemprop="name"]/span/text()')
        else:
            na = response.xpath('//a[@class="vacancy-company-name"]/span[@itemprop="name"]/text()').extract_first()
            me = response.xpath('//a[@class="vacancy-company-name"]/span[@itemprop="name"]/span/text()').extract_first()
            name = f'{na} {me}'
            item.add_value('organization', name)
        item.add_xpath('org_url', '//a[@class="vacancy-company-name"]/@href')
        item.add_xpath('logo_url', '//a[contains(@class, "vacancy-company-logo")]/img[contains(@class, "vacancy-company-logo__image")]/@src')
        yield item.load_item()
