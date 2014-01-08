# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:44:57 2013

@author: jaroslawb
"""
import os
from pandas import *
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def transform_raw_scores_2_rank(strategies,orig_DF,transf_DF,transf_type="AvgSimpleRank",side="Long",out_dir = ""):
    
    if transf_type=="AvgSimpleRank":
        for filt in strategies:
            transf_DF[filt] = orig_DF[filt].rank(axis=1,method='first',ascending=True) #could try using method='max', might be better
            transf_DF[filt].to_csv(out_dir+'t_ranked_'+filt+'_'+side+'.csv')
            
    elif transf_type=="AvgNormalizedRank":  
        for filt in strategies:
            mins = orig_DF[filt].min(axis=1)
            maxs = orig_DF[filt].max(axis=1)
            transf_DF[filt] =  orig_DF[filt]/(maxs-mins)
            transf_DF[filt].to_csv(out_dir+'t_ranked_'+filt+'_'+side+'.csv')
    else:
        print "!!! ERROR: no transformation type was given"
        



if __name__=="__main__":

    directory = ".."+os.sep+'data'+os.sep+'mix_strategies'+os.sep
    
    resultDirectory = directory+'outputs'+os.sep
    if not os.path.exists(resultDirectory):
        os.makedirs(resultDirectory)
    
    startDate = datetime(2005,1,1)   #2005,2,1
    HDS = ['HD5']# 'HD3','HD1',

    fscores = ['F2(6)']#,'F2(8)']
    
    THS = ['TH3']
    poolTHS = ['size300']
    methods = ["MarketUpDown","IR","F2SensitivityMCC"]

 
    for f2 in fscores:
        for hd in HDS:
            for poolth in poolTHS:
                strategies = []   
                for method in methods:                
                    filt = method+'_'+f2+'_'+hd+'_'+poolth
                    if method.upper() != 'IR':
                        for th in THS:
                            strategies.append(filt+'_'+th)
                    else:
                        strategies.append(filt)

                loopname = f2+"_"+hd+'_'+poolth  
                           
                #print "methods", methods
                print "A/V strategies:",strategies
                
                longPool = {} #dict of DataFrames
                shortPool = {}    
                
                poolIndicDF = DataFrame.from_csv(directory+"SP500_PoolIndicator.csv")[startDate:]
                poolIndicDF.replace(0,np.nan,inplace=True)
                
                for method in methods:
                    for filt in strategies:
                        if method == filt.split("_")[0]:
                            long_fn = filt+'_'+'long_FilterF.csv'
                            short_fn = filt+'_'+'short_FilterF.csv'
                            #print long_fn, short_fn
                            df = DataFrame.from_csv(directory+method+os.sep+long_fn)[startDate:]
                            longPool[filt] = df*poolIndicDF
                            
                            df = DataFrame.from_csv(directory+method+os.sep+short_fn)[startDate:]
                            shortPool[filt] = df*poolIndicDF                
            
                            longPool[filt].to_csv(resultDirectory+"t_afterApplPoolInd_"+long_fn)                
                            shortPool[filt].to_csv(resultDirectory+"t_afterApplPoolInd_"+short_fn)
                   
                #transform raw scores
                L_transf = {}
                S_transf = {}    
                transformation = 'AvgSimpleRank'#'AvgNormalizedRank'# #
                transform_raw_scores_2_rank(strategies,longPool,L_transf,transf_type=transformation,side="Long",out_dir=resultDirectory) 
                transform_raw_scores_2_rank(strategies,shortPool,S_transf,transf_type=transformation,side="Short",out_dir=resultDirectory)    
            
                #weigh and combine
                longMix_df = ''
                shortMix_df = ''
                for filt in strategies:
                    if type(longMix_df) != DataFrame:
                        longMix_df = L_transf[filt]/float(len(methods))
                        shortMix_df = S_transf[filt]/float(len(methods))
                    else:
                        longMix_df += L_transf[filt]/float(len(methods))
                        shortMix_df += S_transf[filt]/float(len(methods))
            
                
                longMix_df.to_csv(resultDirectory+'_'.join(methods)+'_'+transformation+"_"+loopname+"_long.csv")
                shortMix_df.to_csv(resultDirectory+'_'.join(methods)+'_'+transformation+"_"+loopname+"_short.csv")
     
