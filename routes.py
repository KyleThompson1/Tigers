from flask import render_template, Blueprint, request, redirect, url_for, session, flash
import pymysql
from werkzeug.security import check_password_hash
from csi3335f2024 import mysql

# --------- LOGIC FOR HTTP REQUESTS WILL BE IN THIS FILE ---------
# def get_teams():
#     try:
#         con = pymysql.connect(host=cfg.mysql['host'], user=cfg.mysql['user'], password=cfg.mysql['password'],
#                               database=cfg.mysql['database'])
#         cur = con.cursor()
#         SQL = "SELECT DISTINCT team_name FROM teams ORDER BY team_name ASC"
#         cur.execute(SQL)
#         teams = cur.fetchall()
#         return [team[0] for team in teams]
#
#     finally:
#         con.close()



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
    return render_template('Roster.html')

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
            cursor.execute("SELECT username, banned FROM users WHERE username != 'admin'")
            users = cursor.fetchall()  # Returns a tuple of tuples

            # Convert tuple of tuples to a list of dictionaries
            user_list = [{'username': user[0], 'banned': user[1]} for user in users]

            return render_template('Admin.html', users=user_list)
        except pymysql.Error as e:
            print(f"Database Error: {e}")
            flash("An error occurred while fetching users.")
        finally:
            if conn.open:
                cursor.close()
                conn.close()

    # Flash message for unauthorized access
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

            # Fetch user id, username, password, role, and banned status
            cursor.execute(
                "SELECT id, username, password, role, banned FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()  # Use fetchone() since we expect one record per username

            if result:
                user_id, db_username, stored_password, role, banned = result  # Unpack the result tuple

                # Check if the user is banned
                if banned == 1:  # User is banned
                    flash('Your account has been banned. Contact the administrator for more information.')
                    return redirect(url_for('main.home'))

                # Check if the password is correct
                if check_password_hash(stored_password, password):
                    session.clear()  # Clear existing session data
                    session['user_id'] = user_id  # Store the user ID in the session
                    session['username'] = db_username  # Store the username in the session
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
@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('main.home'))

@main.route('/ban_user', methods=['POST'])
def ban_user():
    username = request.form.get('user')  # Get the selected username from the form

    if not username:
        flash("No user selected to ban.")
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

        # Update the `banned` column for the selected user
        cursor.execute("UPDATE users SET banned = 1 WHERE username = %s", (username,))
        conn.commit()

        flash(f"User {username} has been banned successfully.")
    except pymysql.Error as e:
        print(f"Database error: {e}")
        flash(f"Database error: {e}")
    finally:
        if conn.open:
            cursor.close()
            conn.close()

    return redirect(url_for('main.admin_page'))
