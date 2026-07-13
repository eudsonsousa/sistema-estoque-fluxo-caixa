from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CashFlow
from app.utils.decorators import role_required
from app.utils.validators import validate_positive_number
from datetime import datetime

bp = Blueprint('cashflow', __name__, url_prefix='/api/cashflow')

@bp.route('', methods=['GET'])
@jwt_required()
def list_cashflow():
    """Lista movimentações de fluxo de caixa"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    cash_type = request.args.get('type')  # entrada, saida
    status = request.args.get('status')  # pendente, pago, cancelado
    
    query = CashFlow.query
    if cash_type:
        query = query.filter_by(type=cash_type)
    if status:
        query = query.filter_by(status=status)
    
    cashflows = query.order_by(CashFlow.created_at.desc()).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'total': cashflows.total,
        'pages': cashflows.pages,
        'current_page': page,
        'cashflows': [{
            'id': c.id,
            'type': c.type,
            'description': c.description,
            'amount': float(c.amount),
            'category': c.category,
            'reference': c.reference,
            'status': c.status,
            'due_date': c.due_date.isoformat() if c.due_date else None,
            'payment_date': c.payment_date.isoformat() if c.payment_date else None,
            'created_at': c.created_at.isoformat()
        } for c in cashflows.items]
    }), 200

@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_cashflow_summary():
    """Obtém resumo do fluxo de caixa"""
    from sqlalchemy import func
    
    # Entradas
    entradas = db.session.query(
        func.sum(CashFlow.amount)
    ).filter_by(type='entrada', status='pago').scalar() or 0
    
    # Saídas
    saidas = db.session.query(
        func.sum(CashFlow.amount)
    ).filter_by(type='saida', status='pago').scalar() or 0
    
    # Pendências
    pendencias = db.session.query(
        func.sum(CashFlow.amount)
    ).filter_by(status='pendente').scalar() or 0
    
    saldo = float(entradas) - float(saidas)
    
    return jsonify({
        'entradas': float(entradas),
        'saidas': float(saidas),
        'pendencias': float(pendencias),
        'saldo': saldo
    }), 200

@bp.route('', methods=['POST'])
@role_required(['admin', 'gerente'])
def create_cashflow():
    """Cria uma nova movimentação de fluxo de caixa"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Validações
    required_fields = ['type', 'description', 'amount', 'category']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': f'Campos obrigatórios: {required_fields}'}), 400
    
    if data['type'] not in ['entrada', 'saida']:
        return jsonify({'message': 'Type deve ser entrada ou saida'}), 400
    
    if not validate_positive_number(data['amount']):
        return jsonify({'message': 'Amount deve ser positivo'}), 400
    
    # Criar movimentação
    cashflow = CashFlow(
        type=data['type'],
        description=data['description'],
        amount=float(data['amount']),
        category=data['category'],
        reference=data.get('reference'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        status=data.get('status', 'pendente'),
        notes=data.get('notes'),
        created_by=user_id
    )
    
    db.session.add(cashflow)
    db.session.commit()
    
    return jsonify({
        'message': 'Movimentação de fluxo de caixa criada com sucesso',
        'cashflow_id': cashflow.id
    }), 201

@bp.route('/<int:cashflow_id>', methods=['PUT'])
@role_required(['admin', 'gerente'])
def update_cashflow(cashflow_id):
    """Atualiza uma movimentação de fluxo de caixa"""
    cashflow = CashFlow.query.get(cashflow_id)
    
    if not cashflow:
        return jsonify({'message': 'Movimentação não encontrada'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        if data['status'] in ['pendente', 'pago', 'cancelado']:
            cashflow.status = data['status']
            if data['status'] == 'pago' and not cashflow.payment_date:
                cashflow.payment_date = datetime.utcnow()
    
    if 'description' in data:
        cashflow.description = data['description']
    if 'amount' in data:
        if validate_positive_number(data['amount']):
            cashflow.amount = float(data['amount'])
    if 'notes' in data:
        cashflow.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({'message': 'Movimentação atualizada com sucesso'}), 200
