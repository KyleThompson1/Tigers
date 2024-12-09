from flask import render_template, Blueprint, request, redirect, url_for, session, flash, jsonify
import pymysql
from sqlalchemy.sql.coercions import WhereHavingImpl
from werkzeug.security import check_password_hash
from csi3335f2024 import mysql
import requests
from bs4 import BeautifulSoup
import sqlite3

# Create a blueprint to organize routes
main = Blueprint('main', __name__)

CONDITIONS_MAP = {
        ".300+\xa0AVG CareerBatting": "b.playerID IN (SELECT playerid FROM batting b WHERE b.b_AB > 0 GROUP BY b.playerID HAVING AVG(b.b_H * 1.0 / b.b_AB) >= 0.300)",
        ".300+\xa0AVG SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID AND ba.teamID = t.teamID AND ba.b_AB > 0 GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_H) / SUM(ba.b_AB) >= 0.300)",
        "≤\xa03.00\xa0ERA Season": "EXISTS (SELECT 1 FROM pitching pit WHERE pit.playerID = b.playerID AND pit.teamID = t.teamID AND pit.p_ERA <= 3.00 GROUP BY pit.playerID, pit.yearID)",
        "10+ HR SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID AND ba.teamID = t.teamID GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_HR) > 10)",
        "10+ WIN SEASON": "p.W >= 10",
        "100+\xa0RBI SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID AND ba.teamID = t.teamID AND ba.b_AB > 0 GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_RBI) > 100)",
        "100+\xa0Run SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.teamID = t.teamID AND ba.playerID = b.playerID GROUP BY ba.playerID, ba.yearId HAVING SUM(ba.b_R) > 100)",
        "20+ Win SeasonPitching": "EXISTS (SELECT 1 FROM pitching pit WHERE pit.playerID = b.playerID AND pit.W >= 20 AND pit.yearID = b.yearID)",
        "200+ Hits SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID AND ba.teamID = t.teamID GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_H) >= 200)",
        "200+ K SeasonPitching": "EXISTS (SELECT 1 FROM pitching pit WHERE pit.playerID = b.playerID AND pit.teamID = t.teamID GROUP BY pit.playerID, pit.yearID HAVING SUM(pit.p_SO) >= 200)",
        "200+\xa0Wins CareerPitching": "b.playerID IN (SELECT pit.playerID FROM pitching pit GROUP BY pit.playerID HAVING SUM(pit.p_W) >= 200)",
        "2000+ K CAREER": "SUM(p.SO) >= 2000",
        "2000+\xa0Hits CareerBatting": "b.playerID IN (SELECT b.playerID FROM batting b GROUP BY b.playerID HAVING SUM(b.b_H) >= 2000)",
        "30+ HR / 30+ SB SEASON": "b.b_HR >= 30 AND b.b_SB >= 30",
        "30+ HR SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.teamID = t.teamID AND ba.playerID = b.playerID GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_HR) >= 30)",
        "30+ SB Season": "SUM(b.b_SB) >= 30",
        "30+ SAVE Season": "p.SV >= 30",
        "300+ HR CareerBatting": "b.playerID IN (SELECT ba.playerID FROM batting ba GROUP BY ba.playerID HAVING SUM(ba.b_HR) >= 300)",
        "300+ SAVE CAREER": "SUM(p.SV) >= 300",
        "300+ WINS CAREER": "SUM(p.W) >= 300",
        "3000+ K CAREER": "SUM(p.SO) >= 3000",
        "3000+\xa0Hits CareerBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID GROUP BY ba.playerID HAVING SUM(ba.b_H) >= 3000)",
        "40+ 2B SEASON": "b.b_2B >= 40",
        "40+ HR SeasonBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.teamID = b.teamID AND ba.playerID = b.playerID GROUP BY ba.playerID, ba.yearID HAVING SUM(ba.b_HR) >= 30)",
        "40+ SAVE SEASON": "p.SV >= 40",
        "40+ WAR CAREER": "SUM(b.WAR) >= 40",
        "500+ HR CareerBatting": "EXISTS (SELECT 1 FROM batting ba WHERE ba.playerID = b.playerID GROUP BY ba.playerID HAVING SUM(ba.b_HR) >= 500)",
        "All Star": "EXISTS (SELECT 1 FROM allstarfull a WHERE a.playerID = b.playerID AND a.yearID = b.yearID)",
        "BORN OUTSIDE US 50 STATES AND DC": "p.birthCountry NOT IN ('USA')",
        "Cy Young": "EXISTS (SELECT 1 FROM awards a WHERE a.awardID = 'Cy Young Award' AND a.playerID = b.playerID and a.yearID = b.yearID)",
        "Designated Hittermin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'DH' AND f.playerID = b.playerID AND f.teamID = b.teamID)",
        "First Round Draft Pick": "EXISTS (SELECT 1 FROM collegeplaying cp WHERE cp.playerID = b.playerID AND cp.yearID = YEAR(MAX(p.debutDate)))",
        "Gold Glove": "EXISTS (SELECT 1 FROM awards a WHERE a.awardID = 'Gold Glove' AND a.playerID = b.playerID AND a.yearID = b.yearID)",
        "Hall of Fame": "EXISTS (SELECT 1 FROM halloffame h WHERE h.playerID = b.playerID AND h.inducted = 'Y')",
        "MVP": "(SELECT 1 FROM awards a WHERE a.awardID = 'Most Valuable Player' AND a.playerID = b.playerID AND a.yearID = b.yearId)",
        "Only One Team": "b.playerID IN (SELECT b1.playerID FROM batting b1 GROUP BY b1.playerID HAVING COUNT(DISTINCT b1.teamID) = 1)",
        "Pitchedmin. 1 game": "EXISTS (SELECT 1 FROM pitching p WHERE p.playerID = b.playerID)",
        "Played Catchermin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'C' AND f.playerID = b.playerID)",
        "Played Center\xa0Fieldmin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'CF' AND f.playerID = b.playerID)",
        "Played First\xa0Basemin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = '1B' AND f.playerID = b.playerID AND b.teamID = f.teamID)",
        "Played Third\xa0Basemin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = '3B' AND f.teamID = t.teamID AND f.playerID = b.playerID)",
        "Rookie of the Year": "(SELECT 1 FROM awards a WHERE a.awardID = 'Rookie of the Year' AND a.playerID = b.playerID AND a.yearID = b.yearId)",
        "WORLD SERIES CHAMP": "EXISTS (SELECT 1 FROM awards a WHERE a.awardID = 'World Series' AND a.playerID = b.playerID)",
        "Played Left\xa0Fieldmin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'LF' AND f.f_G >= 1 AND f.playerID = b.playerID)",
        "Played Right\xa0Fieldmin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'RF' AND f.f_G >= 1 AND f.playerID = b.playerID)",
        "6+ WAR Season": "SUM((((b.b_H + b.b_BB - IFNULL(b.b_CS, 0) + IFNULL(b.b_HBP, 0)) * ((b.b_H - b.b_2B - b.b_3B - b.b_HR) + (2 * b.b_2B) + (3 * b.b_3B) + (4 * b.b_HR) +  (0.26 * (b.b_BB - IFNULL(b.b_IBB, 0) + IFNULL(b.b_HBP, 0))) + (0.52 * (IFNULL(b.b_SH, 0) + IFNULL(b.b_SF, 0) + IFNULL(b.b_SB, 0)))))/ (b.b_AB + b.b_BB + IFNULL(b.b_HBP, 0) + IFNULL(b.b_SH, 0) + IFNULL(b.b_SF, 0)))) / 10 >= 6",
        "Silver Slugger": "EXISTS (SELECT 1 FROM awards a WHERE a.awardID = 'Silver Slugger' AND a.playerID = b.playerID)",
        "Played Shortstopmin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = 'SS' AND f.f_g > 0 AND f.teamID = b.teamID AND b.playerID = f.playerID)",
        "Played Outfieldmin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE (f.position = 'CF' OR f.position = 'LF' OR f.position = 'RF')  AND f.f_G >= 1 AND f.playerID = b.playerID)",
        "Played Second\xa0Basemin. 1 game": "EXISTS (SELECT 1 FROM fielding f WHERE f.position = '2B' AND f.playerID = b.playerID)",
        "Born Outside US 50 States and\xa0DC": "EXISTS (SELECT 1 FROM people p2 WHERE p2.playerID = b.playerID AND p2.birthCountry NOT IN ('USA') AND p2.birthCountry IS NOT NULL)",
        "Threw a No‑Hitter": "EXISTS (SELECT 1 FROM pitching pit WHERE pit.playerID = b.playerID AND pit.teamID = t.teamID AND pit.p_H = 0  AND pit.p_IPOuts >= 27 AND pit.p_ER = 0 )",
        "10+ Win SeasonPitching": "EXISTS (SELECT 1 FROM pitching pit WHERE pit.playerID = b.playerID AND pit.teamID = t.teamID GROUP BY pit.playerID, pit.yearID HAVING SUM(pit.p_W) >= 10)",
    }

