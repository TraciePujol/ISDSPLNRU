#app.py 
# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_session import Session
from flask import request  # Import the request object
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy import join

from datetime import datetime


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
    # Check if the 'user_username' key is present in the session
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

        # Check if a user with the same username or email already exists
        existing_user = dbsession.query(User).filter(or_(User.user_username == username, User.user_email == email)).first()

        if existing_user:
            if existing_user.user_username == username:
                flash('Username already exists. Please choose a different username.', 'danger')
            if existing_user.user_email == email:
                flash('Email already registered. Please use a different email.', 'danger')
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
            return redirect(url_for('home'))  # Redirect to the home page or another appropriate page upon successful login
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

# Example route for searching students with the same .edu domain
@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        search_type = request.form.get('search_type')

        if search_type == 'edu_domain':
            # Get the current user's email domain
            user_email = session.get('user_email', '')  # Replace with your session variable

            # Extract the domain from the email
            user_domain = user_email.split('@')[1]

            # Query the database for students with the same domain and public profiles
            matching_students = User.query.filter_by(user_email.like(f'%@{user_domain}')).filter_by(user_status='public').all()

            return render_template('search_results.html', students=matching_students)
    
    # Handle other search types or errors here
    return redirect(url_for('home'))



# Profile route
@app.route('/profile')
def profile():
    # Retrieve the user's profile information from the database
    user_username = session.get('user_username')
    user = dbsession.query(User).filter_by(user_username=user_username).first()

    # Render the profile template with the user's information
    return render_template('profile.html', user=user)

# Edit profile route
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Determine if the user is logged in
    is_user_logged_in = 'user_username' in session

    if is_user_logged_in:
        # The user is logged in, continue with profile editing logic

        # Retrieve the user's profile data from your database or session
        # For example, if you store user data in session, you can retrieve it like this:
        user = session.get('user_data', {})

        if request.method == 'POST':
            # Update the user's profile based on the form data

            # Get the form data
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            email = request.form.get('email')
            school = request.form.get('school')
            major = request.form.get('major')
            graduation = request.form.get('graduation')
            classification = request.form.get('classification')

            # Update the user's profile in the database (assuming you have a User model)
            user_in_db = User.query.filter_by(user_username=user['user_username']).first()
            user_in_db.user_firstName = first_name
            user_in_db.user_lastName = last_name
            user_in_db.user_email = email
            user_in_db.user_college = school
            user_in_db.user_major = major
            user_in_db.user_graduation = graduation
            user_in_db.user_classification = classification

            # Update searchability
            is_searchable = request.form.get('is_searchable')  # Get the value from the form
            user_in_db = User.query.filter_by(user_username=user['user_username']).first()
            user_in_db.is_searchable = is_searchable  # Update the searchability field


            # Commit the changes to the database
            db.session.commit()  # <-- Place it here

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
    if 'user_username' in session:
        # Retrieve the username of the currently logged-in user
        logged_in_username = session['user_username']

        # Query the UserXTask table to get the user_x_task rows associated with the logged-in user
        user_x_task_rows = dbsession.query(UserXTask).filter_by(user_username=logged_in_username).all()

        # Extract the task IDs associated with the logged-in user
        task_ids = [row.task_ID for row in user_x_task_rows]

        # Query the Task table to retrieve the tasks associated with the logged-in user
        tasks = dbsession.query(Task).filter(Task.task_ID.in_(task_ids)).all()

        return render_template('tasks.html', tasks=tasks)
    else:
        # Handle the case when the user is not logged in
        flash('Please log in to access your tasks.', 'info')
        return redirect(url_for('login'))


# Create Task route
@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        if not is_user_logged_in():  # Check if the user is not logged in
            flash('Please log in to create a task.', 'info')
            return redirect(url_for('login'))  # Redirect to the login page

        task_description = request.form.get('task_description')
        task_notes = request.form.get('task_notes')
        task_startDate = request.form.get('task_startDate')
        task_dueDate = request.form.get('task_dueDate')
        task_timeEstimate = request.form.get('task_timeEstimate')
        task_timeEstimateUnit = request.form.get('task_timeEstimateUnit')
        task_Course = request.form.get('task_Course')
        user_username = request.form.get('user_username')  # This is a hidden field

        # Calculate the task duration based on the selected unit
        if task_timeEstimateUnit == 'minute':
            task_duration = int(task_timeEstimate)
        elif task_timeEstimateUnit == 'hour':
            task_duration = int(task_timeEstimate) * 60  # Convert hours to minutes
        elif task_timeEstimateUnit == 'day':
            task_duration = int(task_timeEstimate) * 60 * 24  # Convert days to minutes

        # Create a new Task instance with the calculated duration
        new_task = Task(
            task_description=task_description,
            task_Notes=task_notes,
            task_startDate=task_startDate,
            task_dueDate=task_dueDate,
            task_timeEstimate=task_duration,  # Use the calculated duration
            task_Course=task_Course,
            user_username=user_username,  # Associate the task with the user
        )

        # Add and commit the new task to the database
        dbsession.add(new_task)
        dbsession.commit()

        # Check if the task was successfully committed to the database
        created_task = dbsession.query(Task).filter_by(task_description=task_description).first()

        if created_task:
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks'))  # Redirect to the tasks page after creating the task
        else:
            flash('Task creation failed. Please try again.', 'error')
            return redirect(url_for('create_task'))  # Redirect back to the create_task page in case of failure

    # Handle other HTTP methods or errors here
    return render_template('create_task.html')  # Render the create_task.html page



# Edit Task route
@app.route('/edit_task/<int:task_ID>', methods=['GET', 'POST'])
def edit_task(task_ID):
    # Retrieve the task to edit from the database
    task = Task.query.get(task_ID)

    if request.method == 'POST':
        # Update the task with user-submitted data
        task.task_description = request.form['task_description']
        task.task_Notes = request.form['task_Notes']
        task.task_startDate = request.form['task_startDate']
        task.task_dueDate = request.form['task_dueDate']
        task.task_timeEstimate = request.form['task_timeEstimate']
        task.task_Course = request.form['task_Course']

        # Calculate task priority based on the new due date
        priority = calculate_priority(task.task_dueDate)

        # Update the task's priority
        task.task_priority = priority

        # Save the changes to the database
        dbsession.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('update_task'))  # Redirect to the update_task page

    return render_template('edit_task.html', task=task)

# Delete Task route
@app.route('/delete_task/<int:task_ID>', methods=['GET', 'POST'])
def delete_task(task_ID):
    # Retrieve the task to delete from the database
    task = Task.query.get(task_ID)

    if request.method == 'POST':
        # Delete the task from the database
        dbsession.delete(task)
        dbsession.commit()

        flash('Task deleted successfully!', 'success')
        return redirect(url_for('tasks'))  # Redirect to the tasks page

    return render_template('delete_task.html', task=task)


@app.route('/logout/<confirmation>', methods=['GET', 'POST'])
def logout(confirmation=None):
    if confirmation == 'confirmed':
        # Clear the user's session
        session.pop('user_username', None)
        # Redirect to the login page or any other desired page
        return redirect(url_for('login'))
    else:
        return render_template('logout.html')




# Your other routes and views...

if __name__ == '__main__':
    app.run(debug=True)
