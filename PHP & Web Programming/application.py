import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

#Make sure API key is set

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Identify current user by id
    current_user = db.execute("SELECT cash FROM users where id = :curr_user", curr_user=session["user_id"])

    # Look up stock info
    stock_list = db.execute("SELECT symbol, share_price, SUM(share_qty) as share_total FROM transactions WHERE user_id = :curr_user GROUP BY symbol HAVING share_total > 0",
                            curr_user=session["user_id"])

    # Create portfolio
    portfolio = {}

    for stock in stock_list:
        portfolio[stock["symbol"]] = lookup(stock["symbol"])

    # current balance
    balance = current_user[0]["cash"]


    return render_template("portfolio.html", portfolio=portfolio, stock_list=stock_list, balance=balance)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        # Check for Symbol
        if quote == None:
            return apology("invalid symbol")

        # Check for whole #
        try:
            share_qty = int(request.form.get("shares"))
        except:
            return apology("shares must be a positive integer")

        # Check shares are positive #
        if share_qty <= 0:
            return apology("shares must be greater than 0")

        # Get us
        rows = db.execute("SELECT cash from users WHERE id = :user_id", user_id=session["user_id"])

        # Check cash balance
        current_cash = rows[0]["cash"]
        share_price = quote["price"]

        # Find total price
        price = share_price * share_qty

        # Check that sale
        if price > current_cash:
            return apology("need more funds")

        # Update the cash field
        db.execute("UPDATE users SET cash = cash - :cost WHERE id = :user_id", cost=price, user_id=session["user_id"])

        # Put transaction to transactions database
        db.execute("INSERT INTO transactions (user_id, symbol, share_qty, share_price) VALUES(:user_id, :symbol, :quantity, :price)",
                    user_id=session["user_id"], symbol=request.form.get("symbol"), quantity=share_qty, price=share_price)

        flash("Purchased!", 200)

        return redirect(url_for('index'))

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = request.args.get("username")

    usernames = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    if usernames:
        return jsonify(False)
    else:
        return jsonify(True)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get time in db in chrono order
    transact_list = db.execute("SELECT symbol, share_qty, share_price, chrono FROM transactions where user_id = :curr_user ORDER BY chrono ASC",
                                curr_user=session["user_id"])

    return render_template("history.html", transactions=transact_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Clear user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check username
        if not request.form.get("username"):
            return apology("must provide username")

        # Check password
        elif not request.form.get("password"):
            return apology("must provide password")

        # Find us
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Check username and pw correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect  to home page
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        if quote == None:
            return apology("invalid stock symbol")

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        un = request.form.get("username")
        pw = request.form.get("password")

        if not un:
            return apology("You must provide an username!", 400)
        elif not pw:
            return apology("Missing password", 400)
        elif not request.form.get("confirmation"):
            return apology("Password does not match", 400)
        elif pw != request.form.get("confirmation"):
            return apology("Password does not match", 400)
        elif db.execute("SELECT * FROM users WHERE username = :username",
                        username=un):
            return apology("Username already exists", 400)
        hash_pw = generate_password_hash(pw)
        table = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=un, hash=hash_pw)
        session["user_id"] = table
        flash("Registered!")
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
def password():
    """Change"""
    # User reached route via POST
    if request.method == "POST":

        # Check us
        if not request.form.get("username"):
            return apology("must provide username")

        # Check old password
        elif not request.form.get("oldpassword"):
            return apology("must provide password")

         # check new pw
        elif not request.form.get("newpassword"):
            return apology("must provide new password")

        # check pw match
        if request.form.get("newpassword") != request.form.get("newconfirmation"):
            return apology("passwords do not match")

        # Find username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # check us and pw correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            return apology("invalid username and/or password")

        # Make Pw #
        hash = generate_password_hash(request.form.get("newpassword"))

        # Write us and # database
        rows = db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", user_id=session["user_id"], hash=hash)


        flash("Password Changed!", 200)

        return redirect("/")

    else:
        return render_template("password.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

    # Check symbol
        if quote == None:
            return apology("invalid symbol")

        try:
            share_qty = int(request.form.get("shares"))
        except:
            return apology("shares must be a positive integer")

        if share_qty <= 0:
            return apology("must be greater than 0")

        # double check shares to sell
        stock_list = db.execute("SELECT SUM(share_qty) as share_total FROM transactions WHERE user_id = :curr_user AND symbol = :symbol GROUP BY symbol",
                                curr_user=session["user_id"], symbol=request.form.get("symbol"))

        # Error handling
        if len(stock_list) != 1:
            return apology("you do not own stock")
        elif stock_list[0]["share_total"] <= 0:
            return apology("select a positive value")
        elif stock_list[0]["share_total"] < share_qty:
            return apology("you do not have enough shares")

        # Retrieve user's cash from database
        user_query = db.execute("SELECT cash FROM users WHERE id = :curr_user", curr_user=session["user_id"])
        balance = user_query[0]["cash"]

        # Calculate sale revenue
        share_price = quote["price"]
        sale = share_price * share_qty

        # Update user's cash on database
        db.execute("UPDATE users SET cash = cash + :sale WHERE id = :curr_user", sale=sale, curr_user=session["user_id"])

        # Update transaction record
        db.execute("INSERT INTO transactions (user_id, symbol, share_qty, share_price) VALUES(:curr_user, :symbol, :share_qty, :share_price)",
                    curr_user=session["user_id"], symbol=request.form.get("symbol"), share_qty=-share_qty, share_price=share_price)

        flash("Sale successful!", 200)

        return redirect(url_for("index"))

    #  redirect stock list
    else:
        stock_list = db.execute("SELECT symbol, SUM(share_qty) as share_total FROM transactions WHERE user_id = :curr_user GROUP BY symbol HAVING share_total > 0",
                                curr_user=session["user_id"])

    return render_template("sell.html", stock_list=stock_list)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
