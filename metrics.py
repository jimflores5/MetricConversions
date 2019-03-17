import random
from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal

base_units = ['m','L','g','s']
prefixes = [('M','Mega',6), ('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3), ('µ','micro',-6), ('n','nano',-9)]
no_excuse_prefixes = [('k','kilo',3), (base_units,'base',0), ('c','centi',-2), ('m','milli',-3)]

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'yrtsimehc'

def selectUnits():
    units = []
    base = random.choice(base_units) #Choose base unit.
    while len(units) != 2:              #Pick the starting and ending prefixes.
        new_unit = random.choice(prefixes)
        if new_unit not in units:
            units.append(new_unit)
    for index in range(len(units)):     #Generate unit abbreviations (e.g. 'kg').
        if units[index][1] == 'base':
            units.append(base)
        else:
            units.append(units[index][0]+base)
    return units        #units = ['starting prefix', 'ending prefix', 'starting abbr', 'ending abbr']

def selectNumbers(sigFigs, power):
    allDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    firstDigit = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    if power < 0:
        value = "0."+ -(power+1)*"0" + random.choice(firstDigit)
        for digit in range(sigFigs-1):
            value += random.choice(allDigits)
        return value
    elif sigFigs - power < 2:
        value = random.choice(firstDigit)
        for digit in range(sigFigs-1):
            if digit == sigFigs-2:
                value += random.choice(firstDigit)
            else:
                value += random.choice(allDigits)
        value += (power-sigFigs+1)*"0"
        return value
    else:
        value = random.choice(firstDigit)
        decimalLocation = power +1
        for digit in range(1, sigFigs+1):
            if digit == decimalLocation:
                value += "."
            else:
                value += random.choice(allDigits)
        return value

def convertValue(units,value):
    #TODO - Determine the correct answer for the requested metric conversion.
    return

def checkAnswer(units, answer, value):
    if answer == '':        #Check for null result.
        return False

    if answer[0] == ".":    #Convert '.xx' to '0.xx'.
        answer = "0"+answer

    if answer == convertValue(units, value):    #Check for exact result.
        return True
    else:
        return False

@app.route('/')
def index():
    #session.clear()
    return render_template('index.html',title="Metric Practice")

@app.route('/conversion_practice/<type>', methods=['POST', 'GET'])
def conversion_practice(type):
    if request.method == 'POST':
        answer = request.form['answer']
        units = request.form['units']
        value = request.form['value']
        if checkAnswer(units, answer, value):
            flash('Correct!  :-)', 'correct')
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
        
        return render_template('countingSigFigs.html', value=value, units = units, answer = answer, type = type)

    units = selectUnits()               #Generate starting & ending units
    sigFigs = random.randrange(1,4)
    power = random.randrange(-3,4)
    value = selectNumbers(sigFigs, power)
    return render_template('conversionPractice.html',title="Metric Conversion Practice", units = units, value=value, type = type)

if __name__ == '__main__':
    app.run()