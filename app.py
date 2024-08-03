from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, Response
from datetime import datetime, timedelta
from pymongo import MongoClient, DESCENDING
from werkzeug.utils import secure_filename  # Import secure_filename function
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from bson import ObjectId
from bson.binary import Binary
import io
import datetime
app = Flask(__name__)
app.secret_key = 'adjkda))KJ@IJJS139012'  # Change this to a secure random key
import json
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb+srv://lionking:iOiyIkAZU8bRWPI4@cluster0.jmrqsig.mongodb.net/')
db = client['user_database']
user_collection = db['user']  # Collection for regular users
staff_collection = db['staff']  # Collection for staff members
report_collection = db['report']  # Collection for staff members
animal_collection = db['animal']
medical_collection = db['medical']
moment_collection = db['moment']
adoption_collection = db['adoption']
transaction_collection= db['transaction']


def convert_dates(collection, date_field):
    documents = collection.find({date_field: {'$type': 'string'}})
    for doc in documents:
        try:
            date_value = datetime.strptime(doc[date_field], '%Y-%m-%d')  # Adjust the date format as needed
            collection.update_one({'_id': doc['_id']}, {'$set': {date_field: date_value}})
        except ValueError:
            print(f"Error converting date for document ID {doc['_id']}")

# Call this function for each collection
convert_dates(db.report_collection, 'date')
convert_dates(db.animal_collection, 'date')
convert_dates(db.adoption_collection, 'date')
convert_dates(db.transaction_collection, 'date')

# Define age ranges for different categories
AGE_RANGES = {
    'young': (0, 3),  # Age range for young animals: 0-3 years
    'adult': (4, 7),  # Age range for adult animals: 4-7 years
    'senior': (8, 40)  # Age range for senior animals: 8 years and above
}

@app.route('/')
def index():
    return render_template('user_home.html')

@app.route('/user_home')
def user_home():
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True
    return render_template('user_home.html',user_logged_in=user_logged_in)

@app.route('/staff_home')
def staff_home():

    return render_template('staff_home.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':  # Assuming logout button triggers a POST request
        session.clear()  # Clear the session data (logout)
        return render_template('user_home.html', message="You have been logged out.")
    return render_template('user_home.html')


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        phone_number = request.form['phone_number']
        email = request.form['email']
        
        # Check if username already exists
        if user_collection.find_one({'username': username}):
            return '''
                <script>
                    alert("Username already exist!");
                    window.location.href = "/register";
                </script>
            '''
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)
        
        # Insert new user into MongoDB (regular user)
        # Store user information in the database
        user_data = {
            'username': username,
            'password': hashed_password,
            'name': name,
            'age': age,
            'phone_number': phone_number,
            'email': email
        }
        user_collection.insert_one(user_data)
        session['username'] = username
        return redirect(url_for('user_home'))
    
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists
        user = user_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            # If username exists and password matches
            session['username'] = username
            return redirect(url_for('user_home'))
        else:
            return '''
                <script>
                    alert("Invalid username or password!");
                    window.location.href = "/login";
                </script>
            '''
    
    return render_template('login.html')

