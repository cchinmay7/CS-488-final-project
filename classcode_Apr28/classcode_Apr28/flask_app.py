from flask import Flask, redirect, request, render_template, session, make_response
from flask_session import Session


import example
import json
import aws

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)


def auto_login():
    cookie = request.cookies.get('remember')
    if cookie is None: return False

    table = aws.get_table('Remember')
    result = table.get_item(Key={'key':cookie})
    if 'Item' not in result: return False

    # Found the key in the table
    remember = result['Item']
    table = aws.get_table('Users')
    result = table.get_item(Key={'email':remember['email']})
    user = result['Item']

    # Now I have the user
    session['email'] = user['email']
    session['username'] = user['username']
    return True



def is_logged_in():
    if not session.get('email'):
        return auto_login()
    return True


@app.route('/login.html')
def login_html():
    if is_logged_in():
        return redirect('/account.html')
    return render_template('login.html')

@app.route('/account.html')
def account_html():
    if is_logged_in():
        return render_template('account.html', username=session['username'])
    return redirect('/login.html')

@app.route('/logout.html')
def logout():
    session.pop('email', None)
    session.pop('username', None)

    response = make_response(redirect('/login.html'))
    response.delete_cookie('remember')
    return response




@app.route('/login')
def login():
    email = request.args.get('email', '')
    password = request.args.get('password', '')
    if email == '': return {'result':'Email cannot be blank'}
    if password == '': return {'result':'Password cannot be blank'}

    table = aws.get_table('Users')
    item = table.get_item(Key={'email':email})
    if 'Item' not in item: return {'result':'Email address not found.'}

    user = item['Item']
    if password != user['password']: return {'result':'Bad Password'}

    # At this point we are good!
    session['email'] = user['email']
    session['username'] = user['username']

    response = make_response({'result':'OK'})
    remember = request.args.get('remember', 'no')
    if (remember == 'no'):
        response.delete_cookie('remember')
    else:
        key = aws.add_remember_key(user['email'])
        response.set_cookie('remember', key, max_age=60*60*24*14) # 14 days

    return response



@app.route('/liststudents')
def liststudents():
    results = aws.list_students()
    return { 'results':results }


@app.route('/listfiles')
def listfiles():
    return aws.listfiles()

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    return aws.uploadfile()

def find_course(search):
    f = open('/home/cguida/data/courses.json')
    courses = json.load(f)
    f.close()
    for c in courses:
        if c['number'].lower() == search.lower():
            return c

    return { 'name':'Not found', 'description':'Try searching again....' }


@app.route('/course/<number>')
def course_search(number):
    c = find_course(number)
    return render_template('course.html', course=c)


@app.route('/seidenberg')
def seidenberg():
    return redirect('https://www.pace.edu/seidenberg')

@app.route('/linkedin')
def linkedin():
    return redirect('https://www.linkedin.com/in/carmineguida')

@app.route('/search')
def search():
    return example.search()

@app.route('/')
def home():
    return example.home()

@app.route('/about')
def about():
    return example.about()

@app.route('/fact')
def fact():
    return example.fact()

@app.route('/add/<a>/<b>')
def add(a, b):
    result = int(a) + int(b)
    return str(result)
