# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 18:12:57 2013

@author: olenag
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from class_definitions import *
import utils

    
def ols_F2vsYvar(df,stock,f2scores,yVar,QUANTILES=None):
    df = df.dropna()  
    
    #print df.to_string()
    
    for f2score in f2scores:
        condition = []
        print "\n",f2score
        if QUANTILES != None:
            condition.append(df[f2score] < df[f2score].quantile(QUANTILES[0]))
            condition.append(df[f2score] > df[f2score].quantile(QUANTILES[1]))
            print "Quantiles cut offs:",df[f2score].quantile(QUANTILES[0]),df[f2score].quantile(QUANTILES[1])
            #RelRet = df['Rel Ret'][condition[0]|condition[1]].values 
            RelRet = df[yVar][condition[0]|condition[1]].values 
            Xf2score = df[f2score][condition[0]|condition[1]].values
            signif_df = df[condition[0] | condition[1]] #for debugging of condition-statments only
        else:
            RelRet = df[yVar].values
            Xf2score = df[f2score].values
            signif_df = df #for debugging of condition-statments only
        
        #utils.dump_data_csv(signif_df,stock,"t_"+stock.name+"_"+f2score+"_vs_"+yVar+".csv")
        
        print "number of observations (i.e. F2score.length)",len(Xf2score)
        Xf2score = sm.add_constant(Xf2score)
        model = sm.OLS(RelRet,Xf2score).fit()
        
        if f2score not in stock.OLS_Statistics_F2vsRelRet.keys():
            stock.OLS_Statistics_F2vsRelRet[f2score]= {}
        #print model.summary()
        """Rsquared","OLS_alpha","alpha-pScore","OLS_beta","beta-pScore","number_of_observations","AIC"""
        stock.OLS_Statistics_F2vsRelRet[f2score]["OLS_beta"] = model.params[0]
        stock.OLS_Statistics_F2vsRelRet[f2score]["OLS_alpha"] = model.params[1]
        stock.OLS_Statistics_F2vsRelRet[f2score]['Rsquared'] = model.rsquared
        stock.OLS_Statistics_F2vsRelRet[f2score]['AIC'] = model.aic
        stock.OLS_Statistics_F2vsRelRet[f2score]['BIC'] = model.bic
        stock.OLS_Statistics_F2vsRelRet[f2score]['beta-pScore'] = model.pvalues[0]
        stock.OLS_Statistics_F2vsRelRet[f2score]['alpha-pScore'] = model.pvalues[1]
        stock.OLS_Statistics_F2vsRelRet[f2score]['number_of_observations'] = model.nobs
        """debugging only"""
        print "model's number of obs =",model.nobs
        stock.OLS_Statistics_F2vsRelRet[f2score]['number_of_observations'] 
        print "model.params =",model.params
        print "model.rsquared =",model.rsquared
        print "model.aic =",model.aic
        print "model.pvalues =",model.pvalues
    
      



########################################################################
### keep for a while might be useful
########################################################################
def get_stationary_quantiles(df,F2scores,QUANTILES):
    s_Q = []
    for f2score in F2scores:
        t_Q = []
        for quantile in QUANTILES:
            t_Q.append(np.percentile(df[f2score],quantile*10))# this one includes NaN entries of an array in quantile calculation       print f2score,t_Q
        s_Q.append(t_Q)
    return s_Q
    
def get_stationary_quantiles1(df,F2scores,QUANTILES):
    s_Q = []
    for f2score in F2scores:
        t_Q = []
        for quantile in [0.1,0.9]:
            t_Q.append(df[f2score].quantile(quantile))
        print f2score, t_Q        
        s_Q.append(t_Q)
    return s_Q