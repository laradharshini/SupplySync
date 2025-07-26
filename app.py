from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)

# Upload folder config
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/vendor', methods=['GET', 'POST'])
def signup_vendor():
    if request.method == 'GET':
        return render_template('signup_vendor.html')  # Your vendor signup page if needed

    # POST method: handle form submission after OTP verification
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

    # Save the uploaded certificate file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    # Hash the password securely
    hashed_password = generate_password_hash(password)

    # TODO: Save user data to your database here (example):
    # save_user_to_db(
    #    full_name=full_name,
    #    business_name=business_name,
    #    email=email,
    #    phone=phone,
    #    address=address,
    #    product_desc=product_desc,
    #    password_hash=hashed_password,
    #    certificate_path=filepath
    # )

    # For now, just simulate success response
    return jsonify({'message': 'Vendor signup successful!'}), 200

@app.route('/signup/supplier', methods=['GET', 'POST'])
def signup_supplier():
    if request.method == 'GET':
        return render_template('signup_supplier.html')  # Your vendor signup page if needed

    # POST method: handle form submission after OTP verification
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

    # Save the uploaded certificate file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    # Hash the password securely
    hashed_password = generate_password_hash(password)

    # TODO: Save user data to your database here (example):
    # save_user_to_db(
    #    full_name=full_name,
    #    business_name=business_name,
    #    email=email,
    #    phone=phone,
    #    address=address,
    #    product_desc=product_desc,
    #    password_hash=hashed_password,
    #    certificate_path=filepath
    # )

    # For now, just simulate success response
    return jsonify({'message': 'Supplier signup successful!'}), 200

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/vendor')
def login_vendor():
    return render_template('login_vendor.html')

@app.route('/login/supplier')
def login_supplier():
    return render_template('login_supplier.html')

if __name__ == '__main__':
    app.run(debug=True)
