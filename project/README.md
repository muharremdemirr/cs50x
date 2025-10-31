# ORDERLY
#### Video Demo:  <URL HERE>
#### Description:

Orderly is a flask and SQL based food ordering web application as the final project of CS50x 2025. All food ordering workflow is applied in this project. A database was created for this project to store and manage all the information is used at the workflow. Moreover, Flask is used for creating back-end of project. The application uses Flask-Session to manage user authentication. Login status and role (user or business) are stored in the session to control access to pages and features securely. 

Technologies Used: Python, Flask, SQL, SQLite, HTML, CSS, JavaScript, Bootstrap.

##### Introduction: 
A database-management system (DBMS) is a collection of interrelated data and a set of programs to access those data. The collection of data, usually referred to as the database, contains information relevant to an enterprise. The primary goal of a DBMS is to provide a way to store and retrieve database information that is both convenient and efficient. Database systems are designed to manage large bodies of information. Management of data involves both defining structures for storage of information and providing mechanisms for the manipulation of information. In addition, the database system must ensure the safety of the information stored, despite system crashes or attempts at unauthorized access. If data are to be shared among several users, the system must avoid possible anomalous results. Because information is so important in most organizations, computer scientists have developed a large body of concepts and techniques for managing data. These concepts and techniques form the focus of this book. This chapter briefly introduces the principles of database systems.

##### Purpose Of Application: 
The main purpose of the project is gathering or rather bring together users who want to place order of food with restaurants. We store
all the data created by people and restaurants in our database. The database structure takes place as follows:

###### Schemas:

```sql
CREATE TABLE orders (                                                     
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    total TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'received',
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

```sql
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    subtotal TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    business_id INTEGER NOT NULL,
    business_name TEXT NOT NULL,
    order_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    comment TEXT,
    answer TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
CREATE UNIQUE INDEX unique_order_review
ON reviews (order_id);
```

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    surname TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL,
    phone TEXT NOT NULL DEFAULT '',
    hash TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    province TEXT NOT NULL DEFAULT ''
);
```

```sql
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL,
    phone TEXT NOT NULL DEFAULT '',
    hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'close',
    min_amount REAL DEFAULT 0.0,
    receivable REAL NOT NULL DEFAULT 0.0,
    rating REAL DEFAULT 0.0,
    country TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    province TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT ''
);
```

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    is_for_sale INTEGER DEFAULT 1,
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);
```

##### UI And Features:

This project is built on many pages and features. The pages are as follows:

Login and Register Pages: On these pages, there are two types of forms. The login form requires you to choose whether you are signing in as a customer or a business, and to provide an email address and password. The register page includes an additional field to confirm your password, them register and log the user in. 

Profile Page: Profile page is the page that users and businesses updates or add their info. For instance, name, surname, address etc. In this page businesses see their receivable, and they can change minimum amount of order and status of the restaurant whether open or close. 

In this section, the register page is redirecting people to the this page and this page has a mechanism that guarantees both types of users they can't use app without completing their profile.

Change Password: This menu allows to change your password.

Orders History: This page is a list of orders that placed by users and orders took by business, depending on the user’s role. This page allow user to redirect to leave review page and order details for both.

Reviews:  This page is a list of reviews that left by users and reviews took by business and businesses' answer, depending on the user’s role. In this page businesses can answer the reviews.

Order Details: This page shows details of order selected. Also, it allow businesses to manage status of order like preparing, on the way, completed or canceled.


User Pages:
The user pages represent the pages that are used by the users.

Restaurants: In this page users see the restaurants near their location. 

Restaurant Details: The page provide users info about restaurants and their menu. There is also a tab that allows people to see reviews about restaurant. Plus, there is a condition that prevents that placing order from two different restaurants at the same time.

Cart: Represents the shopping cart of user. User can go to the purchase or clear the cart. Every restaurant own their minimum delivery value, so that there is a condition that prevents creating order that's total is less than the min amount.

Purchase: The purchase page is allows users to buy items selected by credit card. It validate the card using functions in credit.py which from Week 1 and Week 6 Credit problem set.

Leave Reviews: The Page that allows users leave a review for businesses.

Business Pages:
The business pages represent the pages that are used by the businesses.

Dashboard: The main page of businesses. The dashboard is for managing and monitoring active orders received.

Inventory: Inventory page is the page businesses can monitor and manage their product. Whether add or edit products. Set product for sale or not for sale, update name, category, price, description.

 