from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Product
from app.utils.decorators import role_required
from app.utils.validators import validate_sku, validate_positive_number

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """Lista todos os produtos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    query = Product.query
    if active_only:
        query = query.filter_by(active=True)
    
    products = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': products.total,
        'pages': products.pages,
        'current_page': page,
        'products': [{
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'category': p.category,
            'cost_price': float(p.cost_price),
            'sale_price': float(p.sale_price),
            'unit': p.unit,
            'active': p.active
        } for p in products.items]
    }), 200

@bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Obtém detalhes de um produto"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Produto não encontrado'}), 404
    
    return jsonify({
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'cost_price': float(product.cost_price),
        'sale_price': float(product.sale_price),
        'ncm': product.ncm,
        'icms_rate': float(product.icms_rate),
        'ipi_rate': float(product.ipi_rate),
        'pis_rate': float(product.pis_rate),
        'cofins_rate': float(product.cofins_rate),
        'unit': product.unit,
        'barcode': product.barcode,
        'weight': float(product.weight) if product.weight else None,
        'height': float(product.height) if product.height else None,
        'width': float(product.width) if product.width else None,
        'depth': float(product.depth) if product.depth else None,
        'active': product.active,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }), 200

@bp.route('', methods=['POST'])
@role_required(['admin', 'gerente'])
def create_product():
    """Cria um novo produto"""
    data = request.get_json()
    
    # Validações
    if not data or not data.get('sku') or not data.get('name'):
        return jsonify({'message': 'SKU e nome são obrigatórios'}), 400
    
    if not validate_sku(data['sku']):
        return jsonify({'message': 'SKU inválido'}), 400
    
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'message': 'Produto com este SKU já existe'}), 409
    
    if not validate_positive_number(data.get('cost_price', 0)) or not validate_positive_number(data.get('sale_price', 0)):
        return jsonify({'message': 'Preços devem ser números positivos'}), 400
    
    # Criar produto
    product = Product(
        sku=data['sku'],
        name=data['name'],
        description=data.get('description'),
        category=data.get('category'),
        cost_price=float(data['cost_price']),
        sale_price=float(data['sale_price']),
        ncm=data.get('ncm'),
        icms_rate=float(data.get('icms_rate', 0)),
        ipi_rate=float(data.get('ipi_rate', 0)),
        pis_rate=float(data.get('pis_rate', 0)),
        cofins_rate=float(data.get('cofins_rate', 0)),
        unit=data.get('unit'),
        barcode=data.get('barcode'),
        weight=float(data.get('weight')) if data.get('weight') else None,
        height=float(data.get('height')) if data.get('height') else None,
        width=float(data.get('width')) if data.get('width') else None,
        depth=float(data.get('depth')) if data.get('depth') else None
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Produto criado com sucesso',
        'product_id': product.id,
        'sku': product.sku
    }), 201

@bp.route('/<int:product_id>', methods=['PUT'])
@role_required(['admin', 'gerente'])
def update_product(product_id):
    """Atualiza um produto"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Produto não encontrado'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'category' in data:
        product.category = data['category']
    if 'cost_price' in data:
        if not validate_positive_number(data['cost_price']):
            return jsonify({'message': 'Preço de custo deve ser positivo'}), 400
        product.cost_price = float(data['cost_price'])
    if 'sale_price' in data:
        if not validate_positive_number(data['sale_price']):
            return jsonify({'message': 'Preço de venda deve ser positivo'}), 400
        product.sale_price = float(data['sale_price'])
    if 'icms_rate' in data:
        product.icms_rate = float(data['icms_rate'])
    if 'ipi_rate' in data:
        product.ipi_rate = float(data['ipi_rate'])
    if 'pis_rate' in data:
        product.pis_rate = float(data['pis_rate'])
    if 'cofins_rate' in data:
        product.cofins_rate = float(data['cofins_rate'])
    if 'unit' in data:
        product.unit = data['unit']
    if 'active' in data:
        product.active = data['active']
    
    db.session.commit()
    
    return jsonify({'message': 'Produto atualizado com sucesso'}), 200

@bp.route('/<int:product_id>/duplicate', methods=['POST'])
@role_required(['admin', 'gerente'])
def duplicate_product(product_id):
    """Duplica um produto existente"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Produto não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('new_sku'):
        return jsonify({'message': 'Novo SKU é obrigatório'}), 400
    
    if not validate_sku(data['new_sku']):
        return jsonify({'message': 'Novo SKU inválido'}), 400
    
    if Product.query.filter_by(sku=data['new_sku']).first():
        return jsonify({'message': 'Produto com este SKU já existe'}), 409
    
    # Duplicar produto
    new_product = product.duplicate(
        new_sku=data['new_sku'],
        new_name=data.get('new_name')
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({
        'message': 'Produto duplicado com sucesso',
        'product_id': new_product.id,
        'sku': new_product.sku
    }), 201

@bp.route('/<int:product_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_product(product_id):
    """Deleta um produto (apenas admin)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Produto não encontrado'}), 404
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Produto deletado com sucesso'}), 200
