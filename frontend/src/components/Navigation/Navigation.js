import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navigation.css';

const Navigation = () => {
  const { user, logout, hasPermission } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h2>📦 Estoque</h2>
      </div>

      <ul className="nav-menu">
        <li>
          <Link to="/dashboard">Dashboard</Link>
        </li>

        {/* Produtos - Admin e Gerente */}
        {hasPermission(['admin', 'gerente']) && (
          <li>
            <Link to="/products">Produtos</Link>
          </li>
        )}

        {/* Estoque - Todos exceto Visualizador */}
        {hasPermission(['admin', 'gerente', 'operacional']) && (
          <li>
            <Link to="/inventory">Estoque</Link>
          </li>
        )}

        {/* Fluxo de Caixa - Admin e Gerente */}
        {hasPermission(['admin', 'gerente']) && (
          <li>
            <Link to="/cashflow">Fluxo de Caixa</Link>
          </li>
        )}

        {/* Relatórios - Todos */}
        <li>
          <Link to="/reports">Relatórios</Link>
        </li>
      </ul>

      <div className="nav-footer">
        <div className="user-info">
          <p>{user?.name}</p>
          <small>{user?.role}</small>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Sair
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
