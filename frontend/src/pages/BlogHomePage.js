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
            🍄
            APEBRAIN
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

      {/* Newsletter Section */}
      <div className="newsletter-section">
        <div className="newsletter-content">
          <h2>Join the Consciousness Collective</h2>
          <p>Expand your mind with weekly insights on mycology, consciousness, and human evolution</p>
          <div className="newsletter-form">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="newsletter-input"
            />
            <button className="newsletter-btn">
              Subscribe
            </button>
          </div>
          <div className="apebrain-branding">
            <span>🍄 + 🧠</span>
            <span>APEBRAIN</span>
          </div>
        </div>
      </div>

      <Footer />

      <style>{`
        /* Knowledge Portal Hero */
        .knowledge-portal-hero {
          text-align: center;
          padding: 4rem 2rem 3rem;
          background: linear-gradient(135deg, rgba(255, 23, 68, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%);
        }

        .hero-icon-combo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .hero-icon-combo .plus {
          font-size: 1.8rem;
          color: #ff6b8a;
          opacity: 0.8;
        }

        .knowledge-portal-hero h1 {
          font-size: clamp(2.5rem, 5vw, 4rem);
          margin-bottom: 1rem;
          background: linear-gradient(135deg, #ff1744 0%, #ec4899 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-subtitle-line {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          font-size: 1.1rem;
          font-weight: 500;
          letter-spacing: 2px;
          text-transform: uppercase;
          color: #d4b5d9;
          margin-bottom: 2rem;
        }

        .hero-subtitle-line .dot {
          color: #ff6b8a;
        }

        .hero-mckenna-quote {
          max-width: 800px;
          margin: 0 auto;
          font-family: 'Playfair Display', serif;
          font-size: 1.2rem;
          font-style: italic;
          line-height: 1.8;
          color: #f8e8f0;
          padding: 2rem;
          background: rgba(255, 23, 68, 0.08);
          border-left: 4px solid #ff1744;
          border-radius: 12px;
        }

        .hero-mckenna-quote cite {
          display: block;
          margin-top: 1rem;
          font-size: 0.95rem;
          font-style: normal;
          color: #ff6b8a;
          font-family: 'Inter', sans-serif;
        }

        /* Category Navigation */
        .category-navigation {
          display: flex;
          justify-content: center;
          gap: 1rem;
          padding: 2rem;
          flex-wrap: wrap;
          max-width: 1000px;
          margin: 0 auto;
        }

        .category-btn {
          padding: 0.75rem 1.5rem;
          background: rgba(30, 20, 35, 0.6);
          border: 1px solid rgba(255, 23, 68, 0.3);
          border-radius: 50px;
          color: #e0d5e5;
          font-weight: 500;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .category-btn:hover {
          background: rgba(255, 23, 68, 0.2);
          border-color: rgba(255, 23, 68, 0.6);
          box-shadow: 0 0 20px rgba(255, 23, 68, 0.4);
          transform: translateY(-2px);
        }

        .category-btn.active {
          background: linear-gradient(135deg, #ff1744 0%, #ec4899 100%);
          border-color: rgba(255, 23, 68, 0.7);
          color: white;
          box-shadow: 0 0 25px rgba(255, 23, 68, 0.6);
        }

        .cat-icon {
          font-size: 1.2rem;
        }

        /* Newsletter Section */
        .newsletter-section {
          background: rgba(30, 20, 35, 0.8);
          border-top: 1px solid rgba(255, 23, 68, 0.3);
          padding: 4rem 2rem;
          margin-top: 4rem;
        }

        .newsletter-content {
          max-width: 700px;
          margin: 0 auto;
          text-align: center;
        }

        .newsletter-content h2 {
          font-size: 2.5rem;
          margin-bottom: 1rem;
          color: #f8e8f0;
          text-shadow: 0 0 20px rgba(255, 23, 68, 0.5);
        }

        .newsletter-content p {
          font-size: 1.15rem;
          color: #d4b5d9;
          margin-bottom: 2rem;
        }

        .newsletter-form {
          display: flex;
          gap: 1rem;
          max-width: 500px;
          margin: 0 auto 2rem;
        }

        .newsletter-input {
          flex: 1;
          padding: 1rem 1.5rem;
          background: rgba(20, 10, 25, 0.8);
          border: 2px solid rgba(255, 23, 68, 0.3);
          border-radius: 50px;
          color: #e0d5e5;
          font-size: 1rem;
          transition: all 0.3s;
        }

        .newsletter-input:focus {
          outline: none;
          border-color: #ff1744;
          box-shadow: 0 0 20px rgba(255, 23, 68, 0.4);
        }

        .newsletter-btn {
          padding: 1rem 2.5rem;
          background: linear-gradient(135deg, #ff1744 0%, #ec4899 100%);
          border: none;
          border-radius: 50px;
          color: white;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 0 20px rgba(255, 23, 68, 0.5);
        }

        .newsletter-btn:hover {
          box-shadow: 0 0 30px rgba(255, 23, 68, 0.8);
          transform: translateY(-2px);
        }

        .apebrain-branding {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          font-size: 1.1rem;
          color: #ff6b8a;
          font-weight: 600;
          margin-top: 2rem;
        }

        .apebrain-branding span:first-child {
          font-size: 1.5rem;
        }
      `}</style>
    </div>
  );
};

export default BlogHomePage;