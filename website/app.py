from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="poultry_auth"
)

UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            # Debug statements to check received data
            print(f"Received data: name={name}, email={email}, message={message}")

            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)',
                (name, email, message))
            db.commit()
            cursor.close()

            flash('Message sent successfully')
            return redirect(url_for('contact'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            print(f"Database error: {err}")
        except Exception as e:
            flash(f"Error: {e}")
            print(f"Error: {e}")
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) AS total_users FROM users')
    result = cursor.fetchone()
    cursor.close()
    total_users = result['total_users'] if result else 0
    return render_template('dashboard.html', total_users=total_users)


@app.route('/categories')
def categories():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()
    cursor.close()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    sort_description = request.form['sort_description']
    full_description = request.form['full_description']
    product_tags = request.form['product_tags']

    # Check if the post request has the file part
    if 'category_image' not in request.files:
        flash('No file part')
        return redirect(request.url)

    category_image = request.files['category_image']

    # If the user does not select a file, browser also
    # submit an empty part without filename
    if category_image.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # Check if the file extension is allowed
    if not allowed_file(category_image.filename):
        flash('File not allowed. Allowed file types are png, jpg, jpeg, gif.')
        return redirect(request.url)

    # Save the file to the upload folder
    filename = secure_filename(category_image.filename)
    category_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_url = os.path.join('static', 'uploads', filename)  # Adjusted path for URL

    try:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO categories (name, sort_description, full_description, product_tags, image_url) VALUES (%s, %s, %s, %s, %s)',
            (name, sort_description, full_description, product_tags, image_url)
        )
        db.commit()
        cursor.close()
        flash('Category added successfully')
    except mysql.connector.Error as err:
        flash(f"Database error: {err}")
        print(f"Database error: {err}")
    except Exception as e:
        flash(f"Error: {e}")
        print(f"Error: {e}")

    return redirect(url_for('categories'))



@app.route('/new_products', methods=['GET', 'POST'])
def new_products():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    cursor.close()
    
    if request.method == 'POST':
        product_name = request.form['productName']
        category_id = request.form['categories']
        slug = request.form['slug']
        sort_description = request.form['description']
        colors = ','.join(request.form.getlist('colors'))
        sizes = ','.join(request.form.getlist('sizes'))
        price = request.form['price']
        quantity = request.form['quantity']
        full_detail = request.form['fullDetail']
        product_tags = request.form['tags']

        image_url = None
        if 'category_image' in request.files:
            file = request.files['category_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = filepath  # Store the path to the image

        try:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO products (product_name, category_id, slug, sort_description, colors, sizes, price, quantity, full_detail, product_tags, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (product_name, category_id, slug, sort_description, colors, sizes, price, quantity, full_detail, product_tags, image_url)
            )
            db.commit()
            cursor.close()

            flash('Product added successfully')
            return redirect(url_for('new_products'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
        except Exception as e:
            flash(f"Error: {e}")

    return render_template('new_products.html', categories=categories)

@app.route('/order_history')
def order_history():
    return render_template('order_history.html')

def execute_query(connection, query, params=None):
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor
    except Error as e:
        print(f"Error executing query: {e}")
        return None

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')


@app.route('/blogs_list')
def blogs_list():
    try:
        cursor = db.cursor(dictionary=True)
        # SQL query to fetch all blog details
        sql = "SELECT * FROM blogs ORDER BY blog_date DESC"
        cursor.execute(sql)
        blogs = cursor.fetchall()
        cursor.close()

    except mysql.connector.Error as e:
        print(f"Error fetching data from database: {str(e)}")
        blogs = []

    return render_template('blogs.html', blogs=blogs)


@app.route('/products_by_category/<int:category_id>')
def products_by_category(category_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM products WHERE category_id = %s', (category_id,))
        products = cursor.fetchall()
        cursor.close()
        return jsonify({'products': products})
    except mysql.connector.Error as e:
        print(f"Error fetching products: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500




@app.route('/post_blog', methods=['POST'])
def post_blog():
    if request.method == 'POST':
        try:
            # Fetching form data
            blog_image = request.files['blog-image']
            blog_title = request.form['blog-title']
            blog_text = request.form['blog-text']
            blog_date = request.form['blog-date']

            # Validate file upload
            if blog_image.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if blog_image and allowed_file(blog_image.filename):
                filename = secure_filename(blog_image.filename)
                blog_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join('static', 'uploads', filename)  # Adjusted path for URL

                # Insert blog data into database
                cursor = db.cursor()
                cursor.execute(
                    'INSERT INTO blogs (image_url, title, content, blog_date) VALUES (%s, %s, %s, %s)',
                    (image_url, blog_title, blog_text, blog_date)
                )
                db.commit()
                cursor.close()

                flash('Blog posted successfully')
                return redirect(url_for('blogs_list'))
            else:
                flash('File not allowed. Allowed file types are png, jpg, jpeg, gif.')
                return redirect(request.url)

        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            print(f"Database error: {err}")
        except Exception as e:
            flash(f"Error: {e}")
            print(f"Error: {e}")

    return render_template('blogs.html')




@app.route('/')
def index():
    if 'username' in session:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT username, email, phone FROM users')
        users = cursor.fetchall()
        cursor.close()
        return render_template('home.html', users=users)
    return render_template('home.html')


@app.route('/products')
def products():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, name, sort_description, full_description, product_tags, image_url FROM categories')
        categories = cursor.fetchall()
        cursor.close()
        return render_template('products.html', categories=categories)
    except mysql.connector.Error as e:
        print(f"Error fetching categories: {e}")
        flash(f"Database error: {e}")
        return render_template('error.html', error_message="Database error occurred")
    except Exception as e:
        print(f"Error: {e}")
        flash(f"Error: {e}")
        return render_template('error.html', error_message="An error occurred")





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Debug statement to check email and password
        print(f"Login attempt with email: {email} and password: {password}")

        # Special case for admin login
        if email == 'admin@gmail.com' and password == 'admin':
            session['username'] = 'admin'
            print("Admin login successful")
            return redirect(url_for('dashboard'))

        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print(f"User found: {user['username']}")
            if check_password_hash(user['password'], password):
                session['username'] = user['username']
                print("User login successful")
                return redirect(url_for('index'))
            else:
                print("Password mismatch")
        else:
            print("User not found")

        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            # Debug statements
            print(f"Received data: username={
                  username}, email={email}, phone={phone}")

            if password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('signup'))

            if 'profile_photo' not in request.files:
                flash('No file part')
                return redirect(url_for('signup'))
            file = request.files['profile_photo']

            if file.filename == '':
                flash('No selected file')
                return redirect(url_for('signup'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)
            else:
                flash('File not allowed')
                return redirect(url_for('signup'))

            hashed_password = generate_password_hash(password)
            session_id = str(uuid.uuid4())

            # Debug statements
            print(f"Saving to database: session_id={session_id}, username={username}, email={email}, phone={
                  phone}, profile_photo_path={profile_photo_path}, hashed_password={hashed_password}")

            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO users (session_id, username, email, phone, profile_photo, password) VALUES (%s, %s, %s, %s, %s, %s)',
                (session_id, username, email, phone, profile_photo_path, hashed_password))
            db.commit()
            cursor.close()

            flash('Account created successfully')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            print(f"Database error: {err}")
        except Exception as e:
            flash(f"Error: {e}")
            print(f"Error: {e}")
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
