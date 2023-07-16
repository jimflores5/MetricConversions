import random
from flask import Flask, request, redirect, render_template, session, flash
from decimal import Decimal
from metric_manips import Number, selectUnits
from copy import deepcopy

base_units = ['m','L','g','s']
prefixes = [('M','Mega',6), ('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3), ('µ','micro',-6), ('n','nano',-9)]
standard_prefixes = [('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3)]
no_excuse_prefixes = [('k','kilo',3), (base_units,'base',0), ('c','centi',-2), ('m','milli',-3)]

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'yrtsimehc'

def checkAnswer(correct_answer, answer):
    if answer == '':        #Check for null result.
        return False

    if answer[0] == ".":    #Convert '.xx' to '0.xx'.
        answer = "0"+answer

    # if answer == correct_answer:  # Check for exact result, including trailing 0 edge case.
    #     return True
    # return False
    
    try:
        if Decimal(answer) == Decimal(correct_answer):  #Check result ignoring sig figs with trailing zeros.
            return True
        else:
            return False
    except:
        return False # Catch non-numerical entries.

def generate_question_set(num_questions, select_from, sig_figs = 3):
    practice_list = []
    prefix_choices = []
    while len(practice_list) < num_questions:
        units = selectUnits(select_from)  #Generate starting & ending units
        if accept_prefix(select_from, units, prefix_choices):
            prefix_choices.append(units[0][1]+units[1][1])
            power = random.randrange(-3,4)
            value = Number(sig_figs, power, units)
            practice_list.append(value)
            session['num_attempted'] += 1
    return deepcopy(practice_list)

def accept_prefix(selection, units, prefixes):
    # Goal: Limit repeats of a specific conversion.
    new_option = units[0][1] + units[1][1]
    flipped_option = units[1][1] + units[0][1]
    frequency = prefixes.count(new_option) + prefixes.count(flipped_option)
    if selection == 'basic':
        prevent = ['kilocenti', 'centikilo', 'kilomilli', 'millikilo']
        if new_option not in prefixes and new_option not in prevent:
            return True
    elif selection == 'no_excuse':
        # Select 2 each from kilo <-> base, base <-> centi, base <-> milli, centi <-> milli
        # Select 1 each from kilo <-> centi and kilo <-> milli
        one_each = ['kilocenti', 'centikilo', 'kilomilli', 'millikilo']
        if new_option not in prefixes and new_option not in one_each:
            return True
        elif new_option in one_each and frequency == 0:
            return True
    elif selection == 'mega':
        # Each question must include a Mega, micro, or nano prefix.
        for option in units:
            if new_option not in prefixes and ('Mega' in option or 'micro' in option or 'nano' in option):
                return True
        return False
    else:
        # Allow only one example each for converting between 2 specific prefixes.
        if new_option not in prefixes and flipped_option not in prefixes:
            return True
    return False

@app.route('/')
def index():
    session.clear()
    return render_template('index.html',title="Metric Practice")

@app.route('/conversion_practice/<page>', methods=['POST', 'GET'])
def conversion_practice(page):
    practiceList = []
    answers = []
    if request.method == 'POST':
        numCorrect = 0
        for item in range(session['num_attempted']):
            answers.append(request.form['answer'+str(item)])  #Pull user answers into a list.
            value_dict = session.get('practiceList'+str(item),None)     #Retrieve original value (dictionary) and return to Number format.
            value = Number(value_dict['sigFigs'], value_dict['power'], value_dict['units'])
            value.answer = value_dict['answer']
            value.value = value_dict['value']
            practiceList.append(value)   
            if checkAnswer(practiceList[item].answer, answers[item]):
                numCorrect += 1
                flash('Correct!  :-)', 'correct')
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
        if session['first_try']:
            session['numCorrect'] += numCorrect
            session['first_try'] = False
            session['first_score'] = session['numCorrect']
        elif numCorrect > session['first_score']:
            correction = (numCorrect - session['first_score'])/2
            session['numCorrect'] = session['first_score'] + correction
        percentage = round(session['numCorrect']/session['num_attempted']*100,1)
        return render_template('conversion_practice.html', practiceList = practiceList, answers = answers, page = page, percentage = percentage, numCorrect = numCorrect)

    else:
        session['first_try'] = True
        session['num_attempted'] = 0
        session['numCorrect'] = 0
        practiceList = generate_question_set(10, page, 3)

        for item in range(len(practiceList)):  #Store values in session as dictionaries
            session['practiceList'+str(item)] = practiceList[item].__dict__

        return render_template('conversion_practice.html',title="Metric Conversion Practice", practiceList = practiceList, answers = answers, page = page)

@app.route('/why_metric/<page>', methods=['POST', 'GET'])
def why_metric(page):
    page_title = 'Metric Conversion Basics'
    num_pages = 3
    template_name = 'why_metric'
    return render_template('why_metric.html', title='Why Use Metric?', page = int(page), page_title = page_title, num_pages = num_pages, template = template_name)

@app.route('/conversions/<page>', methods=['POST', 'GET'])
def conversions(page):
    page_title = 'Metric Conversion Basics'
    num_pages = 4
    template_name = 'conversions'
    practiceList = []
    answers = []
    if request.method == 'POST':
        numCorrect = 0
        for item in range(session['num_attempted']):
            answers.append(request.form['answer'+str(item)])  #Pull user answers into a list.
            value_dict = session.get('practiceList'+str(item),None)     #Retrieve original value (dictionary) and return to Number format.
            value = Number(value_dict['sigFigs'], value_dict['power'], value_dict['units'])
            value.answer = value_dict['answer']
            value.value = value_dict['value']
            practiceList.append(value)   
            if checkAnswer(practiceList[item].answer, answers[item]):
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
        return render_template('conversions.html', title='Level 1 Metric Conversions', page = int(page), 
                           page_title = page_title, num_pages = num_pages, template = template_name,
                           practiceList = practiceList, answers = answers, numCorrect = numCorrect)
    else:
        num_problems = 4
        session['num_attempted'] = 0
        if int(page) == 2:
            select_from = 'basic'
        else:
            select_from = 'standard'
        
        practiceList = generate_question_set(num_problems, select_from, 2)

        for item in range(len(practiceList)):  #Store values in session as dictionaries
            session['practiceList'+str(item)] = practiceList[item].__dict__

    return render_template('conversions.html', title='Level 1 Metric Conversions', page = int(page), 
                           page_title = page_title, num_pages = num_pages, template = template_name,
                           practiceList = practiceList, answers = answers)

@app.route('/more_conversions/<page>', methods=['POST', 'GET'])
def more_conversions(page):
    page_title = 'Larger and Smaller Prefixes'
    num_pages = 2
    template_name = 'more_conversions'
    practiceList = []
    answers = []
    if request.method == 'POST':
        numCorrect = 0
        for item in range(session['num_attempted']):
            answers.append(request.form['answer'+str(item)])  #Pull user answers into a list.
            value_dict = session.get('practiceList'+str(item),None)     #Retrieve original value (dictionary) and return to Number format.
            value = Number(value_dict['sigFigs'], value_dict['power'], value_dict['units'])
            value.answer = value_dict['answer']
            value.value = value_dict['value']
            practiceList.append(value)   
            if checkAnswer(practiceList[item].answer, answers[item]):
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
        return render_template('more_conversions.html', title='Level 2 Metric Conversions', page = int(page), 
                           page_title = page_title, num_pages = num_pages, template = template_name,
                           practiceList = practiceList, answers = answers, numCorrect = numCorrect)
    else:
        num_problems = 4
        session['num_attempted'] = 0
        select_from = 'mega'

        if int(page)%2 == 0:
            practiceList = generate_question_set(num_problems, select_from, 2)

        for item in range(len(practiceList)):  #Store values in session as dictionaries
            session['practiceList'+str(item)] = practiceList[item].__dict__

    return render_template('more_conversions.html', title='Level 2 Metric Conversions', page = int(page),
                           page_title = page_title, num_pages = num_pages, template = template_name,
                           practiceList = practiceList, answers = answers)

if __name__ == '__main__':
    app.run()