teams_map = {
        "Anaheim Angels": "ANA",
        "Altoona Mountain City": "ALT",
        "Arizona Diamondbacks": "ARI",
        "Atlanta Braves": "ATL",
        "Baltimore Orioles": "BAL",
        "Baltimore Canaries": "BL1",
        "Baltimore Marylands": "BL4",
        "Baltimore Terrapins": "BLF",
        "Baltimore Monumentals": "BLU",
        "Boston Americans": "BOS",
        "Boston   Red Sox": "BOS",
        "Boston Red Stockings": "BS1",
        "Boston Beaneaters": "BSN",
        "Boston Bees": "BSN",
        "Boston Braves": "BSN",
        "Boston Doves": "BSN",
        "Boston Red Caps": "BSN",
        "Boston Rustlers": "BSN",
        "Boston Reds": "BSU",
        "Brooklyn Eckfords": "BR1",
        "Brooklyn Atlantics": "BR3",
        "Brooklyn Gladiators": "BR4",
        "Brooklyn Tip-Tops": "BRF",
        "Brooklyn Bridegrooms": "BRO",
        "Brooklyn Dodgers": "BRO",
        "Brooklyn Grooms": "BRO",
        "Brooklyn Robins": "BRO",
        "Brooklyn Superbas": "BRO",
        "Brooklyn Ward's Wonders": "BRP",
        "Buffalo Blues": "BUF",
        "Buffalo Buffeds": "BUF",
        "Buffalo Bisons": "BFN",
        "California Angels": "CAL",
        "Chicago Chi-Feds": "CHF",
        "Chicago Whales": "CHF",
        "Chicago  White Sox": "CHA",
        "Chicago Colts": "CHN",
        "Chicago Cubs": "CHN",
        "Chicago Orphans": "CHN",
        "Chicago White Stockings": "CHN",
        "Chicago Pirates": "CHP",
        "Cincinnati Red Stockings": "CIN",
        "Cincinnati Redlegs": "CIN",
        "Cincinnati Reds": "CIN",
        "Cincinnati Outlaw Reds": "CNU",
        "Cleveland Blues": "CLE",
        "Cleveland Bronchos": "CLE",
        "Cleveland Guardians": "CLE",
        "Cleveland Indians": "CLE",
        "Cleveland Naps": "CLE",
        "Cleveland Spiders": "CLE",
        "Cleveland Forest Citys": "CL1",
        "Cleveland Spiders": "CL4",
        "Columbus Buckeyes": "CL5",
        "Columbus Solons": "CL6",
        "Cleveland Infants": "CLP",
        "Colorado Rockies": "COL",
        "Detroit Tigers": "DET",
        "Detroit Wolverines": "DTN",
        "Elizabeth Resolutes": "ELI",
        "Florida Marlins": "FLO",
        "Fort Wayne Kekiongas": "FW1",
        "Houston Astros": "HOU",
        "Houston Colt .45’s": "HOU",
        "Hartford Dark Blues": "HR1",
        "Indianapolis Blues": "IN1",
        "Indianapolis Hoosiers": "IN3",
        "Kansas City Royals": "KCA",
        "Kansas City Athletics": "KC1",
        "Kansas City Cowboys": "KC2",
        "Kansas City Packers": "KCF",
        "Keokuk Westerns": "KEO",
        "Los Angeles Dodgers": "LAN",
        "Los Angeles Angels": "LAA",
        "Louisville Grays": "LS1",
        "Louisville Colonels": "LS2",
        "Louisville Eclipse": "LS2",
        "Miami Marlins": "MIA",
        "Milwaukee Brewers": "MIL",
        "Milwaukee Braves": "ML1",
        "Milwaukee Grays": "ML2",
        "Minnesota Twins": "MIN",
        "Middletown Mansfields": "MID",
        "Montreal Expos": "MON",
        "Newark Pepper": "NEW",
        "New Haven Elm Citys": "NH1",
        "New York Giants": "NY1",
        "New York Gothams": "NY1",
        "New York Mutuals": "NY2",
        "New York Metropolitans": "NY4",
        "New York Highlanders": "NYA",
        "New York Yankees": "NYA",
        "New York Mets": "NYN",
        "Oakland Athletics": "OAK",
        "Philadelphia Athletics": "PHA",
        "Philadelphia Whites": "PH2",
        "Philadelphia Centennials": "PH3",
        "Philadelphia Blue Jays": "PHI",
        "Philadelphia Phillies": "PHI",
        "Philadelphia Quakers": "PHI",
        "Philadelphia Keystones": "PHU",
        "Pittsburg Alleghenys": "PIT",
        "Pittsburgh Rebels": "PTF",
        "Pittsburgh Burghers": "PTP",
        "Pittsburgh Pirates": "PIT",
        "Providence Grays": "PRO",
        "Rockford Forest Citys": "RC1",
        "Rochester Broncos": "RC2",
        "Richmond Virginians": "RIC",
        "San Diego Padres": "SDN",
        "San Francisco Giants": "SFN",
        "St. Louis Red Stockings": "SL1",
        "St. Louis Brown Stockings": "SL2",
        "St. Louis Maroons": "SL5",
        "St. Louis Cardinals": "SLN",
        "St. Louis Perfectos": "SLN",
        "St. Louis Browns": "SLA",
        "St. Louis Terriers": "SLF",
        "St. Paul White Caps": "SPU",
        "Syracuse Stars": "SR1",
        "Tampa Bay Devil Rays": "TBA",
        "Tampa Bay Rays": "TBA",
        "Texas Rangers": "TEX",
        "Toledo Blue Stockings": "TL1",
        "Toledo Maumees": "TL2",
        "Toronto  Blue Jays": "TOR",
        "Troy Haymakers": "TRO",
        "Troy Trojans": "TRN",
        "Washington Nationals": "WAS",
        "Wilmington Quicksteps": "WIL",
        "Worcester Ruby Legs": "WOR",
        "Washington Senators": "WS1",
        "Washington Olympics": "WS3",
        "Washington Blue Legs": "WS5",
        "Washington Statesmen": "WS9"
    }

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

