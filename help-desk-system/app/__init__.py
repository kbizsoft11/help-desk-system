from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the database and migration objects
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static')

    # Application Configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'kZD7rHGTSPNhEcfyWTcicgYKwkFhPqK0')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)


    # Session Configuration
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Initialize the database and migration with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import your models to register them with SQLAlchemy
    from .models import User, Ticket  # Ensure the models are imported before calling db.create_all()

    # Create the database and tables if they don't exist
    try:
        with app.app_context():
            db.create_all()
            print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")


    # Import and initialize routes
    from .routes import init_app  # Import init_app function from routes.py
    init_app(app)  # Register the routes with the app

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    return app
