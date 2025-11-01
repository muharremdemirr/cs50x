import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required, usd, apology
from credit import is_valid, decide_card

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Db connections
db = SQL("sqlite:///orderly.db")
db.execute("PRAGMA foreign_keys = ON")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    # Adds products into the cart
    product_id = request.form.get("product_id")
    business_id = request.form.get("business_id")

    # if there is no order_list
    if "order_list" not in session:
        session["order_list"] = []

    if not product_id:
        flash("Invalid product.")
        return redirect(f"/restaurant-details?restaurant_id={business_id}")

    if not business_id:
        flash("Invalid restaurant.")
        return redirect("/")

    # taking product from db
    product = db.execute("SELECT * FROM products WHERE id = ?", product_id)
    if not product:
        flash("Product not found.")
        return redirect(f"/restaurant-details?restaurant_id={business_id}")
    product = product[0]  # list -> dict

    # wheter is for sale or not
    if not product["is_for_sale"]:
        flash("This product is not for sale.")
        return redirect(f"/restaurant-details?restaurant_id={business_id}")

    # is restaurant open
    business = db.execute("SELECT status FROM businesses WHERE id = ?", business_id)[0]
    if business["status"].lower() == "close":
        flash("Restaurant is currently closed.")
        return redirect("/restaurants")

    # if order list includes product from another restaurant
    if session.get("order_list") and len(session["order_list"]) > 0:
        current_restaurant = session["order_list"][0]["business_id"]
        if str(current_restaurant) != str(business_id):
            flash("There Is Some Product From Another Restaurant In Your Cart", "error")
            session["pending_add"] = {
                "product_id": product_id,
                "business_id": business_id,
            }
            return redirect("/cart")

    # add to cart
    # session["order_list"] represents the cart

    for item in session["order_list"]:
        # if products included by order_list increment quantity
        if item['id'] == product['id']:
            item['quantity'] += 1
            flash(f"{product['name']} added to cart 🛒")
            return redirect(f"/restaurant-details?restaurant_id={business_id}")

    # never bought
    if not product.get('quantity'):
        product['quantity'] = 1
        session["order_list"].append(product)

    flash(f"{product['name']} added to cart 🛒")
    return redirect(f"/restaurant-details?restaurant_id={business_id}")


@app.route("/")
@login_required
def index():
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    if session['role'] == 'user':
        return redirect("/restaurants")
    else:
        return redirect("/dashboard")


@app.route("/cart")
@login_required
def cart():
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    is_hidden = True # controlls is cart empty or not
    total = 0.0
    business_name = ' '
    # if there're some products in the cart
    if len(session["order_list"]) != 0:
        session["order_list"] = [item for item in session["order_list"] if item["is_for_sale"] == 1]
        # calculate the subtotal of every product and total of order
        for item in session["order_list"]:
            item['subtotal'] = float(item['quantity']) * item['price']
            total += item['subtotal']

        is_hidden = False
        business_name = db.execute("SELECT name FROM businesses WHERE id = ?",
                                   session["order_list"][0]['business_id'])[0]['name']

    return render_template("cart.html", order_list=session["order_list"], is_hidden=is_hidden, total=usd(total), business_name=business_name)


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    if request.method == "POST" and request.form.get('password'):
        # role check
        role = session["role"]
        if role == 'user':
            user_hash = db.execute("SELECT hash FROM users WHERE id = ?", session['id'])[0]['hash']
        else:
            user_hash = db.execute("SELECT hash FROM businesses WHERE id = ?",
                                   session['id'])[0]['hash']
        # checks the old password
        if not request.form.get('password'):
            return apology("must provide password", 403)

        if not check_password_hash(user_hash, request.form.get('password')):
            return apology("check your password", 403)

        if not request.form.get('new-password'):
            return apology("must provide new password", 403)

        if not request.form.get('repeat-password'):
            return apology("must provide new password again", 403)
        # new password and confirmation are the same
        if request.form.get('new-password') != request.form.get('repeat-password'):
            return apology("passwords doesn't match")

        hash = generate_password_hash(request.form.get('new-password'))
        # save profile into the database
        if role == 'user':
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session['id'])
        else:
            db.execute("UPDATE businesses SET hash = ? WHERE id = ?", hash, session['id'])

        flash("Password changed successfully!")
        return redirect("/profile")

    return render_template("change.html")


