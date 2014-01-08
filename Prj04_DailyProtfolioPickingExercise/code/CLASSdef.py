# -*- coding: utf-8 -*-
"""
Created on Thu Sep 05 14:47:59 2013

@author: olenag
"""
import pandas

class STOCK:
    def __init__(self,name):
        self.name = name
        self.GISC = None
        self.sector = None
        self.df = pandas.DataFrame()
        
class PORTFOLIO:
    def __init__(self,strategy,hd,value,capital_per_stock,investment_mode):
        self.strategy = strategy
        self.HD = hd        
        self.value = value
        self.capital_per_stock = capital_per_stock
        self.investment_mode = investment_mode
        self.holdings = {}
        self.summary = {}