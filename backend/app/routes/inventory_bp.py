from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Inventory, InventoryMovement, Product
from app.utils.decorators import role_required
from app.utils.validators import validate_positive_number

bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

@bp.route('', methods=['GET'])
@jwt_required()
def list_inventory():
    """Lista inventário de produtos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    warehouse = request.args.get('warehouse', 'Principal')
    
    inventories = Inventory.query.filter_by(warehouse=warehouse).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'total': inventories.total,
        'pages': inventories.pages,
        'current_page': page,
        'warehouse': warehouse,
        'items': [{
            'id': i.id,
            'product': {
                'id': i.product.id,
                'sku': i.product.sku,
                'name': i.product.name
            },
            'quantity': float(i.quantity),
            'min_quantity': float(i.min_quantity),
            'max_quantity': float(i.max_quantity),
            'last_update': i.last_update.isoformat()
        } for i in inventories.items]
    }), 200

@bp.route('/<int:inventory_id>', methods=['GET'])
@jwt_required()
def get_inventory(inventory_id):
    """Obtém detalhes do inventário de um produto"""
    inventory = Inventory.query.get(inventory_id)
    
    if not inventory:
        return jsonify({'message': 'Inventário não encontrado'}), 404
    
    return jsonify({
        'id': inventory.id,
        'product': {
            'id': inventory.product.id,
            'sku': inventory.product.sku,
            'name': inventory.product.name
        },
        'warehouse': inventory.warehouse,
        'quantity': float(inventory.quantity),
        'min_quantity': float(inventory.min_quantity),
        'max_quantity': float(inventory.max_quantity),
        'last_update': inventory.last_update.isoformat()
    }), 200

@bp.route('/movements', methods=['GET'])
@jwt_required()
def list_movements():
    """Lista movimentações de estoque"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    movement_type = request.args.get('type')
    
    query = InventoryMovement.query
    if movement_type:
        query = query.filter_by(movement_type=movement_type)
    
    movements = query.order_by(InventoryMovement.created_at.desc()).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'total': movements.total,
        'pages': movements.pages,
        'current_page': page,
        'movements': [{
            'id': m.id,
            'product': {
                'id': m.product.id,
                'sku': m.product.sku,
                'name': m.product.name
            },
            'movement_type': m.movement_type,
            'quantity': float(m.quantity),
            'reference': m.reference,
            'reason': m.reason,
            'created_by': m.user.name if m.user else None,
            'created_at': m.created_at.isoformat()
        } for m in movements.items]
    }), 200

@bp.route('/movements', methods=['POST'])
@role_required(['admin', 'gerente', 'operacional'])
def create_movement():
    """Registra uma movimentação de estoque"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Validações
    if not data or not data.get('product_id') or not data.get('movement_type') or not data.get('quantity'):
        return jsonify({'message': 'product_id, movement_type e quantity são obrigatórios'}), 400
    
    if not validate_positive_number(data['quantity']):
        return jsonify({'message': 'Quantidade deve ser positiva'}), 400
    
    # Verificar se produto existe
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Produto não encontrado'}), 404
    
    # Obter ou criar inventário
    warehouse = data.get('warehouse', 'Principal')
    inventory = Inventory.query.filter_by(
        product_id=data['product_id'],
        warehouse=warehouse
    ).first()
    
    if not inventory:
        inventory = Inventory(product_id=data['product_id'], warehouse=warehouse)
        db.session.add(inventory)
        db.session.flush()  # Obter ID antes de salvar
    
    # Validar quantidade em estoque para saídas
    if data['movement_type'] in ['saida', 'devolucao']:
        if float(inventory.quantity) < float(data['quantity']):
            return jsonify({'message': 'Quantidade insuficiente em estoque'}), 400
    
    # Atualizar quantidade
    if data['movement_type'] in ['entrada', 'devolucao']:
        inventory.quantity += float(data['quantity'])
    else:  # saida, ajuste
        inventory.quantity -= float(data['quantity'])
    
    # Registrar movimento
    movement = InventoryMovement(
        product_id=data['product_id'],
        inventory_id=inventory.id,
        movement_type=data['movement_type'],
        quantity=float(data['quantity']),
        reference=data.get('reference'),
        reason=data.get('reason'),
        created_by=user_id
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'message': 'Movimentação registrada com sucesso',
        'movement_id': movement.id,
        'new_quantity': float(inventory.quantity)
    }), 201
