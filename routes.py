from flask import render_template, Blueprint, request, redirect, url_for, session, flash
import pymysql
from werkzeug.security import check_password_hash
from csi3335f2024 import mysql

# Create a blueprint to organize routes
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('Home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # Fetch form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate inputs
        if not (first_name and last_name and username and password and confirm_password):
            flash("All fields are required.")
            return render_template('Registration.html', first_name=first_name, last_name=last_name,
                                   username=username, password=password, confirm_password=confirm_password)

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('Registration.html', first_name=first_name, last_name=last_name,
                                   username=username, password=password, confirm_password=confirm_password)

        try:
            # Hash the password
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password, method='scrypt')

            # Connect to the database
            conn = pymysql.connect(
                host=mysql["host"],
                user=mysql["user"],
                password=mysql["password"],
                db=mysql["database"]
            )
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                flash("Username already taken. Please choose another.")
                return redirect(url_for('main.register'))

            # Insert the new user
            cursor.execute(
                """
                INSERT INTO users (username, password, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username, hashed_password, first_name, last_name, 'regular user')
            )
            conn.commit()

            flash("Registration successful! Please log in.")
            return redirect(url_for('main.home'))
        except pymysql.Error as e:
            print(f"Database Error: {e}")
            flash("An error occurred during registration. Please try again.")
        finally:
            if conn.open:
                cursor.close()
                conn.close()

    return render_template('Registration.html')


@main.route('/play_grid')
def play_grid():
    return render_template('Play-Immaculate-Grid.html')


@main.route('/roster_grid', methods=['GET', 'POST'])
def roster_grid():
    username = session.get('username', 'Guest')  # Get username from session or use 'Guest' as default
    return render_template('Roster-Grid.html', username=username)

@main.route('/team_year', methods=['GET'])
def team_year():
    con = pymysql.connect(
        host=mysql["host"],
        user=mysql["user"],
        password=mysql["password"],
        db=mysql["database"]
    )
    try:
        cur = con.cursor()
        sql = "SELECT DISTINCT team_name FROM teams ORDER BY team_name"
        cur.execute(sql)
        teams = [team[0] for team in cur.fetchall()]
        return render_template('Team-Year.html', teams=teams)

    finally:
        con.close()

@main.route('/generate_roster', methods=['GET'])
def generate_roster():
    team_name = request.args.get('team_name')
    year_id = request.args.get('yearID')

    if team_name and year_id:
        # Retrieve user_id from session
        user_id = session.get('user_id')

        if user_id is None:
            flash("You must be logged in to request a roster.")
            return redirect(url_for('auth.login'))  # Redirect to login if not logged in

        # Log the request in the roster_requests table
        con = pymysql.connect(
            host=mysql["host"],
            user=mysql["user"],
            password=mysql["password"],
            db=mysql["database"]
        )
        try:
            cursor = con.cursor()

            # Insert the request data into the 'roster_requests' table
            sql_log = """
            INSERT INTO roster_requests (user_id, team_name, yearID)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql_log, (user_id, team_name, year_id))
            con.commit()

            flash(f"Roster request for {team_name} ({year_id}) logged successfully.")

            # Render a message confirming the request or redirect to another page
            return render_template('Roster.html', team_name=team_name, year_id=year_id)

        finally:
            con.close()

    else:
        flash("Please select both team and year.")
        return redirect(url_for('main.team_year'))

@main.route('/get_years')
def get_years():
    team_name = request.args.get('team_name')

    con = pymysql.connect(
        host=mysql["host"],
        user=mysql["user"],
        password=mysql["password"],
        db=mysql["database"]
    )

    try:
        cur = con.cursor()
        sql = "SELECT DISTINCT yearID FROM teams WHERE team_name = %s ORDER BY yearID DESC"
        cur.execute(sql, (team_name,))
        years = [(year[0]) for year in cur.fetchall()]
        return ','.join(str(year) for year in years)

    finally:
        con.close()


@main.route('/admin')
def admin_page():
    # Check if the user is logged in and has the 'admin' role
    if session.get('username') and session.get('role') == 'admin':
        try:
            conn = pymysql.connect(
                host=mysql["host"],
                user=mysql["user"],
                password=mysql["password"],
                db=mysql["database"]
            )
            cursor = conn.cursor()

            # Fetch usernames and banned status except for 'admin'
            cursor.execute("SELECT id, username, banned FROM users WHERE username != 'admin'")
            users = cursor.fetchall()  # Returns a tuple of tuples

            return render_template('Admin.html', users=users)
        except pymysql.Error as e:
            print(f"Database Error: {e}")
            flash("An error occurred while fetching users.")
        finally:
            if conn.open:
                cursor.close()
                conn.close()

    flash("You must be an admin to access this page.")
    return redirect(url_for('main.home'))

