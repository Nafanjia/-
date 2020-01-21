# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry/prodam?cd=1']

    def parse(self, response: HtmlResponse):
        tmp = int(response.css('div.pagination-root-2oCjZ span.pagination-item-1WyVp.pagination-item_active-25YwT::text').get())
        if tmp >= 10:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[3]
        elif tmp == 1:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[1]
        elif tmp == 2:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[2]
        elif tmp == 3:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[3]
        elif tmp == 4:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[4]
        elif tmp == 5:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[5]
        elif tmp == 6:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[6]
        elif tmp == 7:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[7]
        elif tmp == 8:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[8]
        elif tmp == 9:
            next_page = list(response.css('div.pagination-hidden-3jtv4 div.pagination-pages.clearfix a::attr(href)').getall())[9]
        yield response.follow(next_page, callback=self.parse)
        # page = 2
        # while page <= 100:
        #     text = f'div.pagination-hidden-3jtv4 a[href="/moskva/kvartiry/prodam?p={page}&cd=1"]::attr(href)'
        #     page += 1
        #     next_page = response.css(text).extract_first()
        #     yield response.follow(next_page, callback=self.parse)
        posts = response.css('div.js-catalog_serp div.snippet-horizontal div.item__line a.item_table-extended-description::attr(href)').extract()
        for post in posts:
             yield response.follow(post, callback=self.post_parse)



    def post_parse(self, response: HtmlResponse):
        title = response.css('span.title-info-title-text::text').extract_first()
        price = response.css('span.js-item-price::text').extract_first()
        list1 = response.css('ul.item-params-list span::text').extract()
        list2 = response.css('ul.item-params-list li::text').extract()
        list2 = [itm for itm in list2 if itm != ' ']
        params = {}
        for i, itm in enumerate(list1):
            params[itm] = list2[i]

        yield {
            'title': title,
            'price': price,
            'params': params
        }
        pass
