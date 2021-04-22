import os, requests
import csv
from dotenv import load_dotenv
from flask import Flask, session, render_template, url_for, flash, redirect, request
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


@app.route("/", methods=["GET","POST"])
@app.route("/home", methods=["GET","POST"])
def home():
    books = db.execute("SELECT * from books")   
    # books = [
    #     {
    #         "title": "heyy",
    #         "detail": "Detail case",
    #         "reviews": "Reveiws"
    #     },
    #     {
    #         "title": "heyy",
    #         "detail": "Detail case",
    #         "reviews": "Reveiws"
    #     },
    #     {
    #         "title": "heyy",
    #         "detail": "Detail case",
    #         "reviews": "Reveiws"
    #     },
    #     {
    #         "title": "heyy",
    #         "detail": "Detail case",
    #         "reviews": "Reveiws"
    #     },
    # ]
    print(books)
    if request.method == "GET":
        return render_template("home.html", books=books)
    else:
        if session["logged_in"] == False:
            return redirect(url_for('login'))
        query = request.form.get("input-search")
        if query is None:
            flash(f'Search field can not be empty', 'danger')
        try:
            result = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE :query OR LOWER(title) LIKE :query OR LOWER(author) LIKE :query", {"query": "%" + query.lower() + "%"}).fetchall()
        except Exception as e:
            flash(f'{e}', 'warning')
            return render_template("home.html", books=books)
        if not result:
            flash(f'Your query did not match any documents', 'danger')
            return render_template("home.html", books=books)

        return render_template("list.html", result=result)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session["logged_in"] == True:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
                db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                               {"username": form.username.data, "email":form.email.data, "password": hashed_password})
                flash(f'Account created for {form.username.data}!', 'success')
                db.commit()
        
        except Exception as e:
            flash(f'Account not created for {e}!', 'danger')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session["logged_in"] == True:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        try: 
            Q = db.execute("SELECT * FROM users WHERE email LIKE :email", {"email": form.email.data}).fetchone()

            # User exists ?
            if Q is None:
                 flash(f'User does not exists', 'danger')
            # Valid password ?
            elif not (Q and bcrypt.check_password_hash(Q.password, form.password.data)):
                flash(f'Invalid Login', 'danger')
            else:
                flash(f'Logged in successfully', 'success')
                

        except Exception as e:
            flash(f'{e}', 'warning')

        session["users_id"] = Q.id
        session["email"] = Q.email
        session["username"] = Q.username
        session["password"] = Q.password
        session["logged_in"] = True
        return redirect(url_for("home"))

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    session["logged_in"] = False

    # Redirect user to login index
    return redirect(url_for("home"))


@app.route("/details/<int:bookid>", methods=["GET","POST"])
def details(bookid):
    if session["logged_in"] == False:
        return redirect(url_for('login'))
    if request.method == "GET":
        #Get book details
        result = db.execute("SELECT * from books WHERE id = :id", {"id": bookid}).fetchone()

        #Get API data from Google API
        try:
            google = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{result.isbn}")
        except Exception as e:
            flash(f'API Error {e}!', 'danger')

        # Get comments particular to one book
        comment_list = db.execute("SELECT u.username, u.email, r.review_score, r.review_msg from reviews r JOIN users u ON u.id=r.users_id WHERE books_id = :id", {"id": bookid}).fetchall()
        if not result:
            flash(f'Invalid book id', 'danger')
    
        return render_template("details.html", result=result, comment_list=comment_list , bookid=bookid, google=google.json())
    else:
        ######## Check if the user commented on this particular book before ###########
        user_reviewed_before = db.execute("SELECT * from reviews WHERE users_id = :users_id AND books_id = :book_id",  {"users_id": session["users_id"], "book_id": bookid}).fetchone()
        if user_reviewed_before:
            flash(f'You reviewed this book before!', 'warning')
            return redirect(url_for("details", bookid=bookid))
        ######## Proceed to get user comment ###########
        user_comment = request.form.get("comments")
        user_rating = request.form.get("rating")

        if not user_comment:
            flash(f'Comment section cannot be empty!', 'danger')
            return redirect(url_for("details", bookid=bookid))

        # try to commit to database, raise error if any
        try:
            db.execute("INSERT INTO reviews (users_id, books_id, review_score, review_msg) VALUES (:users_id, :books_id, :review_score, :review_msg)",
                           {"users_id": session["users_id"], "books_id": bookid, "review_score":user_rating, "review_msg": user_comment})
        except Exception as e:
            flash(f'Error occured {e}', 'warning')

        #success - redirect to details page
        db.commit()
        return redirect(url_for("details", bookid=bookid))



if __name__ == '__main__':
    app.run(debug=True)