@app.route("/clear-cart", methods=["POST"])
@login_required
def clear_cart():
    session["order_list"] = []

    flash("Cart has been cleared.")
    return redirect(request.referrer)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    # buesiness dashboard, here we manage the orders
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result
    # takes active orders from the database
    orders = db.execute(
        "SELECT * FROM orders WHERE business_id = ? AND status NOT IN ('canceled', 'completed')", session["id"])
    # calculate the total quantity of every order
    for order in orders:
        order['count'] = db.execute("SELECT SUM(quantity) AS total_quantity FROM order_items WHERE order_id = ?",
                                    order['id'])[0]['total_quantity']
        order['address'] = db.execute(
            "SELECT address FROM users WHERE id = ?", order['user_id'])[0]['address']

    return render_template("dashboard.html", orders=orders)


@app.route("/history")
@login_required
def history():
    # order history
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result
    # if signed as user
    if session['role'] == 'user':
        # takes orders from db, newest first
        order_history = db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY date DESC", session['id'])
        # takes the names and reviews of restaurants to show user the business name
        for order in order_history:
            business_name = db.execute(
                "SELECT name FROM businesses WHERE id = ?", order['business_id'])[0]['name']
            order['business_name'] = business_name
            review = db.execute("SELECT * FROM reviews WHERE order_id = ?", order['id'])
            order['review'] = review
    # if signed as business
    else:
        # takes orders from db
        order_history = db.execute(
            "SELECT * FROM orders WHERE business_id = ? ORDER BY date DESC", session['id'])
        # takes customer full name and maske it since privacy
        for order in order_history:
            customer_name = db.execute(
                "SELECT name FROM users WHERE id = ?", order['user_id'])[0]['name']
            customer_surname = db.execute(
                "SELECT surname FROM users WHERE id = ?", order['user_id'])[0]['surname']
            fullname = customer_name + ' ' + customer_surname[0:1]+'***'
            order['customer_name'] = fullname

    return render_template("history.html", order_history=order_history)


@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    # a screen to manage product
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    # edit or add product
    if request.method == 'POST':
        # if new product
        product_id = request.form.get('product_id')
        # to fulfill the form if edit product there is a button and form in front-end file
        if not request.form.get('name'):
            # find product in db
            selected_product = db.execute(
                "SELECT * FROM products WHERE id = ? AND business_id = ?",
                product_id, session['id']
            )[0]
            # update it
            products = db.execute("SELECT * FROM products WHERE business_id = ?", session['id'])
            return render_template("inventory.html", products=products, selected_product=selected_product)

        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        is_for_sale = request.form.get('is_for_sale')

        # check all requirements satisfied
        if not all([name, category, price, description, is_for_sale]):
            return apology("All fields required")

        if float(price) < 0:
            return apology("Invalid price")
        # edit product
        if product_id:
            db.execute("""
                UPDATE products
                SET name = ?, category = ?, price = ?, description = ?, is_for_sale = ?
                WHERE id = ? AND business_id = ?
            """, name, category, round(float(price), 2), description, int(is_for_sale), int(product_id), session['id'])
        # add new product
        else:
            db.execute("""
                INSERT INTO products (business_id, name, category, price, description, is_for_sale)
                VALUES (?, ?, ?, ?, ?, ?)
            """, session['id'], name, category, round(float(price), 2), description, int(is_for_sale))

        return redirect('/inventory')

    products = db.execute("SELECT * FROM products WHERE business_id = ?", session['id'])
    return render_template('inventory.html', products=products)


@login_required
def is_full():
    # if there is missing info
    # especially it guaranties that profiles are fullfilled
    if session['role'] == 'business':
        check = db.execute("SELECT * FROM businesses WHERE id = ?", session['id'])[0]
    else:
        check = db.execute("SELECT * FROM users WHERE id = ?", session['id'])[0]

    required_fields = ['name', 'phone', 'country', 'city', 'province', 'address']
    if session['role'] != 'business':
        required_fields.append('surname')

    is_full = True
    for field in required_fields:
        if check[field] == '':
            is_full = False
            break

    if is_full:
        session['is_full'] = True
    else:
        flash('Need To Complete Your Profile First')
        return redirect('/profile')


