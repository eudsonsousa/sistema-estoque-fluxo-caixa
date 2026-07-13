import os
from datetime import timedelta

class Config:
    """Configurações base"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    """Configurações de testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
