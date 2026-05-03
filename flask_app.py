from flask import Flask, request, redirect, render_template, session
from flask_session import Session
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid

import aws

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def has_active_session():
    email = session.get('email')
    if email is None:
        return False

    if session.get('username') is not None:
        return True

    user = aws.get_user_by_email(email)
    if user is None:
        session.pop('email', None)
        session.pop('username', None)
        return False

    username = user.get('username', '')
    if username == '':
        session.pop('email', None)
        session.pop('username', None)
        return False

    session['username'] = username
    return True


@app.route('/')
def go_to_login():
    if has_active_session():
        return redirect('/feed.html')
    return redirect('/login.html')


@app.route('/final')
def project_entry():
    return redirect('/')


@app.route('/project5')
def project5_entry():
    return redirect('/')


@app.route('/login.html')
def login_page():
    if has_active_session():
        return redirect('/feed.html')
    return render_template('login.html')


@app.route('/signup.html')
def signup_page():
    if has_active_session():
        return redirect('/feed.html')
    return render_template('signup.html')


@app.route('/feed.html')
def feed_page():
    if not has_active_session():
        return redirect('/login.html')
    return render_template('feed.html', username=session['username'])


@app.route('/home.html')
def home_page():
    return redirect('/feed.html')


@app.route('/u/<username>')
def profile_page(username):
    if not has_active_session():
        return redirect('/login.html')

    own_profile = session.get('username', '').lower() == username.lower()
    return render_template('profile.html', username=username, own_profile=own_profile)


@app.route('/editor.html')
def editor_page():
    if not has_active_session():
        return redirect('/login.html')
    return redirect('/u/' + session['username'])


@app.route('/post.html')
def post_view_page():
    if not has_active_session():
        return redirect('/login.html')

    entry_id = request.args.get('id', '').strip()
    if entry_id == '':
        return redirect('/feed.html')
    return render_template('post.html', entry_id=entry_id)


@app.route('/login')
def login():
    login_id = request.args.get('login', '').strip()
    password = request.args.get('password', '').strip()

    if login_id == '':
        return {'result': 'Email or username cannot be blank'}
    if password == '':
        return {'result': 'Password cannot be blank'}

    account = aws.verify_login(login_id, password)
    if account is None:
        return {'result': 'Invalid login or password'}

    session['email'] = account['email']
    session['username'] = account['username']
    return {'result': 'OK'}


@app.route('/signup')
def signup():
    email = request.args.get('email', '').strip()
    username = request.args.get('username', '').strip()
    password = request.args.get('password', '').strip()

    if email == '':
        return {'result': 'Email cannot be blank'}
    if '@' not in email or '.' not in email:
        return {'result': 'Email is invalid'}
    if username == '':
        return {'result': 'Username cannot be blank'}
    if password == '':
        return {'result': 'Password cannot be blank'}

    result = aws.signup_user(email, username, password)
    if result['result'] != 'OK':
        return result

    account = result['user']
    session['email'] = account['email']
    session['username'] = account['username']
    return {'result': 'OK'}


@app.route('/logout')
def sign_out():
    session.pop('email', None)
    session.pop('username', None)
    return {'result': 'OK'}


@app.route('/feedposts')
def feed_posts_api():
    if not has_active_session():
        return {'result': 'Please login first', 'results': []}

    results = aws.list_recent_posts(10)
    return {'results': results}


@app.route('/profileinfo')
def profile_info_api():
    if not has_active_session():
        return {'result': 'Please login first'}

    username = request.args.get('username', '').strip()
    if username == '':
        return {'result': 'Username cannot be blank'}

    user = aws.get_user_by_username(username)
    if user is None:
        return {'result': 'User not found'}

    photo = user.get('photo', '')
    if photo == '':
        photo = aws.DEFAULT_PHOTO_URL

    own_profile = session.get('username', '').lower() == user.get('username', '').lower()
    return {
        'result': 'OK',
        'username': user.get('username', ''),
        'email': user.get('email', ''),
        'photo': photo,
        'ownProfile': own_profile
    }


@app.route('/userposts')
def user_posts_api():
    if not has_active_session():
        return {'result': 'Please login first', 'results': []}

    username = request.args.get('username', '').strip()
    if username == '':
        return {'result': 'Username cannot be blank', 'results': []}

    results = aws.list_posts_by_username(username)
    return {'results': results}


@app.route('/createpost')
def create_post_api():
    if not has_active_session():
        return {'result': 'Please login first'}

    text = request.args.get('text', '').strip()
    parent_id = request.args.get('parent', '').strip()

    return aws.add_post(session['email'], session['username'], text, parent_id)


@app.route('/post')
def post_api():
    if not has_active_session():
        return {'result': 'Please login first'}

    entry_id = request.args.get('id', '').strip()
    if entry_id == '':
        return {'result': 'Post id cannot be blank'}

    post = aws.get_post(entry_id)
    if post is None:
        return {'result': 'Post not found'}

    replies = aws.list_replies(entry_id)
    return {'result': 'OK', 'post': post, 'replies': replies}


@app.route('/uploadphoto', methods=['POST'])
def upload_photo_api():
    if not has_active_session():
        return {'result': 'Please login first'}

    if 'file' not in request.files:
        return {'result': 'Please choose a file'}

    file = request.files['file']
    if file.filename == '':
        return {'result': 'Please choose a file'}

    filename = secure_filename(file.filename)
    if filename == '':
        return {'result': 'Invalid filename'}

    extension = filename.split('.')[-1].lower()
    if extension not in ['jpg', 'jpeg', 'png', 'gif']:
        return {'result': 'Only jpg, jpeg, png or gif files are allowed'}

    save_name = str(uuid.uuid4()) + '_' + filename
    upload_dir = Path(app.root_path) / 'static' / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)

    file.save(upload_dir / save_name)
    photo_url = '/static/uploads/' + save_name

    aws.update_photo(session['email'], photo_url)
    return {'result': 'OK', 'url': photo_url}

