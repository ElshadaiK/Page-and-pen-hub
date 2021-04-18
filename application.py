import os

from dotenv import load_dotenv
from flask import Flask, session, render_template, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '2f217088a246a54d6da5d92c50b499df'
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/about")
def index():
    return "Project One: TODO"

@app.route("/home")
@app.route("/")
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

@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

@app.route('/login')
def register():
    form = LoginForm()
    return render_template('login.html', form=form)