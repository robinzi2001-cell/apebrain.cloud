import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, BookOpen, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const navigate = useNavigate();
  const [showBlog, setShowBlog] = useState(true);
  const [showShop, setShowShop] = useState(true);
  const [showMinigames, setShowMinigames] = useState(true);
  const [settings, setSettings] = useState(null);
  const [mushrooms, setMushrooms] = useState([]);

  useEffect(() => {
    fetchLandingSettings();
    startMushroomRain();
  }, []);

  const fetchLandingSettings = async () => {
    try {
      const response = await axios.get(`${API}/landing-settings`);
      setSettings(response.data);
      setShowBlog(response.data.show_blog);
      setShowShop(response.data.show_shop);
      setShowMinigames(response.data.show_minigames);
    } catch (error) {
      console.error('Error fetching landing settings:', error);
    }
  };

  const startMushroomRain = () => {
    const spawnMushroom = () => {
      const mushroomId = Date.now() + Math.random();
      const startX = Math.random() * 100;
      const duration = 3 + Math.random() * 2; // 3-5 seconds
      const mushroomEmoji = ['🍄'][Math.floor(Math.random() * 1)];

      setMushrooms(prev => [...prev, { id: mushroomId, x: startX, duration, emoji: mushroomEmoji }]);

      setTimeout(() => {
        setMushrooms(prev => prev.filter(m => m.id !== mushroomId));
      }, duration * 1000);
    };

    // Spawn mushroom every 20-40 seconds
    const interval = setInterval(() => {
      const delay = 20000 + Math.random() * 20000; // 20-40 seconds
      setTimeout(spawnMushroom, delay);
    }, 1000);

    return () => clearInterval(interval);
  };

  const renderGalleryCard = (section, icon, title, description, route) => {
    if (!settings) return null;

    const galleryMode = settings[`${section}_gallery_mode`];
    const galleryImages = settings[`${section}_gallery_images`] || [];
    const imageCount = galleryImages.length;

    // Dynamic grid layout based on image count
    let gridTemplate = 'none';
    if (imageCount === 1) gridTemplate = '1fr';
    if (imageCount === 2) gridTemplate = '1fr 1fr';
    if (imageCount >= 3) gridTemplate = 'repeat(3, 1fr)';

    // Get custom background colors
    const bgColorStart = settings.card_bg_color_start || 'rgba(167, 139, 250, 0.15)';
    const bgColorMiddle = settings.card_bg_color_middle || 'rgba(139, 92, 246, 0.12)';
    const bgColorEnd = settings.card_bg_color_end || 'rgba(124, 58, 237, 0.15)';

    return (
      <div 
        className="landing-gallery-card"
        onClick={() => route && navigate(route)}
        style={{
          cursor: route ? 'pointer' : 'default',
          opacity: route ? 1 : 0.7
        }}
      >
        {/* Gallery Background or Custom color fallback */}
        {galleryMode !== 'none' && imageCount > 0 ? (
          <div className="gallery-background" style={{ gridTemplateColumns: gridTemplate }}>
            {galleryImages.slice(0, 3).map((img, idx) => (
              <div
                key={idx}
                className="gallery-img"
                style={{
                  backgroundImage: `url(${img})`,
                  animationDelay: `${idx * 0.2}s`,
                  gridColumn: imageCount === 1 ? '1 / -1' : 'auto'
                }}
              />
            ))}
            <div className="gallery-overlay"></div>
          </div>
        ) : (
          <div 
            className="custom-background"
            style={{
              background: `linear-gradient(135deg, ${bgColorStart} 0%, ${bgColorMiddle} 50%, ${bgColorEnd} 100%)`
            }}
          ></div>
        )}

        {/* Card Content */}
        <div className="gallery-card-content">
          <div className="card-icon">{icon}</div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="landing-page" data-testid="landing-page">
      <div className="landing-overlay"></div>
      
      {/* Mini Mushroom Rain Easter Egg */}
      {mushrooms.map(mushroom => (
        <div
          key={mushroom.id}
          className="mini-mushroom-rain"
          style={{
            left: `${mushroom.x}%`,
            animation: `mushroomFall ${mushroom.duration}s linear forwards`
          }}
        >
          {mushroom.emoji}
        </div>
      ))}

      <div className="landing-content">
        {/* Hero Section with Icon Combination */}
        <div className="landing-header">
          <div className="icon-combination">
            <span className="mushroom-icon">🍄</span>
            <span className="plus-icon">+</span>
            <span className="brain-icon">🧠</span>
          </div>
          <h1 className="landing-title" data-testid="landing-title">APEBRAIN</h1>
          <div className="consciousness-tagline">
            <span>Consciousness</span>
            <span className="separator">•</span>
            <span>Mycology</span>
            <span className="separator">•</span>
            <span>Evolution</span>
          </div>
          <blockquote className="mckenna-quote">
            "The history of the human race is a history of the human race's relationship with psychoactive plants."
            <cite>— Terence McKenna</cite>
          </blockquote>
        </div>

        {/* Featured Quote Section - Stoned Ape Theory */}
        <div className="featured-quote-section">
          <div className="theory-badge">STONED APE THEORY</div>
          <p className="theory-text">
            What if consciousness expansion through psilocybin mushrooms catalyzed human evolution? 
            Terence McKenna proposed that our ancestors' encounter with psychedelic fungi 
            accelerated brain development, language, and self-awareness — transforming apes into humans.
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="landing-cards" data-testid="landing-cards">
          {showBlog && renderGalleryCard(
            'blog',
            <BookOpen size={48} />,
            'Knowledge Portal',
            'Explore consciousness, mycology & evolutionary philosophy',
            '/blog'
          )}

          {showShop && renderGalleryCard(
            'shop',
            <ShoppingBag size={48} />,
            'Sacred Shop',
            'Premium Amanita muscaria products for conscious exploration',
            '/shop'
          )}

          {showMinigames && renderGalleryCard(
            'minigames',
            <Sparkles size={48} />,
            'Consciousness Games',
            'Interactive experiences • Coming Soon',
            null
          )}
        </div>

        <div className="landing-footer">
          <p>"Nature loves courage. You make the commitment and nature will respond to that commitment by removing impossible obstacles."</p>
          <cite>— Terence McKenna</cite>
        </div>
      </div>

      <style>{`
        .landing-gallery-card {
          position: relative;
          background: linear-gradient(135deg, rgba(122, 144, 83, 0.1) 0%, rgba(58, 69, 32, 0.1) 100%);
          border-radius: 20px;
          padding: 2.5rem;
          min-height: 300px;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          overflow: hidden;
          border: 2px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
        }

        .landing-gallery-card:hover {
          transform: translateY(-10px) scale(1.02);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .gallery-background {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          display: grid;
          gap: 0;
          z-index: 0;
        }

        .gallery-img {
          background-size: cover;
          background-position: center;
          animation: galleryPulse 8s ease-in-out infinite;
          opacity: 0.4;
          transition: opacity 0.3s ease;
        }

        .landing-gallery-card:hover .gallery-img {
          opacity: 0.6;
        }

        .gallery-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(122, 144, 83, 0.75) 0%, rgba(58, 69, 32, 0.85) 100%);
          backdrop-filter: blur(2px);
        }

        /* Custom background for cards without images - Dynamic from settings */
        .custom-background {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 0;
          transition: all 0.3s ease;
        }

        .landing-gallery-card:hover .custom-background {
          filter: brightness(1.15);
        }

        .gallery-card-content {
          position: relative;
          z-index: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          text-align: center;
        }

        .gallery-card-content .card-icon {
          color: #fff;
          margin-bottom: 1rem;
          filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
        }

        .gallery-card-content h2 {
          color: #fff;
          font-size: 2rem;
          margin-bottom: 0.5rem;
          text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .gallery-card-content p {
          color: rgba(255, 255, 255, 0.9);
          font-size: 1.1rem;
          text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }

        @keyframes galleryPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        /* Mini Mushroom Rain */
        .mini-mushroom-rain {
          position: fixed;
          top: -50px;
          font-size: 1.5rem;
          z-index: 9999;
          pointer-events: none;
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
        }

        @keyframes mushroomFall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