@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Please enter both username and password')  # Flash message
            return redirect(url_for('main.home'))  # Redirect back to the login page

        try:
            conn = pymysql.connect(
                host=mysql["host"],
                user=mysql["user"],
                password=mysql["password"],
                db=mysql["database"]
            )
            cursor = conn.cursor()

            # Fetch user id, username, password, first_name, last_name, role, and banned status
            cursor.execute(
                "SELECT id, username, first_name, last_name, password, role, banned FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()  # Use fetchone() since we expect one record per username

            if result:
                user_id, db_username, first_name, last_name, stored_password, role, banned = result  # Unpack the result tuple

                # Check if the user is banned
                if banned == 1:  # User is banned
                    flash('Your account has been banned. Contact the administrator for more information.')
                    return redirect(url_for('main.home'))

                # Check if the password is correct
                if check_password_hash(stored_password, password):
                    session.clear()  # Clear existing session data
                    session['user_id'] = user_id  # Store the user ID in the session
                    session['username'] = db_username  # Store the username in the session
                    session['first_name'] = first_name  # Store the first name in the session
                    session['last_name'] = last_name  # Store the last name in the session
                    session['role'] = role  # Store the role in the session

                    if role == 'admin':
                        return redirect(url_for('main.admin_page'))  # Redirect to admin page if user is an admin
                    else:
                        return redirect(url_for('main.roster_grid'))  # Redirect to landing page for regular users
                else:
                    flash('Invalid username or password')
                    return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('main.home'))
        except pymysql.Error as err:
            print("Error: {}".format(err))
            flash('A database error occurred')
            return redirect(url_for('main.home'))
        finally:
            if conn.open:
                cursor.close()
                conn.close()

    return render_template('Home.html')

# Logout route
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('main.home'))


@main.route('/manage_user', methods=['POST'])
def manage_user():
    # Retrieve the username and action from the form
    username = request.form.get('username')  # Get the selected username
    action = request.form.get('action')  # Get the action (either 'ban' or 'unban')

    # Validate input
    if not username:
        flash("No user selected.")
        return redirect(url_for('main.admin_page'))

    try:
        # Connect to the database
        conn = pymysql.connect(
            host=mysql["host"],
            user=mysql["user"],
            password=mysql["password"],
            db=mysql["database"]
        )
        cursor = conn.cursor()

        # Perform the requested action
        if action == 'ban':
            # Ban the user by setting the banned column to 1
            cursor.execute("UPDATE users SET banned = 1 WHERE username = %s", (username,))
            conn.commit()
            flash(f"User '{username}' has been banned successfully.")

        elif action == 'unban':
            # Unban the user by setting the banned column to 0
            cursor.execute("UPDATE users SET banned = 0 WHERE username = %s", (username,))
            conn.commit()
            flash(f"User '{username}' has been unbanned successfully.")

        else:
            flash("Invalid action.")
            return redirect(url_for('main.admin_page'))

    except pymysql.Error as e:
        print(f"Database error: {e}")
        flash(f"Database error: {e}")

    finally:
        # Ensure the connection is closed
        if conn.open:
            cursor.close()
            conn.close()

    return redirect(url_for('main.admin_page'))

@main.route('/view_profile', methods=['GET'])
def view_profile():
    username = session.get('username', 'Guest')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    profile_pic = session.get('profile_pic', 'PicOne.png')  # Default profile picture if not set
    user_id = session.get('user_id')

    # Fetch the roster requests and their count using the helper function
    roster_requests = get_roster_requests_profile(user_id)
    roster_request_count = len(roster_requests)

    # Render the profile page with the necessary data
    return render_template('Profile.html',
                           username=username,
                           first_name=first_name,
                           last_name=last_name,
                           profile_pic=profile_pic,
                           roster_requests=roster_requests,
                           roster_request_count=roster_request_count)

