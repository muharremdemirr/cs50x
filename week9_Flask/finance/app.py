import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from credit import is_valid, decide_card
from datetime import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    total = 0

    portfolio = db.execute(
        "SELECT symbol, shares FROM portfolios WHERE user_id = ?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    for stock in portfolio:
        stock_info = lookup(stock['symbol'])

        total += stock_info['price'] * stock['shares']  # total amount

        stock['symbol'] = stock_info['symbol']  # capitalized
        stock['price'] = usd(stock_info['price'])  # portfolios price info
        stock['total'] = usd(stock_info['price'] * stock['shares'])  # total per stock

    return render_template("portfolio.html", portfolio=portfolio, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    cash_before = float(db.execute("SELECT cash FROM users WHERE id = ?",
                        session["user_id"])[0]["cash"])

    if request.method == 'POST':
        amount = 0
        shares = request.form.get('shares')
        stock = lookup(request.form.get('symbol'))

        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares", 400)

        if not request.form.get('symbol'):
            return apology("enter a stock symbol", 400)

        if not stock:
            return apology("invalid symbol", 400)

        if cash_before < float(stock['price']) * int(shares):
            return apology("not enough cash", 400)

        shares = int(shares)
        amount = float(stock['price']) * shares
        cash_after = cash_before - amount

        check = db.execute("SELECT * FROM portfolios WHERE user_id = ? AND symbol = ?",
                           session["user_id"], stock['symbol'])

        if len(check) > 0:  # If already bought
            number_of_stock = check[0]["shares"] + shares
            db.execute("UPDATE portfolios SET shares = ? WHERE user_id = ? AND symbol = ?",
                       number_of_stock, session["user_id"], stock['symbol'])

        else:  # If never
            db.execute("INSERT INTO portfolios (user_id, symbol, shares) VALUES (?, ?, ?)",
                       session["user_id"], stock['symbol'], shares)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_after, session["user_id"])
        db.execute("INSERT INTO history (user_id, symbol, shares, price, total, cash_before, cash_after, transaction_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   session["user_id"], stock['symbol'], shares, usd(stock['price']), usd(
                       amount), usd(cash_before), usd(cash_after), "BUY"
                   )

        flash("Shares bought successfully!")
        return redirect("/")

    return render_template("buy.html", cash=usd(cash_before))


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "POST":

        if not request.form.get('password'):
            return apology("must provide password", 403)

        if not check_password_hash(db.execute("SELECT hash FROM users WHERE id = ?", session['user_id'])[0]['hash'], request.form.get('password')):
            return apology("check your password", 403)

        if not request.form.get('new-password'):
            return apology("must provide new password", 403)

        if not request.form.get('repeat-password'):
            return apology("must provide new password again", 403)

        if request.form.get('new-password') != request.form.get('repeat-password'):
            return apology("passwords doesn't match")

        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(request.form.get('new-password')), session['user_id']
                   )

        flash("Password changed successfully!")
        return redirect("/")

    return render_template("change.html")


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():

    if request.method == 'POST':

        if float(request.form.get('money')) <= 0:
            return apology("enter a valid amount", 400)

        if not is_valid(request.form.get('card-number')):
            return apology("enter valid card number", 400)

        if not decide_card(request.form.get('card-number')):
            return apology("enter valid card number", 400)

        if int(request.form.get('cvv')) < 100 and request.form.get('cvv') > 999:
            return apology("enter valid CVV", 400)

        if int(request.form.get('skt-year')) < datetime.now().year:
            return apology("must enter valid expiration date", 400)

        if int(request.form.get('skt-year')) == datetime.now().year and int(request.form.get('skt-month')) < datetime.now().month:
            return apology("must enter valid expiration date", 400)

        cash_before = db.execute("SELECT cash FROM users WHERE id = ?",
                                 session['user_id'])[0]['cash']
        amount = float(request.form.get('money'))
        cash_after = cash_before + amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_after, session['user_id'])

        db.execute("INSERT INTO history (user_id, symbol, shares, price, total, cash_before, cash_after, transaction_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   session["user_id"], "-", "-", "-", usd(amount), usd(
                       cash_before), usd(cash_after), "DEPOSIT"
                   )

        return render_template("deposit.html", deposit_amount=amount, cash_before=cash_before, cash_after=cash_after)

    return render_template("deposit.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute("SELECT * FROM history WHERE user_id = ?", session['user_id'])

    return render_template("history.html", history=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

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

    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        stock = lookup(stock_symbol)
        if not stock:
            return apology("stock not found", 400)
        stock['price'] = usd(stock['price'])
        return render_template("quote.html", company=stock)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Clear the other user data
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide proper username", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("must enter your password again", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be same", 400)

        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(user) >= 1:
            return apology("the username is already taken", 400)
        else:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password"))
            )

            # log user in
            session["user_id"] = db.execute(
                "SELECT id FROM users WHERE username = ?", request.form.get("username"))[0]['id']

            # Redirect user to home page
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        user_share = db.execute("SELECT shares FROM portfolios WHERE user_id = ? AND symbol = ?",
                                session["user_id"], request.form.get('symbol').upper())[0]['shares']

        if not request.form.get('symbol'):
            return apology("invalid symbol", 400)

        if not lookup(request.form.get('symbol')):
            return apology("invalid symbol", 400)

        if not request.form.get('shares'):
            return apology("invalid amount of shares", 400)

        if int(request.form.get('shares')) < 0:
            return apology("you provide invalid amount of shares", 400)

        if user_share < int(request.form.get('shares')):
            return apology("invalid amount of shares in portfolio", 400)

        cash_before = float(db.execute("SELECT cash FROM users WHERE id = ?",
                            session["user_id"])[0]["cash"])

        sold_shares = int(request.form.get('shares'))
        symbol = request.form.get('symbol')
        stock = lookup(symbol)

        price = stock['price']
        total = price * sold_shares
        cash_after = cash_before + total
        user_share -= sold_shares

        if user_share == 0:
            db.execute("DELETE from portfolios WHERE user_id = ? AND symbol = ?",
                       session['user_id'], stock['symbol'])
        else:
            db.execute("UPDATE portfolios SET shares = ? WHERE user_id = ? AND symbol = ?",
                       user_share, session['user_id'], stock['symbol'])

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_after, session['user_id'])
        db.execute("INSERT INTO history (user_id, symbol, shares, price, total, cash_before, cash_after, transaction_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   session['user_id'], stock['symbol'], sold_shares, usd(price), usd(total), usd(cash_before), usd(cash_after), "SELL")

        flash("Shares successfully sold!")
        return redirect("/")

    stocks = db.execute("SELECT symbol FROM portfolios WHERE user_id = ?", session['user_id'])

    return render_template("sell.html", stocks = stocks)