@app.route('/user_main', methods=['GET', 'POST'])
def user_main():
    return render_template('user_main.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True
    if request.method == 'POST':
        # Prefix for the report ID
        prefix = 'R'
            
        # Generate a random UUID and convert to string
        random_suffix = str(uuid.uuid4().hex)[:4]
        report_id = f"{prefix}{random_suffix}"

        # Get data from the form
        animal_type = request.form['animal_type']
        location = request.form['location']
        description = request.form['description']
        phone_number = request.form['phone_number']
        date = request.form['date']
        time = request.form['time']

        # Read the binary data of the photo
        photo = request.files['photo']
        photo_binary = Binary(photo.read())  # Read photo binary data
        
        # Set default values for new fields
        report_status = 'unchecked'  # Default status when reported
        remarks = ''  # Default empty remarks
        
        # Save the report to the database (regular user)
        report_data = {
            'report_id': report_id,
            'animal_type': animal_type,
            'location': location,
            'description': description,
            'phone_number': phone_number,
            'date': date,
            'time': time,
            'photo': photo_binary,  # Save file path to photo in database
            'report_status': report_status,  # Set default report status
            'remarks': remarks  # Set default remarks
        }
        report_collection.insert_one(report_data)
        
        return redirect(url_for('index'))
    
    return render_template('report.html', user_logged_in=user_logged_in)


@app.route('/stafflogin', methods=['GET', 'POST'])
def stafflogin():
    if request.method == 'POST':
        staffid = request.form['staffid']
        password = request.form['password']
        
        # Check if username exists in the staff collection
        staff = staff_collection.find_one({'staffid': staffid})
        
        if staff and check_password_hash(staff['password'], password):
            # If username exists and password matches
            session['staffid'] = staffid
            return redirect(url_for('staff_home'))  # Redirect to staff_main route
        else:
            return '''
                <script>
                    alert("invalid staffid or password!");
                    window.location.href = "/stafflogin";
                </script>
            '''
    
    return render_template('stafflogin.html')

@app.route('/staff_main')
def staff_main():
    return render_template('staff_main.html')

@app.route('/photo/<collection_id>')
def get_photo(collection_id):

    # Try to find the report by report_id
    moment = moment_collection.find_one({'moment_id': collection_id})
    if moment:
        # Retrieve the photo binary data from the report
        photo_binary = moment.get('moment_photo')
        if photo_binary:
            # Return the photo binary data as a file
            return send_file(io.BytesIO(photo_binary), mimetype='image/jpeg')  # Assuming JPEG format

    # Try to find the report by report_id
    report = report_collection.find_one({'report_id': collection_id})
    if report:
        # Retrieve the photo binary data from the report
        photo_binary = report.get('photo')
        if photo_binary:
            # Return the photo binary data as a file
            return send_file(io.BytesIO(photo_binary), mimetype='image/jpeg')  # Assuming JPEG format
    
        # Try to find the report by report_id
    animal = animal_collection.find_one({'animal_id': collection_id})
    if animal:
        # Retrieve the photo binary data from the report
        photo_binary = animal.get('photo')
        if photo_binary:
            # Return the photo binary data as a file
            return send_file(io.BytesIO(photo_binary), mimetype='image/jpeg')  # Assuming JPEG format
        
    # If not found in either collection, return 404
    return 'Photo not found', 404

@app.route('/latest_report')
def latest_report():
    # Retrieve all data from the report collection and sort by date in descending order
    reports = list(report_collection.find().sort('date', -1))
    
    return render_template('latest_report.html', reports=reports)

@app.route('/update_status', methods=['POST'])
def update_status():
    report_id = request.form['report_id']
    new_status = request.form['status']
    report_collection.update_one({'report_id': report_id}, {'$set': {'report_status': new_status}})
    return jsonify({'message': 'Status updated successfully'})

@app.route('/update_remarks', methods=['POST'])
def update_remarks():
    report_id = request.form['report_id']
    new_remarks = request.form['remarks']
    report_collection.update_one({'report_id': report_id}, {'$set': {'remarks': new_remarks}})
    return jsonify({'status': 'success'})

@app.route('/delete_report', methods=['POST'])
def delete_report():
    report_id = request.form['report_id']
    report_collection.delete_one({'_id': ObjectId(report_id)})
    return jsonify({'status': 'success'})

# Route for registering new staff
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        staffid = request.form['staffid']
        password = request.form['password']
        
        # Check if username already exists
        if staff_collection.find_one({'staffid': staffid}):
            return '''
                <script>
                    alert("staffid already exist!");
                    window.location.href = "/register_staff";
                </script>
            '''
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)
        
        # Insert new staff member into the database
        staff_collection.insert_one({
            'staffid': staffid,
            'password': hashed_password,
            'phone': '',
            'email': '',
            'address': '',
            'birthdate': ''
        })
        
        return redirect(url_for('staff_home'))  # Redirect to staff main page
    
    # If it's a GET request, render the registration form
    return render_template('register_staff.html')

@app.route('/update_staff', methods=['GET', 'POST'])
def update_staff():
    staff = None  # Initialize staff variable
    
    if request.method == 'POST':
        # Process POST request
        if 'staffid' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401  # Return JSON response if not logged in
        
        staffid = session['staffid']
        staff = staff_collection.find_one({'staffid': staffid})

        old_password = request.form['old_password']
        new_staffid = request.form['staffid']
        new_password = request.form.get('password', '')

        # Check if old password matches the password stored in the database
        if not check_password_hash(staff['password'], old_password):
            return jsonify({'success': False, 'message': 'Old password is incorrect.'}), 400
        
        # Check if new username already exists and is not the same as the current username
        if new_staffid != staffid and staff_collection.find_one({'staffid': new_staffid}):
            return jsonify({'success': False, 'message': 'Username already exists! Please choose a different one.'}), 400
        
        # Prepare the update data
        updated_data = {
            'staffid': new_staffid,
            'phone': request.form['phone'],
            'email': request.form['email'],
            'address': request.form['address'],
            'birthdate': request.form['birthdate']
        }

        # Only update the password if a new one is provided
        if new_password:
            updated_data['password'] = generate_password_hash(new_password)

        # Update staff details in the database
        staff_collection.update_one({'staffid': staffid}, {'$set': updated_data})
        session['staffid'] = new_staffid  # Update session username
        
        return jsonify({'success': True, 'message': 'Details updated successfully.'}), 200
    
    # For GET request or initial page load
    if 'staffid' in session:
        staffid = session['staffid']
        staff = staff_collection.find_one({'staffid': staffid})
    
    return render_template('update_staff.html', staff=staff)



