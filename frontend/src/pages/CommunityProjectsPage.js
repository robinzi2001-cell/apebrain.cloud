import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Users, Github, MessageCircle } from 'lucide-react';
import Footer from '@/components/Footer';
import UserDropdown from '@/components/UserDropdown';

const CommunityProjectsPage = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const projects = [
    {
      id: 1,
      title: 'Open Source Mycelium Network',
      description: 'Dezentrales Kommunikationsnetzwerk inspiriert von Pilz-Myzelien',
      category: 'technology',
      status: 'active',
      github: 'https://github.com/apebrain/mycelium-network',
      contributors: 12
    },
    {
      id: 2,
      title: 'Community Garden Initiative',
      description: 'Lokale Garten-Projekte für nachhaltige Pilzzucht',
      category: 'nature',
      status: 'active',
      contributors: 8
    },
    {
      id: 3,
      title: 'Consciousness Research Collective',
      description: 'Forschungsgruppe zu Bewusstseinserweiterung und Psychedelika',
      category: 'research',
      status: 'planning',
      contributors: 15
    }
  ];

  const categories = [
    { id: 'all', label: 'All Projects', icon: '🌍' },
    { id: 'technology', label: 'Technology', icon: '💻' },
    { id: 'nature', label: 'Nature', icon: '🌱' },
    { id: 'research', label: 'Research', icon: '🔬' },
    { id: 'art', label: 'Art & Culture', icon: '🎨' },
    { id: 'education', label: 'Education', icon: '📚' }
  ];

  const filteredProjects = selectedCategory === 'all' 
    ? projects 
    : projects.filter(p => p.category === selectedCategory);

  return (
    <div>
      <nav className="navbar" data-testid="navbar">
        <div className="navbar-content">
          <a href="/" className="logo" data-testid="logo-link">
            🍄 APEBRAIN
          </a>
          <div className="nav-links">
            <a href="/" data-testid="home-link"><Home size={20} /> Home</a>
            <a href="/blog" data-testid="blog-link">Blog</a>
            <a href="/shop" data-testid="shop-link">Shop</a>
            <a href="/community" data-testid="community-link">Community</a>
            <UserDropdown />
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(122, 144, 83, 0.15) 0%, rgba(90, 108, 58, 0.15) 100%)',
        padding: '4rem 2rem',
        textAlign: 'center',
        borderBottom: '1px solid rgba(255, 23, 68, 0.2)'
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🍄🧠</div>
          <h1 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            color: '#f8e8f0',
            marginBottom: '1rem',
            textShadow: '0 0 20px rgba(255, 23, 68, 0.4)'
          }}>
            Community Projekte
          </h1>
          <p style={{
            fontSize: '1.2rem',
            color: '#d4b5d9',
            fontStyle: 'italic',
            maxWidth: '700px',
            margin: '0 auto 2rem'
          }}>
            "We are not separate from nature. We are nature."<br/>
            — Terence McKenna
          </p>
          <p style={{ color: '#e0d5e5', fontSize: '1.1rem', lineHeight: '1.8' }}>
            Gemeinsam wachsen wir wie ein Myzel-Netzwerk — verbunden, dezentral und resilient.
          </p>
        </div>
      </div>

      {/* Category Navigation */}
      <div style={{
        maxWidth: '1400px',
        margin: '3rem auto',
        padding: '0 2rem'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem',
          marginBottom: '3rem'
        }}>
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              style={{
                padding: '1rem',
                background: selectedCategory === cat.id 
                  ? 'linear-gradient(135deg, #ff1744 0%, #ec4899 100%)'
                  : 'rgba(122, 144, 83, 0.2)',
                border: selectedCategory === cat.id
                  ? '2px solid #ff1744'
                  : '2px solid rgba(122, 144, 83, 0.3)',
                borderRadius: '12px',
                color: '#f8e8f0',
                cursor: 'pointer',
                transition: 'all 0.3s',
                fontSize: '1rem',
                fontWeight: '500',
                textAlign: 'center'
              }}
              onMouseEnter={(e) => {
                if (selectedCategory !== cat.id) {
                  e.target.style.background = 'rgba(122, 144, 83, 0.4)';
                  e.target.style.transform = 'translateY(-2px)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== cat.id) {
                  e.target.style.background = 'rgba(122, 144, 83, 0.2)';
                  e.target.style.transform = 'translateY(0)';
                }
              }}
            >
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{cat.icon}</div>
              {cat.label}
            </button>
          ))}
        </div>

        {/* Projects Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '2rem'
        }}>
          {filteredProjects.map(project => (
            <div
              key={project.id}
              style={{
                background: 'rgba(20, 10, 25, 0.7)',
                border: '1px solid rgba(255, 23, 68, 0.3)',
                borderRadius: '16px',
                padding: '2rem',
                transition: 'all 0.3s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-8px)';
                e.currentTarget.style.boxShadow = '0 15px 40px rgba(255, 23, 68, 0.4)';
                e.currentTarget.style.border = '1px solid rgba(255, 23, 68, 0.6)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.border = '1px solid rgba(255, 23, 68, 0.3)';
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'start',
                marginBottom: '1rem'
              }}>
                <h3 style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: '1.5rem',
                  color: '#ff6b8a',
                  marginBottom: '0.5rem'
                }}>
                  {project.title}
                </h3>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  background: project.status === 'active' 
                    ? 'rgba(76, 175, 80, 0.2)'
                    : 'rgba(255, 152, 0, 0.2)',
                  color: project.status === 'active' ? '#81c784' : '#ffb74d',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  fontWeight: '500'
                }}>
                  {project.status === 'active' ? '✓ Active' : '⏳ Planning'}
                </span>
              </div>
              
              <p style={{
                color: '#d4b5d9',
                marginBottom: '1.5rem',
                lineHeight: '1.6'
              }}>
                {project.description}
              </p>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
                paddingTop: '1rem',
                borderTop: '1px solid rgba(255, 23, 68, 0.2)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#e0d5e5' }}>
                  <Users size={18} />
                  <span>{project.contributors} Contributors</span>
                </div>
                {project.github && (
                  <a 
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      color: '#ff6b8a',
                      textDecoration: 'none',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => e.target.style.color = '#ff1744'}
                    onMouseLeave={(e) => e.target.style.color = '#ff6b8a'}
                  >
                    <Github size={18} />
                    GitHub
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Join Community CTA */}
        <div style={{
          marginTop: '4rem',
          padding: '3rem',
          background: 'linear-gradient(135deg, rgba(122, 144, 83, 0.15) 0%, rgba(255, 23, 68, 0.08) 100%)',
          borderRadius: '16px',
          border: '1px solid rgba(122, 144, 83, 0.3)',
          textAlign: 'center'
        }}>
          <MessageCircle size={48} style={{ color: '#ff6b8a', marginBottom: '1rem' }} />
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '2rem',
            color: '#f8e8f0',
            marginBottom: '1rem'
          }}>
            Join the Collective
          </h2>
          <p style={{
            color: '#d4b5d9',
            fontSize: '1.1rem',
            marginBottom: '2rem',
            maxWidth: '600px',
            margin: '0 auto 2rem'
          }}>
            Werde Teil unserer Community und bringe deine eigenen Projekte ein.
          </p>
          <button
            onClick={() => window.open('https://discord.gg/apebrain', '_blank')}
            style={{
              padding: '1rem 2rem',
              background: 'linear-gradient(135deg, #ff1744 0%, #ec4899 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 25px rgba(255, 23, 68, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            Join Discord Community
          </button>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default CommunityProjectsPage;
