from flask import Flask
import os

def create_app():

    app = Flask(__name__, static_folder='Application/static', template_folder='Application/templates')

    # Set the secret key for session management
    app.secret_key = os.getenv('SECRET_KEY', 'default_dev_key')

    # Import and register the blueprint
    from routes import main
    app.register_blueprint(main)

    return app
