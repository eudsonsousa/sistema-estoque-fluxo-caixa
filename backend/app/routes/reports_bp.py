from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Product, Inventory, CashFlow, InventoryMovement
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@bp.route('/inventory-summary', methods=['GET'])
@jwt_required()
def inventory_summary():
    """Relatório resumido de inventário"""
    warehouse = request.args.get('warehouse', 'Principal')
    
    inventories = Inventory.query.filter_by(warehouse=warehouse).all()
    
    total_items = len(inventories)
    total_quantity = sum(float(i.quantity) for i in inventories)
    low_stock = sum(1 for i in inventories if float(i.quantity) <= float(i.min_quantity))
    
    return jsonify({
        'warehouse': warehouse,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'low_stock_items': low_stock,
        'items': [{
            'sku': i.product.sku,
            'name': i.product.name,
            'quantity': float(i.quantity),
            'min_quantity': float(i.min_quantity),
            'status': 'Baixo' if float(i.quantity) <= float(i.min_quantity) else 'Normal'
        } for i in inventories]
    }), 200

@bp.route('/cashflow-summary', methods=['GET'])
@jwt_required()
def cashflow_summary():
    """Relatório resumido de fluxo de caixa"""
    period = request.args.get('period', '30')  # dias
    start_date = datetime.utcnow() - timedelta(days=int(period))
    
    # Entradas
    entradas = db.session.query(
        func.sum(CashFlow.amount)
    ).filter(
        CashFlow.type == 'entrada',
        CashFlow.status == 'pago',
        CashFlow.created_at >= start_date
    ).scalar() or 0
    
    # Saídas
    saidas = db.session.query(
        func.sum(CashFlow.amount)
    ).filter(
        CashFlow.type == 'saida',
        CashFlow.status == 'pago',
        CashFlow.created_at >= start_date
    ).scalar() or 0
    
    # Pendências
    pendencias = db.session.query(
        func.sum(CashFlow.amount)
    ).filter(
        CashFlow.status == 'pendente',
        CashFlow.created_at >= start_date
    ).scalar() or 0
    
    saldo = float(entradas) - float(saidas)
    
    return jsonify({
        'period_days': int(period),
        'period_start': start_date.isoformat(),
        'period_end': datetime.utcnow().isoformat(),
        'entradas': float(entradas),
        'saidas': float(saidas),
        'pendencias': float(pendencias),
        'saldo': saldo
    }), 200

@bp.route('/movements', methods=['GET'])
@jwt_required()
def movements_report():
    """Relatório de movimentações"""
    period = request.args.get('period', '30')  # dias
    movement_type = request.args.get('type')
    start_date = datetime.utcnow() - timedelta(days=int(period))
    
    query = InventoryMovement.query.filter(InventoryMovement.created_at >= start_date)
    
    if movement_type:
        query = query.filter_by(movement_type=movement_type)
    
    movements = query.all()
    
    # Agrupar por tipo
    by_type = {}
    for m in movements:
        if m.movement_type not in by_type:
            by_type[m.movement_type] = 0
        by_type[m.movement_type] += float(m.quantity)
    
    return jsonify({
        'period_days': int(period),
        'period_start': start_date.isoformat(),
        'period_end': datetime.utcnow().isoformat(),
        'total_movements': len(movements),
        'by_type': by_type,
        'movements': [{
            'product': {
                'sku': m.product.sku,
                'name': m.product.name
            },
            'type': m.movement_type,
            'quantity': float(m.quantity),
            'reference': m.reference,
            'created_at': m.created_at.isoformat()
        } for m in movements]
    }), 200
