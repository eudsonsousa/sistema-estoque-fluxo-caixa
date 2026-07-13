from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Role
from app.utils.validators import validate_email
from datetime import timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    data = request.get_json()
    
    # Validações
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Email, nome e senha são obrigatórios'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'message': 'Email inválido'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'message': 'A senha deve ter no mínimo 6 caracteres'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Usuário com este email já existe'}), 409
    
    # Obter role (padrão: visualizador)
    role = Role.query.filter_by(name=data.get('role', 'visualizador')).first()
    if not role:
        # Criar role padrão se não existir
        role = Role(name='visualizador', description='Apenas visualização')
        db.session.add(role)
        db.session.commit()
    
    # Criar novo usuário
    user = User(
        email=data['email'],
        name=data['name'],
        role_id=role.id
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Usuário registrado com sucesso',
        'user_id': user.id,
        'email': user.email
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Email ou senha inválidos'}), 401
    
    if not user.active:
        return jsonify({'message': 'Usuário inativo'}), 403
    
    # Criar token JWT
    additional_claims = {'role': user.role.name}
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.name
        }
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna informações do usuário autenticado"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role.name
    }), 200
