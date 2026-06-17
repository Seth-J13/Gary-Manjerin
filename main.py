from Data_Collection_and_Formatting.format_file import Format_File
from Predictive_Model.predict import Predict
# from Reasonable_Gerrymandering.renderer import Render


def main():
    step_flag = 0
    previous_step_flag = -1
    prediction_file_path = ""

    while step_flag != -1:
        # Beginning 
        if step_flag == 0:
            step_flag = int(input("Please input an integer representing which step of the prediction process you would like to undergo?\n1: Format more data\n2: Re-train model and predict more data\n3: Redistrict with the same predicted data\n(1, 2, or 3) (-1 to quit) "))
            # previous_step_flag = 0

        elif step_flag == 1:
            Format_File()

            while step_flag not in {0, 2}:
                step_flag = int(input("\n\nWhat would you like to do?\n1: Format more data\n2: Continue to AI model training and prediction\n(1 or 2) (-1 to quit) "))
            # previous_step_flag = 1

        elif step_flag == 2:
            render_path = Predict() # Predict returns the file path to the prediction needed to render the prediction

            while step_flag not in {0, 1, 3}:
                step_flag = int(input("\n\nWhat would you like to do?\n1: Format more data\n2: Repeat training and prediction\n3: Redistrict with newly-predicted data\n(0, 1, or 3) (-1 to quit) "))
            # previous_step_flag = 2
        
        elif step_flag == 3:
            if previous_step_flag != 1:
                # [Function Here](prediction_file_path)
                _ = None # filler line to make the interpreter shut up
            else:
                print("There's nothing to render yet!")
                step_flag = 2

            while step_flag not in {0, 1, 2}:
                step_flag = int(input("\n\nWhat would you like to do?\n1: Format more data\n2: Re-train model and predict more data\n3: Redistrict with the same predicted data\n(0, 1, or 2) (-1 to quit) "))
            # previous_step_flag = 3
            

if __name__ == "__main__":
    main()