import random
from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal
from metricManips import Number, selectUnits, selectNumbers, convertValue, roundValue, sciToStd

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

    if answer == correct_answer:    #Check for exact result.
        return True
    else:
        return False

@app.route('/')
def index():
    #session.clear()
    return render_template('index.html',title="Metric Practice")

@app.route('/conversion_practice/<type>', methods=['POST', 'GET'])
def conversion_practice(type):
    practiceList = []
    answers = []
    if request.method == 'POST':
        numCorrect = 0
        for item in range(4):
            answers.append(request.form['answer'+str(item)])  #Pull user answers into a list.
            given_units = request.form['given_units'+str(item)]
            desired_units = request.form['desired_units'+str(item)]
            orig_value = request.form['value'+str(item)]
            correct_answer = request.form['correct_answer'+str(item)]
            practiceList.append([orig_value, correct_answer, given_units, desired_units]) #Pull original data into a list.
            if checkAnswer(correct_answer, answers[item]):
                numCorrect += 1
                flash('Correct!  :-)', 'correct')
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
        
        return render_template('conversionPractice.html', practiceList = practiceList, answers = answers, type = type, checked = True, numCorrect = numCorrect)

    while len(practiceList) <= 4:
        units = selectUnits(type)              #Generate starting & ending units
        sigFigs = random.randrange(1,4)
        power = random.randrange(-3,4)
        value = Number(sigFigs, power, units)
        if value not in practiceList:       #TODO: Make practiceList format consistent between GET and POST events.
            practiceList.append(value)

    return render_template('conversionPractice.html',title="Metric Conversion Practice", practiceList = practiceList, answers = answers, type = type, checked = False)

if __name__ == '__main__':
    app.run()