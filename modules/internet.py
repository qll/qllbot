#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, re
from xml.etree.ElementTree import ElementTree
from qllbot.basic_functions import strip_tags
from qllbot.Registry import *
from settings import *


def google(param):
	''' Starts a google search for a given string (e.g. #google test -> results for 'test') '''
	if param == '':
		return u'No search string submitted.'
	param   = urllib2.quote(param.encode('utf8', 'replace'))
	request = urllib2.Request('http://www.google.de/search?hl=de&q=%s&btnG=Suche' % param)
	# Google does not like strange user agents :-)
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.3 Safari/534.24') 
	opener  = urllib2.build_opener()
	content = opener.open(request).read().decode('utf-8')

	regex  = r'<li class=(g|w0)( style=[^>]+)??><div[^>]+><span[^>]+><h3 class="r"><a href="(?P<url>[^>]+)" class=l[^>]+>(?P<page_title>.*?)</a>'
	output = 'No match.'
	i      = 0
	for result in re.finditer(regex, content):
		if i == 0:
			output = ''
		if i >= GOOGLE_MAX_RESULTS:
			break
		# strip html tags and replace &amp; with &
		title  = strip_tags(result.group('page_title')).replace('&amp;', '&')
		output += u'%s: %s\n' % (title, result.group('url'))
		i += 1
	# cut last \n and return output
	return output[:-1]

def get_weather(param):
	''' Get weather details for your city. Other location can be checked too: #weather [location] (e.g. #weather Berlin) '''
	location = WEATHER_LOCATION
	if param != '':
		if not re.match('^[\w\d ]+$', param):
			return 'Invalid location. Use city name or postal code.'
		location = param
	try:
		location = urllib2.quote(location.encode('utf8', 'replace'))
		handle   = urllib2.urlopen('http://www.google.com/ig/api?weather=%s' % location)
	except:
		return 'Error opening URL.'
	tree = ElementTree()
	tree.parse(handle)
	handle.close()
	
	city = tree.find('weather/forecast_information/city')
	if city == None:
		return 'Did not find city.'
	city = city.attrib['data']
	
	condition = tree.find('weather/current_conditions/condition').attrib['data']
	curtemp   = tree.find('weather/current_conditions/temp_c').attrib['data']
	
	weather = u'Currently: %s at %s°C in %s\n' % (condition, curtemp, city)
	
	for condition in tree.getiterator('forecast_conditions'):
		minTemp = condition.find('low').attrib['data']
		maxTemp = condition.find('high').attrib['data']
		day     = condition.find('day_of_week').attrib['data']
		cond    = condition.find('condition').attrib['data']
		if cond == '':
			cond = u'Unknown condition'
		unit    = u'F'
		if WEATHER_IN_CELSIUS:
			# convert fahrenheit to celsius
			minTemp = (float(minTemp) - 32.0) * (5.0/9)
			maxTemp = (float(maxTemp) - 32.0) * (5.0/9)
			unit    = u'°C'
		weather += u'%s: %s at %d-%d%s\n' % (
			day, cond, round(minTemp), round(maxTemp), unit
		)
	
	return weather[:-1]

def get_random_imdb(param):
	''' Returns random movie from imdb.com '''
	handle = urllib2.urlopen('http://www.imdb.com/random/title')
	content = handle.read().decode('utf-8')
	handle.close()

	seriesMatch = re.search(r'<meta name="title" content=".+ \(TV Series', content)
	if seriesMatch != None:
		# found a tv series ... try again
		return get_random_imdb(param)
	titleMatch  = re.search(r'<meta name="title" content="(?P<title>.+) \((?P<year>[0-9]{4})\) - IMDb" />', content)
	ratingMatch = re.search(r'<span class="rating-rating">(?P<rating>[0-9](.[0-9])?)<span>/10</span></span>', content)
	urlMatch    = re.search(r'<meta property="og:url" content="(?P<site_url>http://www.imdb.com/title/tt[0-9]+)/" />', content)
	
	title  = u''
	year   = u''
	rating = u''
	url    = u''
	if titleMatch != None:
		title = titleMatch.group('title')
		year  = titleMatch.group('year')
	if ratingMatch != None:
		rating = ratingMatch.group('rating')
	if urlMatch != None:
		url = urlMatch.group('site_url')
	return u'%s (%s) [Rating %s] %s' % (title, year, rating, url)


add_command('g', google)
add_command('google', google)
add_command('weather', get_weather)
add_command('randommovie', get_random_imdb)
add_command('givemovie', get_random_imdb)
