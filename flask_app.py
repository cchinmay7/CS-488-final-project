from flask import Flask, request, redirect, render_template, session
from flask_session import Session

import aws

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def has_active_session():
    return session.get('email') is not None


@app.route('/')
def go_to_login():
    return redirect('/login.html')


@app.route('/project5')
def project_entry():
    return redirect('/login.html')


@app.route('/login.html')
def login_page():
    if has_active_session():
        return redirect('/editor.html')
    return render_template('login.html')


@app.route('/home.html')
def home_page():
    if not has_active_session():
        return redirect('/login.html')
    return render_template('home.html')


@app.route('/editor.html')
def editor_page():
    if not has_active_session():
        return redirect('/login.html')
    return render_template('editor.html', email=session['email'])


@app.route('/login')
def login():
    email = request.args.get('email', '').strip()
    password = request.args.get('password', '').strip()

    if email == '':
        return {'result': 'Email cannot be blank'}
    if password == '':
        return {'result': 'Password cannot be blank'}

    account = aws.verify_login(email, password)
    if account is None:
        return {'result': 'Invalid email or password'}

    session['email'] = account['email']
    return {'result': 'OK'}


@app.route('/logout')
def sign_out():
    session.pop('email', None)
    return {'result': 'OK'}

@app.route('/listentries')
def list_entries_api():
    if not has_active_session():
        return {'result': 'Please login first', 'results': []}

    results = aws.list_posts()
    return {'results': results}


@app.route('/addentry')
def add_entry_api():
    if not has_active_session():
        return {'result': 'Please login first'}
    return aws.add_post()


@app.route('/deleteentry')
def delete_entry_api():
    if not has_active_session():
        return {'result': 'Please login first'}
    return aws.remove_post()

