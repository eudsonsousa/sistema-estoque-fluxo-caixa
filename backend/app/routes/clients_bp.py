from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Client
from app.utils.decorators import role_required
from app.utils.validators import validate_email

bp = Blueprint('clients', __name__, url_prefix='/api/clients')

@bp.route('', methods=['GET'])
@jwt_required()
def list_clients():
    """Lista todos os clientes"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    query = Client.query
    if active_only:
        query = query.filter_by(active=True)
    
    clients = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': clients.total,
        'pages': clients.pages,
        'current_page': page,
        'clients': [{
            'id': c.id,
            'name': c.name,
            'type': c.type,
            'cpf_cnpj': c.cpf_cnpj,
            'email': c.email,
            'phone': c.phone,
            'city': c.city,
            'state': c.state,
            'active': c.active
        } for c in clients.items]
    }), 200

@bp.route('/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    """Obtém detalhes de um cliente"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'message': 'Cliente não encontrado'}), 404
    
    return jsonify({
        'id': client.id,
        'name': client.name,
        'type': client.type,
        'cpf_cnpj': client.cpf_cnpj,
        'email': client.email,
        'phone': client.phone,
        'street': client.street,
        'number': client.number,
        'complement': client.complement,
        'city': client.city,
        'state': client.state,
        'zip_code': client.zip_code,
        'active': client.active,
        'created_at': client.created_at.isoformat()
    }), 200

@bp.route('', methods=['POST'])
@role_required(['admin', 'gerente'])
def create_client():
    """Cria um novo cliente"""
    data = request.get_json()
    
    # Validações
    if not data or not data.get('name') or not data.get('cpf_cnpj'):
        return jsonify({'message': 'Nome e CPF/CNPJ são obrigatórios'}), 400
    
    if Client.query.filter_by(cpf_cnpj=data['cpf_cnpj']).first():
        return jsonify({'message': 'Cliente com este CPF/CNPJ já existe'}), 409
    
    if data.get('email') and not validate_email(data['email']):
        return jsonify({'message': 'Email inválido'}), 400
    
    # Criar cliente
    client = Client(
        name=data['name'],
        type=data.get('type', 'juridica'),
        cpf_cnpj=data['cpf_cnpj'],
        email=data.get('email'),
        phone=data.get('phone'),
        street=data.get('street'),
        number=data.get('number'),
        complement=data.get('complement'),
        city=data.get('city'),
        state=data.get('state'),
        zip_code=data.get('zip_code')
    )
    
    db.session.add(client)
    db.session.commit()
    
    return jsonify({
        'message': 'Cliente criado com sucesso',
        'client_id': client.id
    }), 201

@bp.route('/<int:client_id>', methods=['PUT'])
@role_required(['admin', 'gerente'])
def update_client(client_id):
    """Atualiza um cliente"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'message': 'Cliente não encontrado'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'name' in data:
        client.name = data['name']
    if 'email' in data:
        if data['email'] and not validate_email(data['email']):
            return jsonify({'message': 'Email inválido'}), 400
        client.email = data['email']
    if 'phone' in data:
        client.phone = data['phone']
    if 'street' in data:
        client.street = data['street']
    if 'number' in data:
        client.number = data['number']
    if 'complement' in data:
        client.complement = data['complement']
    if 'city' in data:
        client.city = data['city']
    if 'state' in data:
        client.state = data['state']
    if 'zip_code' in data:
        client.zip_code = data['zip_code']
    if 'active' in data:
        client.active = data['active']
    
    db.session.commit()
    
    return jsonify({'message': 'Cliente atualizado com sucesso'}), 200

@bp.route('/<int:client_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_client(client_id):
    """Deleta um cliente"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'message': 'Cliente não encontrado'}), 404
    
    db.session.delete(client)
    db.session.commit()
    
    return jsonify({'message': 'Cliente deletado com sucesso'}), 200
