# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 14:15:28 2013

@author: olenag
"""

import os
from datetime import datetime

import functions_compareNmix

if __name__=="__main__":

    startDate = datetime(2010,1,1)   #2005,2,1  
    DATA_DIR = ".."+os.sep+'data'+os.sep+"mix_portfolios"+os.sep
    out_dir_name = "PorfolioMix"
    
    portf2combine = []

    resultDirectory = ".."+os.sep+'outputs_'+out_dir_name+os.sep 
    if not os.path.exists(resultDirectory):
        os.makedirs(resultDirectory)

    if portf2combine == []:
        for direc in os.listdir(DATA_DIR):
            if os.path.isdir(DATA_DIR+direc):
                portf2combine.append(direc)
                
    print portf2combine                

    logF = open("log_"+datetime.now().strftime("%Y%m%d_%H%M")+"compPortf.csv",'w')
    logF.write("from "+startDate.strftime("%d/%m/%Y")+",,LONG,,,SHORT"+"\n"+"strategy 1,strategy 2, max num of positions in combined Portf, min num of positions in combined Portf,avg num of positions in combined Portf,max num of positions in combined Portf, min num of positions in combined Portf,avg num of positions in combined Portf"+"\n")
  
    for d1 in range(len(portf2combine)):
        for d2 in range(d1+1,len(portf2combine)):
            #print portf2combine[d1],portf2combine[d2]
            for f1 in os.listdir(DATA_DIR+portf2combine[d1]+os.sep):
                for f2 in os.listdir(DATA_DIR+portf2combine[d2]+os.sep):
                    print f1, f2
                    fn1 = DATA_DIR+portf2combine[d1]+os.sep+f1
                    fn2 = DATA_DIR+portf2combine[d2]+os.sep+f2
                    if os.path.isfile(fn1) and os.path.isfile(fn2):
                        functions_compareNmix.compare_2_holdings(fn1,fn2,resultDirectory,startDate,log =logF)

    logF.close()