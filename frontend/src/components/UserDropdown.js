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
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '20px',
          cursor: 'pointer',
          transition: 'all 0.2s',
          boxShadow: isOpen ? '0 4px 12px rgba(0,0,0,0.1)' : 'none'
        }}
      >
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #7a9053 0%, #5a7039 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '600',
          fontSize: '0.9rem'
        }}>
          {user.first_name ? user.first_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
        </div>
        <div style={{ textAlign: 'left' }}>
          <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Hallo,</div>
          <div style={{ fontSize: '0.9rem', color: '#3a4520', fontWeight: '600' }}>
            {user.first_name || user.email.split('@')[0]}
          </div>
        </div>
        <ChevronDown size={16} style={{ color: '#9ca3af', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 0.5rem)',
          right: 0,
          minWidth: '200px',
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
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
              color: '#3a4520',
              transition: 'background 0.2s',
              borderBottom: '1px solid #f3f4f6'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
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
              color: '#3a4520',
              transition: 'background 0.2s',
              borderBottom: '1px solid #f3f4f6'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
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
              background: 'white',
              border: 'none',
              color: '#ef4444',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'background 0.2s',
              fontSize: '1rem'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#fef2f2'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
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
