#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 12:40:54 2019

@author: HM
"""
 
from contextlib import closing
import bs4 as BeautifulSoup
from requests import get
from requests.exceptions import RequestException
import re
import urllib.request as urllib2
import urllib.parse
import urllib.error
 


class WebScrapper:
    
    def __init__(self): 
        self.baseURL = 'https://www.google.co.in/search?q='
        self.reviews_list = []
    
    
    def get_soup(self, url, header):
        request = urllib.request.Request(url, headers=header)
        return BeautifulSoup.BeautifulSoup(urllib.request.urlopen(request), 'html.parser')


    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    def is_good_response(self,resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)


    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    def log_error(self,e):
        return e
   
    def getURLFromGoogle(self, soup, siteName):
        for reviewDiv in soup.findAll('div', attrs = {'class' : 'r'}):
                for a in reviewDiv.findAll('a',href=True):
                    if a['href'].find(siteName) != -1:
                         return a['href']
                       
    """
            Attempts to get the content at `url` by making an HTTP GET request.
            If the content-type of response is some kind of HTML/XML, return the
            text content, otherwise return None.
    """
    
    def getReviews(self, movieName):
        try:
            # This script has only been tested with google.co.in
            
             # Add some recent user agent to prevent amazon from blocking the request 
            # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
            
            header = { 'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
            #get(amazon_url, headers = headers, verify=False,
          
            #get URL for rottentomatoes reviews
            searchURL  = self.baseURL + urllib.parse.quote_plus(movieName + ' movie reviews rottentomatoes')
          
            rottenTomatoesURL_GoogleSoup = self.get_soup(searchURL, header)
            
            rottenTomatoesURL = self.getURLFromGoogle(rottenTomatoesURL_GoogleSoup,'www.rottentomatoes.com')
            
            #get URL for rottentomatoes reviews
            searchURL  = self.baseURL + urllib.parse.quote_plus(movieName + ' movie reviews  imdb')
          
            imdbURL_GoogleSoup = self.get_soup(searchURL, header)
            
          
            imdbURL = self.getURLFromGoogle(imdbURL_GoogleSoup,'www.imdb.com')
            
            rottenTomatoes_Soup = self.get_soup(rottenTomatoesURL, header)
            imdb_Soup = self.get_soup(imdbURL+'reviews?ref_=tt_urv', header)
            
            self.ParseRottentomatoesReviews(rottenTomatoes_Soup)
            self.ParseimdbReviews(imdb_Soup)
            
             #sum(list2,[])
            
            return sum(self.reviews_list,[])
    
        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(searchURL, str(e)))
            return None

   
    def ParseRottentomatoesReviews(self,rottenTomatoes_Soup):
        list1={}
        
        for div in rottenTomatoes_Soup.findAll('div',{'class':'review_quote'}):
            list1[div.find('p')] = div.text.strip().replace('','')
            for dt in list1:
                rev=re.findall('\s([a-zA-Z].*)',str(dt))
                self.reviews_list.append(rev)
       
    
    def ParseimdbReviews(self,imdb_Soup):
        #review-container> content> text
        for container_div in imdb_Soup.findAll('div',{'class':'review-container'}):
            for content_div in container_div.findAll('div',{'class':'content'}):
                 for text_div in content_div.findAll('div',{'class':'text'}):
                        rev=re.findall('\s([a-zA-Z].*)',str(text_div.text))
                        self.reviews_list.append(rev)
                        
                        
                        