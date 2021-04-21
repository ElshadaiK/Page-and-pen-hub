import os
import csv
from dotenv import load_dotenv
from flask import Flask, session, render_template, url_for, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '2f217088a246a54d6da5d92c50b499df'
bcrypt = Bcrypt(app)
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/about")
def index():
    return "Project One: TODO"

@app.route("/home")
def home():
    books = [
        {
            "title": "heyy",
            "detail": "Detail case",
            "reviews": "Reveiws"
        },
        {
            "title": "heyy",
            "detail": "Detail case",
            "reviews": "Reveiws"
        },
        {
            "title": "heyy",
            "detail": "Detail case",
            "reviews": "Reveiws"
        },
        {
            "title": "heyy",
            "detail": "Detail case",
            "reviews": "Reveiws"
        },
    ]
    return render_template('home.html', books=books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
                db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                               {"username": form.username.data, "email":form.email.data, "password": hashed_password})
                flash(f'Account created for {form.username.data}!', 'success')
                db.commit()
        
        except Exception as e:
            flash(f'Account not created for {e}!', 'error')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Forget any user_id
    # session.clear()

    form = LoginForm()
    if form.validate_on_submit():
        try: 
            Q = db.execute("SELECT * FROM users WHERE email LIKE :email", {"email": form.email.data}).fetchone()

            # User exists ?
            if Q is None:
                 flash(f'User does not exists', 'error')
            # Valid password ?
            elif not (Q and bcrypt.check_password_hash(Q.password, form.password.data)):
                flash(f'Invalid Login', 'error')
            else:
                flash(f'Logged in successfully', 'success')
                

        except Exception as e:
            flash(f'{e}', 'error')

        session["user_id"] = Q.id
        session["email"] = Q.email
        session["username"] = Q.username
        session["logged_in"] = True
        return redirect(url_for("home"))

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('login.html', form=form)
