#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 18:15:45 2019

@author: rida
"""
from MovieRecommender.MovieRecommender import MovieRecommender
'''
from nltk.corpus import stopwords

import string
import nltk.stem.porter as porter
import numpy as np
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
'''
movieName = 'Star Wars: The Last Jedi'
mvRcmd =MovieRecommender()
htmlText = mvRcmd.getMovieRecommendation(movieName)

     
'''
    
dfcl= mvRcmd.remove_stopword(dfrev['Movie_Review'])
dfflt= mvRcmd.rem_shortword(dfcl)
dfflt= mvRcmd.replace_empty_rows(dfflt)
dfflt= mvRcmd.drop_na(dfflt)
rev_tokens=mvRcmd.create_wordtokens(dfflt)
dfrev['Filt_revstm']=dfflt.apply(mvRcmd.stem_words)
dfrev['Filt_revlem']=dfflt.apply(mvRcmd.lem_words)

'''