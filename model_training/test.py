import pandas as pd
import numpy as np
import pickle as pkl

# Load the test data
test_data = pd.read_csv("test.csv")

# Load the trained Decision Tree model
loaded_model = pkl.load(open("Decision_tree_model.sav", 'rb'))

# Predict dyslexia for each row in the test data
predictions = loaded_model.predict(test_data.drop("presence_of_dyslexia", axis=1))

# Add the predictions to the test data
test_data["predicted_dyslexia"] = np.where(predictions == 1, "Yes", "No")

# Print the test data with predicted dyslexia
print(test_data)
