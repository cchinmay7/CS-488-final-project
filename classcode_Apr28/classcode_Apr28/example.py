from flask import Flask, request, redirect, render_template

import random
import json

facts = [
    'Penguins can swim up to 15mph',
    'Scientists don\'t know how many penguins',
    'Penguins love fish',
    'There are no penguins in the artic'
    ]

def fact():
    return random.choice(facts)

def home():
    return 'Hello'

def about():
    return 'My name is <b>Carmine</b>. I am cool dude.'



def search():
    s = request.args.get('s', '').lower()
    bedrooms = request.args.get('beds', '0')
    bedrooms = int(bedrooms)

    f = open('/home/cguida/data/courses.json')
    courses = json.load(f)
    f.close()

    results = []

    for course in courses:
        if (course['number'].lower().startswith(s)) or (s in course['name'].lower()):
            results.append(course)

    # We can only return strings or dictionaries

    return { 'results':results }
























