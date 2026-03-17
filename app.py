"""
Home Decor E-commerce Website - Complete Flask App
"""
import os
import random
import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__, 
            template_folder='templates',
            static_folder='client/static',
            static_url_path='/static')
app.secret_key = 'home-decor-secret-key-2024'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'client', 'static')

CATEGORIES = {
    'sofa': {'name': 'Sofas', 'icon': '🛋️', 'description': 'Comfortable sofas', 'cover_image': '/static/image/sofa/sofa1.jpg'},
    'bed': {'name': 'Beds', 'icon': '🛏️', 'description': 'Modern beds', 'cover_image': '/static/image/bed/bed1.jpg'},
    'diningtable': {'name': 'Dining Tables', 'icon': '🍽️', 'description': 'Elegant tables', 'cover_image': '/static/image/DiningTable/dining1.jpg'},
    'coffee': {'name': 'Coffee Tables', 'icon': '☕', 'description': 'Contemporary tables', 'cover_image': '/static/image/coffee/coffee1.jpg'},
    'wallart': {'name': 'Wall Art', 'icon': '🖼️', 'description': 'Decorative art', 'cover_image': '/static/image/wallart/wallart1.jpg'},
    'lighting': {'name': 'Lighting', 'icon': '💡', 'description': 'Ambient lighting', 'cover_image': '/static/image/lighting/lighting1.jpg'},
    'mirrior': {'name': 'Mirrors', 'icon': '🪞', 'description': 'Elegant mirrors', 'cover_image': '/static/image/mirrior/mirror1.jpg'},
    'rug': {'name': 'Rugs', 'icon': '🧵', 'description': 'Warm rugs', 'cover_image': '/static/image/rug/rug1.jpg'}
}

DESCRIPTIONS = [
    "Premium quality furniture",
    "Modern stylish design", 
    "Handcrafted with care"
]

def get_products_from_csv(category_name):
    products = []
    csv_path = 'products.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, 1):
                if row['category'].lower() == category_name or row['category'].lower() == CATEGORIES[category_name]['name'].lower():
                    products.append({
                        'id': int(row['id']),
                        'name': row['name'],
                        'description': row["image_name"],
                        'price': float(row['price']) * 83,
                        'image': f'/static/image/{category_name}/{row["image_name"]}',
                        'category': category_name
                    })
    
    return products

def get_products_from_folder(category_folder):
    products = []
    image_dir = os.path.join(STATIC_DIR, 'image', category_folder)
    
    if os.path.exists(image_dir):
        files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.png'))]
        for i, filename in enumerate(files):
            name = os.path.splitext(filename)[0]
            product_name = name.replace('_', ' ').title()
            
            products.append({
                'id': i + 1,
                'name': product_name,
                'description': random.choice(DESCRIPTIONS),
                'price': random.randint(5000, 50000),
                'image': f'/static/image/{category_folder}/{filename}',
                'category': category_folder
            })
    return products

@app.route('/')
def index():
    featured = []
    for cat in ['coffee', 'wallart', 'lighting', 'mirrior']:
        featured.extend(get_products_from_folder(cat)[:3])
    return render_template('index.html', categories=CATEGORIES, featured_products=featured[:9])

@app.route('/category/<category_key>')
def category(category_key):
    if category_key not in CATEGORIES:
        flash('Category not found', 'error')
        return redirect(url_for('index'))
    
    products = get_products_from_csv(category_key)
    if not products:
        products = get_products_from_folder(category_key)
    
    return render_template('category.html', 
                         category=CATEGORIES[category_key], 
                         products=products)

@app.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    category_name = request.args.get('category', 'sofa')
    
    # Get product from CSV
    all_products = []
    csv_path = 'products.csv'
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            all_products = [row for row in reader]
    
    product = None
    for row in all_products:
        if int(row['id']) == product_id:
            product = {
                'id': int(row['id']),
                'name': row['name'],
                'description': row["image_name"],
                'price': float(row['price']) * 83,
                'image': f'/static/image/{category_name}/{row["image_name"]}',
                'category': category_name
            }
            break
    
    if not product:
        # Fallback product
        product = {
            'id': product_id,
            'name': f'{category_name.title()} Product {product_id}',
            'description': 'Premium quality product with modern design',
            'price': 15000,
            'image': f'/static/image/{category_name}/1.jpg',
            'category': category_name
        }
    
    return render_template('product_detail.html', product=product, category_name=category_name)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    total = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart_items)
    tax = (total * 0.1)
    final_total = total + tax
    return render_template('checkout.html', cart_items=cart_items, total=total, tax=tax, final_total=final_total)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Simulate payment processing
    name = request.form['name']
    email = request.form['email']
    payment_method = request.form.get('payment_method', 'cod')
    
    # Clear cart after successful payment
    session.pop('cart', None)
    
    if payment_method == 'cod':
        flash('Order placed successfully! Cash on Delivery confirmed.', 'success')
    else:
        flash('Payment successful! Order confirmed.', 'success')
    
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    category = request.args.get('category', 'general')
    qty = int(request.args.get('quantity', 1))
    
    # Get real product from CSV
    all_products = []
    csv_path = 'products.csv'
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            all_products = [row for row in reader]
    
    product = None
    for row in all_products:
        if int(row['id']) == product_id:
            product = {
                'id': int(row['id']),
                'name': row['name'],
                'price': float(row['price']) * 83,
                'image': f'/static/image/{category}/{row["image_name"]}',
                'quantity': qty,
                'category': category
            }
            break
    
    if not product:
        # Fallback for folder products
        product = {
            'id': product_id,
            'name': f'{category} Product {product_id}',
            'price': 9999,
            'image': f'/static/image/{category}/1.jpg',
            'quantity': qty,
            'category': category
        }
    
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product)
    flash(f'{product["name"]} ({qty}x) added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_item/<int:index>')
def remove_item(index):
    if 'cart' in session and index < len(session['cart']):
        removed_item = session['cart'].pop(index)
        flash(f'{removed_item["name"]} removed from cart', 'success')
    else:
        flash('Item not found in cart', 'error')
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'cart' in session:
        cart_count = len(session['cart'])
        session.pop('cart', None)
        flash(f'Cart cleared! {cart_count} items removed', 'success')
    else:
        flash('Cart is already empty', 'info')
    return redirect(url_for('cart'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Demo login
        session['user'] = {'email': email, 'name': 'User'}
        flash('Logged in successfully', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        session['user'] = {'name': name, 'email': email}
        flash('Registration successful! You are logged in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

