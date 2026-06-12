# import tensorflow as tf
import tkinter

# #from claude AI VVVV
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# # ^^^^

import csv
import math
import numpy as np
import os.path as osPath
import sklearn as sklearn
from pathlib import Path as path


# I saw your note. This worked with a few minor tweaks
training_path = ""
testing_path = ""

def findFiles():
    working_dir = path.cwd()
    working_dir = working_dir.parent.as_posix() + "/Data_Collection_and_Formatting"
    if(osPath.exists(working_dir)):
        training_path = working_dir + "/training"
    else:
        print("No training path exists")
    if(osPath.exists(working_dir)):
        testing_path = working_dir + "/testing"
    else:
        print("No testing path exists")
    return training_path, testing_path
training_path, testing_path = findFiles()

# Rounds data out to be proportionately between 0 and 1 with floating point accuracy
def normalize(value, min_value, max_value):
    normalized_value = ((math.log(1.0 + value) - math.log(1.0 + min_value)) / (math.log(1.0 + max_value) - math.log(1.0 + min_value)))
    return normalized_value

# Not sure what you did here, but it works
print("\nSelect a file to use for training the model.\n")
paths = path.rglob(path(training_path), "*.csv")
paths_list = tuple(paths)
num = 0
for x in paths_list:
    print(str(num) + ": " + str(x))
    num += 1

num = int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))
selected_training_path = paths_list[num]

paths = path.rglob(path(testing_path), "*.csv")
paths_list = tuple(paths)
selected_testing_path = paths_list[num]

# Initialize input and output arrays
X, y = [],[]
correct_answers = []

max_y, max_x = 0.0, 0.0     # These need to start low so everything is higher than them
min_y, min_x = 999.0, 999.0 # These need to start high so everything is lower than them

# We need to keep track of these so we know which lines we use later for testing
row_number = 0
rows_visited = []

# --------------
# Begin training
# --------------
with open(selected_training_path) as train:
    filereader = csv.reader(train)
    
    row_n = 0
    for row in filereader:
        rows_visited.append(row_number)
        X.append([float(row[0]), float(row[1]), float(row[2]), float(row[3])]) # Given the first 3 columns

        # Calculate normalized percentage of republican and democrat votes returned
        if float(row[3]) != 0.0 and int(row[2]) != 0: # Skip and auto-set to 0 if there is no population in this block
            total_share = float(row[4]) + float(row[5]) # Total up vote share
            r_percent = float(row[4]) / float(total_share) # Calculate republican share
            d_percent = float(row[5]) / float(total_share) # Calculate democrat share
            y.append(d_percent) # Predict the 6th column (5th column is just [1.0 - 4th_column])
        else:
            r_percent = 0
            d_percent = 0
            y.append(d_percent)
        correct_answers.append([float(r_percent), float(d_percent)])

        # Storing min and max X and Y values this way greatly increases performance rather
        # than using built in functions to find the min and max of the whole array after it's built
        if float(row[5]) > max_y:
            max_y = float(row[5])
        if float(row[5]) < min_y:
            min_y = float(row[5]) if float(row[5]) != 0 else min_y

        if float(row[2]) > max_x:
            max_x = float(row[2])
        if float(row[2]) < min_x:
            min_x = float(row[2]) if float(row[2]) != 0 else min_x

        # # This skips lines randomly (but never 5 times in a row)
        # jumper = np.random.randint(0,4)
        # for _ in range(jumper):
        #     try:
        #         filereader.__next__()
        #     except StopIteration:
        #         break
        # row_number += jumper + 1 # Include random jump and this line to row number

    # Normalize our Population and Predicted Democrat Values for statistical stability
    normalized_x = []
    for _ in X:
        if _[2] == 0: # Ignore if 0 population
            break
        else:
            _[2] = math.log(1+_[2]) # Normalize population
        if _[3] == 0: # Ignore if 0 votes
            break
        else:
            _[3] = math.log(1+_[3]) # Normalize vote count
        
    
    # # This loop scheme greatly increases perfomance at the cost of being ugly
    # line = 0
    # for _ in X:
    #     _[2] = normalized_x[line]
    #     line += 1

# Similar casing added for redundancy and east of use for people with different typing styles.
# If we find this unnecessary, we can remove it later
training_kernel = ""
while training_kernel.lower() not in ["linear", "rbf", "poly", "sigmoid"]:
    training_kernel = input("\nSelect a kernel for the SVM model\n- linear (somewhat fast but less accurate)\n- rbf (terribly slow, generally more accuracy)\n- poly (fairly quick, much less accurate) \n- sigmoid (no)\n")

print("\nTraining model... This might take a really long time!\n")
print("Note: results might look the same twice with only a few small differences.\n")

# Define the model and its characteristics
prediction_model = None
if training_kernel.lower() == 'linear':
    prediction_model = sklearn.pipeline.Pipeline([
        ('scaler', sklearn.preprocessing.StandardScaler()), # This scales everything to within significantly narrow range
        ('svm',    sklearn.svm.LinearSVR(loss='squared_epsilon_insensitive', C=1000, epsilon=0.1))
    ])
elif training_kernel.lower() == 'poly':
    prediction_model = sklearn.pipeline.Pipeline([
        ('scaler', sklearn.preprocessing.StandardScaler()), # This scales everything to within significantly narrow range
        ('poly_approx', sklearn.kernel_approximation.PolynomialCountSketch(degree=8, n_components=300, gamma=0.2)),
        ('sgd', sklearn.linear_model.SGDRegressor())
    ])
else:
    prediction_model = sklearn.pipeline.Pipeline([
        ('scaler', sklearn.preprocessing.StandardScaler()), # This scales everything to within significantly narrow range
        ('svm',    sklearn.svm.SVR(kernel=training_kernel.lower(), C=1.5, gamma='scale'))
    ])

prediction_model.fit(X, y) # Train model

print("Model Trained!\nTesting its accuracy now...\n")

with open(selected_testing_path) as test:
    filereader = csv.reader(test)
    line = 0
    correct_index = 0 # This tracks the index of the correct_answers array instead of the line number

    democrats = 0.0
    republicans = 0.0
    for row in filereader:
        # if line in rows_visited:
        if float(row[2]) == 0.0: # This is used to breeze past areas with 0 population
            republicans = 0.0
            democrats = 0.0
        else:
            democrats = prediction_model.predict([[float(row[0]), float(row[1]), float(row[2]), float(row[3])]])
            republicans = 1.0 - democrats
        if type(democrats) == np.ndarray:
            print(f"Predicted Vote Shares: {republicans[0]*100:.2f}% Republican | {democrats[0]*100:.2f}% Democrat | Actual Vote Shares: {correct_answers[correct_index][0]*100:.2f}% Republican | {correct_answers[correct_index][1]*100:.2f}% Democrat")
        else:
            print(f"Predicted Vote Shares: {republicans*100:.2f}% Republican | {democrats*100:.2f}% Democrat | Actual Vote Shares: {correct_answers[correct_index][0]*100:.2f}% Republican | {correct_answers[correct_index][1]*100:.2f}% Democrat")
        correct_index += 1
        line += 1

