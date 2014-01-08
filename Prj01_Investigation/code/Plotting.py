'''
Created on 07/07/2013

@author: olena
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
import pandas as pd



COLORS =["#8533D6","#52A3CC","#5C5C8A","#6600FF","#5C85D6","#1963D1","#0066FF","#5C5C8A","#6666FF",]
light_COLORS = ["#FFFF99","#66CCFF","#7f7f7f","#B8E65C",]
Q_COLORS = ["#FFFF99","#1963D1","#0066FF","#B8E65C",]
short_color = "#FF3300"
long_color = "#009900"

#############################################
## auxiliary functions
#############################################

def format_legend(leg):
    try:
        for text in leg.get_texts():
            text.set_fontsize('x-small')
        for line in leg.get_lines():
            line.set_linewidth(0.7)
    except:
        pass

def add_to_scatter_plots(ax,xlabel,title):
    ax.axhline(color='#000000')
    ax.axvline(color='#000000')
    ax.set_xlabel(xlabel,fontsize=9)
    ax.tick_params(labelsize=9)
    ax.set_title(title,fontsize=10,color='blue')
    ax.grid(True)
    t_leg = ax.legend(loc='best')
    format_legend(t_leg)

def form_suptitle(suptitle,date1=None, date2=None):
    if date1 != None:
        suptitle += " for "+date1.strftime("%d/%m/%Y")
    if date2 != None:
        suptitle += " thru "+ date2.strftime("%d/%m/%Y")
    return suptitle


################################################################
## scatter plots
################################################################

def ScatterSubplots_F2vsYvar(df,stock,f2scores,QUANTILES=None,fig_fn=None,date1=None, 
                             date2=None,suptitle='',yVar='Rel Ret',ymin=None,ymax=None):

    fig, axs = plt.subplots(len(f2scores), 1, sharex=True, sharey=True)    
    fig.subplots_adjust(hspace=0.3)
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=11,color='red')    
    
    for f in range(len(f2scores)):
        title =  f2scores[f]+" vs. "+ yVar+" of "+stock.name
        if QUANTILES != None:
            strong_color = np.where((df[f2scores[f]] < df[f2scores[f]].quantile(QUANTILES[0])) | (df[f2scores[f]] > df[f2scores[f]].quantile(QUANTILES[1])), 'b','y' )
        else:
            strong_color = 'b'

        markersizes = [20 for elem in df[yVar]]
        #if "corr_Ret" in df.columns: markersizes = [45*math.pow(abs(elem),2.5) for elem in df['corr_Ret']]
        
        axs[f].scatter(df[f2scores[f]],df[yVar],marker='+',c=strong_color,label="",s=markersizes)

        if stock.OLS_Statistics_F2vsRelRet[f2scores[f]] != {}: # case when OLS for F2 has been done
            add_OLSline(axs[f],stock.OLS_Statistics_F2vsRelRet[f2scores[f]]['OLS_alpha'],
                        stock.OLS_Statistics_F2vsRelRet[f2scores[f]]['OLS_beta'],df[f2scores[f]],stock.OLS_Statistics_F2vsRelRet[f2scores[f]]['beta-pScore'])
        add_to_scatter_plots(axs[f],f2scores[f],title)
        if ymin != None:
            axs[f].axes.set_ylim(ymin,ymax)

    if fig_fn != None:
        plt.savefig(fig_fn)    
    else:
        plt.show()
    
def add_OLSline(ax,alpha,beta,X,beta_pScore):
    ax.plot(X,beta*X+alpha,label="OLS fitted Line (p="+str(round(beta_pScore,2))+")",color='#0066FF',ls=':',alpha=(1-beta_pScore))
 
   
"""
        if "corr_Ret" not in df.columns:  
            axs[f].scatter(df[f2scores[f]],df[yVar],marker='+',c=strong_color,label="",s=markersizes)            
        else:
            axs[f].scatter(df[f2scores[f]][df['corr_Ret'] > 0],df[yVar][df['corr_Ret'] > 0],marker='+',c=strong_color,label="",s=markersizes)
            axs[f].scatter(df[f2scores[f]][df['corr_Ret'] <= 0],df[yVar][df['corr_Ret'] <= 0],marker='x',c=strong_color,label="",s=markersizes)
"""    



def stacked_ScatterPlots(df,stock_name,depVARS,xVar,
                         suptitle ='',fig_fn=None,date1=None,date2=None,Quantiles=None):
   
    fig,axes = plt.subplots(nrows=len(depVARS),ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)
    
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    for f in range(len(depVARS)):  
        ax = axes[f]
        yVar = depVARS[f] 
        t_title = xVar +" vs. "+ yVar 
            
        ax.scatter(df[xVar],df[yVar],marker="+",c=COLORS[f],label="")
           
        if f == len(depVARS)-1:
            add_to_scatter_plots(ax,xVar,t_title) 
        else:
            add_to_scatter_plots(ax,'',t_title) 
    if fig_fn != None:
        plt.savefig(fig_fn)    
    else:
        plt.show() 

##############################################
### combination plots
##############################################

def overlays_TimeSeries(df,stock_name,Fscore,yVar1=None,yVar2=None,
                         suptitle ='',fig_fn=None,date1=None,date2=None,Quantiles=None,mean_per= 1,ymin=None,ymax=None,stock=None):
                   
    if yVar1 != None and yVar2 != None:
        nrows = 2
    else:
        nrows = 1
    fig,axes = plt.subplots(nrows=nrows,ncols=1,sharex=False,sharey=False)
    fig.subplots_adjust(hspace=0.25)
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    if nrows == 2:
        ax = axes[0]
    else:
        ax = axes
    #the scatter plot    
    if yVar1 != None:
        title =  Fscore+" vs. "+ yVar1 +" of "+stock.name
        if Quantiles != None:
            strong_color = np.where((df[Fscore] < df[Fscore].quantile(Quantiles[0])) | (df[Fscore] > df[Fscore].quantile(Quantiles[1])), 'b','y' )
        else:
            strong_color = 'b'
     
        ax.scatter(df[Fscore],df[yVar1],marker='+',c=strong_color,label="")
    
        if stock != None and stock.OLS_Statistics_F2vsRelRet[Fscore] != {}: # case when OLS for F2 has been done
            add_OLSline(ax,stock.OLS_Statistics_F2vsRelRet[Fscore]['OLS_alpha'],
                            stock.OLS_Statistics_F2vsRelRet[Fscore]['OLS_beta'],df[Fscore],stock.OLS_Statistics_F2vsRelRet[Fscore]['beta-pScore'])
        add_to_scatter_plots(ax,Fscore,title)
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)

    if nrows == 2:
        ax = axes[1]     

    #time series to plot   
    if yVar2 != None:
        t_title = yVar2 
        df[t_title].plot(kind='line',color=COLORS[0],label=t_title,ax=ax,alpha=0.9) #ax.scatter(df.index, df[t_title],marker='x',c=COLORS[f],label=t_title) #   
        pd.rolling_mean(df[t_title],mean_per).plot(color=COLORS[0],ax=ax,alpha=0.75,linewidth=3,label=str(mean_per)+"D rolling mean") #ls=':'
        
        Q01 = df[Fscore].quantile(Quantiles[0])
        Q90 = df[Fscore].quantile(Quantiles[1])
        for i in range(len(df[Fscore])):
            if df[Fscore][i] <= Q01:
                ax.axvline(x=df[Fscore].index[i], color='g')
            if  df[Fscore][i] >= Q90:
                ax.axvline(x=df[Fscore].index[i], color='r')
    
        format_plot(ax,"Date",t_title)        
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)

            
    #plots finished
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()     


###############################################
####### for time series #######################
###############################################
   

def format_plot(ax,x_label,title,display_title=False):
    ax.set_xlabel(x_label,fontsize=9)
    ax.axhline(color='#000000')
    t_leg = ax.legend(loc='best')
    format_legend(t_leg)
    ax.tick_params(labelsize=8)
    if display_title:
        ax.set_title(title,color='blue',fontsize=9)
        

    
def subplots_TimeSeries(df,stock,f2scores,yVar="RelRet",date1=None, date2=None,suptitle = '',fig_fn=None):

    fig,axes = plt.subplots(nrows=2,ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.2)

    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    ax = axes[0]
    t_title = yVar
    df[yVar].plot(style='g+-',label=t_title,ax=ax)
    format_plot(ax,"Date",t_title)

    ax = axes[1]
    for f in range(len(f2scores)):       
        t_title = f2scores[f] 
        df[f2scores[f]].plot(kind='line',color=COLORS[f],label=t_title,ax=ax,alpha=0.8)
    format_plot(ax,"Date",t_title)        

    if fig_fn != None:
        plt.savefig(fig_fn)    
    else:
        plt.show()       

  

def stacked_TimeSeries(df,stock_name,VARS,
                         suptitle ='',fig_fn=None,date1=None,date2=None,Quantiles=None,mean_per= 1,ymin=None,ymax=None):
                             #for most stacked graphs enforce ymin=ymax=None as different scales apply
    fig,axes = plt.subplots(nrows=len(VARS),ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)
    #fig.set_size_inches(25.5,20.5)
    
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    for f in range(len(VARS)):  
        if len(VARS) == 1:
            ax = axes
        else:
            ax = axes[f]
        t_title = VARS[f] 
        df[t_title].plot(kind='line',color=COLORS[f],label=t_title,ax=ax,alpha=0.9)
        if mean_per > 1:
            pd.rolling_mean(df[t_title],mean_per).plot(color='blue',ax=ax,alpha=0.75/len(VARS),linewidth=3/float(len(VARS)),label=str(mean_per)+" rolling mean") #ls=':'
        if Quantiles != None:
            ax.axhline(y=df[t_title].quantile(Quantiles[0]),color="#A3CC29")
            ax.axhline(y=df[t_title].quantile(Quantiles[1]),color="#A3CC29")
        if f == len(VARS)-1:
            format_plot(ax,"Date",t_title)        
        else:
            format_plot(ax,"",t_title) 
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)
            
                  
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()         




                             
#########################################
### histograms
#########################################    
def subplots_histograms(df,stock,f2scores,date1=None, date2=None):
    fig,axes = plt.subplots(nrows=2,ncols=1,sharex=True,sharey=True)
    fig.subplots_adjust(hspace=0.3)

    suptitle = stock.name
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,color="#FF3300",fontsize=12,fontweight='bold')
    
    for f in range(len(f2scores)):
        ax = axes[f]        
        t_title = "Distribution of "+ f2scores[f] 
        df[f2scores[f]].hist(bins=100,color=COLORS[f],label=t_title,ax=ax)
        ax.set_title(t_title,color=COLORS[f],fontsize=9,fontweight='bold')
        ax.set_xlabel(f2scores[f],fontsize=9)
        ax.set_ylabel('Frequency',fontsize=9)
        ax.tick_params(labelsize=9)
  
def stacked_histograms(df,stock_name,VARS,
                         suptitle ='',fig_fn=None,date1=None,date2=None):
    fig,axes = plt.subplots(nrows=len(VARS),ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)
    #fig.set_size_inches(25.5,20.5)
    
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    for f in range(len(VARS)):  
        if len(VARS) == 1:
            ax = axes
        else:
            ax = axes[f]
        var = VARS[f]
        t_title = "Distribution of "+var
        df[var].hist(bins=100,color=COLORS[f],label=t_title,ax=ax)
        ax.axvline(x=df[var].quantile(0.5),linewidth=4, color='r')
        ax.set_title(t_title,color=COLORS[f],fontsize=9,fontweight='bold')
        ax.set_xlabel(var,fontsize=9)
        ax.set_ylabel('Frequency',fontsize=9)
        ax.tick_params(labelsize=9)                 
    
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()         
    
    
#######################################################################    
####   Work in progress               ########## 
####################################################################### 

#####################################################
### some old working functions to keep for right now   
#####################################################  

def ScatterSubplots_F2vsYvar_multipleStocks(DF,Stocks,f2scores,QUANTILES=None,fig_fn=None,
                                            date1=None, date2=None,suptitle='', yVar ='Rel Ret'):
    """this function is not useful if there are many differnt Stocks to compare, but 2-4 are ok"""    
    fig, axs = plt.subplots( len(f2scores),len(Stocks), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.3)

    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color='red') 
    
    for s in range(len(Stocks)):
        stock = Stocks[s]
        df = DF[s]
        for f in range(len(f2scores)):
            title =  f2scores[f]+" vs. "+ yVar+" of "+stock.name
            if QUANTILES != None:
                strong_color = np.where((df[f2scores[f]] < df[f2scores[f]].quantile(QUANTILES[0])) | (df[f2scores[f]] > df[f2scores[f]].quantile(QUANTILES[1])), 'b','y' )
            else:
                strong_color = 'b'
            
            axs[f,s].scatter(df[f2scores[f]],df[yVar],marker='+',c=strong_color,label="")
            add_to_scatter_plots(axs[f,s],f2scores[f],title)
    
    if fig_fn != None:
        plt.savefig(fig_fn)    
    else:
        plt.show()  
        

            

####################################################    
def plotting1(df,stock):
    fig = plt.figure(num=None,figsize=(9,6),)
    fig.subplots_adjust(hspace=0.3)
    ax1 = fig.add_subplot(2,1,1)
    
    Pax1 = ax1.plot(df["IBM F2"],(df["IBM Ret"]-df["Pool Ret"]).shift(-2),color='#3eb677',marker='+',linestyle='')
    ax1.axhline(color='#FFF333')
    #ax1.axes.get_xaxis().set_visible(False) #will make gridlines disappear too
    #ax1.axes.get_xaxis().set_ticks([]) #will make gridlines disappear too
    #ax1.axis('off') #use this only if unless for some reason no coordinates are necessary, don't bother using this
    ax1.axes.xaxis.set_ticklabels([])
   
    ax1t="Relationship between F2 and Excess Ret of "+stock.name
    ax1.set_title(ax1t,fontsize=12,color='#000000')
    ax1.set_ylabel('Excess Return')

    #ax1.scatter(df["IBM F2"],(df["IBM Ret"]-df["Pool Ret"]).shift(-2),c='r',marker='+',label="F2 vs. Excess Ret")
    ax1.grid(True)
    

    ax2 = fig.add_subplot(2,1,2)
    ax2.scatter(df["IBM F2"],(df["IBM Ret"]).shift(-2),c='b',marker='+')
    ax2.axhline(color='#FFF333')
    #ax2.axes.xaxis.set_ticklabels([])
    ax2.set_ylabel("Earning Return of "+stock.name)
    ax2.grid(True)
    fig_name = stock.name+".jpg"
    plt.savefig(fig_name)
    #plt.show()
        

    

    
