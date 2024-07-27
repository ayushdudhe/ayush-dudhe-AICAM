from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123*#Ayu',
    'database': 'profile_db'
}

# Sample data for local crafts and user profile
local_crafts = [
    {'id': 1, 'name': 'Applique ', 'description': 'Appliqué is an art form that involves sewing pieces of fabric onto a larger piece to create patterns or pictures. This technique has been used for centuries in various cultures to adorn clothing, quilts, and other textile items. Known for its vibrant colors and intricate designs, appliqué allows artisans to express their creativity while preserving traditional crafting methods. Each piece is meticulously hand-stitched, making every creation unique and a true work of art. Whether used for decorative purposes or functional items, appliqué adds a touch of elegance and individuality to any fabric it graces','summary':'Applique Craft is a traditional Indian art form that involves sewing pieces of fabric onto a larger fabric surface to create intricate designs and patterns. This craft is especially prominent in regions like Odisha, Rajasthan, and Gujarat.','price':'₹1,500 to ₹10,000 depending on the size, complexity, and materials used.','availability':'Available in odisha for its colorful and elaborate Pipili applique work,Rajasthan for traditional motifs and vibrant colors. and Gujarat renowned for mirror work and intricate embroidery in their applique designs.','delivery':'Delivery charges within India range from ₹100 to ₹500, depending on the location and size of the order. For international deliveries, charges typically range from ₹1,500 to ₹3,000, based on the country and shipment weight. Exporting from India involves costs between ₹2,000 and ₹5,000, which cover handling, packaging, and shipping. Importing to other countries can vary significantly based on customs duties and taxes specific to each country, generally ranging from 5% to 20% of the item value.'},
    {'id': 2, 'name': 'Art metal ware ', 'description': 'Art metal ware encompasses a diverse range of decorative and functional items crafted from metals such as brass, copper, silver, and gold. These exquisite pieces often include intricate designs and patterns, reflecting the rich cultural heritage and skilled craftsmanship of artisans. Common examples include jewelry, utensils, sculptures, and ornamental objects, each showcasing the beauty and versatility of metal as a medium. Art metal ware not only serves as a testament to traditional craftsmanship but also adds a touch of elegance and sophistication to any space.','summary':'Art Metal Ware refers to decorative and functional items crafted from various metals, such as brass, copper, and bronze. These items often feature intricate designs and are popular for their aesthetic appeal and durability.','price':'₹2,000 to ₹15,000 depending on the size, craftsmanship, and metal used.','availability':'Known for its traditional Bidriware and brass artifacts in Maharashtra, Famous for its intricate metalwork, including brass and copper items in Rajasthan and Renowned for bronze sculptures and traditional metal artifact in Tamil Nadu','delivery':' ₹200 to ₹800, based on location and size of the item within India.₹2,000 to ₹5,000 depending on the destination country and shipment weight for International Delivery Service.₹3,000 to ₹7,000, which includes handling, packaging, and shipping.'},
    {'id': 3, 'name': 'Beads craft', 'description': 'Beads Craft is a traditional art form that involves the use of small, decorative beads to create beautiful jewelry, accessories, and decorative items. Skilled artisans meticulously thread, weave, and stitch beads together to form intricate patterns and designs. This craft is celebrated for its versatility and the vibrant, colorful creations it produces, making it a popular choice for both fashion and home decor enthusiasts.', 'summary':'Beads Craft involves creating intricate designs and patterns using small, decorative beads. This traditional art form is used to make a wide range of items including jewelry, accessories, and home decor.','price':'₹500 to ₹5,000, depending on the complexity of the design, the type of beads used, and the item’s size.','availability':'Kolkata is known for its vibrant beadwork, especially in jewelry and Jaipur is famous for its beaded embroidery and embellishments..','delivery':'₹100 to ₹500, depending on the location and size of the order within India.₹1,500 to ₹3,000, based on the destination country and shipment weight.'},
]

# Define the path to the Excel file
base_dir = os.path.abspath(os.path.dirname(__file__))
excel_path_1 = os.path.join(base_dir, 'data', 'Artisans.xlsx')

# Load artisans data
artisans_df = pd.read_excel(excel_path_1)

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials against the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        # Insert new user into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, name, email, address, phone) VALUES (%s, %s, %s, %s, %s, %s)',
                       (username, password, name, email, address, phone))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html', crafts=local_crafts)

@app.route('/craft/<int:craft_id>')
def craft_details(craft_id):
    craft = next((c for c in local_crafts if c['id'] == craft_id), None)
    if craft is None:
        return "Craft not found", 404

    # Match the name of the craft in the dataset
    craft_name = craft['name'].strip().lower()
    craft_artisans = artisans_df[artisans_df['Craft'].str.strip().str.lower() == craft_name]
    
    # Convert to list of dictionaries
    artisans_list = craft_artisans.to_dict(orient='records')
    
    return render_template('craft_details.html', craft=craft, artisans=artisans_list)

@app.route('/shop')
def shop():
    # Logic to get items and categories
    return render_template('shop.html')

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection
    
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        flash('You are not logged in.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        flash('User not found.', 'error')
        return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('You are not logged in.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Get user input from the form
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        # Update the user's information in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET username=%s, password=%s, name=%s, email=%s, address=%s, phone=%s 
            WHERE id=%s
        ''', (username, password, name, email, address, phone, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('profile'))

    else:
        # Load existing user data for the GET request
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return render_template('edit_profile.html', user=user)
        else:
            flash('User not found.', 'error')
            return redirect(url_for('profile'))


@app.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session:
        flash('You need to be logged in to view your cart.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM cart WHERE user_id=%s', (user_id,))
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash('You need to be logged in to add items to your cart.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    item_name = request.form.get('item_name')
    item_price = float(request.form.get('item_price'))
    quantity = int(request.form.get('quantity', 1))  # Default quantity to 1 if not provided

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cart WHERE user_id=%s AND item_name=%s', (user_id, item_name))
    existing_item = cursor.fetchone()

    if existing_item:
        cursor.execute('UPDATE cart SET quantity=quantity+%s WHERE user_id=%s AND item_name=%s', (quantity, user_id, item_name))
    else:
        cursor.execute('INSERT INTO cart (user_id, item_name, item_price, quantity) VALUES (%s, %s, %s, %s)', (user_id, item_name, item_price, quantity))

    conn.commit()
    cursor.close()
    conn.close()

    flash(f'{item_name} has been added to your cart!', 'success')
    return redirect(url_for('shop'))

@app.route('/payment', methods=['GET'])
def payment():
    # Handle payment processing here
    return render_template('payment.html')


# Sample order data
orders = [
    {
        'order_id': 'ORD123456',
        'name': 'Applique Art',
        'price': 1500,
        'date': '2023-07-20',
        'status': 'Delivered'
    },
    {
        'order_id': 'ORD123457',
        'name': 'Metal Ware',
        'price': 3000,
        'date': '2023-07-21',
        'status': 'Shipped'
    },
    {
        'order_id': 'ORD123458',
        'name': 'Beads Craft',
        'price': 500,
        'date': '2023-07-22',
        'status': 'Processing'
    }
]

@app.route('/order_history')
def order_history():
    return render_template('order_history.html', orders=orders)

@app.route('/sign_out')
def sign_out():
    session.pop('user_id', None)
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


if __name__ == '__main__':
    app.run(debug=True)
