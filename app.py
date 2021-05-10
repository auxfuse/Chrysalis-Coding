import os
import datetime
from os import path
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from forms import LoginForm, RegisterForm, CreatePost, EditPost, DeletePost


if path.exists("env.py"):
    import env

app = Flask(__name__)
app.config.update(
    MONGO_DB = os.environ.get('MONGO_DB'),
    MONGO_URI = os.environ.get('MONGO_URI'),
    SECRET_KEY = os.environ.get('SECRET_KEY')
)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
users = mongo.db.users
posts = mongo.db.posts

# Static page routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')


@app.route('/wit')
def wit():
    return render_template('inspirationalwomenintechpage.html')


# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        found_username = users.find_one({
            'username': request.form['username']
        })

        if not found_username:
            hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            users.insert_one({
                'username': register_form.username.data,
                'password': hashed_pw
            })
            session['username'] = request.form.get('username')
            flash(f'Thank you for Registering. You are now signed in!', 'primary')
            return redirect(url_for('index'))
        else:
            flash(f'Duplicate account detected. Please try again!', 'danger')
            return redirest(url_for('register'))
    
    return render_template('register.html', title='Register', form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        found_username = users.find_one({
            'username': request.form['username']
        })

        if found_username:
            if bcrypt.check_password_hash(
                found_username['password'], request.form.get('password').encode('utf-8')):
                session['username'] = request.form.get('username')
                session['logged-in'] = True
                flash(f'You are now logged in.', 'primary')
                return redirect(url_for('index'))

        flash(f'Login details not found. Please try again', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=login_form)


@app.route('/logout')
def logout():
    session.clear()
    flash(f'Thank you for inspiring Women in Tech. See you soon!', 'primary')
    return redirect(url_for('index'))


# Forum routes
@app.route('/forum')
def forum():
    return render_template('forum.html', title='forum', posts=posts.find())


@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    create_post_form = CreatePost()

    if create_post_form.validate_on_submit():
        posts.insert_one({
            'username': session['username'],
            'date': datetime.datetime.utcnow().strftime('%H:%M:%S - %d/%m/%Y'),
            'title': create_post_form.title.data,
            'content': create_post_form.content.data,
            'inspirational_quote': create_post_form.inspirational_quote.data
        })
        flash(f'Post created.', 'primary')
        return redirect(url_for('forum', title='Post created.'))

    return render_template('create-post.html', form=create_post_form)


if __name__ == "__main__":
    app.run(
        host = os.environ.get('IP', '127.0.0.1'),
        port = os.environ.get('PORT', '5000'),
        debug=True
    )