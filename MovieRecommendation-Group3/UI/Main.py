#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 07:34:10 2019

@author: Harsha Menon
"""

# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from MovieRecommender.MovieRecommender import MovieRecommender

from nltk.corpus import stopwords

app =  Flask(__name__)

@app.route('/')
def home():
    return render_template('Search.html')

@app.route('/submit', methods=['post'])
def getReviews():
    #url = request.form.get('url')
    movieName = request.form.get('movie')
    
    
    movieName = 'Star Wars: The Last Jedi'
    mvRcmd =MovieRecommender()
    htmlText = mvRcmd.getMovieRecommendation(movieName)
    e=''
    return render_template('Search.html',HtmlText = htmlText, ExceptionText = e)
  
    
if __name__ == '__main__':
    app.debug = True
    app.run()
    

