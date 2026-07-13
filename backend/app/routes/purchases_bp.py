from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Purchase, PurchaseItem, Product, Supplier, Inventory, InventoryMovement
from app.utils.decorators import role_required
from app.utils.nfe_parser import NFeParser
from datetime import datetime
import base64

bp = Blueprint('purchases', __name__, url_prefix='/api/purchases')

@bp.route('', methods=['GET'])
@jwt_required()
def list_purchases():
    """Lista todas as compras"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Purchase.query
    if status:
        query = query.filter_by(status=status)
    
    purchases = query.order_by(Purchase.created_at.desc()).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'total': purchases.total,
        'pages': purchases.pages,
        'current_page': page,
        'purchases': [{
            'id': p.id,
            'nf_number': p.nf_number,
            'nf_series': p.nf_series,
            'supplier': p.supplier.name if p.supplier else None,
            'total_amount': float(p.total_amount),
            'status': p.status,
            'purchase_date': p.purchase_date.isoformat(),
            'created_at': p.created_at.isoformat()
        } for p in purchases.items]
    }), 200

@bp.route('/<int:purchase_id>', methods=['GET'])
@jwt_required()
def get_purchase(purchase_id):
    """Obtém detalhes de uma compra"""
    purchase = Purchase.query.get(purchase_id)
    
    if not purchase:
        return jsonify({'message': 'Compra não encontrada'}), 404
    
    return jsonify({
        'id': purchase.id,
        'nf_number': purchase.nf_number,
        'nf_series': purchase.nf_series,
        'nf_key': purchase.nf_key,
        'supplier': {
            'id': purchase.supplier.id,
            'name': purchase.supplier.name,
            'cnpj': purchase.supplier.cnpj
        } if purchase.supplier else None,
        'total_amount': float(purchase.total_amount),
        'tax_amount': float(purchase.tax_amount),
        'net_amount': float(purchase.net_amount),
        'status': purchase.status,
        'purchase_date': purchase.purchase_date.isoformat(),
        'due_date': purchase.due_date.isoformat() if purchase.due_date else None,
        'received_date': purchase.received_date.isoformat() if purchase.received_date else None,
        'notes': purchase.notes,
        'items': [{
            'id': item.id,
            'product_id': item.product_id,
            'sku': item.sku,
            'description': item.description,
            'quantity': float(item.quantity),
            'unit': item.unit,
            'unit_cost': float(item.unit_cost),
            'total_cost': float(item.total_cost),
            'icms_rate': float(item.icms_rate),
            'ipi_rate': float(item.ipi_rate),
            'pis_rate': float(item.pis_rate),
            'cofins_rate': float(item.cofins_rate),
            'suggested_sale_price': float(item.suggested_sale_price) if item.suggested_sale_price else None,
            'final_sale_price': float(item.final_sale_price) if item.final_sale_price else None,
            'processed': item.processed
        } for item in purchase.items],
        'created_at': purchase.created_at.isoformat()
    }), 200

@bp.route('/import-nfe', methods=['POST'])
@role_required(['admin', 'gerente'])
def import_nfe():
    """Importa uma NF-e e extrai os dados"""
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'message': 'Arquivo não enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'Arquivo não selecionado'}), 400
        
        # Validar extensão
        allowed_extensions = {'xml'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'message': 'Apenas arquivos XML são permitidos'}), 400
        
        # Ler conteúdo do arquivo
        xml_content = file.read()
        
        # Parse da NF-e
        result = NFeParser.parse_nfe_xml(xml_content)
        
        if not result['success']:
            return jsonify({'message': f"Erro ao processar NF-e: {result['error']}"}), 400
        
        # Retornar dados extraídos para confirmação do usuário
        return jsonify({
            'message': 'NF-e processada com sucesso',
            'nfe_info': result['nfe_info'],
            'supplier': result['supplier'],
            'items': result['items'],
            'xml_content': base64.b64encode(xml_content).decode('utf-8')
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao importar arquivo: {str(e)}'}), 500

@bp.route('', methods=['POST'])
@role_required(['admin', 'gerente'])
def create_purchase():
    """Cria uma nova compra a partir de dados importados"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Validações
    if not data or not data.get('supplier_id'):
        return jsonify({'message': 'supplier_id é obrigatório'}), 400
    
    # Verificar se fornecedor existe
    supplier = Supplier.query.get(data['supplier_id'])
    if not supplier:
        return jsonify({'message': 'Fornecedor não encontrado'}), 404
    
    try:
        # Criar compra
        purchase = Purchase(
            supplier_id=data['supplier_id'],
            nf_number=data.get('nf_number'),
            nf_series=data.get('nf_series'),
            nf_key=data.get('nf_key'),
            total_amount=float(data.get('total_amount', 0)),
            tax_amount=float(data.get('tax_amount', 0)),
            net_amount=float(data.get('net_amount', 0)),
            purchase_date=datetime.fromisoformat(data['purchase_date']) if data.get('purchase_date') else datetime.utcnow(),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            status=data.get('status', 'rascunho'),
            notes=data.get('notes'),
            nf_xml=data.get('nf_xml'),
            created_by=user_id
        )
        
        # Adicionar itens da compra
        for item_data in data.get('items', []):
            # Buscar ou criar produto
            product = None
            if item_data.get('product_id'):
                product = Product.query.get(item_data['product_id'])
            
            # Se não encontrou produto e tem SKU, tenta buscar por SKU
            if not product and item_data.get('sku'):
                product = Product.query.filter_by(sku=item_data['sku']).first()
            
            item = PurchaseItem(
                purchase=purchase,
                product_id=product.id if product else None,
                sku=item_data.get('sku'),
                description=item_data.get('description'),
                quantity=float(item_data.get('quantity', 0)),
                unit=item_data.get('unit'),
                unit_cost=float(item_data.get('unit_cost', 0)),
                total_cost=float(item_data.get('total_cost', 0)),
                icms_rate=float(item_data.get('icms_rate', 0)),
                ipi_rate=float(item_data.get('ipi_rate', 0)),
                pis_rate=float(item_data.get('pis_rate', 0)),
                cofins_rate=float(item_data.get('cofins_rate', 0)),
                suggested_sale_price=float(item_data['unit_cost']) * 1.5 if item_data.get('unit_cost') else None,  # Margem padrão de 50%
                final_sale_price=float(item_data.get('final_sale_price')) if item_data.get('final_sale_price') else None,
            )
            purchase.items.append(item)
        
        db.session.add(purchase)
        db.session.commit()
        
        return jsonify({
            'message': 'Compra criada com sucesso',
            'purchase_id': purchase.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar compra: {str(e)}'}), 500

@bp.route('/<int:purchase_id>/process', methods=['POST'])
@role_required(['admin', 'gerente', 'operacional'])
def process_purchase(purchase_id):
    """Processa uma compra e adiciona itens ao estoque"""
    purchase = Purchase.query.get(purchase_id)
    
    if not purchase:
        return jsonify({'message': 'Compra não encontrada'}), 404
    
    if purchase.status == 'processada':
        return jsonify({'message': 'Compra já foi processada'}), 400
    
    user_id = get_jwt_identity()
    
    try:
        # Processar cada item
        for item in purchase.items:
            if item.processed:
                continue
            
            # Se não tem produto, criar um novo
            if not item.product_id:
                # Verificar se já existe produto com esse SKU
                product = Product.query.filter_by(sku=item.sku).first()
                
                if not product:
                    # Criar novo produto
                    product = Product(
                        sku=item.sku,
                        name=item.description,
                        cost_price=float(item.unit_cost),
                        sale_price=float(item.final_sale_price or item.suggested_sale_price or item.unit_cost * 1.5),
                        ncm=None,
                        icms_rate=float(item.icms_rate),
                        ipi_rate=float(item.ipi_rate),
                        pis_rate=float(item.pis_rate),
                        cofins_rate=float(item.cofins_rate),
                        unit=item.unit
                    )
                    db.session.add(product)
                    db.session.flush()
                
                item.product_id = product.id
            
            # Atualizar ou criar inventário
            inventory = Inventory.query.filter_by(
                product_id=item.product_id,
                warehouse='Principal'
            ).first()
            
            if not inventory:
                inventory = Inventory(
                    product_id=item.product_id,
                    warehouse='Principal',
                    quantity=0
                )
                db.session.add(inventory)
                db.session.flush()
            
            # Adicionar quantidade ao inventário
            inventory.quantity += float(item.quantity)
            
            # Registrar movimento de entrada
            movement = InventoryMovement(
                product_id=item.product_id,
                inventory_id=inventory.id,
                movement_type='entrada',
                quantity=float(item.quantity),
                reference=f"NF {purchase.nf_number}/{purchase.nf_series}",
                reason=f"Compra do fornecedor {purchase.supplier.name}",
                created_by=user_id
            )
            db.session.add(movement)
            
            # Marcar item como processado
            item.processed = True
        
        # Atualizar status da compra
        purchase.status = 'processada'
        purchase.received_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Compra processada com sucesso',
            'items_processed': len([i for i in purchase.items if i.processed])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao processar compra: {str(e)}'}), 500

@bp.route('/<int:purchase_id>', methods=['PUT'])
@role_required(['admin', 'gerente'])
def update_purchase(purchase_id):
    """Atualiza uma compra"""
    purchase = Purchase.query.get(purchase_id)
    
    if not purchase:
        return jsonify({'message': 'Compra não encontrada'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        purchase.status = data['status']
    if 'notes' in data:
        purchase.notes = data['notes']
    if 'due_date' in data:
        purchase.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    
    # Atualizar itens
    if 'items' in data:
        for item_data in data['items']:
            item = PurchaseItem.query.get(item_data.get('id'))
            if item:
                if 'final_sale_price' in item_data:
                    item.final_sale_price = float(item_data['final_sale_price'])
    
    db.session.commit()
    
    return jsonify({'message': 'Compra atualizada com sucesso'}), 200
