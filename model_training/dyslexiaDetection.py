import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import pickle as pkl
import m2cgen

train_data = pd.read_csv("train.csv")
test_data = pd.read_csv("test.csv")
train_data.head()

x_train = train_data.drop(["presence_of_dyslexia"], axis= "columns")
x_test = test_data.drop(["presence_of_dyslexia"], axis= "columns")
y_train = train_data.presence_of_dyslexia
y_test = test_data.presence_of_dyslexia

model_logistic = LogisticRegression()
model_logistic.fit(x_train, y_train)
print(model_logistic.score(x_test, y_test))
print(model_logistic.score(x_train,y_train))

sns.heatmap(confusion_matrix(model_logistic.predict(x_test), y_test), annot=True)

sns.heatmap(confusion_matrix(model_logistic.predict(x_train), y_train), annot=True)

model_DT = DecisionTreeClassifier()
model_DT.fit(x_train, y_train)

print(model_DT.score(x_test, y_test))
print(model_DT.score(x_train, y_train))

sns.heatmap(confusion_matrix(model_DT.predict(x_test), y_test), annot=True)

sns.heatmap(confusion_matrix(model_DT.predict(x_train), y_train), annot=True)

model_svc_linear = SVC(kernel = 'linear',gamma = 'scale', shrinking = False,)
model_svc_linear.fit(x_train, y_train)

print(model_svc_linear.score(x_test, y_test))
print(model_svc_linear.score(x_train, y_train))

pkl.dump(model_DT, open("Decision_tree_model.sav", 'wb'))

# print("model exported done")