@app.route('/delete_staff', methods=['POST'])
def delete_staff():
    staffid = session['staffid']
    staff_collection.delete_one({'staffid': staffid})
    return redirect(url_for('index'))

@app.route('/animalprofile', methods=['GET', 'POST'])
def animalprofile():

    if request.method == 'POST':
        # Get data from the form
        # Prefix for the report ID
        prefix = 'A'
        
        # Generate a random UUID and convert to string
        random_suffix = str(uuid.uuid4().hex)[:4]
        animal_id = f"{prefix}{random_suffix}"

         # Read the binary data of the photo
        photo = request.files['photo']
        photo_binary = Binary(photo.read())  # Read photo binary data
        name = request.form['name']
        species = request.form['species']
        breed = request.form['breed']
        age = request.form['age']
        overall_health = request.form['overall_health']
        vaccination = request.form['vaccination']
        spayed_neutered = request.form['spayed_neutered']
        energy_level = request.form['energy_level']
        temperament = request.form['temperament']
        trainability = request.form['trainability']
        interaction_with_other_animals = request.form.getlist('interaction_with_other_animals')
        date_of_intake = request.form['date']
        notes = request.form['notes']
        description = request.form['description']

        # Insert into MongoDB
        animal_data = {
            'animal_id': animal_id,
            'name': name,
            'photo': photo_binary,
            'species': species,
            'breed': breed,
            'age': int (age),
            'overall_health': overall_health,
            'vaccination': vaccination,
            'spayed_neutered': spayed_neutered,
            'energy_level': energy_level,
            'temperament': temperament,
            'trainability': trainability,
            'interaction_with_other_animals': interaction_with_other_animals,
            'date_of_intake': date_of_intake,
            'last_grooming_date':'',
            'notes': notes,
            'description': description


        }
        animal_collection.insert_one(animal_data)

        return redirect(url_for('display_animal'))  # Redirect to staff main page
    
    return render_template('animalprofile.html')

@app.route('/display_animal')
def display_animal():
    animal_data = animal_collection.find().sort('date_of_intake', -1)  # Retrieve animal data from the database
    return render_template('animal_data.html', animal_data=animal_data)

@app.route('/update_animal/<animal_id>', methods=['GET', 'POST'])
def update_animal(animal_id):
    animal = animal_collection.find_one({'animal_id': animal_id})
    if request.method == 'POST':
        # Check if a new photo is uploaded
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                # Read the binary data of the photo
                photo_binary = Binary(photo.read())  # Read photo binary data
                # Update the photo binary data in the database
                animal_collection.update_one({'animal_id': animal_id}, {'$set': {'photo': photo_binary}})

        # Update other fields of the animal document in the database
        animal_collection.update_one({'animal_id': animal_id}, {'$set': {
            'name': request.form['name'],
            'species': request.form['species'],
            'breed': request.form['breed'],
            'age': int(request.form['age']),
            'overall_health': request.form['overall_health'],
            'vaccination': request.form['vaccination'],
            'spayed_neutered': request.form['spayed_neutered'],
            'energy_level': request.form['energy_level'],
            'temperament': request.form['temperament'],
            'trainability': request.form['trainability'],
            'interaction_with_other_animals': request.form.getlist('interaction_with_other_animals'),
            'date_of_intake': request.form['date_of_intake'],
            'last_grooming_date': request.form['last_grooming_date'],
            'notes': request.form['notes'],
            'description': request.form['description']
        }})
        return redirect(url_for('display_animal'))
    return render_template('update_animal.html', animal=animal)


@app.route('/delete_animal', methods=['POST'])
def delete_animal():
    animal_id = request.form['animal_id']
    animal_collection.delete_one({'animal_id': animal_id})
    return redirect(url_for('display_animal'))

