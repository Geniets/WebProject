from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kl35B1855@'
app.config['MYSQL_DB'] = 'projecttrip'
app.secret_key = 'supersecretkey'

mysql = MySQL(app)

@app.route("/")
def form():
    return render_template("home.html")



@app.route("/tres", methods=['GET', 'POST'])
def res():
    dbconn = mysql.connection
    cursor = dbconn.cursor()

    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    # If it's a POST request, process filters
    if request.method == 'POST':
        # Search by name (if provided)
        name = request.form.get('searchr')
        if name:
            query += " AND name LIKE %s"
            params.append('%' + name + '%')

        # Filter by rating (if provided)
        rating = request.form.get('rating')
        if rating:
            rating = float(rating) 
            query += " AND rating >= %s"  
            params.append(rating)

        # Filter by price range (if provided)
        price_range = request.form.get('price_range')
        if price_range:
            if price_range == 'low':
                query += " AND price_range <= 10"
            elif price_range == 'medium':
                query += " AND price_range BETWEEN 11 AND 30"
            elif price_range == 'high':
                query += " AND price_range > 30"

        
        country = request.form.get('country')
        if country:
            country = country.lower()
            query += " AND country = %s"
            params.append(country)

    
    cursor.execute(query, params)
    resulttt = cursor.fetchall()
    cursor.close()

    
    return render_template("top_rest.html", rest=resulttt)

@app.route("/des", methods=['GET', 'POST'])
def des():
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    if request.method == 'POST':
        name = request.form.get('searchd')
        cursor.execute("SELECT * FROM destination WHERE Attraction LIKE %s", ('%' + name + '%',))
        resulttt = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM destination")
        resulttt = cursor.fetchall()
    cursor.close()
    return render_template("top_dest.html", dest=resulttt)

@app.route("/search", methods=['POST'])
def search():
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    country = request.form.get('search').lower()
    cursor.execute("SELECT * FROM countries WHERE name = %s", (country,))
    listing = cursor.fetchone()
    cursor.close()
    
    if listing:
        return redirect(url_for('show_listing', listing_id=listing[0]))
    else:
        return render_template("no_listing.html", country=country), 404


@app.route("/listing/<int:listing_id>")
def show_listing(listing_id):
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("SELECT * FROM countries WHERE country_id = %s", (listing_id,))
    listing = cursor.fetchone()
    cursor.execute("SELECT * FROM restaurants WHERE country_id = %s", (listing_id,))
    rest = cursor.fetchall()
    cursor.execute("SELECT * FROM dest WHERE country_id = %s", (listing_id,))
    dest = cursor.fetchall()
    cursor.execute("SELECT * FROM packages WHERE country_id = %s", (listing_id,))
    pack = cursor.fetchall()
    cursor.close()
    
    if listing:
        return render_template("project_us.html", listing=listing, rest=rest, dest=dest,pack=pack)
    else:
        return "Listing not found.", 404

@app.route("/detail/<int:destination_id>")
def detail(destination_id):
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("SELECT * FROM dest WHERE destination_id = %s", (destination_id,))
    destination = cursor.fetchone()
    cursor.close()
    
    if destination:
        return render_template("detail.html", dest=destination)
    else:
        return "Destination not found", 404

@app.route("/restdetail/<int:restaurant_id>")
def restdetail(restaurant_id):
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
    restaurant = cursor.fetchone()
    cursor.close()
    
    if restaurant:
        return render_template("restdetail.html", rest=restaurant)
    else:
        return "restaurant not found", 404
@app.route("/packdetail/<int:Package_id>")
def packdetail(Package_id):
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("SELECT * FROM packages WHERE Package_id = %s", (Package_id,))
    package = cursor.fetchone()
    cursor.close()
    
    if package:
        return render_template("packdetail.html", pack=package)
    else:
        return "restaurant not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return render_template('home.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, hashed_password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/packages')
def pack():
    return render_template("packages.html")

