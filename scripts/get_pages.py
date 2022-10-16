#!/usr/bin/python
# coding: utf-8

import sys
import os
import requests
from bs4 import BeautifulSoup

channel = sys.argv[1]
index = sys.argv[2]

ad = open('links.md', mode='r').read()

def get_index(link):
	response = requests.get(link)
	text = response.text.encode('utf-8').replace('</p>\n</p>','</p>')
	parser = BeautifulSoup(text, 'html.parser')

	## id=artlist -> class=arttitle ; class=post_list -> class=title
	post_list = parser.find('div', attrs = {'class': 'post_list'})
	if post_list is None:
		titles = parser.find_all('div', attrs = {'class': 'arttitle'})	
	else:
		titles = post_list.find_all('div', attrs = {'class': 'title'})

	articleList = []
	for title_div in titles:
		a_link = title_div.find('a')
		articleList.append((a_link.text.encode('utf-8'), a_link['href'].encode('utf-8')))
	return articleList[::-1]	


def get_article(link):
	response = requests.get(link)
	text = response.text.encode('utf-8').replace('</p>\n</p>','</p>')
	parser = BeautifulSoup(text, 'html.parser')

	for img in parser.find_all('img'):
		del img['width']
		del img['height']
	for iframe in parser.find_all('iframe'):
		iframe.decompose()
	for script in parser.find_all('script'):
		script.decompose()
	for a in parser.find_all('a'):
		del a['title']
		del a['class']

	body = parser.find('div', id='artbody')
	try:
		for twitter in body.find_all('twitter-widget'):
			twitter.decompose()
		body.find('header').decompose()
		body.find('div', id='below_article_ad').decompose()
		body.find('aside').decompose()
		body.find('div', id='recommend_post').decompose()
	except:
		pass	
	content = body.prettify().encode('utf-8')


	# get post image
	post_image = parser.find('div', attrs = {'class': 'featured_image'})
	if post_image is None:
		post = ''
	else:
		img = post_image.find('noscript').find('img')
		caption = post_image.find('div', attrs = {'class': 'caption'})
		if img is None or caption is None:
			post = ''
		else:
			del img['width']
			del img['height']
			post = '<div>' + img.prettify().encode('utf-8') + \
				caption.prettify().encode('utf-8') + '</div><hr/>'
	return (post + content ) \
		.replace('<a href', '<ok href').replace('</a>', '</ok>') \
		.replace('</figure>','</figure><br/>') \
		.replace('<figcaption','<br/><figcaption') \
		.replace('</figcaption>','</figcaption><br/>') \
		.replace('<h2>', '<h4>') \
		.replace('<h2 ', '<h4 ') \
		.replace('</h2>', '</h4>')


def get_name(link):
	fname = link.split('/')[-1].split('.')[0] 
	path = "../pages/%s/%s.md" % (channel, fname)
	return fname, path


def page_exists(file_path):
	return os.path.exists(file_path)


def write_page(fname, path, title, content, link):
	fh = open(path, 'w')
	ads = ad.replace(')', '?%s)' % fname)
	counter = "<img src='http://gfw-breaker.win/easy2view/%s' width='0px' height='0px'/>" % (path)
	print(counter)
	md = "### %s\n\n---\n\n%s\n\n%s\n\n%s\n\n---\n\n原文链接（需翻墙）：%s" % (title, ads, counter, content, link)
	fh.write(md)
	fh.close()


def append_to_index(fname, title):
	path = "../indexes/%s.csv" % (channel)
	myfile = open(path, "a+") 
	line = "%s,%s\n" % (fname.encode('utf-8'), title)
	myfile.write(line)
	myfile.close()


## main
items = get_index(index)
for item in items:
	link = item[1]
	title = item[0]
	fname, path = get_name(link)
	if page_exists(path):
		continue
	print link, title
	try:
		content = get_article(link)
		write_page(fname, path, title, content, link)
		append_to_index(fname, title)
	except Exception as e:
		print "Failed to parse %s\nError: %s" % (link, str(e))




