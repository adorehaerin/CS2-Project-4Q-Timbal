from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid
import random

app = Flask(__name__)

# flash messages still need a secret key apparently (coding on some nonchalant shi)
app.secret_key = "kaiza_secret_key" 

# secret codes bc security is my passion 
SECRET_ADMIN_CODE = "1234" 
COMPANY_INVITE_CODE = "SHARPAY-428" 

# proof nga WALA KO GA DATABASE @sirmearsk hi
data_store = {
    'admin': {'password': 'admin123', 
              'name': 'System Admin', 
              'role': 'admin', 
              'failed_attempts': 0, 
              'locked_until': None, 
              'age': 'N/A', 
              'address': 'Kaiza Corp HQ', 
              'requests': []},
    'itsupportjim': {'password': 'rescue911', 
                     'name': 'IT Support Team', 
                     'role': 'admin', 
                     'failed_attempts': 0, 
                     'locked_until': None, 
                     'age': 'N/A', 
                     'address': 'Kaiza Corp Server Room', 
                     'requests': []},
    'geto_suguruu': {'password': 'ilovekaiza', 
                     'name': 'Suguru Geto', 
                     'role': 'employee', 
                     'failed_attempts': 0, 
                     'locked_until': None, 
                     'age': '21', 
                     'address': 'Kaiza Corp Building 3, Floor 2, Desk 45', 
                     'requests': [{"id":"1", "date":"March 10, 2026 at 10:00 AM", "text":"Requesting a new keyboard for my workstation."}]},
    'satoru_gojo': {'password': 'limitless99', 
                    'name': 'Satoru Gojo', 
                    'role': 'employee', 
                    'failed_attempts': 0, 
                    'locked_until': None, 
                    'age': '28', 
                    'address': 'Kaiza Corp Building 1, Floor 5, Desk 12', 
                    'requests': [{"id":"2", "date":"March 11, 2026 at 2:30 PM", "text":"Need IT support to fix my dual monitor setup :P"}]},
    'emily_watson': {'password': 'emily2026', 
                     'name': 'Emily Watson', 
                     'role': 'employee', 
                     'failed_attempts': 0, 
                     'locked_until': None, 
                     'age': '34', 
                     'address': 'Kaiza Corp Building 2, Floor 3, Desk 78', 
                     'requests': [{"id":"3", "date":"March 12, 2026 at 9:15 AM", "text":"Please inform Gojo to keep it down."}]},
    'mark_lee': {'password': 'letmeintroduceyoutosomenewthings', 
                'name': 'Mark Lee',
                'role': 'admin', 
                'failed_attempts': 0, 
                'locked_until': None, 
                'age': '27', 
                'address': 'Kaiza Corp Building 3, Floor 1, Desk 15', 
                'requests': []},
    'adorehaerin': {'password': 'ilovegeto<3', 
                    'name': 'Kaiza Timbal', 
                    'role': 'employee', 
                    'failed_attempts': 0, 
                    'locked_until': None, 
                    'age': '25', 
                    'address': 'Kaiza Corp Building 2, Floor 2, Desk 30', 
                    'requests': []}
}

@app.route('/')
def home():
    splashes = [
        "Welcome to the future of office services!",
        "I need coffee... and maybe some IT support!",
        "Office cat puked? Make a request now! 🐱",
        "Need 5 photocopies? Just ask! 📠",
        "Always at your service! 🌟",
        "The Admin is watching... 👀",
        "What's broken today? Let's fix it together!",
        "Locked out? Get out, you hacker. (jk, just ask for help!)",
        "Hello, Kaiza Corp! 👋",
        "The coffee machine is broken again...",
        "DU DU DU DU Max Verstappen 🫡",
        "Ring-ring-ring-ring (4x) pick up the phone!📞",
        "Need to confess to a co-worker but you're too shy? We're here to save you!😉",
        "Work! The Schuyler Sisters 🎶",
        "Lewis, Lewis Hamilton... 🏎️💨"
    ]
    random_splash = random.choice(splashes)
    return render_template('home.html', splash_text=random_splash)

@app.route('/about')
def about():
    return render_template('about.html')


