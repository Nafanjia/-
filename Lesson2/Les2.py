import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from database.db import BlogDb
from database.models import (
    Base,
    BlogPost,
    Writer,
    Tag
)


domain = 'https://geekbrains.ru'
start_url = 'https://geekbrains.ru/posts?page=53'

db_url = 'sqlite:///blogpost.sqlite'
db = BlogDb(db_url)

def page_soap(url):
    response = requests.get(url)
    soap = BeautifulSoup(response.text, 'lxml')
    return soap


def get_post_page(url):
    soap = page_soap(url)
    posts = soap.find('div', attrs={'class': 'post-items-wrapper'})
    title = posts.find_all('a', attrs={'class': 'post-item__title'})
    post_list = []
    for i in range(2):#len(title)):
        post_url = title[i].attrs['href']
        post_url = f'{domain}{post_url}'
        soap_post = page_soap(post_url)
        writer_url = soap_post.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('a', attrs={'style': 'text-decoration:none;'}).attrs['href']
        post_dict = {
            'post_title': soap_post.find('article', attrs={'class': 'col-sm-6 col-md-8 blogpost__article-wrapper'}).h1.text,
            'post_date': soap_post.find('article', attrs={'class': 'col-sm-6 col-md-8 blogpost__article-wrapper'}).find('div', attrs={'class': 'blogpost-date-views'}).find('time').text,
            'post_url': post_url,
            'post_tags': soap_post.find('i', attrs={'class': 'i i-tag m-r-xs text-muted text-xs'}).attrs['keywords'].replace(', ', ',').split(','),
            'writer_name': soap_post.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('div', attrs={'itemprop': 'author'}).text,
            'writer_url': f'{domain}{writer_url}'
        }
        post_list.append(post_dict)
    return post_list


def pars(url):
    posts = []
    while True:
        soap = page_soap(url)
        posts.extend(get_post_page(url))
        li = soap.find('ul', attrs={'class': 'gb__pagination'}).find_all('li', attrs={'class': 'page'})
        try:
            next_page = li[-1].find('a', attrs={'rel': 'next'}).attrs['href']
        except AttributeError:
            break
        url = f'{domain}{next_page}'
        time.sleep(1)
    return posts


result = pars(start_url)


for i in range(len(result)):
    writer = Writer(result[i]['writer_name'], result[i]['writer_url'])
    tags = [Tag(result[i]['post_tags'][itm]) for itm in range(len(result[i]['post_tags']))]
    blogpost = BlogPost(result[i]['post_title'], result[i]['post_url'], writer, tags[:len(tags)])

    if db.session.query(Tag).filter_by(name=writer.name).all():
        blogpost = BlogPost(result[i]['post_title'], result[i]['post_url'], db.session.query(Writer).filter_by(name=writer.name).all(), tags[:len(tags)])
    else:
        db.session.add(writer)
    for i in range(len(tags)):
        name = tags[i].name
        if db.session.query(Tag).filter_by(name=name).all():
            tags.remove(tags[i])
            blogpost = BlogPost(result[i]['post_title'], result[i]['post_url'], db.session.query(Writer).filter_by(name=writer.name).all(), tags[:len(tags)])

    db.session.add_all(tags)
    db.session.add(blogpost)
    db.session.commit()

print(1)


