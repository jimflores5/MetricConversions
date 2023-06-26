import random
from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal
from metricManips import Number, selectUnits

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

@app.route('/')
def index():
    session.clear()
    return render_template('index.html',title="Metric Practice")

@app.route('/conversion_practice/<type>', methods=['POST', 'GET'])
def conversion_practice(type):
    practiceList = []
    answers = []
    if request.method == 'POST':
        numCorrect = 0
        for item in range(10):
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
        return render_template('conversionPractice.html', practiceList = practiceList, answers = answers, type = type, percentage = percentage, numCorrect = numCorrect)

    else:
        session['first_try'] = True
        session['num_attempted'] = 0
        session['numCorrect'] = 0
        while len(practiceList) < 10:
            units = selectUnits(type)              #Generate starting & ending units
            # sigFigs = random.randrange(1,4)
            sigFigs = 3
            power = random.randrange(-3,4)
            value = Number(sigFigs, power, units)
            if value not in practiceList:    
                practiceList.append(value)
                session['num_attempted'] += 1
        percentage = round(session['numCorrect']/session['num_attempted']*100,1)
        for item in range(len(practiceList)):       #Store values in session as dictionaries
            session['practiceList'+str(item)] = practiceList[item].__dict__

        return render_template('conversionPractice.html',title="Metric Conversion Practice", practiceList = practiceList, answers = answers, type = type, percentage = percentage)

if __name__ == '__main__':
    app.run()