@app.route("/leave-review", methods=["POST"])
@login_required
def leave_reviwe():
    # leave review page to create new review
    order = db.execute("SELECT * FROM orders WHERE id = ?", request.form.get('order_id'))[0]
    check = db.execute("SELECT * FROM reviews WHERE order_id = ?", request.form.get('order_id'))
    if len(check) != 0:
        flash("Review has already exist")
        return redirect("/history")

    return render_template("leave_review.html", order=order)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("role"):
            return apology("pick a valid role", 403)

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        if '@'not in request.form.get("email") and '.' not in request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Customer
        if request.form.get("role") == "user":

            # Query database for email
            rows = db.execute(
                "SELECT * FROM users WHERE email = ?", request.form.get("email")
            )

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("invalid email and/or password", 403)

            # Remember which user has logged in
            session["id"] = rows[0]["id"]
            session["role"] = 'user'
            if 'order_list' not in session:
                session["order_list"] = []

        # login for business
        elif request.form.get("role") == "business":
            # Query database for email
            rows = db.execute(
                "SELECT * FROM businesses WHERE email = ?", request.form.get("email")
            )

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("invalid email and/or password", 403)

            # Remember which user has logged in
            session["id"] = rows[0]["id"]
            session["role"] = 'business'

        # Check the db's
        session['is_full'] = False
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/order-details", methods=["POST"])
@login_required
def order_details():
    # A page that shows details of selected order

    order_id = request.form.get('order_id')
    order = db.execute('SELECT * FROM orders WHERE id = ?', order_id)[0]
    order_items = db.execute('SELECT * FROM order_items WHERE order_id = ?', order_id)
    user_info = db.execute("SELECT * FROM users WHERE id = ?", order['user_id'])[0]
    business_info = db.execute("SELECT * FROM businesses WHERE id = ?", order['business_id'])[0]
    review = db.execute("SELECT * FROM reviews WHERE order_id = ?", order_id)

    order['business_name'] = business_info['name']
    order['business_phone'] = business_info['phone']
    order['user_name'] = user_info['name']
    order['user_phone'] = user_info['phone']
    order['review'] = review

    for item in order_items:
        item['product_name'] = db.execute(
            "SELECT name FROM products WHERE id = ?", item['product_id'])[0]['name']

    return render_template('order_details.html', order=order, order_items=order_items)


@app.route("/orders")
@login_required
def orders():
    return redirect("/history")
# Redirects /orders to /history since it's a bit confusing


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    role = session["role"]


    if role == "user":
        data = db.execute("SELECT * FROM users WHERE id = ?", session["id"])[0]
    else:
        data = db.execute("SELECT * FROM businesses WHERE id = ?", session["id"])[0]
        # calculates receivable, app commission and VAT
        receivable = data['receivable']
        commission = receivable * 0.17
        vat = receivable * 0.2
        net = receivable - commission - vat
        data['receivable'] = usd(receivable)
        data['commission'] = usd(commission)
        data['vat'] = usd(vat)
        data['net'] = usd(net)

    # profile info form
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        country = request.form.get("country")
        city = request.form.get("city")
        province = request.form.get("province")
        address = request.form.get("address")

        if not name:
            return apology("must provide proper name", 403)

        if not name.replace(" ","").isalpha() and session['role'] == 'user':
            return apology("must provide proper name", 403)

        if not phone or not phone.isdigit():
            return apology("must provide a phone number")

        if len(phone) < 10 or len(phone) > 15:
            return apology("invalid phone number", 403)

        if not country:
            return apology("must provide a country")

        if not city:
            return apology("must provide a city")

        if not province:
            return apology("must provide a province")

        if not address:
            return apology("must provide an address")

        if not email:
            return apology("must provide an email")

        if role == "user":
        # if email is already registered
            surname = request.form.get("surname")
            if not surname or not surname.isalpha():
                return apology("must provide proper surname", 403)

            check = db.execute("SELECT * FROM users WHERE email = ? AND id != ?",
                               email, session['id'])
            if len(check) != 0:
                return apology("email already exist", 403)

            db.execute(
                "UPDATE users SET name = ?, surname = ?, email = ?, phone = ?, country = ?, city = ?, province = ?, address = ? WHERE id = ?",
                name, surname, email, phone, country, city, province, address, session["id"])
        else:
            # if email is already registered
            check = db.execute(
                "SELECT * FROM businesses WHERE email = ? AND id != ?", email, session['id'])
            if len(check) != 0:
                return apology("email already exist", 403)

            db.execute("UPDATE businesses SET name = ?, email = ?, phone = ?, country = ?, city = ?, province = ?, address = ? WHERE id = ?",
                       name, email, phone, country, city, province, address, session["id"])

        flash("Profile updated successfully!")
        return redirect("/profile")

    return render_template("profile.html", data=data)


