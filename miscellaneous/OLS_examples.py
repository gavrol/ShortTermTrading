# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 10:44:58 2013

@author: olenag
"""

import numpy as np
import scikits.statsmodels.api as sm

a = np.array([[.001,.05,-.003,.014,.035,-.01,.032,-.0013,.0224,.005],[-.011,.012,.0013,.014,-.0015,.019,-.032,.013,-.04,-.05608],
 [.0021,.02,-.023,.0024,.025,-.081,.032,-.0513,.00014,-.00015],[.001,.02,-.003,.014,.035,-.001,.032,-.003,.0224,-.005],
 [.0021,-.002,-.023,.0024,.025,.01,.032,-.0513,.00014,-.00015],[-.0311,.012,.0013,.014,-.0015,.019,-.032,.013,-.014,-.008],
 [.001,.02,-.0203,.014,.035,-.001,.00032,-.0013,.0224,.05],[.0021,-.022,-.0213,.0024,.025,.081,.032,.05313,.00014,-.00015],
 [-.01331,.012,.0013,.014,.01015,.019,-.032,.013,-.014,-.012208],[.01021,-.022,-.023,.0024,.025,.081,.032,.0513,.00014,-.020015]])

y = a[:, 0]
x = a[:, 1:]
results = sm.OLS(y, x).fit()
print results.summary()

import pylab
import numpy as np
import statsmodels.api as sm

x = np.arange(-10, 10)
x1 =np.arange(-10, 10)
y = 2*x + np.random.normal(size=len(x))

# model matrix with intercept
X = sm.add_constant(a)

# least squares fit
model = sm.OLS(y, X)
fit = model.fit()

print fit.summary()

pylab.scatter(x, y)
pylab.plot(x, fit.fittedvalues)

##############################################

import numpy as np
import statsmodels.api as sm

# Generate artificial data (2 regressors + constant)
nobs = 10
X = np.random.random((nobs, 2))
X = sm.add_constant(X)
beta = [1, .1, .5]
e = np.random.random(nobs)
y = np.dot(X, beta) + e

# Fit regression model
results = sm.OLS(y, X).fit()

# Inspect the results
print results.summary()


##########################
from urllib2 import urlopen
import numpy as np
import pandas
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import interaction_plot, abline_plot

import statsmodels
from scipy import stats

try:
     kidney_table = pandas.read_csv('kidney.csv')
except:
     url = 'http://stats191.stanford.edu/data/kidney.table'
     #the next line is not necessary with recent version of pandas
     url = urlopen(url)
     kidney_table = pandas.read_table(url, delimiter=" *")

kidney_table = pandas.read_csv('kidney.csv')
print kidney_table.groupby(['Weight', 'Duration']).size()

kt = kidney_table
interaction_plot(kt['Weight'], kt['Duration'], np.log(kt['Days'] + 1),
                   colors=['red', 'blue'], markers=['D', '^'], ms=10, ax=plt.gca())

stats.f_oneway(kt['Weight'],kt['Duration'])                   
kt['const'] = 1
kt.head(5)
kt["Weight*Duration"] = kt['Weight']*kt['Duration']
kt.head(5)
xVnames =['const',"Weight","Duration","Weight*Duration"]
kt["log(Days)"] = np.log(kt['Days']+1)
kt.head(20)
yVar = kt["log(Days)"]
yVar1 =kt['Days']
mod1a = sm.OLS(yVar1,kt[xVnames]).fit() 
mod1 = sm.OLS(kt['Days'],kt[xVnames]).fit()
mod2 = sm.OLS(yVar,kt[xVnames]).fit()
print mod1.summary()



########################################
from urllib2 import urlopen
import numpy as np
from scipy import stats
import statsmodels.api as sm


data = pandas.read_csv("lgtrans.csv")
print data.female.unique()
data['female'] = data.female.replace(dict(male=0, female=1))
data[['math', 'read']] = np.log(data[['math', 'read']])
data['const'] = 1 # sm.add_constant(data)
y_name = 'write'
x_name = ['const', 'female', 'math', 'read']
test_scores = sm.OLS(data[y_name], data[x_name]).fit()


############## logistic regression #####
from datetime import datetime
import numpy as np
import pylab as pl
from sklearn import linear_model
from sklearn import datasets
from sklearn.svm import l1_min_c

iris = datasets.load_iris()
X = iris.data
y = iris.target

X = X[y != 2]
y = y[y != 2]
X -= np.mean(X, 0)

cs = l1_min_c(X, y, loss='log') * np.logspace(0, 3)


print("Computing regularization path ...")
start = datetime.now()
clf = linear_model.LogisticRegression(C=1.0, penalty='l1', tol=1e-6)
coefs_ = []
for c in cs:
    clf.set_params(C=c)
    clf.fit(X, y)
    coefs_.append(clf.coef_.ravel().copy())
print("This took ", datetime.now() - start)

coefs_ = np.array(coefs_)
pl.plot(np.log10(cs), coefs_)
ymin, ymax = pl.ylim()
pl.xlabel('log(C)')
pl.ylabel('Coefficients')
pl.title('Logistic Regression Path')
pl.axis('tight')
pl.show()