@main.route('/player_search')
def player_search():
    return render_template('Player_Search.html')

@main.route('/roster_grid', methods=['GET', 'POST'])
def roster_grid():
    username = session.get('username', 'Guest')  # Get username from session or use 'Guest' as default
    return render_template('Roster-Grid.html', username=username)

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
        sql = "SELECT DISTINCT team_name FROM teams ORDER BY team_name"
        cur.execute(sql)
        teams = [team[0] for team in cur.fetchall()]
        return render_template('Team-Year.html', teams=teams)

    finally:
        con.close()



# @main.route('/get_years')
# def get_years():
#     team_name = request.args.get('team_name')
#     try:
#         cur = con.cursor()

#         # Fetch the roster requests made by the logged-in user
#         sql_roster_requests = """
#         SELECT id, team_name, yearID FROM roster_requests WHERE user_id = %s ORDER BY timestamp DESC
#         """
#         cur.execute(sql_roster_requests, (user_id,))
#         roster_requests = cur.fetchall()  # Fetch the roster requests for the user

#         # Count the number of roster requests
#         roster_request_count = len(roster_requests)

#     finally:
#         con.close()

#     # Render the profile page with roster requests, teams, and user data
#     return render_template('Profile.html',
#                            username=username,
#                            first_name=first_name,
#                            last_name=last_name,
#                            profile_pic=profile_pic,
#                            roster_requests=roster_requests,
#                            roster_request_count=roster_request_count)  # Pass the count to the template

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

