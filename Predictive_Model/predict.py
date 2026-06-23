import csv

import numpy as np
import os.path as osPath
import sklearn as sklearn
from pathlib import Path as path

# ----------------------------------------------------------------------- #
# - findFiles() detects the training and testing folders on your system - #
# - this requires you to have run format_file.py first                  - #
# ----------------------------------------------------------------------- #
def findFiles():
    working_dir = path.cwd() # Get current file path
    working_dir = working_dir.as_posix() # Modify for navigation

    # If the previous folder exists on the computer already, add the training and testing folders
    if(osPath.exists(working_dir)):
        training_path = working_dir + "/Data_Collection_and_Formatting/training"
    else:
        print("No training path exists")
    if(osPath.exists(working_dir)):
        testing_path = working_dir + "/Data_Collection_and_Formatting/testing"
    else:
        print("No testing path exists")
    return training_path, testing_path

def Predict():
    training_path = ""
    testing_path = ""
    training_path, testing_path = findFiles() # Grab the training and testing folders

    # Use the detected file paths from above to grab the training and testing CSV files for our model
    print("\nSelect a file to use for training the model.\n")
    paths = path.rglob(path(training_path), "*.csv")
    paths_list = tuple(paths)
    num = 0
    for x in paths_list:
        print(str(num) + ": " + str(x)[-33:])
        num += 1

    # Let the use select which training and testing file to use
    num = -1
    while num < 0 or num > paths_list.__len__():
        num = int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))
    selected_training_path = paths_list[num]

    paths = path.rglob(path(testing_path), "*.csv") # <-- Automatically select the testing file based on training
    paths_list = tuple(paths)
    selected_testing_path = paths_list[num]

    # Initialize input and output arrays
    X, y = [],[]
    correct_answers = [] # <-- this just shows the real vote shares during training

    max_y, max_x = 0.0, 0.0         # These need to start low so everything is higher than them
    min_y, min_x = 99999.0, 99999.0 # These need to start high so everything is lower than them

    # --------------
    # Begin training
    # --------------
    with open(selected_training_path) as train:
        filereader = csv.reader(train)
        
        # Collect all the proper vote shares already existing in the data (includes zero'd entries)
        for row in filereader:
            rep_share = row[5]
            dem_share = row[6]
            total_share = float(rep_share) + float(dem_share) # Total up vote share
            
            # Normalize the vote shares if the sum of them is over 100%, otherwise add them raw
            if total_share >= 1:
                r_percent = float(rep_share) / float(total_share) # Normalize republican share
                d_percent = float(dem_share) / float(total_share) # Normalize democrat share
                correct_answers.append([r_percent, d_percent])
            else:
                correct_answers.append([float(rep_share), float(dem_share)])

        # Restart the file reader so we can do the actual training
        train.seek(0)
        filereader = csv.reader(train)
        for row in filereader:
            id = row[0]
            lon = row[1]
            lat = row[2]
            pop = row[3]
            total_votes = row[4]
            rep_share = row[5]
            dem_share = row[6]
            # Calculate normalized percentage of republican and democrat votes returned
            if float(total_votes) != 0.0 and int(pop) != 0: # Skip and auto-set to 0 if there is no population in this block
                X.append([float(lon), float(lat), float(pop), float(total_votes)]) # Given the first 3 columns
                y.append(correct_answers[filereader.line_num-1][1]) # Predict the normalized 6th column (normalized 5th column is just [1.0 - 4th_column])

            # Storing min and max X and Y values this way greatly increases performance rather
            # than using built in functions to find the min and max of the whole array after it's built
            if float(dem_share) > max_y:
                max_y = float(dem_share)
            if float(dem_share) < min_y:
                min_y = float(dem_share) if float(dem_share) != 0 else min_y

            if float(pop) > max_x:
                max_x = float(pop)
            if float(pop) < min_x:
                min_x = float(pop) if float(pop) != 0 else min_x

            # This skips lines randomly (but never 5 times in a row)
            jumper = np.random.randint(0,4)
            for _ in range(jumper):
                try:
                    filereader.__next__()
                except StopIteration:
                    continue

    # List to use the same selection scheme as before, but for kernels; this lets us add other kernels in the future in case we want/need them
    # Also lets the user easily add kernels by appending to this array of strings
    kernels = ["linear", "rbf"]
    kernel_descriptions = [" (fast but less accurate)", " (slow but more accurate)"]
    print("\nSelect a kernel (learning style) to train the predictive model on:\n")
    for _ in kernels:
        print(str(kernels.index(_)) + ". " + _ + kernel_descriptions[kernels.index(_)]) 

    training_kernel = -1 # Keep asking for input until it's within range
    while training_kernel < 0 or training_kernel > kernels.__len__():
        training_kernel = int(input("\nSelect a kernel for the SVM model (start from index 0 and count up): "))
    training_kernel = kernels[training_kernel]

    # Inform the user we're training the model
    print("\nTraining model... This might take a really long time!\n")

    # Define the model and its characteristics
    prediction_model = None
    if training_kernel == 'linear':
        prediction_model = sklearn.pipeline.Pipeline([
            ('scaler', sklearn.preprocessing.StandardScaler()), # This scales everything to within significantly narrow range
            ('svm',    sklearn.svm.LinearSVR(loss='squared_epsilon_insensitive', C=1.5, epsilon=0.1))
        ])
    else: # In case other kernels are ever added in the future, just convert the kernel to lowercase so we can use it
        prediction_model = sklearn.pipeline.Pipeline([
            ('scaler', sklearn.preprocessing.StandardScaler()), # This scales everything to within significantly narrow range
            ('svm',    sklearn.svm.SVR(kernel=training_kernel.lower(), C=10, gamma=0.1))
        ])

    prediction_model.fit(X, y) # Train model

    print("Model Trained!\nTesting its accuracy now...\n")

    # -------------
    # Begin Testing
    # -------------
    with open(selected_testing_path) as test:
        filereader = csv.reader(test)
        
        correct_index = 0 # This tracks the index of the correct_answers array instead of the line number

        # Initialize output variables
        democrats = 0.0
        republicans = 0.0
        deviations = []
        result_list = []
        # Test through every line in the CSV
        for row in filereader:
            # lon[0], lat[1], pop[2], tot[3], rep[4], dem[5]
            id = row[0]
            lon = row[1]
            lat = row[2]
            pop = row[3]
            
            if float(pop) == 0.0: # This is used to breeze past areas with 0 population
                republicans = 0.0
                democrats = 0.0
                result_list.append(str(id) + "," + str(lon) + "," + str(lat) + "," + str(pop) + "," + str(democrats) + "," + str(republicans) + "\n")
            else:
                democrats = prediction_model.predict([[float(lon), float(lat), float(pop), float(total_votes)]])[0] # Predict vote share
                # Clamp democrat results to between 0.01% and 99.99%
                democrats = 0.9999 if democrats > 0.9999 else democrats
                democrats = 0.0001 if democrats < 0.0001 else democrats

                # Calculate republican votes based on democrats (ignore other parties since that would require four separate Support-Vector-Regressors)
                republicans = 1.0 - democrats
                result_list.append(str(id) + "," + str(lon) + "," + str(lat) + "," + str(pop) + "," + str(democrats) + "," + str(republicans) + "\n")

                # Calculate deviation from correct scores by updating current deviation with the average between the current and previous deviation
                deviations.append(abs(correct_answers[correct_index][1] - democrats)/2)

                print(f"Predicted Vote Shares: {republicans*100:.2f}% Republican | {democrats*100:.2f}% Democrat\t\tActual Vote Shares: {correct_answers[correct_index][0]*100:.2f}% Republican | {correct_answers[correct_index][1]*100:.2f}% Democrat\nError: {abs(correct_answers[correct_index][1] - democrats)*100:.2f}%\n")
            
            correct_index += 1 # This updates what index of the correct_answers list we're on

        # Print results
        total_deviation = 0
        for d in deviations:
            total_deviation = total_deviation + d
        total_deviation = total_deviation/deviations.__len__()
        print(f"Final Accuracy: {(1-total_deviation*2)*100:.2f}%")

    # find or create a place to store results
    CONST_PATH = "\\Predictive_Model\\prediction\\"
    if not osPath.exists(str(path.cwd()) + CONST_PATH):
        path.mkdir(str(path.cwd()) + CONST_PATH)

    # opening or creating a results.csv
    predict_path = (str(path.cwd()) + CONST_PATH + str(selected_training_path).removeprefix(str(path.cwd()) + "\\Data_Collection_and_Formatting\\training\\").removesuffix("train.csv") + "results.csv").replace("\\", "/")
    with open(predict_path, "+w") as result:
        for line in result_list:
            result.write(line)
    print("finished")

    return predict_path
