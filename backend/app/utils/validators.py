import re

def validate_email(email):
    """Valida o formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cnpj(cnpj):
    """Valida CNPJ (formato básico)"""
    cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
    return len(cnpj) == 14 and cnpj.isdigit()

def validate_sku(sku):
    """Valida SKU"""
    return len(sku) > 0 and len(sku) <= 100

def validate_positive_number(value):
    """Valida se o número é positivo"""
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False
