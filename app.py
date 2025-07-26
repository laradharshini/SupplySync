from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from pymongo import MongoClient
import os

app = Flask(__name__)

# Upload folder config
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key'

# MongoDB Config
client = MongoClient("mongodb://localhost:27017/")
db = client['supplysync']
vendor_collection = db['vendor']
supplier_collection = db['supplier']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/vendor', methods=['GET', 'POST'])
def signup_vendor():
    if request.method == 'GET':
        return render_template('signup_vendor.html')

    phone = request.form.get('phone')
    full_name = request.form.get('fullName')
    business_name = request.form.get('businessName')
    email = request.form.get('email')
    address = request.form.get('address')
    product_desc = request.form.get('productDescription')
    password = request.form.get('password')
    file = request.files.get('certificate')

    if not all([phone, full_name, business_name, email, address, product_desc, password, file]):
        return jsonify({'error': 'All fields are required'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    hashed_password = generate_password_hash(password)

    vendor_data = {
        'phone': phone,
        'full_name': full_name,
        'business_name': business_name,
        'email': email,
        'address': address,
        'product_description': product_desc,
        'password_hash': hashed_password,
        'certificate_path': filepath
    }

    try:
        vendor_collection.insert_one(vendor_data)
        return jsonify({'message': 'Vendor signup successful!'}), 200
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/signup/supplier', methods=['GET', 'POST'])
def signup_supplier():
    if request.method == 'GET':
        return render_template('signup_supplier.html')

    phone = request.form.get('phone')
    full_name = request.form.get('fullName')
    business_name = request.form.get('businessName')
    email = request.form.get('email')
    address = request.form.get('address')
    product_desc = request.form.get('productDescription')
    password = request.form.get('password')
    file = request.files.get('certificate')

    if not all([phone, full_name, business_name, email, address, product_desc, password, file]):
        return jsonify({'error': 'All fields are required'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    hashed_password = generate_password_hash(password)

    supplier_data = {
        'phone': phone,
        'full_name': full_name,
        'business_name': business_name,
        'email': email,
        'address': address,
        'product_description': product_desc,
        'password_hash': hashed_password,
        'certificate_path': filepath
    }

    try:
        supplier_collection.insert_one(supplier_data)
        return jsonify({'message': 'Supplier signup successful!'}), 200
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/vendor', methods=['GET', 'POST'])
def login_vendor():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # phone or email
        password = request.form.get('password')

        if not identifier or not password:
            error = 'Please fill all fields.'
        else:
            vendor = vendor_collection.find_one({
                '$or': [
                    {'phone': identifier},
                    {'email': identifier}
                ]
            })

            if vendor and check_password_hash(vendor['password_hash'], password):
                # Login successful - here you can set session or redirect
                return f"Welcome, {vendor['full_name']}! Login successful."
            else:
                error = 'Invalid phone/email or password.'

    return render_template('login_vendor.html', error=error)

@app.route('/login/supplier', methods=['GET', 'POST'])
def login_supplier():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # phone or email
        password = request.form.get('password')

        if not identifier or not password:
            error = 'Please fill all fields.'
        else:
            supplier = supplier_collection.find_one({
                '$or': [
                    {'phone': identifier},
                    {'email': identifier}
                ]
            })

            if supplier and check_password_hash(supplier['password_hash'], password):
                # Login successful - here you can set session or redirect
                return f"Welcome, {supplier['full_name']}! Login successful."
            else:
                error = 'Invalid phone/email or password.'

    return render_template('login_supplier.html', error=error)
if __name__ == '__main__':
    app.run(debug=True)
