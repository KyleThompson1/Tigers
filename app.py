from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='Application/static', template_folder='Application/templates')

    # Import and register the blueprint
    from routes import main
    app.register_blueprint(main)

    return app
