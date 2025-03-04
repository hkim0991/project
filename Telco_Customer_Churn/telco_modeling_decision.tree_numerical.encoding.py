# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 12:15:11 2018

@author: kimi
"""

# Import libraries & funtions ------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

print(os.getcwd())
os.chdir('C:/Users/202-22/Documents/Python - Hyesu/Project/telco')
#os.chdir('D:/Data/Python/project')


# Load dataset ----------------------------------------------------------------
train_path = "../data/telco/telco_data_preprocessing.csv"

train = pd.read_csv(train_path, engine='python')

train.shape # 7043 x 21
train.head()
train.info()
train.isnull().sum() # no missing value now*
train.describe()  # the type of feature 'SeniorCitizen' is still in integer format

# 20 predictor variables and 1 target variable('Churn')
train['Churn'].value_counts() # no:5174, yes:1869


# Feature conversion ----------------------------------------------------------
# Although the type of feature for 'SeniorCitizen' has been changed, it still remains as numerical type 
# therefore, features 'SeniorCitizen' should be changed to categorial feature*

## 1. continous to categorical - SeniorCitizen
for col in ['SeniorCitizen']:
    train[col] = train[col].astype('object')

train.info()
train.isnull().sum()  
train.describe() # 3 numerical features: tenure, MonthlyChargees, & TotalCharges


# Modeling - Decision Tree Classification -------------------------------------
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_tr, X_va, y_tr, y_va = train_test_split(X_train, y_train, test_size=0.3, random_state=0)
print(X_tr.shape, y_tr.shape)
print(X_va.shape, y_va.shape)

tree = DecisionTreeClassifier(random_state=0)
tree.fit(X_tr, y_tr) 
# !! ISSUE !!: this model only consider numerical categorical featutres as categorical features.


# Solution 1 - Numeric encoding -----------------------------------------------
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline

category = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService',
            'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
            'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
            'Contract', 'PaperlessBilling', 'PaymentMethod']

cat_data = pd.DataFrame(data=train, columns=category)

# In order to make thing simple, convert 'SeniorCitizen' feature type from the integer-based to string-based type
cat_data['SeniorCitizen'] = np.where(cat_data['SeniorCitizen']==0, 'No', 'Yes')

cat_data.head()


## Load a function : MultiColumnLabelEncoder ----------------------------------
class MultiColumnLabelEncoder:
    def __init__(self,columns = None):
        self.columns = columns # array of column names to encode

    def fit(self,X,y=None):
        return self # not relevant here

    def transform(self,X):
        '''
        Transforms columns of X specified in self.columns using
        LabelEncoder(). If no columns specified, transforms all
        columns in X.
        '''
        output = X.copy()
        if self.columns is not None:
            for col in self.columns:
                output[col] = LabelEncoder().fit_transform(output[col])
        else:
            for colname,col in output.iteritems():
                output[colname] = LabelEncoder().fit_transform(col)
        return output

    def fit_transform(self,X,y=None):
        return self.fit(X,y).transform(X)

# reference: https://stackoverflow.com/questions/24458645/label-encoding-across-multiple-columns-in-scikit-learn


# Numerical Encoding ----------------------------------------------------------
encoded_cat = MultiColumnLabelEncoder(columns = category).fit_transform(cat_data)
encoded_cat.head()

for i in category:
    print("Frequency table for", i, "\n", encoded_cat[i].value_counts(), "\n")


# Back to Modeling - Decision Tree Classification -----------------------------
# data combination: encoded categorical features + continuous features

continous = ['tenure', 'MonthlyCharges', 'TotalCharges']
cond_data = pd.DataFrame(data=train, columns= continous)

final_data = pd.concat([cond_data, encoded_cat], axis=1)
final_data.head()
final_data.info()
final_data.isnull().sum()


# Train/Test data partition ---------------------------------------------------

X_train = final_data
y_train = train['Churn']

X_tr, X_va, y_tr, y_va = train_test_split(X_train, y_train, test_size=0.3, random_state=0)
print(X_tr.shape, y_tr.shape) # 1930 x 19
print(X_va.shape, y_va.shape) # 2113 x 19


# Modeling - Decision Tree Classification -------------------------------------

tree = DecisionTreeClassifier(random_state=0)
tree.fit(X_tr, y_tr)

print("train data accuracy: {:.3f}".format(tree.score(X_tr, y_tr))) # 0.997
print("test data accuracy: {:.3f}".format(tree.score(X_va, y_va)))  # 0.730 -> overfitting


# Decision Tree visualization

 #!pip install graphviz 
 #!pip install pydotplus 
 # Let's not forget to add the path of graphviz to PATH in environment variables 
 # Then, restart your Python IDE

from sklearn.tree import export_graphviz
from IPython.display import Image
from graphviz import Source
import pydotplus
import graphviz

data_feature_names = final_data.columns.values.tolist()

dot_data = export_graphviz(tree, out_file=None, 
                           feature_names= data_feature_names,
                           class_names='Churn')

graph = Source(dot_data)
png_bytes = graph.pipe(format='jpg')
with open ('dtree_pipe1.jpg', 'wb') as f:
    f.write(png_bytes)
    
Image(png_bytes1)

#graph = pydotplus.graph_from_dot_data(dot_data)
#Image(graph.create_png())


# Model tuning - Decision Tree Classification 
tree2 = DecisionTreeClassifier(max_depth= 10,  # original model : 25
                               max_leaf_nodes=50,
                               # max_features = 10,
                               min_samples_leaf = 3,
                               random_state=0)
tree2.fit(X_tr, y_tr)

print("train data accuracy: {:.3f}".format(tree2.score(X_tr, y_tr))) # 0.831
print("test data accuracy: {:.3f}".format(tree2.score(X_va, y_va)))  # 0.790


dot_data2 = export_graphviz(tree2, out_file=None, 
                           feature_names = data_feature_names,
                           class_names='Churn')

graph = Source(dot_data2)
png_bytes2 = graph.pipe(format='png')
with open ('dtree_pipe.png', 'wb') as f:
    f.write(png_bytes2)
    
Image(png_bytes2)


# Feature importance ----------------------------------------------------------
print("feature importance:\n{}".format(tree2.feature_importances_)) 

def plot_feature_importances_telco(model):
    n_features = final_data.shape[1]
    plt.barh(range(n_features), model.feature_importances_, align='center')
    plt.yticks(np.arange(n_features), final_data.columns)
    plt.xlabel("feature importance")
    plt.ylabel('features')
    plt.ylim(-1, n_features)

fig = plt.figure(figsize=(10,8))
plot_feature_importances_telco(tree)


## find out the most highest accuracy for test dataset ------------------------
max=0; numMax= 0; cnt= 0
l1 = []
lni = []
lnr = []
for i in range(7, 20):
    for j in range(30, 51):
        for n in range(2, 6, 1):
            print("trial #:", cnt, "\n", "max_depth: ", i, "| max_leaf_nodes: ", j, "| min_samples_leaf: ", n)
            tree = DecisionTreeClassifier(max_depth = i,  # original model : 25
                               max_leaf_nodes = j,
                               min_samples_leaf = n,
                               random_state=0)
            tree.fit(X_tr, y_tr)
            treetest = tree.score(X_va, y_va)
            print("train data accuracy: {:.3f}".format(tree.score(X_tr, y_tr))) 
            print("test data accuracy: {:.3f}".format(tree.score(X_va, y_va)))
            lni.append(tree.score(X_tr, y_tr))
            lnr.append(tree.score(X_va, y_va))
            cnt += 1
            l1.append(cnt)
            if max < treetest:
                max = treetest
                numMax = cnt

    
print(max, numMax)


# Ploting the results ---------------------------------------------------------
fig = plt.figure(figsize=(12,8))
plt.plot(lni, "--", label="train set", color="blue")
plt.plot(lnr, "-", label="test set", color="red")
plt.plot(numMax, max, "o")
ann = plt.annotate("is" % str(n))
plt.legend()
plt.show()

# trial #: 166 
# max_depth:  7 | max_leaf_nodes:  31 | min_samples_leaf:  4
# train data accuracy: 0.819
# test data accuracy: 0.795


tree_final = DecisionTreeClassifier(max_depth=7,  
                               max_leaf_nodes= 31, 
                               min_samples_leaf = 4,
                               random_state=0)
tree_final.fit(X_tr, y_tr)

print("train data accuracy: {:.3f}".format(tree_final.score(X_tr, y_tr))) # 0.819
print("test data accuracy: {:.3f}".format(tree_final.score(X_va, y_va)))  # 0.795


# Decision Tree Model Visualization after tuning ------------------------------
dot_data3 = export_graphviz(tree_final, out_file=None, 
                           feature_names = data_feature_names,
                           class_names='Churn')

graph = Source(dot_data3)
png_bytes = graph.pipe(format='png')
with open ('dtree_pipe_final.png', 'wb') as f:
    f.write(png_bytes)
    
Image(png_bytes)


# Feature importance ----------------------------------------------------------

fig = plt.figure(figsize=(10,8))
plot_feature_importances_telco(tree_final)