# nabuang najud ko 
@app.route('/edit_request/<username>/<req_id>', methods=['GET', 'POST'])
def edit_request(username, req_id):
    # Security check: Make sure user exists
    if username not in data_store:
        return redirect(url_for('login'))

    user_requests = data_store[username].get('requests', [])
    
    # looks through the user's dictionary list to find the exact request
    target_req = None
    for req in user_requests:
        if str(req['id']) == str(req_id):
            target_req = req
            break

    # 2. unya naay error handling if di nila makita ang request, basin na delete na or something
    if not target_req:
        flash("❌ Error: We couldn't find that request to edit!")
        return redirect(url_for('submit_request', username=username))

    # 3. REQUIREMENT! make sure nga wala pa naka reply si admin
    if target_req.get('feedback'):
        flash("🔒 You cannot edit a request after the Admin has replied.")
        return redirect(url_for('submit_request', username=username))

    # 4. If they clicked UPDATE (POST request)
    if request.method == 'POST':
        updated_text = request.form.get('updated_request_details', '').strip()

        # Validation: oh fah nah, don't leave it empty
        if not updated_text:
            flash("❌ Error: Request details cannot be empty!")
            # Pass target_req['text'] so the box shows the previous text, not an empty box!
            return render_template('edit_request.html', username=username, req_id=req_id, request_text=target_req['text'])

        # Update ONLY the 'text' part of the dictionary!
        target_req['text'] = updated_text
        
        flash("✅ SUCCESS: Your request has been perfectly updated!")
        return redirect(url_for('submit_request', username=username))

    # 5. If they just clicked the "Edit" button to view the page (GET request)
    return render_template('edit_request.html', username=username, req_id=req_id, request_text=target_req['text'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract data and strip whitespace
        entered_code = request.form.get('invite_code', '').strip()
        user = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        age_str = request.form.get('age', '').strip() # changed to age_str for our check
        address = request.form.get('address', '').strip()

        # Check if any fields are completely blank (oh fah nah)
        if not entered_code or not user or not password or not name or not age_str or not address:
            flash("❌ Error: All fields must be filled out to register!")
            return redirect(url_for('register'))

        # mo check sa age
        try:
            age = int(age_str) # attempts to turn the text into a number
            if age < 18 or age > 79:
                flash("❌ Error: Employee age must be between 18 and 79.")
                return redirect(url_for('register'))
        except ValueError:
            # dapat numbers btw dili "twenty"
            flash("❌ Error: Age must be a valid number.")
            return redirect(url_for('register'))
        # end

        if entered_code != COMPANY_INVITE_CODE:
            flash("❌ Invalid Company Code! Only Kaiza Corp employees can register.")
            return redirect(url_for('register'))

        if user in data_store:
            flash("❌ Username already exists! Please choose another.")
            return redirect(url_for('register'))
        
        # mo save real
        data_store[user] = {
            'password': password,
            'name': name,
            'age': age, 
            'address': address,
            'requests': [], 'role': 'employee', 'failed_attempts': 0, 'locked_until': None
        }
        flash(" Registration successful! Welcome to Kaiza Corp. Please log in.")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # strip spaces to prevent empty space bypass
        user = request.form.get('username', '').strip()
        pw = request.form.get('password', '').strip()
        
        # check if fields are empty
        if not user or not pw:
            flash("❌ Error: Username and password fields cannot be left empty!")
            return render_template('login.html', locked=False)

        if user not in data_store:
            flash("❌ Account not found! Please Register!")
            return render_template('login.html', locked=False)

        user_data = data_store[user]

        # check if the account is locked indefinitely haha l
        if user_data.get('locked_until'):
            flash("🔒 ACCOUNT LOCKED: Please contact the Admin to unlock your account.")
            return render_template('login.html', locked=True)

        # checking password
        if user_data['password'] == pw:
            user_data['failed_attempts'] = 0
            user_data['locked_until'] = None
                
            if user_data.get('role') == 'admin':
                return redirect(url_for('admin_verify', username=user))
            return redirect(url_for('submit_request', username=user))
        else:
            user_data['failed_attempts'] += 1
            tries_left = 3 - user_data['failed_attempts']
            
            if tries_left > 0:
                flash(f"❌ Invalid password! You have {tries_left} tries left.")
            else:
                user_data['locked_until'] = True
                flash("🔒 SECURITY ALERT: Account locked indefinitely due to 3 failed attempts. Contact Admin.")
                return render_template('login.html', locked=True)
            
    return render_template('login.html', locked=False)

@app.route('/admin-verify/<username>', methods=['GET', 'POST'])
def admin_verify(username):
    if request.method == 'POST':
        code = request.form.get('secret_code', '').strip()
        
        if not code:
            flash("❌ Error: Secret code cannot be empty!")
            return render_template('admin_verify.html', username=username)

        if code == SECRET_ADMIN_CODE:
            return redirect(url_for('admin_panel', admin_username=username))
        else:
            flash("Incorrect Secret Code! Access Denied.")
            return redirect(url_for('login'))
    return render_template('admin_verify.html', username=username)

@app.route('/request/<username>', methods=['GET', 'POST'])
def submit_request(username):
    if username not in data_store:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        service_note = request.form.get('request_details', '').strip()
        
        # oh fah nah, cant be empty 
        if not service_note:
            flash("❌ Error: Your request cannot be empty!")
            return render_template('request.html', user=data_store[username], username=username)

        req_id = str(uuid.uuid4())
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p") 
        
        data_store[username]['requests'].append({
            'id': req_id, 'text': service_note, 'date': current_time, 'feedback': ''
        })
        flash("Request sent successfully!")
    return render_template('request.html', user=data_store[username], username=username)

@app.route('/reply/<admin_username>/<target_username>/<req_id>', methods=['POST'])
def reply_request(admin_username, target_username, req_id):
    if target_username in data_store:
        reply_message = request.form.get('reply_message', '').strip()
        
        if not reply_message:
            flash("❌ Error: Reply message cannot be empty!")
            return redirect(url_for('admin_panel', admin_username=admin_username))

        for req in data_store[target_username]['requests']:
            if req['id'] == req_id:
                req['feedback'] = reply_message
                flash(f"Reply sent to {data_store[target_username]['name']}!")
                break
    return redirect(url_for('admin_panel', admin_username=admin_username))

@app.route('/complete/<admin_username>/<target_username>/<req_id>', methods=['POST'])
def complete_request(admin_username, target_username, req_id):
    if target_username in data_store:
        data_store[target_username]['requests'] = [r for r in data_store[target_username]['requests'] if r['id'] != req_id]
        flash("Task marked as complete and removed!")
    return redirect(url_for('admin_panel', admin_username=admin_username))

@app.route('/admin/<admin_username>')
def admin_panel(admin_username):
    if admin_username not in data_store or data_store[admin_username]['role'] != 'admin':
        flash("Unauthorized access!")
        return redirect(url_for('login'))

    search_query = request.args.get('q', '').lower()
    filtered_data = {}
    
    for user, data in data_store.items():
        if search_query:
            search_match = (
                search_query in user.lower() or search_query in data['name'].lower() or search_query in data['address'].lower()
            )
            for req in data.get('requests', []):
                if search_query in req['text'].lower():
                    search_match = True
            if search_match:
                filtered_data[user] = data
        else:
            filtered_data[user] = data
            
    return render_template('admin.html', all_data=filtered_data, search_query=search_query, admin_username=admin_username)

@app.route('/team/<username>')
def team_directory(username):
    if username not in data_store:
        return redirect(url_for('login'))
    return render_template('team.html', user=data_store[username], all_data=data_store, username=username)

@app.route('/ban_user/<admin_username>/<target_username>', methods=['POST'])
def ban_user(admin_username, target_username):
    if target_username in data_store:
        data_store[target_username]['locked_until'] = True
        flash(f"User @{target_username} has been banned! 🔨")
    return redirect(url_for('team_directory', username=admin_username))

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    # Security check: Make sure they exist
    if username not in data_store:
        return redirect(url_for('login'))
    
    user_data = data_store[username]
    
    if request.method == 'POST':
        # 1. Extract the new data from the form
        new_name = request.form.get('name', '').strip()
        new_age_str = request.form.get('age', '').strip()
        new_address = request.form.get('address', '').strip()
        new_password = request.form.get('password', '').strip()
        
        # 2. Validation: Empty Fields Check (Just like we did for 5 points!)
        if not new_name or not new_age_str or not new_address or not new_password:
            flash("❌ Error: All fields must be filled out!")
            return redirect(url_for('profile', username=username))
        
        # 3. Validation: Age Check
        try:
            new_age = int(new_age_str)
            if new_age < 18 or new_age > 100:
                flash("❌ Error: Age must be between 18 and 100.")
                return redirect(url_for('profile', username=username))
        except ValueError:
            flash("❌ Error: Age must be a valid number.")
            return redirect(url_for('profile', username=username))
        
        # 4. work work, angelicaaa
        user_data['name'] = new_name
        user_data['age'] = str(new_age) 
        user_data['address'] = new_address
        user_data['password'] = new_password
        
        flash(" Profile updated successfully!")
        return redirect(url_for('profile', username=username))
        
    return render_template('profile.html', user=user_data, username=username)

@app.route('/delete_user/<admin_username>/<target_username>', methods=['POST'])
def delete_user(admin_username, target_username):
    # Security check: Make sure the person deleting is actually the admin
    if admin_username not in data_store or data_store[admin_username]['role'] != 'admin':
        flash("Unauthorized action.")
        return redirect(url_for('login'))

    # Check if the target user actually exists in our dictionary
    if target_username in data_store:
        # Prevent the admin from accidentally deleting themselves!
        if target_username == admin_username:
            flash("You cannot delete the admin account!")
        else:
            # Delete the user from the data store
            deleted_name = data_store[target_username]['name']
            del data_store[target_username]
            
            # Flash the success message for the rubric
            flash(f" SUCCESS: Employee '{deleted_name}' (@{target_username}) has been permanently deleted.")
    else:
        flash("Error: User not found.")

    # Redirect back to the admin dashboard
    return redirect(url_for('admin_panel', admin_username=admin_username))

@app.route('/admin_edit_request/<admin_username>/<target_username>/<req_id>', methods=['GET', 'POST'])
def admin_edit_request(admin_username, target_username, req_id):
    if admin_username not in data_store or data_store[admin_username]['role'] != 'admin':
        return redirect(url_for('login'))
        
    if target_username not in data_store:
        flash("❌ Error: User not found.")
        return redirect(url_for('admin_panel', admin_username=admin_username))
        
    # this part almost made me crash out so hard trying to find the right request
    target_req = None
    for req in data_store[target_username].get('requests', []):
        if str(req['id']) == str(req_id):
            target_req = req
            break
            
    if not target_req:
        flash("❌ Error: Request not found.")
        return redirect(url_for('admin_panel', admin_username=admin_username))
        
    if request.method == 'POST':
        updated_text = request.form.get('updated_request_details', '').strip()
        
        if not updated_text:
            flash("❌ Error: Request details cannot be empty!")
            return redirect(url_for('admin_edit_request', admin_username=admin_username, target_username=target_username, req_id=req_id))
            
        target_req['text'] = updated_text
        flash("✅ SUCCESS: Request updated by Admin!")
        return redirect(url_for('admin_panel', admin_username=admin_username))
        
    return render_template('admin_edit_request.html', admin_username=admin_username, target_username=target_username, req_id=req_id, request_text=target_req['text'])

@app.route('/admin_edit_user/<admin_username>/<target_username>', methods=['GET', 'POST'])
def admin_edit_user(admin_username, target_username):
    # Admin security check: get out you hacker
    if admin_username not in data_store or data_store[admin_username]['role'] != 'admin':
        flash("Unauthorized action.")
        return redirect(url_for('login'))

    if target_username not in data_store:
        flash("❌ Error: User not found.")
        return redirect(url_for('admin_panel', admin_username=admin_username))
        
    user_data = data_store[target_username]
    
    if request.method == 'POST':
        # extracting data speeding through like lewis lewis hamilton
        new_name = request.form.get('name', '').strip()
        new_age_str = request.form.get('age', '').strip()
        new_address = request.form.get('address', '').strip()
        new_password = request.form.get('password', '').strip()
        
        # 1. RUBRIC CHECK: Empty fields are prevented manually!
        if not new_name or not new_age_str or not new_address or not new_password:
            flash("❌ Error: All fields must be filled out!")
            return redirect(url_for('admin_edit_user', admin_username=admin_username, target_username=target_username))
        
        # 2. RUBRIC CHECK: Age Validation (No infants or negative numbers!)
        try:
            new_age = int(new_age_str)
            if new_age < 18 or new_age > 79:
                flash("❌ Error: Employee age must be between 18 and 79!")
                return redirect(url_for('admin_edit_user', admin_username=admin_username, target_username=target_username))
        except ValueError:
            flash("❌ Error: Age must be a valid number!")
            return redirect(url_for('admin_edit_user', admin_username=admin_username, target_username=target_username))
            
        # THE MAGIC: Admin updating another user's profile
        user_data['name'] = new_name
        user_data['age'] = str(new_age)
        user_data['address'] = new_address
        user_data['password'] = new_password
        
        flash(f"✅ SUCCESS: {target_username}'s profile has been updated by the Admin!")
        return redirect(url_for('admin_panel', admin_username=admin_username))
        
    return render_template('admin_edit_user.html', admin_username=admin_username, target_username=target_username, user=user_data)

@app.route('/logout')
def logout():
    flash("You have been successfully logged out. See you next time!")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