@app.route('/report_detail/<report_id>')
def report_detail(report_id):
    # Assuming you have a function to fetch report details from the database
    report_details = report_collection.find_one({'report_id': report_id})
    
    if report_details:
        return render_template('report_detail.html', report=report_details)
    else:
        return "Report not found", 404

@app.route('/new_treatment', methods=['GET', 'POST'])
def new_treatment():
    animal_id = request.args.get('animal_id')
    if request.method == 'POST':
        animal_id = request.form['animal_id']
        treatment_date = request.form['treatment_date']
        next_due_date = request.form['next_due_date']
        treatment_type = request.form['treatment_type']
        
        if 'treatment_name' in request.form:
            treatment_name = request.form['treatment_name']
        else:
            treatment_name = request.form['treatment_name_text']
        
        diagnosis = request.form['diagnosis']
        veterinarian = request.form['veterinarian']
        veterinary_clinic = request.form['veterinary_clinic']
        notes = request.form['notes']
        
        # Prefix for the report ID
        prefix = 'T'
        
        # Generate a random UUID and convert to string
        random_suffix = str(uuid.uuid4().hex)[:4]
        treatment_id = f"{prefix}{random_suffix}"

        if not animal_collection.find_one({'animal_id': animal_id}):
            return '''
                <script>
                    alert("Animal ID doesn't exist!");
                    window.location.href = "/new_treatment?animal_id={0}";
                </script>
            '''.format(animal_id)

        treatment_data = {
            'treatment_id': treatment_id,
            'animal_id': animal_id,
            'treatment_date': treatment_date,
            'next_due_date': next_due_date,
            'treatment_type': treatment_type,
            'treatment_name': treatment_name,
            'diagnosis': diagnosis,
            'veterinarian': veterinarian,
            'veterinary_clinic': veterinary_clinic,
            'notes': notes
        }
        medical_collection.insert_one(treatment_data)
        return redirect(url_for('medical_record', animal_id=animal_id))
    return render_template('new_treatment.html', animal_id=animal_id)

@app.route('/medical_record/<animal_id>')
def medical_record(animal_id):
    animal_records = list(medical_collection.find({'animal_id': animal_id}).sort('treatment_date', -1))
    return render_template('medical_record.html', records=animal_records, animal_id=animal_id)

@app.route('/view_treatment/<treatment_id>', methods=['GET', 'POST'])
def view_treatment(treatment_id):
    treatment = medical_collection.find_one({'treatment_id': treatment_id})
    if request.method == 'POST':
        animal_id = request.form['animal_id']
        treatment_date = request.form['treatment_date']
        next_due_date = request.form['next_due_date']
        treatment_type = request.form['treatment_type']
        
        if 'treatment_name' in request.form:
            treatment_name = request.form['treatment_name']

        else:
            treatment_name = request.form['treatment_name_text']

        diagnosis = request.form['diagnosis']
        veterinarian = request.form['veterinarian']
        veterinary_clinic = request.form['veterinary_clinic']
        notes = request.form['notes']

        
        treatment_data = {
           'treatment_id': treatment_id,
            'animal_id': animal_id,
            'treatment_date': treatment_date,
            'next_due_date': next_due_date,
            'treatment_type': treatment_type,
            'treatment_name': treatment_name,
            'diagnosis': diagnosis,
            'veterinarian': veterinarian,
            'veterinary_clinic': veterinary_clinic,
            'notes': notes
        }
        medical_collection.update_one({'treatment_id': treatment_id}, {'$set': treatment_data})
        return redirect(url_for('medical_record', animal_id=animal_id))
    return render_template('view_treatment.html', treatment=treatment)

@app.route('/delete_treatment/<treatment_id>', methods=['POST'])
def delete_treatment(treatment_id):
    treatment = medical_collection.find_one({'treatment_id': treatment_id})
    animal_id = treatment['animal_id']
    medical_collection.delete_one({'treatment_id': treatment_id})
    return redirect(url_for('medical_record', animal_id=animal_id))

@app.route('/animal_medical')
def animal_medical():
    animal_records = list(medical_collection.find().sort('treatment_date', -1))
    return render_template('animal_medical.html', records=animal_records)
