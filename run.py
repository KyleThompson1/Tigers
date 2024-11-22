from DatabaseSetup import initialize_database
from app import create_app

app = create_app()

# Initialize the database
initialize_database()  # Ensures the Tigers database and users table are set up

if __name__ == '__main__':
    app.run(debug=True)