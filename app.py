"""
author - Dibyanshu Chatterjee
user - dc7017
"""

import json
import logging
import math
import os
import requests
from zeep import Client
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    """
    This function serves to return the home page
    :return: index.html page
    """
    return render_template("index.html")


def calculate_bmr(sex, weight=0.0, height=0.0, age=0):
    """
    Calculates the BMR based on the inputs and the formula
    :param sex: Gender of the user
    :param weight: Weight of the user
    :param height: Height of the user
    :param age: Age of the user
    :return: bmr floored
    """
    if sex.lower() == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif sex.lower() == "female":
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        return "The BMR formula has been designed for male and female body types"
    return math.floor(bmr)


def suggest_calories(bmr, goal="", activity=1):
    """
    This function recommends the calories intake
    :param bmr: Calculated BMR
    :param goal: fat loss or mass gain goal (gain/loose)
    :param activity: Activity level on the scale of 1 to 3
    :return: Suggested calories when goal is entered correctly, else 0
    """
    if goal.lower() == "gain":
        if activity == 1:
            suggested_cal = bmr + 450
        elif activity == 2:
            suggested_cal = bmr + 550
        elif activity == 3:
            suggested_cal = bmr + 650
        return suggested_cal

    elif goal.lower() == "loose":
        if activity == 1:
            suggested_cal = bmr - 350
        elif activity == 2:
            suggested_cal = bmr - 450
        elif activity == 3:
            suggested_cal = bmr - 550
        return suggested_cal

    # if the goal was not entered correctly, return 0
    else:
        return 0


def evaluate_macros(calories, goal):
    """
    This function evaluates the proteing fat and carbs quantity in grams
    :param calories: calculated calories
    :param goal: The user's goal
    :return: macro nutrients in grams using dict if goal is entered correctly, else, return failure string
    """
    if goal.lower() == "loose":
        carbs = (40 / 100) * calories
        protein = (40 / 100) * calories
        fats = (20 / 100) * calories
        return {'carbs': carbs / 4, 'protein': protein / 4, 'fats': fats / 9}
    if goal.lower() == "gain":
        carbs = (50 / 100) * calories
        protein = (30 / 100) * calories
        fats = (20 / 100) * calories
        return {'carbs': carbs / 4, 'protein': protein / 4, 'fats': fats / 9}
    return "This application aids in weight gain and weight loss GOALS only"