@app.route("/purchase", methods=["GET", "POST"])
@login_required
def purchase():

    # payment screen
    total = sum(float(item['price'] * item['quantity']) for item in session['order_list'])
    business_id = session["order_list"][0]['business_id']
    min_amount = db.execute("SELECT min_amount FROM businesses WHERE id = ?", business_id)[0]['min_amount']
    # check min order amount of restaurant
    if total < min_amount:
        flash(f"Order Total Must Be Greater Than Min Order Value. You Need To Add: {min_amount - total}")
        return redirect(f"/restaurant-details?restaurant_id={business_id}")

    if request.method == 'POST' and request.form.get('from_purchase'):

        # whether card is valid or not uses credit.py from week 6
        if not is_valid(request.form.get('card-number')):
            return apology("enter valid card number", 400)

        if not decide_card(request.form.get('card-number')):
            return apology("enter valid card number", 400)
        if not request.form.get('name'):
            return apology("must provide a name", 403)

        name = request.form.get('name').replace(' ', '')
        if not name.isalpha():
            return apology("enter valid name", 400)

        if int(request.form.get('cvv')) < 100 or int(request.form.get('cvv')) > 999:
            return apology("enter valid CVV", 400)

        if int(request.form.get('skt-year')) < datetime.now().year:
            return apology("must enter valid expiration date", 400)

        if int(request.form.get('skt-year')) == datetime.now().year and int(request.form.get('skt-month')) < datetime.now().month:
            return apology("must enter valid expiration date", 400)


        # adds order history
        db.execute("INSERT INTO orders (business_id, user_id, total, status) VALUES (?, ?, ?, ?)",
                   business_id, session['id'], usd(total), 'received'
                   )
        # takes id of newest order
        order_id = db.execute("SELECT id FROM orders WHERE business_id = ? AND user_id = ? ORDER BY id DESC LIMIT 1",
                              business_id, session["id"]
                              )[0]['id']

        # adds the order items
        for item in session["order_list"]:
            db.execute("INSERT INTO order_items (order_id, product_id, price, quantity, subtotal) VALUES (?, ?, ?, ?, ?)",
                       order_id, item['id'], usd(item['price']), item['quantity'], usd(
                           item['quantity'] * item['price'])
                       )
        # clear the cart
        session["order_list"] = []

        flash("Purchase successful!")
        return redirect("/history")

    else:
        # load page
        return render_template("purchase.html", amount=total)


@app.route("/set-min", methods=["POST"])
@login_required
def set_min():
    # setting min amount of order
    if not request.form.get('min-amount'):
        return apology("Provide Min Order Amount", 403)

    if float(request.form.get('min-amount')) < 0.0:
        return apology("Inalid Min Order Amount", 403)

    if session['role'] != 'business':
        return apology("Unauthorized", 403)

    db.execute("UPDATE businesses SET min_amount = ? WHERE id = ?",
               float(request.form.get('min-amount')), session['id'])
    flash(f"Minimum Order Amount changed to {float(request.form.get('min-amount'))}")
    return redirect("/profile")


