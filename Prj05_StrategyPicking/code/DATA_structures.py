# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 16:54:40 2013

@author: olenag
"""

class INVESTMENT:
    def __init__(self,stock_name,df,start_date=None,end_date=None,strategy_name = None,fscore2apply=None):
        self.start_date = start_date
        self.end_date = end_date
        self.stock_name = stock_name
        self.df = df
        self.fscore2apply = fscore2apply
        self.strategy_name = strategy_name
        self.sharpe = None
        self.some_measure = None
        
        

class STRATEGY:
    def __init__(self,name):
        self.name = name
        
class STOCK:
    def __init__(self,name):
        self.name = name
        self.df = None #dataframe for this stock
        #self.OLS_Statistics_F2 = {} #holds ordinary least quares reg statistics per each F2score examined 
        
        """OLS_Statistics_F2vsRelRet has the following keys: OLS_alpha,alpha-pScore,OLS_beta,beta-pScore,number_of_observations,AIC"""    