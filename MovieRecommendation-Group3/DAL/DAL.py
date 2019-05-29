#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 12:25:57 2019

@author: HM
"""


import pymongo

class DAL:
    
    def insertDataInDB(self, data, dbName, collectionName):
        
        mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = mongoClient[dbName]
        collection = db[collectionName]
        result = collection.insert_one(data).inserted_id
        return result; 
    
    def searchData(self,dbName,collectionName, searchField, searchData):
         mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
         db = mongoClient[dbName]
         collection = db[collectionName]
        
         query = { searchField: { "$regex": "^"+searchData+""} }
         cursor = collection.find_one(query)
       
         return cursor
    