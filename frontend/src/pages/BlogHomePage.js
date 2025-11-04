import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Leaf, Home, Instagram } from 'lucide-react';
import Footer from '@/components/Footer';
import UserDropdown from '@/components/UserDropdown';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BlogHomePage = () => {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchBlogs();
  }, []);

  const fetchBlogs = async () => {
    try {
      const response = await axios.get(`${API}/blogs?status=published`);
      setBlogs(response.data);
    } catch (error) {
      console.error('Error fetching blogs:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getColorTheme = (keywords) => {
    const kw = keywords.toLowerCase();
    if (kw.includes('magic') || kw.includes('psychedelic') || kw.includes('psilocybin')) {
      return { bg: 'linear-gradient(135deg, #a78bfa 0%, #ec4899 100%)', icon: '#a78bfa' };
    }
    if (kw.includes('forest') || kw.includes('nature') || kw.includes('wild')) {
      return { bg: 'linear-gradient(135deg, #6b7c59 0%, #4a5942 100%)', icon: '#6b7c59' };
    }
    if (kw.includes('ocean') || kw.includes('sea') || kw.includes('water')) {
      return { bg: 'linear-gradient(135deg, #7dd3c0 0%, #4a90a4 100%)', icon: '#7dd3c0' };
    }
    if (kw.includes('energy') || kw.includes('vitality') || kw.includes('boost')) {
      return { bg: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)', icon: '#fbbf24' };
    }
    if (kw.includes('calm') || kw.includes('relax') || kw.includes('meditation')) {
      return { bg: 'linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 100%)', icon: '#c7d2fe' };
    }
    return { bg: 'linear-gradient(135deg, #7a9053 0%, #5a6c3a 100%)', icon: '#7a9053' };
  };

  return (
    <div>
      <nav className="navbar" data-testid="navbar">
        <div className="navbar-content">
          <a href="/" className="logo" data-testid="logo-link">
            <Leaf size={32} />
            ApeBrain.cloud
          </a>
          <div className="nav-links">
            <a href="/" data-testid="home-link"><Home size={20} /> Home</a>
            <a href="/blog" data-testid="blog-link">Blog</a>
            <a href="/shop" data-testid="shop-link">Shop</a>
            <a 
              href="https://www.instagram.com/apebrain.cloud" 
              target="_blank" 
              rel="noopener noreferrer"
              data-testid="instagram-link"
              style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}
            >
              <Instagram size={20} />
            </a>
            <UserDropdown />
          </div>
        </div>
      </nav>

      {/* Knowledge Portal Hero */}
      <div className="knowledge-portal-hero" data-testid="hero-section">
        <div className="hero-icon-combo">
          <span>🍄</span>
          <span className="plus">+</span>
          <span>🧠</span>
        </div>
        <h1 data-testid="hero-title">APEBRAIN Knowledge Portal</h1>
        <div className="hero-subtitle-line">
          <span>Consciousness</span>
          <span className="dot">•</span>
          <span>Mycology</span>
          <span className="dot">•</span>
          <span>Evolution</span>
        </div>
        <blockquote className="hero-mckenna-quote">
          "The syntactical nature of reality, the real secret of magic, is that the world is made of words. 
          And if you know the words that the world is made of, you can make of it whatever you wish."
          <cite>— Terence McKenna</cite>
        </blockquote>
      </div>

      {/* Category Navigation */}
      <div className="category-navigation">
        {[
          { id: 'all', label: 'All Articles', icon: '📚' },
          { id: 'philosophy', label: 'Philosophy', icon: '🧠' },
          { id: 'science', label: 'Science', icon: '🔬' },
          { id: 'guides', label: 'Guides', icon: '📖' },
          { id: 'history', label: 'History', icon: '🏛️' },
          { id: 'experiences', label: 'Experiences', icon: '✨' }
        ].map(cat => (
          <button
            key={cat.id}
            className={`category-btn ${selectedCategory === cat.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat.id)}
          >
            <span className="cat-icon">{cat.icon}</span>
            {cat.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading" data-testid="loading-indicator">Loading blogs...</div>
      ) : (
        <div className="blog-grid" data-testid="blog-grid">
          {blogs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', gridColumn: '1 / -1' }} data-testid="no-blogs">
              <p>No blog posts yet. Check back soon!</p>
            </div>
          ) : (
            blogs.map((blog) => {
              const theme = getColorTheme(blog.keywords || '');
              return (
                <div
                  key={blog.id}
                  className="blog-card"
                  onClick={() => navigate(`/blog/${blog.id}`)}
                  data-testid={`blog-card-${blog.id}`}
                >
                  {blog.image_url ? (
                    <img
                      src={blog.image_url}
                      alt={blog.title}
                      className="blog-card-image"
                      data-testid={`blog-image-${blog.id}`}
                    />
                  ) : (
                    <div 
                      className="blog-card-image"
                      style={{ 
                        background: theme.bg,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '1.2rem'
                      }}
                      data-testid={`blog-placeholder-${blog.id}`}
                    >
                      <Leaf size={64} />
                    </div>
                  )}
                  <div className="blog-card-content">
                    <h3 data-testid={`blog-title-${blog.id}`}>{blog.title}</h3>
                    <div className="blog-card-meta" data-testid={`blog-date-${blog.id}`}>
                      {formatDate(blog.published_at || blog.created_at)}
                    </div>
                    <p data-testid={`blog-excerpt-${blog.id}`}>
                      {blog.content.substring(0, 150)}...
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
      <Footer />
    </div>
  );
};

export default BlogHomePage;