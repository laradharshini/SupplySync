from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# MongoDB config
client = MongoClient("mongodb://localhost:27017/")
db = client['supplysync']
vendor_collection = db['vendor']
supplier_collection = db['supplier']
materials = db['materials']
orders = db['orders']

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
        return jsonify({'error': f'File save error: {str(e)}'}), 500

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
        result = vendor_collection.insert_one(vendor_data)
        session['vendor_id'] = str(result.inserted_id)
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
        return jsonify({'error': f'File save error: {str(e)}'}), 500

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
        result = supplier_collection.insert_one(supplier_data)
        session['supplier_id'] = str(result.inserted_id)
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
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            error = 'Please fill all fields.'
        else:
            vendor = vendor_collection.find_one({
                '$or': [{'phone': identifier}, {'email': identifier}]
            })

            if vendor and check_password_hash(vendor['password_hash'], password):
                session['vendor_id'] = str(vendor['_id'])
                return redirect(url_for('dashboard_vendor'))
            else:
                error = 'Invalid phone/email or password.'

    return render_template('login_vendor.html', error=error)

@app.route('/login/supplier', methods=['GET', 'POST'])
def login_supplier():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            error = 'Please fill all fields.'
        else:
            supplier = supplier_collection.find_one({
                '$or': [{'phone': identifier}, {'email': identifier}]
            })

            if supplier and check_password_hash(supplier['password_hash'], password):
                session['supplier_id'] = str(supplier['_id'])
                return redirect(url_for('dashboard_supplier'))
            else:
                error = 'Invalid phone/email or password.'

    return render_template('login_supplier.html', error=error)

@app.route('/dashboard/vendor')
def dashboard_vendor():
    if 'vendor_id' not in session:
        return redirect(url_for('login_vendor'))
    
    vendor = vendor_collection.find_one({'_id': ObjectId(session['vendor_id'])})
    return render_template('dashboard_vendor.html', vendor_name=vendor['full_name'])

@app.route('/dashboard/supplier')
def dashboard_supplier():
    if 'supplier_id' not in session:
        return redirect(url_for('login_supplier'))
    
    supplier = supplier_collection.find_one({'_id': ObjectId(session['supplier_id'])})
    return render_template('dashboard_supplier.html', supplier_name=supplier['full_name'])