@app.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    item_id = request.form.get('item_id')  # ID of the restaurant or destination
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description', '')
    item_cuisine = request.form.get('item_cuisine', None)  # Default to None if not provided
    item_type = request.form.get('item_type')  # 'restaurant' or 'destination'
    item_loc = request.form.get('item_loc', '')  # Default to empty string

    try:
        dbconn = mysql.connection
        cursor = dbconn.cursor()

        # Check if the item already exists in the wishlist
        cursor.execute('''
            SELECT COUNT(*) FROM wishlist WHERE user_id = %s AND item_id = %s
        ''', (user_id, item_id))
        result = cursor.fetchone()

        if result[0] > 0:  # If the count is greater than 0, item already exists
            return "Item already exists in your wishlist."

        # Insert the item into the wishlist
        cursor.execute('''
            INSERT INTO wishlist (user_id, item_id, item_name, item_description, item_cuisine, item_type, item_loc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, item_id, item_name, item_description, item_cuisine, item_type, item_loc))

        dbconn.commit()
        return redirect(url_for('view_wishlist'))

    except Exception as e:
        print(f"Error while adding to wishlist: {e}")
        # Show a generic error to the user
        return "There was an error adding the item to your wishlist. Please try again later."

    finally:
        if cursor:
            cursor.close()



@app.route('/wishlist')
def view_wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT wishlist_id, item_id, item_name, item_description, item_cuisine, item_type,item_loc
            FROM wishlist
            WHERE user_id = %s
        """, (user_id,))
        wishlist = cursor.fetchall()
        
        # Filter items by type
        restaurants = [item for item in wishlist if item['item_type'] == 'restaurant']
        destinations = [item for item in wishlist if item['item_type'] == 'destination']
    except Exception as e:
        print(f"Database error: {e}")
        wishlist, restaurants, destinations = [], [], []
    finally:
        cursor.close()

    return render_template('wishlist.html', wishlist=wishlist, restaurants=restaurants, destinations=destinations)



@app.route('/wishlist/remove/<int:wishlist_id>', methods=['POST'])
def remove_from_wishlist(wishlist_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    dbconn = mysql.connection
    cursor = dbconn.cursor()
    try:
        cursor.execute('DELETE FROM wishlist WHERE wishlist_id = %s AND user_id = %s', (wishlist_id, session['user_id']))
        dbconn.commit()
        flash('Item removed from your wishlist!', 'success')
    except Exception as e:
        flash('There was an error removing the item. Please try again.', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('view_wishlist'))



@app.route('/payment/<int:package_id>', methods=['GET'])
def payment(package_id):
    # Fetch package details based on the package_id
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM packages WHERE Package_id = %s", (package_id,))
    package = cursor.fetchone()
    cursor.close()

    if not package:
        return "Package not found", 404  # Handle case where package doesn't exist

    # Pass package details to the payment template
    return render_template('payment.html', package=package)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    package_id = request.form['package_id']
    cardholder_name = request.form['cardholder_name']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    # Process the payment logic (e.g., save details, call a payment gateway, etc.)
    # Here, you could also save the transaction details in the database.

    # Example: Save transaction in database
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO transaction (package_id, cardholder_name, card_number, expiry_date, cvv)
        VALUES (%s, %s, %s, %s, %s)
    """, (package_id, cardholder_name, card_number, expiry_date, cvv))
    mysql.connection.commit()
    cursor.close()

    # Redirect to a success page or display a success message
    return render_template("success.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    msg = ''
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Insert the data into the database or send an email
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO contact_us (name, email, message)
                VALUES (%s, %s, %s)
            """, (name, email, message))
            mysql.connection.commit()
            msg = 'Your message has been sent. We will get back to you soon!'
        except Exception as e:
            print(f"Error: {e}")
            msg = 'There was an issue submitting your message. Please try again.'
        finally:
            cursor.close()

    return render_template('contact.html', msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