def get_food_suggestions():
    """
    Use API to fetch snacks
    :return: List of recommended snacks(list of dicts)
    """
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByNutrients"

    querystring_1 = {"limitLicense": "false", "minProtein": "0", "minVitaminC": "0", "minSelenium": "0",
                     "maxFluoride": "50", "maxVitaminB5": "50", "maxVitaminB3": "50", "maxIodine": "50",
                     "minCarbs": "0", "maxCalories": "250", "minAlcohol": "0", "maxCopper": "50", "maxCholine": "50",
                     "maxVitaminB6": "50", "minIron": "0", "maxManganese": "50", "minSodium": "0", "minSugar": "0",
                     "maxFat": "20", "minCholine": "0", "maxVitaminC": "50", "maxVitaminB2": "50", "minVitaminB12": "0",
                     "maxFolicAcid": "50", "minZinc": "0", "offset": "0", "maxProtein": "100", "minCalories": "0",
                     "minCaffeine": "0", "minVitaminD": "0", "maxVitaminE": "50", "minVitaminB2": "0", "minFiber": "0",
                     "minFolate": "0", "minManganese": "0", "maxPotassium": "50", "maxSugar": "50", "maxCaffeine": "50",
                     "maxCholesterol": "50", "maxSaturatedFat": "50", "minVitaminB3": "0", "maxFiber": "50",
                     "maxPhosphorus": "50", "minPotassium": "0", "maxSelenium": "50", "maxCarbs": "100",
                     "minCalcium": "0", "minCholesterol": "0", "minFluoride": "0", "maxVitaminD": "50",
                     "maxVitaminB12": "50", "minIodine": "0", "maxZinc": "50", "minSaturatedFat": "0",
                     "minVitaminB1": "0", "maxFolate": "50", "minFolicAcid": "0", "maxMagnesium": "50",
                     "minVitaminK": "0", "maxSodium": "50", "maxAlcohol": "50", "maxCalcium": "50", "maxVitaminA": "50",
                     "maxVitaminK": "50", "minVitaminB5": "0", "maxIron": "50", "minCopper": "0", "maxVitaminB1": "50",
                     "number": "10", "minVitaminA": "0", "minPhosphorus": "0", "minVitaminB6": "0", "minFat": "5",
                     "minVitaminE": "0"}

    headers = {
        "X-RapidAPI-Key": "b94869d978mshc39948d20e50b12p198786jsn6352d3fc0add",
        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    response_1 = requests.request("GET", url, headers=headers, params=querystring_1)

    return response_1.json()


def find_out_least_calory(response):
    """
    Use SOAP based API to sort for the least calories snack
    :param response: respoinse containing list of items with their calories
    :return: String of the recommended snack with least calories
    """
    print(response)
    calories_list_str = ""
    for idx in response:
        calories_list_str += str(idx.get('calories')) + " "

    cal_str = calories_list_str.strip()

    # in the case SOAP API does not respond
    try:
        client = Client(wsdl='http://vhost3.cs.rit.edu/SortServ/Service.svc?singleWsdl')
        key = client.service.GetKey()
        sort_result = client.service.mergeSort(cal_str, key)
    except Exception as e:
        logging.error(msg="There was an error with the SOAP service")
        logging.exception(msg=e)
        return ""

    cal_list = sort_result.split(" ")
    least_cal = cal_list[0]
    least_calory_food = ""

    # for loop to obtain the name of the least calories food
    for idx in response:
        if str(idx.get('calories')) == least_cal:
            least_calory_food = idx.get('title')

    return least_calory_food


def ask_chatGPT(payload):
    """
    Using chatGPT's API to get desired answers
    :param payload: The payload to send chatGPT
    :return: The response String
    """
    url = "https://you-chat-gpt.p.rapidapi.com/"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "b94869d978mshc39948d20e50b12p198786jsn6352d3fc0add",
        "X-RapidAPI-Host": "you-chat-gpt.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.text


def generate_payload(choice_of_cuisine, macro_dict, age, sex, goal, preffered_number_of_meals):
    """
    Aids in generating the payload to be sent to chatGPT's API
    :param choice_of_cuisine: cuisine's name (String)
    :param macro_dict: dictionary containing all the required macro nutrient information (dict)
    :param age: The age of the user (Integer)
    :param sex: The gender of the user (String)
    :param goal: The goal of the user (String)
    :param preffered_number_of_meals: Preferred number of meals bny the user (Integer)
    :return:
    """
    if goal.lower() == "loose":
        payload_str = "Create a fat loss diet chart with " + str(
            preffered_number_of_meals) + " meals. The diet chart should have " + str(
            choice_of_cuisine) + " cuisines and the total protein should be " + str(
            macro_dict.get('protein')) + " grams, the " + "total " + "carbs " + "should " + "be " + str(
            macro_dict.get('carbs')) + " grams and total fats should be " + str(
            macro_dict.get('fats')) + " grams. The diet should be suitable for a " + str(age) + " years old " + str(sex)
        return payload_str

    elif goal.lower() == "gain":
        payload_str = "Create a mass gain diet chart with " + str(
            preffered_number_of_meals) + " meals. The diet chart should have " + str(
            choice_of_cuisine) + " cuisines and the total protein should be " + str(
            macro_dict.get('protein')) + " grams, the " + "total " + "carbs " + "should " + "be " + str(
            macro_dict.get('carbs')) + " grams and total fats should be " + str(
            macro_dict.get('fats')) + " grams. The diet should be suitable for a " + str(age) + " years old " + str(sex)
        return payload_str

    else:
        return False


def write_text(filename, the_string):
    """
    Saves the diet chart into local system into a text file
    :param filename: String denoting the filename
    :param the_string: response string (String)
    :return: String denoting the path of the saved file
    """
    path_of_file = os.getcwd()

    final_string = json.loads(the_string)

    written_file = open(filename + ".txt", "w")
    written_file.write(final_string.get('answer'))
    written_file.close()
    return "Your file has been saved successfully in the directory: " + str(
        path_of_file) + ", with the filename: " + filename


# routing the result into the result page
@app.route('/result', methods=['POST', 'GET'])
def result():
    """
    This function helps fetch data from the webpage and also projects the results.
    :return: The result page
    """
    # user inputs the following details:
    extracted_form = request.form.to_dict()
    weight_unit = extracted_form['Weight_Units']
    height_unit = extracted_form['height_unit']
    weight = float(extracted_form["Weight"])
    height = float(extracted_form['height'])
    age = int(extracted_form['age'])
    sex = extracted_form['sex']
    goal = extracted_form['goal']
    activity = int(extracted_form['activity'])
    choice_of_cuisine = extracted_form['choice_of_cuisine']
    preffered_number_of_meals = int(extracted_form['preffered_number_of_meals'])

    # converting the values to right unit if needed
    if weight_unit.lower() != "kgs" and weight_unit.lower() != "kg":
        weight_in_kg = weight / 2.2

    else:
        weight_in_kg = weight

    if height_unit.lower() != "cms" and height_unit.lower() != "cm":
        height_in_cm = height * 30.48

    else:
        height_in_cm = height
    calculated_bmr = calculate_bmr(sex=sex, weight=weight_in_kg, height=height_in_cm, age=age)

    suggested_calories_per_day = suggest_calories(bmr=calculated_bmr, goal=goal, activity=activity)

    macros_dict = evaluate_macros(calories=suggested_calories_per_day, goal=goal)
    response = get_food_suggestions()

    print("Below here are a few healthy and delicious snack options that match your goal: ")

    healthy_snack_options = ""
    for idx in response:
        healthy_snack_options += str(idx.get('title')) + ","
    healthy_snack_options = healthy_snack_options.rstrip(',')

    least_calory_food = find_out_least_calory(response=response)
    recepie_str = ""
    if least_calory_food != "":
        payload = {
            "question": "Give me the recipe to make " + least_calory_food,
            "max_response_time": 30
        }

        print(
            "Among the given list of snacks, " + str(least_calory_food) + "is the one with least calories. Try making "
                                                                          "it at home using the recipe below: ")
        recepie_str_unprocessed = ask_chatGPT(payload=payload)
        json_str = json.loads(recepie_str_unprocessed)
        recepie_str = json_str.get('answer')

    result = generate_payload(choice_of_cuisine=choice_of_cuisine, macro_dict=macros_dict, age=age, sex=sex, goal=goal,
                              preffered_number_of_meals=preffered_number_of_meals)

    if result is False:
        loc_result = "This application only works for fat loss or mass gain GOALS"
    else:
        payload = {
            "question": result,
            "max_response_time": 30
        }
        print("Below here are your details: ")
        print("Your weight in kgs: " + str(weight_in_kg))
        print("Your height in cms: " + str(height_in_cm))
        print("Your age: " + str(age))
        print("Your BMR: " + str(calculated_bmr))
        print()
        print("Below here is your diet chart: ")
        str_to_write = ask_chatGPT(payload=payload)
        if goal.lower() == "loose":
            filename = "Fat_Loss_Diet_Chart_Sample"
        elif goal.lower() == "gain":
            filename = "Mass_Gain_Diet_Chart_Sample"
        else:
            return "The application only works for fat loss or mass gain goals"
        loc_result = write_text(filename, str_to_write)

    return render_template('index.html', healthy_snack=healthy_snack_options,
                           healthy_snack_least_calories=str(least_calory_food), healthy_snack_recepie=str(recepie_str),
                           diet_chart=loc_result)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