@app.route('/supplier/add_material', methods=['GET', 'POST'])
def add_material():
    if 'supplier_id' not in session:
        return redirect(url_for('login_supplier'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        available_quantity = request.form.get('available_quantity')
        unit = request.form.get('unit')  # Get unit from dropdown
        custom_unit = request.form.get('custom_unit', '').strip()  # Get custom unit input

        # Validate inputs
        if not all([name, description, price, available_quantity, unit]):
            flash('All fields are required.', 'error')
            return redirect(url_for('add_material'))

        try:
            price = float(price)
            available_quantity = float(available_quantity)
        except ValueError:
            flash('Price must be a number and quantity must be numeric.', 'error')
            return redirect(url_for('add_material'))

        # Use custom unit if 'other' selected and custom unit is provided
        if unit == 'other':
            if not custom_unit:
                flash('Please specify a unit.', 'error')
                return redirect(url_for('add_material'))
            quantity_unit = custom_unit
        else:
            quantity_unit = unit

        # Handle image upload
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(image_path)
                image_filename = filename
            else:
                flash('Invalid image format. Allowed formats: png, jpg, jpeg, gif', 'error')
                return redirect(url_for('add_material'))

        material_data = {
            'supplier_id': session['supplier_id'],
            'name': name,
            'description': description,
            'price_in_rupees': price,
            'available_quantity': available_quantity,
            'quantity_unit': quantity_unit,
            'created_at': datetime.now(),
            'image_filename': image_filename  # Save filename or None if no image uploaded
        }

        try:
            db.materials.insert_one(material_data)
            return render_template('add_material.html', success=True)
        except Exception as e:
            flash(f'Error saving material: {str(e)}', 'error')
            return redirect(url_for('add_material'))

    # GET request or no POST
    return render_template('add_material.html')

@app.route('/supplier/view_materials')
def view_materials():
    if 'supplier_id' not in session:
        return redirect(url_for('login_supplier'))

    try:
        materials = list(db.materials.find({'supplier_id': session['supplier_id']}))
    except Exception as e:
        flash(f"Error fetching materials: {str(e)}", "error")
        materials = []

    return render_template('view_materials.html', materials=materials)

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/supplier/edit_material/<material_id>', methods=['GET', 'POST'])
def edit_material(material_id):
    if 'supplier_id' not in session:
        return redirect(url_for('login_supplier'))

    try:
        material = db.materials.find_one({'_id': ObjectId(material_id), 'supplier_id': session['supplier_id']})
        if not material:
            flash("Material not found or unauthorized access.", "error")
            return redirect(url_for('view_materials'))
    except Exception as e:
        flash(f"Error fetching material: {str(e)}", "error")
        return redirect(url_for('view_materials'))

    if request.method == 'POST':
        updated_name = request.form.get('name')
        updated_description = request.form.get('description')
        updated_price = float(request.form.get('price_in_rupees'))
        updated_quantity = float(request.form.get('available_quantity'))
        updated_unit = request.form.get('unit')  # <-- corrected to 'unit'

        # Handle custom unit if 'other' selected
        if updated_unit == 'other':
            custom_unit = request.form.get('custom_unit', '').strip()
            if custom_unit:
                updated_unit = custom_unit
            else:
                flash("Please specify the custom unit.", "error")
                return render_template('edit_material.html', material=material)

        # Handle file upload
        file = request.files.get('image')
        image_filename = None

        if file and file.filename != '':
            # Validate file if needed (extension, size etc.)
            filename = secure_filename(file.filename)
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')  # Adjust path as per your app config
            file_path = os.path.join(upload_folder, filename)

            # Save file to upload folder
            try:
                file.save(file_path)
                image_filename = filename
            except Exception as e:
                flash(f"Failed to upload image: {str(e)}", "error")
                return render_template('edit_material.html', material=material)

        # Prepare update dict
        update_data = {
            'name': updated_name,
            'description': updated_description,
            'price_in_rupees': updated_price,
            'available_quantity': updated_quantity,
            'quantity_unit': updated_unit
        }

        # Add image filename only if new image uploaded
        if image_filename:
            update_data['image_filename'] = image_filename

        try:
            db.materials.update_one(
                {'_id': ObjectId(material_id)},
                {'$set': update_data}
            )
            flash("Material updated successfully.", "success")
            return redirect(url_for('view_materials'))
        except Exception as e:
            flash(f"Error updating material: {str(e)}", "error")

    return render_template('edit_material.html', material=material)

@app.route('/supplier/orders')
def supplier_orders():
    if 'supplier_id' not in session:
        return redirect(url_for('login_supplier'))
    supplier_material_ids = [mat['_id'] for mat in materials.find({'supplier_id': session['supplier_id']})]
    supplier_orders = list(orders.find({'material_id': {'$in': [str(mid) for mid in supplier_material_ids]}}))
    return render_template('supplier_orders.html', orders=supplier_orders)

@app.route('/vendor/browse')
def browse_materials():
    if 'vendor_id' not in session:
        return redirect(url_for('login_vendor'))

    all_materials = list(materials.find())
    
    # To get supplier names, fetch all suppliers once and map by _id
    suppliers_map = {str(s['_id']): s['business_name'] for s in supplier_collection.find()}
    
    # Attach supplier name to materials
    for material in all_materials:
        supplier_id_str = str(material.get('supplier_id'))
        material['supplier_name'] = suppliers_map.get(supplier_id_str, 'Unknown Supplier')
        material['_id_str'] = str(material['_id'])  # For HTML usage
    
    return render_template('browse_materials.html', materials=all_materials)

@app.route('/vendor/place_order', methods=['POST'])
def place_order():
    if 'vendor_id' not in session:
        return redirect(url_for('login_vendor'))

    material_id = request.form['material_id']
    quantity = int(request.form['quantity'])

    material = materials.find_one({'_id': ObjectId(material_id)})

    order = {
        'vendor_id': session['vendor_id'],
        'material_id': material_id,
        'material_name': material['name'],
        'supplier_id': material['supplier_id'],
        'quantity': quantity,
        'status': 'Pending',
        'timestamp': datetime.now()
    }

    orders.insert_one(order)
    return redirect(url_for('order_history'))

@app.route('/vendor/orders')
def order_history():
    if 'vendor_id' not in session:
        return redirect(url_for('login_vendor'))

    vendor_orders = list(orders.find({'vendor_id': session['vendor_id']}))
    return render_template('order_history.html', orders=vendor_orders)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