@app.route('/add_moment', methods=['GET', 'POST'])
def add_moment():
    animal_id = request.args.get('animal_id', '')

    if request.method == 'POST':
        animal_id = request.form['animal_id']
        moment_date = request.form['moment_date']
        caption = request.form['caption']

        # Debugging: Print animal ID to console
        print(f"Animal ID received in POST: {animal_id}")

        if not animal_collection.find_one({'animal_id': animal_id}):
            print("Animal ID does not exist in the database.")
            return '''
                <script>
                    alert("Animal ID doesn't exist!");
                    window.location.href = "/add_moment";
                </script>
            '''

        # Prefix for the report ID
        prefix = 'M'
        
        # Generate a random UUID and convert to string
        random_suffix = str(uuid.uuid4().hex)[:4]
        moment_id = f"{prefix}{random_suffix}"

        # Read the binary data of the photo
        photo = request.files['moment_photo']
        photo_binary = Binary(photo.read())  # Read photo binary data
        
        # Insert data into MongoDB
        moment_collection.insert_one({
            'moment_id': moment_id,
            'animal_id': animal_id,
            'moment_photo': photo_binary,
            'moment_date': moment_date,
            'caption': caption
        })

        return redirect(url_for('moment_record', animal_id=animal_id))
    
    return render_template('add_moment.html', animal_id=animal_id)


@app.route('/view_moments')
def view_moments():
    # Fetch moments data from MongoDB
    moments = moment_collection.find()
    return render_template('view_moments.html', moments=moments)

@app.route('/moment_record/<animal_id>')
def moment_record(animal_id):
    moments = list(moment_collection.find({'animal_id': animal_id}).sort('moment_date', -1))
    return render_template('moment_record.html', animal_id=animal_id, moments=moments)


@app.route('/update_moment/<moment_id>', methods=['GET', 'POST'])
def update_moment(moment_id):
    moment = moment_collection.find_one({'moment_id': moment_id})

    if not moment:
        return '''
            <script>
                alert("Moment not found!");
                window.location.href = "/staff_home";
            </script>
        '''

    if request.method == 'POST':
        animal_id = request.form['animal_id']
        moment_date = request.form['moment_date']
        caption = request.form['caption']

        if not animal_collection.find_one({'animal_id': animal_id}):
            return '''
                <script>
                    alert("Animal Id doesn't exist!");
                    window.location.href = "/update_moment/{}";
                </script>
            '''.format(moment_id)

        update_data = {
            'animal_id': animal_id,
            'moment_date': moment_date,
            'caption': caption
        }

        # Check if a new photo is uploaded
        if 'moment_photo' in request.files and request.files['moment_photo'].filename != '':
            photo = request.files['moment_photo']
            photo_binary = Binary(photo.read())
            update_data['moment_photo'] = photo_binary

        # Update the moment in the database
        moment_collection.update_one({'moment_id': moment_id}, {'$set': update_data})

        return redirect(url_for('staff_home'))

    return render_template('update_moment.html', moment=moment)

@app.route('/delete_moment', methods=['POST'])
def delete_moment():
    moment_id = request.form['moment_id']
    moment_collection.delete_one({'moment_id': moment_id})
    return redirect(url_for('staff_home'))

@app.route('/browse_animals')
def browse_animals():
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True

    # Fetch animals based on filter criteria
    query = {'overall_health': {'$in': ['Good', 'Excellent']}}
    species = request.args.get('species')
    age_category = request.args.get('age')
    search = request.args.get('search')
    if species:
        query['species'] = species
    if age_category:
        min_age, max_age = AGE_RANGES.get(age_category, (0, float('inf')))
        # Calculate birthdate range based on age range
        max_birth_date = datetime.now() - timedelta(days=min_age*365)
        min_birth_date = datetime.now() - timedelta(days=max_age*365)
        query['age'] = {'$gte': min_age, '$lte': max_age}
    if search:
        query['$or'] = [{'name': {'$regex': search, '$options': 'i'}}, {'description': {'$regex': search, '$options': 'i'}}]

    # Use aggregation to filter out animals with 'fee paid' status in adoption collection
    pipeline = [
        {
            '$match': query
        },
        {
            '$lookup': {
                'from': 'adoption',
                'localField': 'animal_id',
                'foreignField': 'animal_id',
                'as': 'adoption_info'
            }
        },
        {
            '$addFields': {
                'adoption_status': {
                    '$arrayElemAt': ['$adoption_info.adoption_status', 0]
                }
            }
        },
        {
            '$match': {
                '$or': [
                    {'adoption_status': {'$ne': 'fee_paid'}},
                    {'adoption_status': {'$exists': False}}
                ]
            }
        },
        {
            '$sort': {'date_of_intake': -1}
        }
    ]

    filtered_animals = list(animal_collection.aggregate(pipeline))
    return render_template('browse_animals.html', user_logged_in=user_logged_in, animals=filtered_animals)