#GENERATE TEAM ROSTERS#
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

@main.route('/generate_roster')
def generate_roster():
    team_name = request.args.get('team_name')
    year = request.args.get('yearID')

    if team_name and year:
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

            with con.cursor(pymysql.cursors.DictCursor) as cursor:
            # Batting Leaders Query
                batting_sql = """
                SELECT 
                    people.playerID, 
                    nameFirst, 
                    nameLast, 
                    b_G,
                    b_SB,
                    b_AB, 
                    b_H, 
                    b_HR, 
                    b_R, 
                    b_RBI,
                    ROUND(((b_2B) + (2 * b_3B) + (3 * b_HR)) / b_AB, 3) AS ISO,
                    (b_AB + b_BB + b_HBP + b_SH + b_SF) AS PA,
                    ROUND((b_H - b_HR)/(b_AB - b_SO - b_HR + b_SF), 3) AS BABIP,
                    ROUND((b_H/b_AB), 3) AS AVG,
                    ROUND((b_H + b_BB + b_HBP)/(b_AB + b_BB + b_HBP + b_SF), 3) AS OBP,
                    ROUND(((b_H - b_2B - b_3B - b_HR) + (2 * b_2B) + (3 * b_3B) + (4 * b_HR)) * 1.0 / NULLIF(b_AB, 0), 3) AS SLG,
                    ROUND(
                    (
                        (0.690 * (b_BB - b_IBB)) +
                        (0.722 * b_HBP) +
                        (0.888 * (b_H - b_2B - b_3B - b_HR)) +
                        (1.271 * b_2B) +
                        (1.616 * b_3B) +
                        (2.101 * b_HR)
                    ) * 1.0 / 
                    NULLIF((b_AB + b_BB - b_IBB + b_SF + b_HBP), 0),4) AS wOBA
                FROM batting 
                JOIN people ON batting.playerID = people.playerID
                WHERE batting.yearID = %s
                AND batting.teamID = (
                    SELECT teamID 
                    FROM teams 
                    WHERE team_name = %s AND yearID = %s
                )
                ORDER BY b_H DESC
                LIMIT 10
                """

                # Pitching Leaders Query
                pitching_sql = """
                SELECT 
                    people.playerID, 
                    nameFirst, 
                    nameLast, 
                    p_G,
                    p_GS,
                    p_IPouts,
                    ROUND(CAST(p_SO AS FLOAT) / p_BFP * 100, 2) AS KPercentage,
                    ROUND(CAST(p_BB AS FLOAT) / p_BFP * 100, 2) AS BBPercentage,
                    ROUND(CAST(p_HR AS FLOAT) * 27 / (p_IPOuts / 3), 2) AS HR9,
                    ROUND(CAST(p_H - p_HR AS FLOAT) / (p_BFP - p_SO - p_BB - p_HR - p_SF), 3) AS BABIP,
                    ROUND((p_H + p_BB + p_HBP - p_R)/(p_H + p_BB + p_HBP - (1.4 * p_HR)), 3) AS LOB,
                    p_BB
                FROM pitching 
                JOIN people ON pitching.playerID = people.playerID
                WHERE pitching.teamID = (
                    SELECT teamID 
                    FROM teams 
                    WHERE team_name = %s AND yearID = %s
                ) AND pitching.yearID = %s
                ORDER BY p_G DESC
                LIMIT 10
                """


                # Execute batting query
                cursor.execute(batting_sql, (year, team_name, year))
                batting_leaders = cursor.fetchall()

                # Execute pitching query
                cursor.execute(pitching_sql, (team_name, year, year))
                pitching_leaders = cursor.fetchall()



                # Insert the request data into the 'roster_requests' table
                sql_log = """
                INSERT INTO roster_requests (user_id, team_name, yearID)
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql_log, (user_id, team_name, year))
                con.commit()

                flash(f"Roster request for {team_name} ({year}) logged successfully.")

                # Render a message confirming the request or redirect to another page
                return render_template('roster.html',
                                   team_name=team_name,
                                   year=year,
                                   batting_leaders=batting_leaders,
                                   pitching_leaders=pitching_leaders)

        finally:
            con.close()

    else:
        flash("Please select both team and year.")
        return redirect(url_for('main.team_year'))
#     try:
#         cur = con.cursor()
#         sql_roster_requests = """
#         SELECT id, team_name, yearID FROM roster_requests WHERE user_id = %s ORDER BY timestamp DESC
#         """
#         cur.execute(sql_roster_requests, (user_id,))
#         roster_requests = cur.fetchall()  # Fetch the roster requests for the user
#         return roster_requests
#     finally:
#         con.close()

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

