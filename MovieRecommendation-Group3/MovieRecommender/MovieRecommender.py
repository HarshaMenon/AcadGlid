#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 06:12:34 2019

@author: rida
"""

from WebScrapper.WebScrapper import WebScrapper
from DAL.DAL import DAL
import pandas as pd

from nltk.corpus import stopwords

import string
import nltk.stem.porter as porter
import numpy as np
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from tqdm import tqdm
tqdm.pandas(desc="progress-bar")

class MovieRecommender:
    

    def getReviews(self, movieName):
        wsc =  WebScrapper()
        reviews = wsc.getReviews(movieName);
        review_D =  {'movieName': movieName.upper(),
                    'review': reviews}
           
        e = ''
        htmlText = ''
        if reviews is not None:
            
            dal = DAL();
            htmlText= dal.insertDataInDB(review_D,'MovieReviewsDB','MovieReviews')
        else:
            e = "Error:" + wsc.log_error('Invalid URL')
        return reviews

    def get_pred_test_data(self,model_file,feat_words):
        model_name=self.get_model(model_file)
        pred_test=model_name.predict(feat_words)
        return pred_test

    def get_file_names(self,model,dfs):
        fnames=dfs[dfs['Model_Type']==model]['Model_FileName']
        for dt1 in fnames:
            fname=dt1
        return fname
    
    
    
    def get_model(self,filename):
        model=pickle.load(open(filename,'rb'))
        return model

    def get_movierev_data(self,dict_data):
        lstname=list()
        lstrev=list()
        lstid=list()
    
        clmns=['Id','Movie_Name','Movie_Review']
        dfrev=pd.DataFrame(columns=clmns)
        dfrev.columns=clmns
        i =1   
         
        for val in  dict_data['review']:
            lstid.append(i)
            lstname.append(dict_data['movieName'])
            lstrev.append(val)
            i=i+1

        dfrev['Id']=lstid
        dfrev['Movie_Name']=lstname
        dfrev['Movie_Review']=lstrev
        return dfrev

    def searchReviews(self,movieName):
         
        dal = DAL();
        reviews= dal.searchData('MovieReviewsDB','MovieReviews','movieName',movieName)
        if reviews is None:
            reviews =  self.getReviews(movieName)
        return reviews
    
    def getMovieRecommendation(self, movieName): 
        recommendation = ''
        reviews = self.searchReviews(movieName.upper())
        if reviews is None:
            reviews = self.getReviews(movieName)
            
        recommendation = self.get_suggestion(reviews)
        return recommendation
    
    def get_suggestion(self,reviews):
        cntgood=0
        cntbad=0
        percentgood=0.0
        percentbad=0.0
        difgood=0.0
        difbad=0.0
        messages=''
        
       # clean data and pass to model and get prediction
        dfrev=self.get_movierev_data(reviews)
        dfcl=self.remove_stopword(dfrev['Movie_Review'])
        dfflt= self.rem_shortword(dfcl)
        dfflt=self.replace_empty_rows(dfflt)
        dfflt=self.drop_na(dfflt)
        rev_tokens=self.create_wordtokens(dfflt)
        dfrev['Filt_revstm']=dfflt.apply(self.stem_words)
        dfrev['Filt_revlem']=dfflt.apply(self.lem_words)
        
        
        bow_stem=self.get_bag_of_words(dfrev['Filt_revstm'],'bag_of_words_stem.pkl')
        bow_lem=self.get_bag_of_words(dfrev['Filt_revlem'],'bag_of_words_lem.pkl')
        df_Results=pd.read_csv('df_result.csv')
        df_Results.columns=['Model_Type','Accuracy','Recall','Precision','F1_Score','Model_FileName']

        fname_naive_BagWord_stem=self.get_file_names('Naive_bayes_With_stem_Bag_words',df_Results)
        pred_test_Naive_BagWord_stem=self.get_pred_test_data(fname_naive_BagWord_stem,bow_stem)
        fname_naive_BagWord_lem= self.get_file_names('Naive_bayes_With_lem_Bag_words',df_Results)
        pred_test_Naive_BagWord_lem=self.get_pred_test_data(fname_naive_BagWord_lem,bow_stem)
        tfwords_test_stem=self.get_tfidf_data(dfrev['Filt_revstm'],'TFIDF_stem.pkl')
        tfwords_test_lem=self.get_tfidf_data(dfrev['Filt_revlem'],'TFIDF_lem.pkl')
        fname_naive_stem_TFIDF=self.get_file_names('Naive_bayes_With_stem_TFIDF',df_Results)
        pred_test_Naive_stem_TFIDF=self.get_pred_test_data(fname_naive_stem_TFIDF,tfwords_test_stem)
        fname_naive_lem_TFIDF=self.get_file_names('Naive_bayes_With_lem_TFIDF',df_Results)
        pred_test_Naive_lem_TFIDF=self.get_pred_test_data(fname_naive_lem_TFIDF,tfwords_test_lem)
        dfrev['pred_test_Naive_BagWord_stem']=pred_test_Naive_BagWord_stem
        dfrev['pred_test_Naive_BagWord_lem']=pred_test_Naive_BagWord_lem
        dfrev['pred_test_Naive_stem_TFIDF']=pred_test_Naive_stem_TFIDF
        dfrev['pred_test_Naive_lem_TFIDF']=pred_test_Naive_lem_TFIDF
        
        cntgood = dfrev[dfrev['pred_test_Naive_BagWord_stem']== 'Good']['Id'].count()
        cntbad = dfrev[dfrev['pred_test_Naive_BagWord_stem']== 'Bad']['Id'].count()
        
   
        movie = dfrev['Movie_Name'][0]
    
        if cntgood==cntbad:
                messages= movie +' seems to be an average movie as number og good reviews are same as number of bad reviews  i.e. ' + str(cntgood)
        else:
            percentgood=((cntgood/(cntgood+cntbad))*100)
            percentbad=((cntbad/(cntgood+cntbad))*100)
            if percentgood>percentbad:
                difgood=percentgood-percentbad
                if difgood>5.:
                    messages= +movie + 'is good movie because we have '+ str(difgood)+'% more good reviews than bad reviews.'
                else:
                    messages=movie + ' seems to be an average movie because we have only '+ str(difgood)+'% difference between good reviews and bad reviews.'

            elif percentbad>percentgood:
                difbad=percentbad-percentgood
                if difbad>5.:
                    messages='It seems that  '+movie + ' has not impressed many audience because we have '+ str(difbad)+'% more bad reviews than good reviews.'
                else:
                    messages=movie + ' seems to be an average movie because we have only '+ str(difbad) +'% difference between good reviews and bad reviews.'
            else:
                messages='Oops the number of good and bad reviews have confused us so please watch the movie and provide other viewers a better review.'
    
      
        #return messages
        return messages

    
    def remove_stopword(self,rawdata):
        stop=stopwords.words('english')
        punc=string.punctuation
        dfcnl=rawdata.apply(lambda x:' '.join([item for item in x.split() if item  not in stop]))
        dfcnl=dfcnl.apply(lambda x: ' '.join([wrd for wrd in x.split() if wrd not in punc]))
        return dfcnl
    
    def rem_shortword(self,textdata):
        filtdata=textdata.apply(lambda x: ' '.join([wd for wd in x.split() if len(wd)>3]))
        return filtdata
    
    def replace_empty_rows(self,dfr):
        dfr.replace('',np.nan,inplace=True)
        return dfr
    
    
    def drop_na(self,dfrs):
        dfrs.dropna(inplace=True)
        return dfrs
    
    def create_wordtokens(self,sent):
        word_tokens=sent.apply(lambda x: x.split())
        return word_tokens
    
    def stem_words(self,sent):
        tokens= str(sent).split()
        #str(sent).split()
        stemmer=porter.PorterStemmer()
        stemed_dt= [stemmer.stem(token) for token in tokens]
        stemed_dt=' '.join(stemed_dt)
        return stemed_dt
    def lem_words(self,sents):
        tokens=str(sents).split()
        #str(sents).split()
        lemmatizer=WordNetLemmatizer()
        lem_word=[lemmatizer.lemmatize(token) for token in  tokens]
        lem_word=' '.join(lem_word)
        return lem_word
    
    def get_bag_of_words(self,filtered_data,fname):
        vectorize=CountVectorizer()
        loaded_vec = CountVectorizer(vocabulary=pickle.load(open(fname, "rb")))
        bow=loaded_vec.fit_transform(filtered_data)
        return bow
    
    
    def get_tfidf_data(self,input_data,fname):
        tfvec=TfidfVectorizer(max_df=0.9,min_df=0.0,max_features=1000,stop_words='english')
        loaded_vec = CountVectorizer(vocabulary=pickle.load(open(fname, "rb")))
        tfidfdt=loaded_vec.fit_transform(input_data)
        return tfidfdt
    