@app.route('/adoptable_animal_detail/<animal_id>')
def adoptable_animal_detail(animal_id):
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True

    # Retrieve animal information from the database based on animal_id
    animal = animal_collection.find_one({'animal_id': animal_id})
    animal_records = list(moment_collection.find({'animal_id': animal_id}).sort('moment_date', -1))
    # Render the HTML template with the animal information
    return render_template('adoptable_animal_detail.html', user_logged_in=user_logged_in, animal=animal, moments=animal_records)

@app.route('/submit_adoption', methods=['POST'])
def submit_adoption():
    if request.method == 'POST':
        # Retrieve form data
        animal_id = request.form['animal_id']
        animal_name = request.form['name']
        datetime1 = request.form['datetime1']
        datetime2 = request.form['datetime2']
        datetime3 = request.form['datetime3']

        # Retrieve user information from session and database
        username = session.get('username')
        user = user_collection.find_one({'username': username})

        if user:
            phone_number = user.get('phone_number')
            email_address = user.get('email')
        else:
            return '''
                <script>
                    alert("Please login to schedule");
                    window.location.href = "/login";
                </script>
            '''

        # Prefix for the adoption ID
        prefix = 'A'
        
        # Generate a random UUID and convert to string
        random_suffix = str(uuid.uuid4().hex)[:4]
        adoption_id = f"{prefix}{random_suffix}"

        # Current date and time
        current_datetime = datetime.now()

        # Combine date-time suggestions into meeting note
        meeting_note = f"Date and Time Suggestions:\n1. {datetime1}\n2. {datetime2}\n3. {datetime3}"

        # Store adoption information in the database
        adoption_data = {
            'adoption_id': adoption_id,
            'animal_id': animal_id,
            'animal_name': animal_name,
            'username': username,
            'phone_number': phone_number,
            'email_address': email_address,
            'adoption_status': 'apply',
            'meeting_location': '',
            'meeting_note': meeting_note,
            'submission_datetime': current_datetime
        }

        # Insert the adoption data into the database
        adoption_collection.insert_one(adoption_data)

        # Redirect to a success page or any other page as needed
        return redirect(url_for('appointment'))


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True

    if 'username' not in session:
        return redirect(url_for('user_home'))  # Redirect to login page if not logged in
    
    username = session['username']
    user = user_collection.find_one({'username': username})
    
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['password']
        
        # Check if old password matches the password stored in the database
        if not check_password_hash(user['password'], old_password):
            return render_template('update_user.html', user=user, error="Old password is incorrect.")
        
        # Update user details in the database
        updated_data = {
            'password': generate_password_hash(new_password) if new_password else user['password'],
            'phone_number': request.form['phone'],
            'email': request.form['email'],
            'name': request.form['name'],
            'age': request.form['age']
        }
        user_collection.update_one({'username': username}, {'$set': updated_data})
        
        return redirect(url_for('update_user', update_success=True))  # Redirect to the update_user route with success flag
    
    return render_template('update_user.html', user=user, user_logged_in=user_logged_in)



@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = session['username']
    user_collection.delete_one({'username': username})
    return redirect(url_for('index'))

@app.route('/appointment')
def appointment():
    user_logged_in = False  # Initialize user_logged_in variable
    # Check if the user is logged in
    if 'username' in session:
        user_logged_in = True

    # Retrieve the username from the session
    username = session.get('username')
    
    # Fetch all appointment details from the database for the logged-in user
    appointments = list(adoption_collection.find({'username': username}).sort('submission_datetime', -1))

    # Render the appointment page with the retrieved data
    return render_template('appointment.html', appointments=appointments, user_logged_in=user_logged_in)

@app.route('/update_adoption_status/<adoption_id>', methods=['POST'])
def update_adoption_status(adoption_id):
    new_status = request.form.get('status')
    adoption_collection.update_one(
        {'adoption_id': adoption_id},
        {'$set': {'adoption_status': new_status}}
    )
    return redirect(url_for('appointment'))

@app.route('/adoptions')
def adoptions():
    # Fetch the adoptions data from the collection
    adoptions = list(adoption_collection.find())
    
    # Sort adoptions based on 'submission_datetime' in descending order
    adoptions.sort(key=lambda x: x['submission_datetime'], reverse=True)
    
    # Render the template with sorted data
    return render_template('adoptions.html', adoptions=adoptions)

