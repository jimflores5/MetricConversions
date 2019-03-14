import random
#from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal

base_units = ['m','L','g','s']
prefixes = [('M','Mega',6), ('k','kilo',3), ('h','hecto',2), ('da','deca',1), (base_units,'base',0), ('d','deci',-1), ('c','centi',-2), ('m','milli',-3), ('µ','micro',-6), ('n','nano',-9)]
no_excuse_prefixes = [('k','kilo',3), (base_units,'base',0), ('c','centi',-2), ('m','milli',-3)]

def selectUnits():
    units = []  #units = ['starting prefix', 'requested prefix']
    while len(units) != 2:
        new_unit = random.choice(prefixes)
        if new_unit not in units:
            units.append(new_unit)
    return units

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

for x in range(10):
    base = random.choice(base_units) #Choose base unit.
    units = selectUnits()
    sigFigs = random.randrange(1,4)
    power = random.randrange(-3,4)
    value = selectNumbers(sigFigs, power)
    for index in range(2):
        if units[index][1] == 'base':
            units.append(base)
        else:
            units.append(units[index][0]+base)

    text = "Number, start units, end units: {} {} {}\n".format(value, units[2], units[3])
    print(text)   