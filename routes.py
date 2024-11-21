from flask import render_template, Blueprint, request
import csi3335f2024 as cfg
import pymysql

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

@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/register')
def register():
    return render_template('Registration.html')

@main.route('/roster', methods=['GET', 'POST'])
def roster_grid():
    if request.method == 'POST':
        # Handle POST request (form submission)
        pass
    return render_template('Roster-Grid.html')

@main.route('/play_grid')
def play_grid():
    return render_template('Play-Immaculate-Grid.html')

@main.route('/team-year', methods=['GET'])
def team_year():
    con = pymysql.connect(host=cfg.mysql['host'], user=cfg.mysql['user'], password=cfg.mysql['password'],
                          database=cfg.mysql['database'])
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

    con = pymysql.connect(host=cfg.mysql['host'], user=cfg.mysql['user'], password=cfg.mysql['password'],
                          database=cfg.mysql['database'])

    try:
        cur = con.cursor()
        sql = "SELECT DISTINCT yearID FROM teams WHERE team_name = %s ORDER BY yearID DESC"
        cur.execute(sql, (team_name,))
        years = [(year[0]) for year in cur.fetchall()]
        return ','.join(str(year) for year in years)

    finally:
        con.close()