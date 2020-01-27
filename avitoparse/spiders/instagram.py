# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime
import scrapy
import json
import re
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from avitoparse.items import FollowItem

HASHES = {
    'followers': 'c76146de99bb02f6415203be841dd25a',
    'following': 'd04b0a864b4b54837c0d870b0e77e076',
    'media': '58b6785bea111c67129decbe6a448951',
    'media_comments': '97b41c52301f77ce508f55e66d17620e',
    'likes': 'd5d763b1e2acf209d62d22d184488e57',
    'tags': '174a5243287c5f3a7de741089750ab3b',

}

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'topotun2020'
    insta_pass = 'topotun'
    insta_login_link = 'https://instagram.com/accounts/login/ajax/'
    parse_user = ['gefestart','ivanslmnk','political_cartoon_gallery','flyjoeairport']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    user_data_hash = 'c9100bf9110dd6361671f113dd02e7d6'


    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield  scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'password': self.insta_pass},
            headers={'X-CSRFToken': csrf_token}
        )
        pass

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_user:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_follow_parse,
                    cb_kwargs={'username': user}
                )

    def user_follow_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            "id": user_id,
            "include_reel": True,
            "first": 50
        }
        url_followers = f'{self.graphql_url}query_hash={HASHES["followers"]}&{urlencode(variables)}'

        yield response.follow(
                    url_followers,
                    callback=self.user_followers_data,
                    cb_kwargs={'username': username,
                               'user_id': user_id,
                               'variables':deepcopy(variables)
                               }
                )
        url_following = f'{self.graphql_url}query_hash={HASHES["following"]}&{urlencode(variables)}'

        yield response.follow(
            url_following,
            callback=self.user_following_data,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)
                       }
        )

    def user_followers_data(self, response: HtmlResponse, username, user_id, variables):
        j_user_followers_data = json.loads(response.text)
        page_info = j_user_followers_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_followers_data = f'{self.graphql_url}query_hash={HASHES["followers"]}&{urlencode(variables)}'
            yield response.follow(
                url_followers_data,
                callback=self.user_followers_data,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables':deepcopy(variables)
                           }
            )

        for follower in j_user_followers_data.get('data').get('user').get('edge_followed_by').get('edges'):
            item = FollowItem(user_name=username,
                              user_id=user_id,
                              follower_id=follower['node']['id'],
                              follower_name=follower['node']['username'],
                              data=follower['node'],
                              date=datetime.now()
                              )
            yield item

    def user_following_data(self, response: HtmlResponse, username, user_id, variables):
        j_user_following_data = json.loads(response.text)
        page_info = j_user_following_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_following_data = f'{self.graphql_url}query_hash={HASHES["following"]}&{urlencode(variables)}'
            yield response.follow(
                url_following_data,
                callback=self.user_following_data,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables':deepcopy(variables)
                           }
            )

        for following in j_user_following_data.get('data').get('user').get('edge_follow').get('edges'):
            item = FollowItem(user_name=following['node']['username'],
                              user_id=following['node']['id'],
                              follower_id=user_id,
                              follower_name=username,
                              data=following['node'],
                              date=datetime.now()
                              )
            yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return  matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

