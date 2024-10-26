from flask import render_template, Blueprint, request

# --------- LOGIC FOR HTTP REQUESTS WILL BE IN THIS FILE ---------

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

@main.route('/team_year', methods=['GET'])
def team_year():
    return render_template('Team-Year.html')

@main.route('/generate_roster', methods=['GET'])
def generate_roster():
    return render_template('Roster.html')