#GENERATE PLAYER PAGE#
@main.route('/player_list', methods=['GET'])
def player_list():
    nameFirst = request.args.get('nameFirst')
    nameLast = request.args.get('nameLast')

    if nameFirst and nameLast:
        # Retrieve user_id from session
        user_id = session.get('user_id')

        # Log the request in the roster_requests table
        con = pymysql.connect(
            host=mysql["host"],
            user=mysql["user"],
            password=mysql["password"],
            db=mysql["database"]
        )

        try:
            cursor = con.cursor()

            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                # Batting Leaders Query
                player_sql = """
                    SELECT 
                        nameFirst,
                        nameLast,
                        playerID,
                        birthYear,
                        deathYear
                    FROM people
                    WHERE nameFirst = %s AND nameLast = %s
                    """

                # Execute batting query
                cursor.execute(player_sql, (nameFirst, nameLast))
                playerData = cursor.fetchall()

                # Render a message confirming the request or redirect to another page
                return render_template('Player_List.html',
                                       nameFirst=nameFirst,
                                       nameLast=nameLast,
                                       playerData=playerData)

        finally:
            con.close()

    else:
        flash("Enter player.")
        return redirect(url_for('main'))

@main.route('/player_profile', methods=['GET'])
def player_profile():
    playerID = request.args.get('playerID')

    if playerID:
        # Retrieve user_id from session
        user_id = session.get('user_id')

        # Log the request in the roster_requests table
        con = pymysql.connect(
            host=mysql["host"],
            user=mysql["user"],
            password=mysql["password"],
            db=mysql["database"]
        )

        try:
            cursor = con.cursor()

            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                # Batting Leaders Query
                batting_sql = """
                    SELECT 
                        nameFirst,
                        nameLast,
                        batting.yearID,
                        b_G,
                        b_SB,
                        b_AB, 
                        b_H, 
                        b_HR, 
                        b_R, 
                        b_RBI,
                        ROUND(((b_2B) + (2 * b_3B) + (3 * b_HR)) / b_AB, 3) AS ISO,
                        (b_AB + b_BB + b_HBP + b_SH + b_SF) AS PA,
                        ROUND((b_H - b_HR)/(b_AB - b_SO - b_HR + b_SF), 3) AS BABIP,
                        ROUND((b_H/b_AB), 3) AS AVG,
                        ROUND((b_H + b_BB + b_HBP)/(b_AB + b_BB + b_HBP + b_SF), 3) AS OBP,
                        ROUND(((b_H - b_2B - b_3B - b_HR) + (2 * b_2B) + (3 * b_3B) + (4 * b_HR)) * 1.0 / NULLIF(b_AB, 0), 3) AS SLG,
                        ROUND(
                        (
                            (0.690 * (b_BB - b_IBB)) +
                            (0.722 * b_HBP) +
                            (0.888 * (b_H - b_2B - b_3B - b_HR)) +
                            (1.271 * b_2B) +
                            (1.616 * b_3B) +
                            (2.101 * b_HR)
                        ) * 1.0 / 
                        NULLIF((b_AB + b_BB - b_IBB + b_SF + b_HBP), 0),4) AS wOBA
                    FROM batting 
                    JOIN people ON batting.playerID = people.playerID
                    WHERE batting.playerID = %s
                    ORDER BY yearID DESC
                    """

                pitching_sql = """
                   SELECT 
                       people.playerID, 
                       nameFirst, 
                       nameLast, 
                       p_G,
                       p_GS,
                        p_IPouts,
                        ROUND(CAST(p_SO AS FLOAT) / p_BFP * 100, 2) AS KPercentage,
                        ROUND(CAST(p_BB AS FLOAT) / p_BFP * 100, 2) AS BBPercentage,
                        ROUND(CAST(p_HR AS FLOAT) * 27 / (p_IPOuts / 3), 2) AS HR9,
                        ROUND(CAST(p_H - p_HR AS FLOAT) / (p_BFP - p_SO - p_BB - p_HR - p_SF), 3) AS BABIP,
                        ROUND((p_H + p_BB + p_HBP - p_R)/(p_H + p_BB + p_HBP - (1.4 * p_HR)), 3) AS LOB,
                        p_BB,
                        yearID
                   FROM pitching 
                   JOIN people ON pitching.playerID = people.playerID
                   WHERE pitching.playerID = %s
                   ORDER BY yearID DESC
                   """

                # Execute batting query
                cursor.execute(batting_sql, (playerID))
                battingData = cursor.fetchall()

                cursor.execute(pitching_sql, (playerID))
                pitchingData = cursor.fetchall()

                name_sql = """
                    SELECT
                        nameFirst,
                        nameLast
                    FROM people 
                    WHERE playerID = %s
                """

                cursor.execute(name_sql, (playerID))
                nameData = cursor.fetchall()
                # Render a message confirming the request or redirect to another page
                return render_template('Player.html',
                                       playerID=playerID,
                                       battingData=battingData,
                                       pitchingData=pitchingData,
                                       nameData=nameData)

        finally:
            con.close()

    else:
        flash("Enter player.")
        return redirect(url_for('main'))


