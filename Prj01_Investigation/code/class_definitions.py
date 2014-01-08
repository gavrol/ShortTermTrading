'''
Created on 07/07/2013

@author: olena
'''

class STOCK:
    def __init__(self,name):
        self.name = name
        self.df = None #dataframe for this stock
        self.OLS_Statistics_F2vsRelRet = {} #holds ordinary least quares reg statistics per each F2score examined 
        
        """OLS_Statistics_F2vsRelRet has the following keys: OLS_alpha,alpha-pScore,OLS_beta,beta-pScore,number_of_observations,AIC"""