#app.py 
# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import your Config class and models
from app.config import Config  # Replace with the actual path to your Config class
from app.models import User, Task, UserXTask, TaskStatus, TaskPriority  # Adjust the import paths as needed

# Create the Flask app instance
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Load the configuration settings defined in the Config class
app.config.from_object(Config)  # Assuming you have a Config class defined

# Configure SQLAlchemy to connect to your database
db_host = 'plnru2.c3omnzoqavtp.us-east-2.rds.amazonaws.com'
db_port = 1433
db_username = 'admin'
db_password = 'ISDS4125'
db_name = 'PLNRU'

# Create the SQLAlchemy engine and session
db_url = f"mssql+pymssql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url)
sqlsession = sessionmaker(bind=engine)
dbsession = sqlsession()

# Create a base class for declarative models
Base = declarative_base()

# Initialize the Flask-Session extension
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# Define the is_user_logged_in function
def is_user_logged_in():
    # Check if the 'user_id' key is present in the session
    return 'user_username' in session

# ... Other routes and functions ...

# Route for the landing page
@app.route('/')
def landing_page():
    return render_template('landing.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if a user with the same username already exists
        existing_user = User.query.filter_by(user_username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            # Create a new user and insert it into the database
            new_user = User(user_username=username, user_password=password, user_email=email)
            dbsession.add(new_user)
            dbsession.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database to find a user with the provided username and password
        user = dbsession.query(User).filter_by(user_username=username, user_password=password).first()

        if user:
            session['user_username'] = user.user_username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to 'home' route upon successful login
        else:
            flash('Username or password is incorrect. Please try again.', 'danger')

    return render_template('login.html')

# Home route
@app.route('/home')
def home():
    if is_user_logged_in():
        # Implement your logic for logged-in users here
        return render_template('home.html')  # Assuming 'user_home.html' is the user's home page
    else:
        # Implement your logic for non-logged-in users here
        return render_template('landing.html')  # Redirect to the landing page for non-logged-in users

# Profile route
@app.route('/profile')
def profile():
    # Retrieve the user's profile information from the database
    user_id = session.get('user_id')
    user = db.session.query(User).get(user_id)

    # Render the profile template with the user's information
    return render_template('profile.html', user=user)

# Edit Profile route
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Determine if the user is logged in
    is_user_logged_in = 'user_id' in session

    if is_user_logged_in:
        # The user is logged in, continue with profile editing logic

        if request.method == 'POST':
            # Update the user's profile
            # ...

            flash('Profile updated successfully!', 'success')

            # Redirect the user to their profile page or another appropriate page
            return redirect(url_for('profile'))

        return render_template('edit_profile.html', user=user, user_is_logged_in=is_user_logged_in)
    else:
        # The user is not logged in, show a message and redirect to the login page
        flash('Please log in to access the edit profile page.', 'info')
        return redirect(url_for('login'))


# Tasks route
@app.route('/tasks')
def tasks():
    # Check if the user is logged in
    if 'user_id' in session:
        # Retrieve the username of the currently logged-in user
        logged_in_username = session['user_id']

        # Query the UserXTask table to get the user_x_task rows associated with the logged-in user
        user_x_task_rows = db.session.query(UserXTask).filter_by(user_username=logged_in_username).all()

        # Extract the task IDs associated with the logged-in user
        task_ids = [row.task_ID for row in user_x_task_rows]

        # Query the Task table to retrieve the tasks associated with the logged-in user
        tasks = db.session.query(Task).filter(Task.task_ID.in_(task_ids)).all()

        return render_template('tasks.html', tasks=tasks)
    else:
        # Handle the case when the user is not logged in
        flash('Please log in to access your tasks.', 'info')
        return redirect(url_for('login'))

# Edit Task route
@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    # Retrieve the task to edit from the database (adjust based on your database structure)
    task = Task.query.get(task_id)

    if request.method == 'POST':
        # Update the task with user-submitted data
        task.title = request.form['title']
        task.description = request.form['description']

        # Save the changes to the database
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))  # Redirect to the tasks page

    return render_template('edit_task.html', task=task)

@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('user_id', None)
    # Redirect to the login page or any other desired page
    return redirect(url_for('login'))

# Your other routes and views...

if __name__ == '__main__':
    app.run(debug=True)