def scrape_immaculate_grid(immaculateGridLink):
    """
    Scrape the Immaculate Grid website to extract grid fields.
    Note: You'll need to replace this with the actual scraping logic
    based on the current website structure.
    """
    try:
        # Example scraping (you'll need to adjust based on actual website)
        response = requests.get(immaculateGridLink)
        soup = BeautifulSoup(response.text, 'html.parser')

        x_axis = soup.find_all(class_=['flex items-center justify-center w-24 sm:w-36 md:w-48 h-16 sm:h-24 md:h-36'])
        y_axis = soup.find_all(class_=['flex items-center justify-center w-20 sm:w-36 md:w-48 h-24 sm:h-36 md:h-48'])

        grid_schema = {
            'x1': 'LOGO' if x_axis and x_axis[0].img and x_axis[0].img['alt'] else (
                'TEXT' if x_axis and x_axis[0].div and x_axis[0].div.div and x_axis[
                    0].div.div.div and x_axis[0].div.div.div.div and x_axis[0].div.div.div.div.div else 'Unknown X1'),
            'x2': 'LOGO' if x_axis and x_axis[1].img and x_axis[1].img['alt'] else (
                'TEXT' if x_axis and x_axis[1].div and x_axis[1].div.div and x_axis[
                    1].div.div.div and x_axis[1].div.div.div.div and x_axis[1].div.div.div.div.div else 'Unknown X2'),
            'x3': 'LOGO' if x_axis and x_axis[2].img and x_axis[2].img['alt'] else (
                'TEXT' if x_axis and x_axis[2].div and x_axis[2].div.div and x_axis[
                    2].div.div.div and x_axis[2].div.div.div.div and x_axis[2].div.div.div.div.div else 'Unknown X3'),
            'y1': 'LOGO' if y_axis and y_axis[0].img and y_axis[0].img['alt'] else (
                'TEXT' if y_axis and y_axis[0].div and y_axis[0].div.div and y_axis[
                    0].div.div.div and y_axis[0].div.div.div.div and y_axis[0].div.div.div.div.div else 'Unknown Y1'),
            'y2': 'LOGO' if y_axis and y_axis[1].img and y_axis[1].img['alt'] else (
                'TEXT' if y_axis and y_axis[1].div and y_axis[1].div.div and y_axis[
                    1].div.div.div and y_axis[1].div.div.div.div and y_axis[1].div.div.div.div.div else 'Unknown Y2'),
            'y3': 'LOGO' if y_axis and y_axis[2].img and y_axis[2].img['alt'] else (
                'TEXT' if y_axis and y_axis[2].div and y_axis[2].div.div and y_axis[
                    2].div.div.div and y_axis[2].div.div.div.div and y_axis[2].div.div.div.div.div else 'Unknown Y3'),
        }

        grid_categories = {
            'x1': x_axis[0].img['alt'] if x_axis and x_axis[0].img and x_axis[0].img['alt'] else (
                x_axis[0].div.div.div.div.div.text if x_axis and x_axis[0].div and x_axis[0].div.div and x_axis[
                    0].div.div.div and x_axis[0].div.div.div.div and x_axis[0].div.div.div.div.div else 'Unknown X1'),
            'x2': x_axis[1].img['alt'] if x_axis and x_axis[1].img and x_axis[1].img['alt'] else (
                x_axis[1].div.div.div.div.div.text if x_axis and x_axis[1].div and x_axis[1].div.div and x_axis[
                    1].div.div.div and x_axis[1].div.div.div.div and x_axis[1].div.div.div.div.div else 'Unknown X2'),
            'x3': x_axis[2].img['alt'] if x_axis and x_axis[2].img and x_axis[2].img['alt'] else (
                x_axis[2].div.div.div.div.div.text if x_axis and x_axis[2].div and x_axis[2].div.div and x_axis[
                    2].div.div.div and x_axis[2].div.div.div.div and x_axis[2].div.div.div.div.div else 'Unknown X3'),
            'y1': y_axis[0].img['alt'] if y_axis and y_axis[0].img and y_axis[0].img['alt'] else (
                y_axis[0].div.div.div.div.div.text if y_axis and y_axis[0].div and y_axis[0].div.div and y_axis[
                    0].div.div.div and y_axis[0].div.div.div.div and y_axis[0].div.div.div.div.div else 'Unknown Y1'),
            'y2': y_axis[1].img['alt'] if y_axis and y_axis[1].img and y_axis[1].img['alt'] else (
                y_axis[1].div.div.div.div.div.text if y_axis and y_axis[1].div and y_axis[1].div.div and y_axis[
                    1].div.div.div and y_axis[1].div.div.div.div and y_axis[1].div.div.div.div.div else 'Unknown Y2'),
            'y3': y_axis[2].img['alt'] if y_axis and y_axis[2].img and y_axis[2].img['alt'] else (
                y_axis[2].div.div.div.div.div.text if y_axis and y_axis[2].div and y_axis[2].div.div and y_axis[
                    2].div.div.div and y_axis[2].div.div.div.div and y_axis[2].div.div.div.div.div else 'Unknown Y3'),
        }
        return {'grid_categories': grid_categories, 'grid_schema': grid_schema}

    except requests.RequestException as e:
        print(f"Error scraping Immaculate Grid: {e}")
        return None

def remove_double_spaces(input_string):
    # Replace consecutive spaces with a single space
    return ' '.join(input_string.split())

