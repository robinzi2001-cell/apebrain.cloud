import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Package, LogOut, ChevronDown } from 'lucide-react';

const UserDropdown = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('userToken');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('user');
    setUser(null);
    setIsOpen(false);
    navigate('/');
  };

  if (!user) {
    return (
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <Link
          to="/login"
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(30, 20, 35, 0.7)',
            color: '#e0d5e5',
            border: '1px solid rgba(255, 23, 68, 0.4)',
            borderRadius: '6px',
            textDecoration: 'none',
            fontSize: '0.9rem',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 23, 68, 0.2)';
            e.currentTarget.style.boxShadow = '0 0 15px rgba(255, 23, 68, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(30, 20, 35, 0.7)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          Anmelden
        </Link>
        <Link
          to="/register"
          style={{
            padding: '0.5rem 1rem',
            background: 'linear-gradient(135deg, #ff1744 0%, #ec4899 100%)',
            color: 'white',
            border: '1px solid rgba(255, 23, 68, 0.5)',
            borderRadius: '6px',
            textDecoration: 'none',
            fontSize: '0.9rem',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = '0 0 20px rgba(255, 23, 68, 0.8)';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          Registrieren
        </Link>
      </div>
    );
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          background: 'rgba(30, 20, 35, 0.8)',
          border: '1px solid rgba(255, 23, 68, 0.3)',
          borderRadius: '20px',
          cursor: 'pointer',
          transition: 'all 0.2s',
          boxShadow: isOpen ? '0 4px 20px rgba(255, 23, 68, 0.4)' : 'none'
        }}
      >
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #ff1744 0%, #ec4899 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '600',
          fontSize: '0.9rem',
          boxShadow: '0 0 15px rgba(255, 23, 68, 0.5)'
        }}>
          {user.first_name ? user.first_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
        </div>
        <div style={{ textAlign: 'left' }}>
          <div style={{ fontSize: '0.75rem', color: '#d4b5d9' }}>Hallo,</div>
          <div style={{ fontSize: '0.9rem', color: '#f8e8f0', fontWeight: '600' }}>
            {user.first_name || user.email.split('@')[0]}
          </div>
        </div>
        <ChevronDown size={16} style={{ color: '#d4b5d9', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 0.5rem)',
          right: 0,
          minWidth: '200px',
          background: 'rgba(20, 10, 25, 0.98)',
          backdropFilter: 'blur(15px)',
          border: '1px solid rgba(255, 23, 68, 0.3)',
          borderRadius: '12px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(255, 23, 68, 0.2)',
          overflow: 'hidden',
          zIndex: 1000
        }}>
          <Link
            to="/dashboard"
            onClick={() => setIsOpen(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              textDecoration: 'none',
              color: '#e0d5e5',
              transition: 'all 0.2s',
              borderBottom: '1px solid rgba(255, 23, 68, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 23, 68, 0.15)';
              e.currentTarget.style.color = '#ff6b8a';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = '#e0d5e5';
            }}
          >
            <User size={18} />
            <span>Mein Dashboard</span>
          </Link>
          <Link
            to="/dashboard"
            onClick={() => setIsOpen(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              textDecoration: 'none',
              color: '#e0d5e5',
              transition: 'all 0.2s',
              borderBottom: '1px solid rgba(255, 23, 68, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 23, 68, 0.15)';
              e.currentTarget.style.color = '#ff6b8a';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = '#e0d5e5';
            }}
          >
            <Package size={18} />
            <span>Meine Bestellungen</span>
          </Link>
          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              background: 'transparent',
              border: 'none',
              color: '#ff6b8a',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              fontSize: '1rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
              e.currentTarget.style.color = '#ef4444';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = '#ff6b8a';
            }}
          >
            <LogOut size={18} />
            <span>Abmelden</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;