@app.route('/update_adoptions', methods=['POST'])
def update_adoptions():
    data = request.json
    updates = data.get('updates', [])
    for update in updates:
        adoption_id = update['adoption_id']
        adoption_status = update['adoption_status']
        meeting_location = update['meeting_location']
        meeting_note = update['meeting_note']
        adoption_collection.update_one(
            {'adoption_id': adoption_id},
            {'$set': {
                'adoption_status': adoption_status,
                'meeting_location': meeting_location,
                'meeting_note': meeting_note
            }}
        )
    return jsonify({'success': True})

@app.route('/delete_adoption/<adoption_id>', methods=['DELETE'])
def delete_adoption(adoption_id):
    result = adoption_collection.delete_one({'adoption_id': adoption_id})
    
    if result.deleted_count == 1:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400

@app.route('/check_transaction/<adoption_id>', methods=['GET'])
def check_transaction(adoption_id):
    transaction_exists = transaction_collection.find_one({'adoption_id': adoption_id}) is not None
    return jsonify({'exists': transaction_exists})

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # Handle form submission to add transaction
        prefix = 'T'
        random_suffix = str(uuid.uuid4().hex)[:4]
        transaction_id = f"{prefix}{random_suffix}"

        adoption_id = request.form['adoption_id']
        animal_id = request.form['animal_id']
        username = request.form['username']
        date = request.form['date']
        description = request.form['description']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        
        # Insert transaction data into your database
        transaction_data = {
            'transaction_id': transaction_id,
            'adoption_id': adoption_id,
            'animal_id': animal_id,
            'username': username,
            'date': date,
            'description': description,
            'amount': amount,
            'payment_method': payment_method
        }
        
        transaction_collection.insert_one(transaction_data)
        
        # Update adoption status to 'fee_paid' in adoption collection
        adoption_collection.update_one(
            {'adoption_id': adoption_id},
            {'$set': {
                'adoption_status': 'fee_paid'
            }}
        )
        
        return redirect(url_for('view_transactions'))
    
    elif request.method == 'GET':
        # Render the transaction form with prefilled data
        adoption_id = request.args.get('adoption_id')
        animal_id = request.args.get('animal_id')
        username = request.args.get('username')

    return render_template('add_transaction.html', adoption_id=adoption_id, animal_id=animal_id, username=username)

@app.route('/view_transactions')
def view_transactions():
    transactions = transaction_collection.find().sort('date', DESCENDING)
    return render_template('view_transactions.html', transactions=transactions)

@app.route('/save_transaction', methods=['POST'])
def save_transaction():
    transaction_data = request.json
    
    for transaction in transaction_data:
        transaction_id = transaction['transaction_id']
        transaction_collection.update_one({'transaction_id': transaction_id}, {'$set': transaction})
    
    return 'Transaction saved successfully', 200

@app.route('/delete_transaction', methods=['DELETE'])
def delete_transaction():
    transaction_id = request.json['transaction_id']
    result = transaction_collection.delete_one({'transaction_id': transaction_id})
    
    if result.deleted_count == 1:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'failed'}), 400
    
