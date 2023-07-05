from flask import Flask, send_from_directory, request
import os
from src.auth import auth
from flask_cors import CORS
from src.comments import comments
from src.database import db
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI='sqlite:///../instance/comments.db',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(comments)

    # Enable CORS for sites
    CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5173"]}})

    with app.app_context():
        db.create_all()

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app

app = create_app()