@main.route('/profile', methods=['GET'])
def profile():
    username = session.get('username')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    profile_pic = session.get('profile_pic', 'PicOne.png')  # Default to PicOne.png if not set
    user_id = session.get('user_id')  # Assuming user_id is stored in the session

    # Fetch the roster requests and their count using the helper function
    roster_requests = get_roster_requests_profile(user_id)
    roster_request_count = len(roster_requests)

    # Fetch teams from the database
    con = pymysql.connect(
        host=mysql["host"],
        user=mysql["user"],
        password=mysql["password"],
        db=mysql["database"]
    )

    try:
        cur = con.cursor()

        # Fetch the roster requests made by the logged-in user
        sql_roster_requests = """
        SELECT id, team_name, yearID FROM roster_requests WHERE user_id = %s ORDER BY timestamp DESC
        """
        cur.execute(sql_roster_requests, (user_id,))
        roster_requests = cur.fetchall()  # Fetch the roster requests for the user

        # Count the number of roster requests
        roster_request_count = len(roster_requests)

    finally:
        con.close()

    # Render the profile page with roster requests, teams, and user data
    return render_template('Profile.html',
                           username=username,
                           first_name=first_name,
                           last_name=last_name,
                           profile_pic=profile_pic,
                           roster_requests=roster_requests,
                           roster_request_count=roster_request_count)  # Pass the count to the template

@main.route('/change_profile_pic', methods=['POST'])
def change_profile_pic():
    profile_pic = request.form.get('profile_pic')
    session['profile_pic'] = profile_pic  # Save the new profile picture in the session

    flash("Your profile picture has been updated.")
    return redirect(url_for('main.profile'))  # Redirect to profile page

# Helper Function for fetching requests for profile
def get_roster_requests_profile(user_id):
    con = pymysql.connect(
        host=mysql["host"],
        user=mysql["user"],
        password=mysql["password"],
        db=mysql["database"]
    )
    try:
        cur = con.cursor()
        sql_roster_requests = """
        SELECT id, team_name, yearID FROM roster_requests WHERE user_id = %s ORDER BY timestamp DESC
        """
        cur.execute(sql_roster_requests, (user_id,))
        roster_requests = cur.fetchall()  # Fetch the roster requests for the user
        return roster_requests
    finally:
        con.close()
        
@main.route('/admin/roster_requests', methods=['GET'])
def view_roster_requests():
    if session.get('role') == 'admin':
        selected_user_id = request.args.get('user_id')  # Capture user ID from the query string
        roster_requests = []
        selected_username = None
        selected_user_request_count = 0  # Initialize the request count for the selected user
        total_requests = 0  # Initialize the total requests counter

        try:
            conn = pymysql.connect(
                host=mysql["host"],
                user=mysql["user"],
                password=mysql["password"],
                db=mysql["database"]
            )
            cursor = conn.cursor()

            # Fetch all users for the dropdown menu
            cursor.execute("SELECT id, username, banned FROM users WHERE role != 'admin' ORDER BY username ASC")
            users = cursor.fetchall()

            # Fetch the total number of requests made by all users
            cursor.execute("SELECT COUNT(*) FROM roster_requests")
            total_requests = cursor.fetchone()[0]

            # If a user is selected, fetch their roster requests
            if selected_user_id:
                # Fetch the username of the selected user
                cursor.execute("SELECT username FROM users WHERE id = %s", (selected_user_id,))
                selected_username = cursor.fetchone()
                if selected_username:
                    selected_username = selected_username[0]

                cursor.execute("""
                    SELECT r.id, u.username, r.team_name, r.yearID, r.timestamp
                    FROM roster_requests r
                    JOIN users u ON r.user_id = u.id
                    WHERE u.id = %s
                    ORDER BY r.timestamp DESC
                """, (selected_user_id,))
                roster_requests = cursor.fetchall()

                # Count the number of requests for the selected user
                cursor.execute("""
                    SELECT COUNT(*) FROM roster_requests WHERE user_id = %s
                """, (selected_user_id,))
                selected_user_request_count = cursor.fetchone()[0]

            return render_template(
                'Admin.html',
                users=users,
                roster_requests=roster_requests,
                selected_username=selected_username,
                total_requests = total_requests,  # Pass the total requests to the template
                selected_user_request_count = selected_user_request_count
            )

        except pymysql.Error as e:
            flash(f"An error occurred while fetching roster requests: {e}", "error")
            return redirect(url_for('main.admin_page'))

        finally:
            if conn.open:
                cursor.close()
                conn.close()

    flash("You must be an admin to access this page.", "error")
    return redirect(url_for('main.home'))