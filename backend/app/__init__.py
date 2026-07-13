from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo para uploads
    
    # Inicializar extensões
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    from app.routes import auth_bp, products_bp, inventory_bp, cashflow_bp, reports_bp, clients_bp, purchases_bp
    
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(products_bp.bp)
    app.register_blueprint(inventory_bp.bp)
    app.register_blueprint(cashflow_bp.bp)
    app.register_blueprint(reports_bp.bp)
    app.register_blueprint(clients_bp.bp)
    app.register_blueprint(purchases_bp.bp)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    return app
