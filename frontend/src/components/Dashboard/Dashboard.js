import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { reportsAPI } from '../services/api';
import Navigation from './Navigation/Navigation';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [inventorySummary, setInventorySummary] = useState(null);
  const [cashflowSummary, setCashflowSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [inventory, cashflow] = await Promise.all([
          reportsAPI.inventorySummary(),
          reportsAPI.cashflowSummary(),
        ]);
        setInventorySummary(inventory.data);
        setCashflowSummary(cashflow.data);
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="dashboard">
      <Navigation />
      <div className="dashboard-content">
        <div className="header">
          <h1>Bem-vindo, {user?.name}!</h1>
          <p>Seu papel: <strong>{user?.role}</strong></p>
        </div>

        <div className="dashboard-grid">
          {/* Card de Estoque */}
          <div className="card">
            <h3>📦 Estoque</h3>
            {inventorySummary && (
              <div className="card-content">
                <div className="stat">
                  <span className="label">Total de Itens</span>
                  <span className="value">{inventorySummary.total_items}</span>
                </div>
                <div className="stat">
                  <span className="label">Quantidade Total</span>
                  <span className="value">{inventorySummary.total_quantity.toFixed(2)}</span>
                </div>
                <div className="stat alert">
                  <span className="label">⚠️ Estoque Baixo</span>
                  <span className="value">{inventorySummary.low_stock_items}</span>
                </div>
              </div>
            )}
          </div>

          {/* Card de Fluxo de Caixa */}
          <div className="card">
            <h3>💰 Fluxo de Caixa</h3>
            {cashflowSummary && (
              <div className="card-content">
                <div className="stat">
                  <span className="label">Entradas</span>
                  <span className="value income">R$ {cashflowSummary.entradas.toFixed(2)}</span>
                </div>
                <div className="stat">
                  <span className="label">Saídas</span>
                  <span className="value expense">R$ {cashflowSummary.saidas.toFixed(2)}</span>
                </div>
                <div className="stat">
                  <span className="label">Saldo</span>
                  <span className={`value ${cashflowSummary.saldo >= 0 ? 'income' : 'expense'}`}>
                    R$ {cashflowSummary.saldo.toFixed(2)}
                  </span>
                </div>
                <div className="stat">
                  <span className="label">Pendências</span>
                  <span className="value">R$ {cashflowSummary.pendencias.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