@app.route('/analysis')
def analysis():
    # Calculate total counts
    reported_stray_count = report_collection.count_documents({})
    saved_stray_count = animal_collection.count_documents({})
    adopted_count = adoption_collection.count_documents({'adoption_status': 'fee_paid'})
    
    # Aggregate the sum of 'amount' field in 'transaction' collection
    transaction_sum_pipeline = [
        {'$addFields': {'amount': {'$toDouble': '$amount'}}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    transaction_sum_result = list(transaction_collection.aggregate(transaction_sum_pipeline))
    transaction_sum = transaction_sum_result[0]['total'] if transaction_sum_result else 0
    transaction_sum_formatted = "{:.2f}".format(transaction_sum)

    # Aggregation for reported stray animals
    yearly_reported_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1}}
    ]
    monthly_reported_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}, 'month': {'$month': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    yearly_reported_counts = list(report_collection.aggregate(yearly_reported_pipeline))
    monthly_reported_counts = list(report_collection.aggregate(monthly_reported_pipeline))

    # Aggregation for saved stray animals
    yearly_saved_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date_of_intake'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1}}
    ]
    monthly_saved_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date_of_intake'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}, 'month': {'$month': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    yearly_saved_counts = list(animal_collection.aggregate(yearly_saved_pipeline))
    monthly_saved_counts = list(animal_collection.aggregate(monthly_saved_pipeline))

    # Aggregation for adopted animals
    yearly_adopted_pipeline = [
        {'$match': {'adoption_status': 'fee_paid'}},
        {'$addFields': {'date': {'$toDate': '$submission_datetime'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1}}
    ]
    monthly_adopted_pipeline = [
        {'$match': {'adoption_status': 'fee_paid'}},
        {'$addFields': {'date': {'$toDate': '$submission_datetime'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}, 'month': {'$month': '$date'}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    yearly_adopted_counts = list(adoption_collection.aggregate(yearly_adopted_pipeline))
    monthly_adopted_counts = list(adoption_collection.aggregate(monthly_adopted_pipeline))

    # Aggregation for transaction amounts
    yearly_transaction_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date'}, 'amount': {'$toDouble': '$amount'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}}, 'total_amount': {'$sum': '$amount'}}},
        {'$sort': {'_id.year': 1}}
    ]
    monthly_transaction_pipeline = [
        {'$addFields': {'date': {'$toDate': '$date'}, 'amount': {'$toDouble': '$amount'}}},
        {'$group': {'_id': {'year': {'$year': '$date'}, 'month': {'$month': '$date'}}, 'total_amount': {'$sum': '$amount'}}},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    yearly_transaction_counts = list(transaction_collection.aggregate(yearly_transaction_pipeline))
    monthly_transaction_counts = list(transaction_collection.aggregate(monthly_transaction_pipeline))

    # Aggregation for reported animal types
    reported_animal_type_distribution_pipeline = [
        {'$group': {'_id': '$animal_type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    reported_animal_type_distribution = list(report_collection.aggregate(reported_animal_type_distribution_pipeline))

    # Aggregation for adopted animal types
    adopted_animal_type_distribution_pipeline = [
        {'$match': {'adoption_status': 'fee_paid'}},  # Filter adopted animals
        {'$lookup': {
            'from': 'animal',
            'localField': 'animal_id',
            'foreignField': 'animal_id',  # Ensure 'foreignField' matches 'localField'
            'as': 'reported_animal'
        }},
        {'$unwind': '$reported_animal'},  # Unwind to normalize the joined data
        {'$group': {'_id': '$reported_animal.species', 'count': {'$sum': 1}}},  # Group by animal type
        {'$sort': {'count': -1}}  # Sort by count in descending order
    ]
    adopted_animal_type_distribution = list(adoption_collection.aggregate(adopted_animal_type_distribution_pipeline))

    # Aggregation for saved animal types
    saved_animal_type_distribution_pipeline = [
        {'$group': {'_id': '$species', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    saved_animal_type_distribution = list(animal_collection.aggregate(saved_animal_type_distribution_pipeline))
    
    return render_template('analysis.html', 
                           reported_stray_count=reported_stray_count,
                           saved_stray_count=saved_stray_count,
                           adopted_count=adopted_count,
                           transaction_sum=transaction_sum_formatted,
                           yearly_reported_counts=yearly_reported_counts,
                           monthly_reported_counts=monthly_reported_counts,
                           yearly_saved_counts=yearly_saved_counts,
                           monthly_saved_counts=monthly_saved_counts,
                           yearly_adopted_counts=yearly_adopted_counts,
                           monthly_adopted_counts=monthly_adopted_counts,
                           yearly_transaction_counts=yearly_transaction_counts,
                           monthly_transaction_counts=monthly_transaction_counts,
                           reported_animal_type_distribution=reported_animal_type_distribution,
                           adopted_animal_type_distribution=adopted_animal_type_distribution,
                           saved_animal_type_distribution=saved_animal_type_distribution)

@app.route('/get_locations')
def get_locations():
    animal_type = request.args.get('animal_type', '')
    report_status = request.args.get('report_status', '')
    locations = []

    query = {}
    if animal_type:
        query['animal_type'] = animal_type
    if report_status:
        query['report_status'] = report_status

    # Retrieve locations from the database
    cursor = report_collection.find(query, {
        'location': 1, 'description': 1, 'phone_number': 1, 'date': 1, 'time': 1, 'report_status': 1, 'remarks': 1, 'report_id': 1, '_id': 0
    })
    for document in cursor:
        coordinates = document['location'].split(',')
        lat = float(coordinates[0])
        lng = float(coordinates[1])
        description = document.get('description', 'No description available')
        phone_number = document.get('phone_number', 'No phone number available')
        date = document.get('date', 'No date available')
        time = document.get('time', 'No time available')
        report_status = document.get('report_status', 'No status available')
        remarks = document.get('remarks', 'No remarks available')
        report_id = document.get('report_id', 'No report ID available')
        
        locations.append({
            'lat': lat, 'lng': lng, 'description': description, 'phone_number': phone_number, 'date': date, 
            'time': time, 'report_status': report_status, 'remarks': remarks, 'report_id': report_id
        })

    return jsonify({'locations': locations})
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
