#!venv/bin/python
# -*- coding: utf-8 -*- 

import os, datetime
import tweepy
from bs4 import BeautifulSoup
from urllib2 import urlopen
from urllib import urlretrieve
from config import *
from PIL import Image, ImageFont, ImageDraw

__DIR__  = os.path.dirname(os.path.abspath(__file__))
host	 = 'http://pogoda.mail.ru/prognoz/sankt_peterburg/'
host2	 = 'http://weather.rambler.ru/v-sankt-peterburge/'
img_name = __DIR__+'/files/weather.jpg'
# get page source
page  	 = urlopen(host2).read()
soup 	 = BeautifulSoup(page)
bg_url	 = soup.find('div','b-day_main').find('div','b-day__bg').get('data-bgurl')

## parse div with img url
# src  	 = soup.find('div', 'block_forecast')
## get url to image
# bg_url 	 = host + src.get('style').split("'")[1]
## get weather type ;-)
# weather  = bg_url.split('/')[-1].split('.')[0]

#auth in Twitter
auth = tweepy.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
auth.set_access_token(TWEEPY_ACCESS_KEY, TWEEPY_ACCESS_SECRET)
twitter = tweepy.API(auth)

def check_img_filesize():
	# check filesize before image download
	img  = urlopen(bg_url)
	meta = img.info()
	img_online_filesize = meta.getheaders("Content-Length")[0]

	f = open(img_name, "rw")
	img_offline_filesize = len(f.read())
	f.close()
	# print "Content-Length:", img_online_filesize, img_offline_filesize
	if (img_online_filesize != img_offline_filesize and img_online_filesize != 0):
		#download image file to disk
		urlretrieve(bg_url, img_name)
		#update twitter banner
		twitter.update_profile_banner(filename=img_name)
		twitter.update_profile_background_image(filename=img_name, use=True, include_entities=True)

		return 1
	else:
		return 0

def add_data_to_avatar(temp,hum):
	now  = datetime.datetime.now().ctime()
	im   = Image.open(__DIR__+'/files/avatar.jpg')
	tmp  = __DIR__+'/files/avatar_updated.jpg'
	draw = ImageDraw.Draw(im)
	# use a bitmap font
	# font = ImageFont.load("arial.pil")
	# font_temp = ImageFont.truetype("Arial.ttf",50)
	font_temp = ImageFont.truetype(__DIR__+"/files/myriadpro-regural.otf", 80)
	font_time = ImageFont.truetype(__DIR__+"/files/Arial.ttf", 11)
	draw.text((270, 50), str(temp) + "'", font=font_temp, fill=(0,0,0,255))
	# draw.text((20, 50), str(temp) + "'C", font=font_time, fill=(0,0,0,255))
	draw.text((10, 385), 'updated: ' + str(now), font=font_time, fill=(170,170,170,255))
	im.save(tmp, "JPEG")
	#update twitter avatar and remove tmp file
	twitter.update_profile_image(filename=tmp)
	os.remove(tmp)
	return 1

def get_data_from_DHT():
	# function to read the temperature from DHT11 temperature sensor:
	cmd  = __DIR__+'/readDHT 11 4'
	data = os.popen(cmd).readline().split(",")
	temp = data[0].split(" ")[2]
	hum  = data[1].split(" ")[3]
	if (temp != '' and hum != ''):
		return (temp, hum)
	else:
		return 0

def send_twitter_message():
	temp, hum = get_data_from_DHT()
	msgRu = 'В Санкт-Петербурге температура сейчас '+str(temp)+'°C, относительная влажность воздуха '+str(hum)+'%.\n#погода #градусник #питер #спб'
	twitter.update_status(msgRu, lat='59.867157', long='30.457755')
	add_data_to_avatar(temp, hum)
	check_img_filesize()
	return 0

send_twitter_message()
