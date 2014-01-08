# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 08:12:58 2013

@author: olenag
"""

import os
from datetime import datetime

import functions_compareNmix

if __name__=="__main__":

    startDate = datetime(2010,1,1)   #2005,2,1  
    DATA_DIR = ".."+os.sep+'data'+os.sep+"mix_portfolios"+os.sep
    OUT_DIR_name = "tmp"
    
#    portf2combine = []
#    if portf2combine == []:
#        for direc in os.listdir(DATA_DIR):
#            print direc
#            if os.path.isdir(DATA_DIR+direc):
#                portf2combine.append(direc)
#                
#    print portf2combine                
#    
#    for d1 in range(len(portf2combine)):
#        for d2 in range(d1+1,len(portf2combine)):
#            print portf2combine[d1],portf2combine[d2]
    
    fn1 = DATA_DIR+"holdings_MUD_IR_F2S_F(6)_PS200_HD5_30L_B0.csv"
    fn2 = DATA_DIR+"holdings_IR_F2S_F(8)_PS200_HD3_45L_B0.csv"    
    resultDirectory = ".."+os.sep+'outputs_'+OUT_DIR_name+os.sep 
    if not os.path.exists(resultDirectory):
        os.makedirs(resultDirectory)

    logF = open("log_tmp_"+datetime.now().strftime("%Y%m%d_%H%M")+"compPortf.csv",'w')
    logF.write("from "+startDate.strftime("%d/%m/%Y")+",,LONG,,,SHORT"+"\n"+"strategy 1,strategy 2, max num of positions in combined Portf, min num of positions in combined Portf,avg num of positions in combined Portf,max num of positions in combined Portf, min num of positions in combined Portf,avg num of positions in combined Portf"+"\n")
    functions_compareNmix.compare_2_holdings(fn1,fn2,resultDirectory,startDate,log = logF)
    logF.close()