@app.route("/set-state", methods=["POST"])
@login_required
def set_state():
    # setting state of the restaurant whether it's open or close
    if session.get("role") != "business":
        return apology("Unauthorized", 403)

    if request.form.get("state") not in ("open", "close"):
        return apology("Unauthorized", 403)

    business_id = session.get("id")
    new_state = request.form.get("state")

    # if profile not fullfilled it's not allowed to open the restaurant
    if new_state == 'open':
        if not session['is_full']:
            result = is_full()
            if result:
                return result

    db.execute("UPDATE businesses SET status = ? WHERE id = ?", new_state, business_id)
    flash(f"Business status changed to {new_state}.")
    return redirect("/profile")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Clear the other user data
    session.clear()

    if request.method == "POST":
        if not request.form.get("role"):
            return apology("pick a valid role", 403)

        if not request.form.get("email"):
            return apology("must provide valid email", 400)

        if '@'not in request.form.get("email") and '.' not in request.form.get("email"):
            return apology("must provide email", 403)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("must enter your password again", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be same", 400)

        if request.form.get("role") == 'user':
            user = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
            if len(user) >= 1:
                return apology("email is already exist", 400)
            else:
                new_id = db.execute(
                    "INSERT INTO users (email, hash) VALUES(?, ?)",
                    request.form.get("email"),
                    generate_password_hash(request.form.get("password")),
                )

                # log user in
                session["id"] = new_id
                # decide the role
                session["role"] = 'user'
                # creates cart
                session["order_list"] = []

        elif request.form.get("role") == 'business':
            business = db.execute("SELECT * FROM businesses WHERE email = ?",
                                  request.form.get("email"))
            if len(business) >= 1:
                return apology("email is already exist", 400)
            else:
                new_id = db.execute("INSERT INTO businesses (email, hash) VALUES (?, ?)",
                                    request.form.get("email"),
                                    generate_password_hash(request.form.get("password"))
                                    )

                # log user in
                session["id"] = new_id
                # decide the role
                session["role"] = 'business'

        # creates profile control flag
        session['is_full'] = False
        # Redirect user to home page
        return redirect("/")
    else:
        # register page
        return render_template("register.html")


@app.route("/restaurant-details", methods=["GET", "POST"])
def restaurant_details():
    # POST
    if request.form.get('restaurant_id'):
        restaurant_id = request.form.get('restaurant_id')
    # GET
    elif request.args.get('restaurant_id'):
        restaurant_id = request.args.get('restaurant_id')

    if not restaurant_id:
        flash("Something Went Wrong", "error")
        return redirect("/")

    # gets the products from db
    restaurant_menu = db.execute(
        "SELECT * FROM products WHERE business_id = ? ORDER BY category", restaurant_id)

    # format the price
    for product in restaurant_menu:
        product['price'] = usd(product['price'])

    # gets restaurants info
    restaurant_info = db.execute("SELECT * FROM businesses WHERE id = ?", restaurant_id)[0]
    # gets reviews
    reviews = db.execute("SELECT * FROM reviews WHERE business_id = ?", restaurant_id)

    restaurant_info['min_amount'] = usd(restaurant_info['min_amount'])

    # acitivate menu tab
    # whether button clicked shows that menu
    active_tab = request.form.get('active_tab', 'menu')

    return render_template("restaurant_details.html",
                           restaurant_info=restaurant_info,
                           restaurant_menu=restaurant_menu,
                           reviews=reviews,
                           active_tab=active_tab
                           )


@app.route("/restaurants", methods=["GET", "POST"])
def restaurants():
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    user_info = db.execute(
        "SELECT country, city, province FROM users WHERE id = ?", session['id'])[0]

    # takes near restaurants that actually same province
    restaurants = db.execute("""
        SELECT * FROM businesses
        WHERE country = ? AND city = ? AND province = ?
        ORDER BY CASE WHEN status = 'open' THEN 0 ELSE 1 END, rating DESC""",
                             user_info['country'], user_info['city'], user_info['province'])

    for r in restaurants:
        r['min_amount'] = usd(r['min_amount'])
    return render_template("restaurants.html", restaurants=restaurants)


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    # checks the profile info
    if not session['is_full']:
        result = is_full()
        if result:
            return result

    if request.method == 'POST':  # POST
        # if a customer will leave a review
        if request.form.get('order_id') and session['role'] == 'user':
            if not request.form.get('rating'):
                return apology("must give a rating", 403)

            order_info = db.execute(
                "SELECT id, business_id FROM orders WHERE id = ?", request.form.get('order_id'))[0]

            user_info = db.execute("SELECT name, surname FROM users WHERE id = ?", session['id'])[0]
            # maskes last name
            user_info['surname'] = user_info['surname'][:2] + '***'
            user_name = user_info['name'] + ' ' + user_info['surname']

            business_name = db.execute(
                "SELECT name FROM businesses WHERE id = ?", order_info['business_id'])[0]['name']

            rating = request.form.get('rating')
            comment = request.form.get('comment')

            db.execute("INSERT INTO reviews (user_id, user_name, business_id, business_name, order_id, rating, comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       session['id'], user_name, order_info['business_id'], business_name, order_info['id'], rating, comment
                       )
            # calculates new rating of business
            avg = db.execute("SELECT ROUND(AVG(rating), 2) AS avg FROM reviews WHERE business_id = ?",
                             order_info['business_id'])[0]['avg']
            db.execute("UPDATE businesses SET rating = ? WHERE id = ?",
                       round(avg, 2), order_info['business_id'])
            return redirect('/review')

        # if a business wants to give answer
        elif request.form.get('order_id') and session['role'] == 'business':
            check = db.execute("SELECT * FROM reviews WHERE order_id = ?",
                               request.form.get('order_id'))
            # checks review exist
            if len(check) != 1:
                return apology("a review does not exist", 403)
            # save answer
            db.execute("UPDATE reviews SET answer = ? WHERE order_id = ?",
                       request.form.get('answer'), request.form.get('order_id'))

            return redirect('/review')

        # fech the comments left for restaurant
        elif request.form.get('business_id'):
            # fetch all comments
            reviews = db.execute("SELECT * FROM reviews WHERE business_id = ?", request.form.get('business_id'))
            # calculates own rating
            avg = db.execute("SELECT ROUND(AVG(rating), 2) AS avg FROM reviews WHERE business_id = ?", session['id'])
            avg_rating = avg[0]["avg"] if avg and avg[0]["avg"] else 'No Review Yet'

            return render_template("reviews.html", reviews=reviews, avg_rating=avg_rating)

    else:  # GET
        # comments made by user
        if session['role'] == 'user':
            reviews = db.execute("SELECT * FROM reviews WHERE user_id = ?", session['id'])
            return render_template("reviews.html", reviews=reviews)

        # comments made for business
        else:
            reviews = db.execute("SELECT * FROM reviews WHERE business_id = ?", session['id'])
            avg = db.execute("SELECT ROUND(AVG(rating), 2) AS avg FROM reviews WHERE business_id = ?", session['id'])
            avg_rating = avg[0]["avg"] if avg and avg[0]["avg"] else 'No Review Yet'
            return render_template("reviews.html", reviews=reviews, avg_rating=avg_rating)


@app.route("/update-status", methods=["GET", "POST"])
@login_required
def update_status():
    # updates orders' status
    current_status = db.execute("SELECT status FROM orders WHERE id = ?",request.form.get('order_id'))[0]['status']
    # restaurants can't change status of orders that already completed or canceled
    if current_status in ['completed', 'canceled']:
        flash("Completed and Canceled orders can't be changed.")
        return redirect('/')

    db.execute("UPDATE orders SET status = ? WHERE id = ?",
               request.form.get('status'),
               request.form.get('order_id')
               )
    flash("Status of order changed.", "success")

    # if the order completed so restaurant earns the receivable
    if request.form.get('status') == 'completed':
        total_raw = db.execute("SELECT total FROM orders WHERE id = ?", request.form.get('order_id'))[0]['total']
        # I used usd format and TEXT at db sometimes it crashes, so Chat GPT recommended try catch blocks
        try:
            total = float(total_raw.replace('$', '').replace(',', ''))
        except:
            total = float(total_raw)
        # calculate receivable of restaurant
        receivable = db.execute("SELECT receivable FROM businesses WHERE id = ?", session['id'])[0]['receivable']
        receivable += total
        # save to db
        db.execute("UPDATE businesses SET receivable = ? WHERE id = ?",
                   round((receivable), 2), session['id']
                   )
    return redirect('/')
