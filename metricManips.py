import random
#from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal

base_units = ['m','L','g','s']
all_prefixes = [('M','Mega',6), ('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3), ('µ','micro',-6), ('n','nano',-9)]
standard_prefixes = [('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3)]
no_excuse_prefixes = [('k','kilo',3), (base_units,'base',0), ('c','centi',-2), ('m','milli',-3)]

class Number():
    def __init__(self, sigFigs, power, units):
        self.sigFigs = sigFigs
        self.power = power
        self.value = selectNumbers(sigFigs, power)
        self.answer = roundValue(convertValue(units,self.value),sigFigs)
        self.units = units

def selectUnits(prefixes = 'all'):
    units = []
    base = random.choice(base_units) #Choose base unit.
    while len(units) != 2:              #Pick the starting and ending prefixes.
        if prefixes == 'no_excuse':
            new_unit = random.choice(no_excuse_prefixes)
        elif prefixes == 'standard':
            new_unit = random.choice(standard_prefixes)
        else:
            new_unit = random.choice(all_prefixes)
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
    change = Decimal(units[0][2] - units[1][2])
    answer = Decimal(value)*10**change
    return str(answer)

def checkAnswer(answer, value):
    if answer == '':        #Check for null result.
        return "Please remember to enter a response."

    if answer[0] == ".":    #Convert '.xx' to '0.xx'.
        answer = "0"+answer

    try:
        if Decimal(answer) == Decimal(value.answer):    #Check for exact result.
            return "CORRECT!"
        else:
            return "Nope. The correct answer is {} {}".format(value.answer, value.units[3])
    except:
        return 'Please enter a numerical result.'

def roundValue(value, sigFigs):      
    if "E" in value and '-' in value:
        return sciToStd(value, sigFigs)

    decimalIndex = value.find('.')
    if decimalIndex < 0:
        decimalIndex = len(value)

    if Decimal(value)<1:
        placeholders = 0
        for x in range(2,len(value)):
            if value[x] == "0":
                placeholders += 1
            else:
                break

        roundToSigFigs = round(Decimal(value)*10**placeholders,sigFigs)
        addPlaceholders = round(roundToSigFigs/10**placeholders,sigFigs+placeholders)

        if len(str(roundToSigFigs))-sigFigs < 3:
            result = str(addPlaceholders)+"0"*(2-(len(str(roundToSigFigs))-sigFigs))
        else:
            result = str(addPlaceholders)
        return result
    else:
        roundToSigFigs = round(float(value)/10**decimalIndex,sigFigs)
        addZeros = round(roundToSigFigs*10**decimalIndex,sigFigs-decimalIndex)

        if sigFigs <= decimalIndex:
            result = str(int(addZeros))
        elif len(str(addZeros))-sigFigs <= 0:
            result = str(addZeros)+"0"*(sigFigs-len(str(addZeros))+1)
        else:
            result = str(addZeros)

        return result

def sciToStd(value, sigFigs):
    powerIndex = value.find('E')
    numZeros = -int(value[powerIndex+1:])-1
    noDecimal = value[:powerIndex].replace('.','')
    newValue = "0."+"0"*numZeros+noDecimal
    return newValue

def Main():
    for x in range(4):
        units = selectUnits()
        sigFigs = random.randrange(1,4)
        power = random.randrange(-3,4)
        value = Number(sigFigs, power, units)

        text = "Convert {} {} into {}: ".format(value.value, units[2], units[3])
        answer = input(text)
        print(checkAnswer(answer, value))