def query_baseball_database(grid, schema):
    """
    Query the baseball database to find players matching grid criteria.

    :param x_category: Category for x-axis
    :param y_category: Category for y-axis
    :return: List of matching players
    """

    try:
        # Connect to SQLite database
        conn = pymysql.connect(
            host=mysql["host"],
            user=mysql["user"],
            password=mysql["password"],
            db=mysql["database"]
        )
        cursor = conn.cursor()

        print(grid)
        print(schema)
        x1y1Answer = ''
        x1y2Answer = ''
        x1y3Answer = ''
        x2y1Answer = ''
        x2y2Answer = ''
        x2y3Answer = ''
        x3y1Answer = ''
        x3y2Answer = ''
        x3y3Answer = ''

        # -------------------------------------x1,y1---------------------------------------------

        if(schema.get('x1') == 'LOGO' and schema.get('y1') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x1'))
            team2 = remove_double_spaces(grid.get('y1'))

            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()

            x1y1Answer = players

            print(players)
        elif(schema.get('x1') == 'TEXT' and schema.get('y1') == 'TEXT'):
            conditions = [grid.get('x1'), grid.get('y1')]

            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x1y1Answer = players
        else:
            if schema.get('x1') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y1'))
                condition = CONDITIONS_MAP.get(grid.get('x1'))
                players = find_players_with_condition_and_team(team, condition)
                x1y1Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x1'))
                condition = CONDITIONS_MAP.get(grid.get('y1'))
                players = find_players_with_condition_and_team(team, condition)
                x1y1Answer = players

        players = ''

        # -------------------------------------x1,y2---------------------------------------------
        if (schema.get('x1') == 'LOGO' and schema.get('y2') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x1'))
            team2 = remove_double_spaces(grid.get('y2'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x1y2Answer = players
            print(players)
        elif (schema.get('x1') == 'TEXT' and schema.get('y2') == 'TEXT'):
            conditions = [grid.get('x1'), grid.get('y2')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x1y2Answer = players
        else:
            if schema.get('x1') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y2'))
                condition = CONDITIONS_MAP.get(grid.get('x1'))
                players = find_players_with_condition_and_team(team, condition)
                x1y2Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x1'))
                condition = CONDITIONS_MAP.get(grid.get('y2'))
                players = find_players_with_condition_and_team(team, condition)
                x1y2Answer = players

        players = ''
        # -------------------------------------x1,y3---------------------------------------------
        if (schema.get('x1') == 'LOGO' and schema.get('y3') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x1'))
            team2 = remove_double_spaces(grid.get('y3'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x1y3Answer = players
            print(players)
        elif (schema.get('x1') == 'TEXT' and schema.get('y3') == 'TEXT'):
            conditions = [grid.get('x1'), grid.get('y3')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x1y3Answer = players
        else:
            if schema.get('x1') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y3'))
                condition = CONDITIONS_MAP.get(grid.get('x1'))
                players = find_players_with_condition_and_team(team, condition)
                x1y3Answer = players
            else:
                # x1 is a logo
                team_name = remove_double_spaces(grid.get('x1'))
                condition = CONDITIONS_MAP.get(grid.get('y3'))
                players = find_players_with_condition_and_team(team_name, condition)
                x1y3Answer = players

        players = ''
        # -------------------------------------x2,y1---------------------------------------------
        if (schema.get('x2') == 'LOGO' and schema.get('y1') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x2'))
            team2 = remove_double_spaces(grid.get('y1'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x2y1Answer = players
            print(players)
        elif (schema.get('x2') == 'TEXT' and schema.get('y1') == 'TEXT'):
            conditions = [grid.get('x2'), grid.get('y1')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x2y1Answer = players
        else:
            if schema.get('x2') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y1'))
                condition = CONDITIONS_MAP.get(grid.get('x2'))
                players = find_players_with_condition_and_team(team, condition)
                x2y1Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x2'))
                condition = CONDITIONS_MAP.get(grid.get('y1'))
                players = find_players_with_condition_and_team(team, condition)
                x2y1Answer = players

        players = ''
        # -------------------------------------x2,y2---------------------------------------------
        if (schema.get('x2') == 'LOGO' and schema.get('y2') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x2'))
            team2 = remove_double_spaces(grid.get('y2'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x2y2Answer = players
            print(players)
        elif (schema.get('x2') == 'TEXT' and schema.get('y2') == 'TEXT'):
            conditions = [grid.get('x2'), grid.get('y2')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x2y2Answer = players
        else:
            if schema.get('x2') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y2'))
                condition = CONDITIONS_MAP.get(grid.get('x2'))
                players = find_players_with_condition_and_team(team, condition)
                x2y2Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x2'))
                condition = CONDITIONS_MAP.get(grid.get('y2'))
                players = find_players_with_condition_and_team(team, condition)
                x2y2Answer = players

        players = ''
        # -------------------------------------x2,y3---------------------------------------------
        if (schema.get('x2') == 'LOGO' and schema.get('y3') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x2'))
            team2 = remove_double_spaces(grid.get('y3'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x2y3Answer = players
            print(players)
        elif (schema.get('x2') == 'TEXT' and schema.get('y3') == 'TEXT'):
            conditions = [grid.get('x2'), grid.get('y3')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x2y3Answer = players
        else:
            if schema.get('x2') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y3'))
                condition = CONDITIONS_MAP.get(grid.get('x2'))
                players = find_players_with_condition_and_team(team, condition)
                x2y3Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x2'))
                condition = CONDITIONS_MAP.get(grid.get('y3'))
                players = find_players_with_condition_and_team(team, condition)
                x2y3Answer = players

        players = ''
        # -------------------------------------x3,y1---------------------------------------------
        if (schema.get('x3') == 'LOGO' and schema.get('y1') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x3'))
            team2 = remove_double_spaces(grid.get('y1'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x3y1Answer = players
            print(players)
        elif (schema.get('x3') == 'TEXT' and schema.get('y1') == 'TEXT'):
            conditions = [grid.get('x3'), grid.get('y1')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x3y1Answer = players
        else:
            if schema.get('x3') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y1'))
                condition = CONDITIONS_MAP.get(grid.get('x3'))
                players = find_players_with_condition_and_team(team, condition)
                x3y1Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x3'))
                condition = CONDITIONS_MAP.get(grid.get('y1'))
                players = find_players_with_condition_and_team(team, condition)
                x3y1Answer = players

        players = ''
        # -------------------------------------x3,y2---------------------------------------------
        if (schema.get('x3') == 'LOGO' and schema.get('y2') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x3'))
            team2 = remove_double_spaces(grid.get('y2'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x3y2Answer = players
            print(players)
        elif (schema.get('x3') == 'TEXT' and schema.get('y2') == 'TEXT'):
            conditions = [grid.get('x3'), grid.get('y2')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x3y2Answer = players
        else:
            if schema.get('x3') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y2'))
                condition = CONDITIONS_MAP.get(grid.get('x3'))
                players = find_players_with_condition_and_team(team, condition)
                x3y2Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x3'))
                condition = CONDITIONS_MAP.get(grid.get('y2'))
                players = find_players_with_condition_and_team(team, condition)
                x3y2Answer = players

        players = ''
        # -------------------------------------x3,y3---------------------------------------------
        if (schema.get('x3') == 'LOGO' and schema.get('y3') == 'LOGO'):
            query = """
                SELECT p.nameFirst, p.nameLast
                FROM batting AS b
                JOIN people AS p ON b.playerID = p.playerID
                JOIN teams AS t ON b.teamID = t.teamID
                WHERE t.team_name IN (%s, %s)
                GROUP BY b.playerID
                HAVING COUNT(DISTINCT b.teamID) = 2;
            """;
            team1 = remove_double_spaces(grid.get('x3'))
            team2 = remove_double_spaces(grid.get('y3'))
            cursor.execute(query, (team1, team2))
            players = cursor.fetchall()
            x3y3Answer = players
            print(players)
        elif (schema.get('x3') == 'TEXT' and schema.get('y3') == 'TEXT'):
            conditions = [grid.get('x3'), grid.get('y3')]
            query = generate_query(conditions)
            cursor.execute(query)
            players = cursor.fetchall()
            x3y3Answer = players
        else:
            if schema.get('x3') == 'TEXT':
                # y1 is logo
                team = remove_double_spaces(grid.get('y3'))
                condition = CONDITIONS_MAP.get(grid.get('x3'))
                players = find_players_with_condition_and_team(team, condition)
                x3y3Answer = players
            else:
                # x1 is a logo
                team = remove_double_spaces(grid.get('x3'))
                condition = CONDITIONS_MAP.get(grid.get('y3'))
                players = find_players_with_condition_and_team(team, condition)
                x3y3Answer = players


        answers = {'x1y1': x1y1Answer, 'x2y1': x2y1Answer, 'x3y1': x3y1Answer,
                   'x1y2': x1y2Answer, 'x2y2': x2y2Answer, 'x3y2': x3y2Answer,
                   'x1y3': x1y3Answer, 'x2y3': x2y3Answer, 'x3y3': x3y3Answer
        }
        conn.close()
        return answers

    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return []


def find_players_with_condition_and_team(team_id, condition):

    # SQL query
    query = f"""
    SELECT DISTINCT p.nameFirst, p.nameLast
    FROM batting b
    JOIN people p ON b.playerID = p.playerID
    JOIN teams t ON b.teamID = t.teamID
    WHERE t.team_name = %s
    AND {condition}
    GROUP BY b.playerID;
    """

    # Connect to the database (adjust the path to your database file)
    # Connect to SQLite database
    conn = pymysql.connect(
        host=mysql["host"],
        user=mysql["user"],
        password=mysql["password"],
        db=mysql["database"]
    )
    cursor = conn.cursor()

    try:
        # Execute query
        cursor.execute(query, (team_id,))
        results = cursor.fetchall()

        conn.close()
        # Return results
        return results
    except sqlite3.Error as e:
        conn.close()
        raise e

def generate_query(conditions):
    base_query = """
    SELECT DISTINCT p.nameFirst, p.nameLast
    FROM batting b
    JOIN people p ON b.playerID = p.playerID
    LEFT JOIN pitching pit ON pit.playerID = b.playerID 
    WHERE {conditions}
    GROUP BY b.playerID
    """
    condition_clauses = []

    for condition in conditions:
        if condition in CONDITIONS_MAP:
            print('condition', condition)
            condition_clauses.append(CONDITIONS_MAP[condition])
        else:
            raise ValueError(f"Unknown condition: {condition}")

    where_clause = " AND ".join(condition_clauses)
    return base_query.format(conditions=where_clause)


@main.route('/solve-grid', methods=['POST'])
def solve_grid():
    """
    Endpoint to solve the Immaculate Grid
    """
    data = request.get_json()
    if not data or 'GridLink' not in data:
        return jsonify({
            'error': 'GridLink is required',
            'status': 'failed'
        }), 400
    immaculateGridLink = data.get('GridLink')
    grid_info = scrape_immaculate_grid(immaculateGridLink)
    if not grid_info:
        return jsonify({
            'error': 'Could not retrieve grid information',
            'status': 'failed'
        }), 500

    grid_categories = grid_info.get('grid_categories', {})
    grid_schema = grid_info.get('grid_schema', {})

    matching_players = query_baseball_database(
        grid_categories,
        grid_schema,
    )
    print('grid info', grid_info)

    return jsonify({
        'grid_categories': grid_info,
        'matching_players': matching_players
    })

@main.route('/new-solver', methods=['GET'])
def scraper():
    return render_template('scraper.html')