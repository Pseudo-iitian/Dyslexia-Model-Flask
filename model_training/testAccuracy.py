import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import pickle as pkl
import m2cgen

# Load the test data
test_data = pd.read_csv("test.csv")

# Extract features and target from the test data
x_test = test_data.drop(["presence_of_dyslexia"], axis="columns")
y_test = test_data["presence_of_dyslexia"]

# Load the trained Decision Tree model
loaded_model = pkl.load(open("Decision_tree_model.sav", 'rb'))

# Evaluate the model on the test data
print("Decision Tree Model Performance:")
print("Test Accuracy:", loaded_model.score(x_test, y_test))

# Generate confusion matrix for the test data
sns.heatmap(confusion_matrix(loaded_model.predict(x_test), y_test), annot=True)
