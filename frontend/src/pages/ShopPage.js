import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Footer from '@/components/Footer';
import UserDropdown from '@/components/UserDropdown';
import { Leaf, Home, Package, Download, ShoppingCart, Plus, Minus, Trash2, Instagram } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import FloatingCoupon from '@/components/FloatingCoupon';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ShopPage = () => {
  const [activeTab, setActiveTab] = useState('physical');
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [couponError, setCouponError] = useState('');
  const [currentQuote, setCurrentQuote] = useState(0);
  const navigate = useNavigate();

  const heroQuotes = [
    "What expanded primate minds can restore yours",
    "god knows how"
  ];

  useEffect(() => {
    // Rotate quotes every 5 seconds
    const quoteInterval = setInterval(() => {
      setCurrentQuote(prev => (prev + 1) % heroQuotes.length);
    }, 5000);
    return () => clearInterval(quoteInterval);
  }, []);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setAllProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const physicalProducts = allProducts.filter(p => p.type === 'physical');
  const digitalProducts = allProducts.filter(p => p.type === 'digital');

  const products = activeTab === 'physical' ? physicalProducts : digitalProducts;

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    setShowCart(true);
  };

  const updateQuantity = (productId, change) => {
    setCart(cart.map(item => {
      if (item.id === productId) {
        const newQuantity = item.quantity + change;
        return newQuantity > 0 ? { ...item, quantity: newQuantity } : item;
      }
      return item;
    }).filter(item => item.quantity > 0));
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const getCartTotal = () => {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    if (appliedCoupon) {
      const discount = appliedCoupon.discount_type === 'percentage' 
        ? subtotal * (appliedCoupon.discount_value / 100)
        : appliedCoupon.discount_value;
      return Math.max(0, subtotal - discount).toFixed(2);
    }
    return subtotal.toFixed(2);
  };

  const getSubtotal = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2);
  };

  const getDiscount = () => {
    if (!appliedCoupon) return 0;
    const subtotal = parseFloat(getSubtotal());
    const discount = appliedCoupon.discount_type === 'percentage'
      ? subtotal * (appliedCoupon.discount_value / 100)
      : appliedCoupon.discount_value;
    return discount.toFixed(2);
  };

  const getCartCount = () => {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
  };

  const handleCheckout = async () => {
    try {
      // Get logged-in user email if available
      let customerEmail = "guest@apebrain.cloud";
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          customerEmail = user.email;
        } catch (e) {
          console.error('Error parsing user data:', e);
        }
      }

      // Prepare order data
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          name: item.name,
          quantity: item.quantity,
          price: item.price,
          product_type: item.type || 'physical'
        })),
        total: parseFloat(getCartTotal()),
        customer_email: customerEmail
      };

      // Add coupon code if applied
      if (appliedCoupon) {
        orderData.coupon_code = appliedCoupon.code;
      }

      // Create PayPal order
      const response = await axios.post(`${API}/shop/create-order`, orderData);
      
      if (response.data.approval_url) {
        // Redirect to PayPal
        window.location.href = response.data.approval_url;
      } else {
        alert('Failed to create PayPal order. Please try again.');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert(error.response?.data?.detail || 'Checkout failed. Please try again.');
    }
  };

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) {
      setCouponError('Please enter a coupon code');
      return;
    }

    try {
      const subtotal = parseFloat(getSubtotal());
      const response = await axios.post(`${API}/coupons/validate`, {
        code: couponCode.toUpperCase(),
        order_total: subtotal
      });

      if (response.data.valid) {
        setAppliedCoupon(response.data.coupon);
        setCouponError('');
      } else {
        setCouponError(response.data.message || 'Invalid coupon code');
        setAppliedCoupon(null);
      }
    } catch (error) {
      console.error('Coupon validation error:', error);
      setCouponError(error.response?.data?.detail || 'Failed to validate coupon');
      setAppliedCoupon(null);
    }
  };

  const handleRemoveCoupon = () => {
    setAppliedCoupon(null);
    setCouponCode('');
    setCouponError('');
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
            <button 
              onClick={() => setShowCart(!showCart)}
              className="btn btn-secondary cart-button"
              data-testid="cart-button"
            >
              <ShoppingCart size={20} />
              {getCartCount() > 0 && (
                <span className="cart-badge">{getCartCount()}</span>
              )}
            </button>
            <UserDropdown />
          </div>
        </div>
      </nav>

      {/* Sacred Shop Hero with Alternating Quotes */}
      <div className="sacred-shop-hero" data-testid="shop-hero">
        <div className="hero-icon-combo">
          <span>🍄</span>
          <span className="plus">+</span>
          <span>🧠</span>
        </div>
        <h1>APEBRAIN Sacred Shop</h1>
        <div className="alternating-quote">
          {heroQuotes[currentQuote]}
        </div>
        <p className="hero-description">Premium Amanita muscaria products for conscious exploration</p>
      </div>

      <div className="shop-container" data-testid="shop-container">
        <div className="shop-tabs">
          <button
            className={`shop-tab ${activeTab === 'physical' ? 'active' : ''}`}
            onClick={() => setActiveTab('physical')}
            data-testid="physical-tab"
          >
            <Package size={20} />
            Physical Products
          </button>
          <button
            className={`shop-tab ${activeTab === 'digital' ? 'active' : ''}`}
            onClick={() => setActiveTab('digital')}
            data-testid="digital-tab"
          >
            <Download size={20} />
            Digital Products
          </button>
        </div>

        <div className="products-grid" data-testid="products-grid">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>Loading products...</div>
          ) : products.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>No products available</div>
          ) : (
            products.map(product => (
              <div key={product.id} className="product-card" data-testid={`product-${product.id}`}>
                {product.image_url ? (
                  <img 
                    src={product.image_url} 
                    alt={product.name}
                    style={{
                      width: '100%',
                      height: '200px',
                      objectFit: 'cover',
                      borderRadius: '12px 12px 0 0'
                    }}
                  />
                ) : (
                  <div className="product-image-placeholder">
                    {activeTab === 'physical' ? <Package size={64} /> : <Download size={64} />}
                  </div>
                )}
                <div className="product-info">
                  <span className="product-category">{product.category}</span>
                  <h3 className="product-name">{product.name}</h3>
                  <p className="product-description">{product.description}</p>
                  <div className="product-footer">
                    <span className="product-price">${product.price.toFixed(2)}</span>
                    <button 
                      className="btn btn-primary" 
                      onClick={() => addToCart(product)}
                      data-testid={`add-to-cart-${product.id}`}
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Educational Section */}
        <div className="educational-section">
          <h2 className="section-title">The APEBRAIN Philosophy</h2>
          <div className="education-grid">
            <div className="education-card">
              <div className="edu-icon">🌿</div>
              <h3>Traditional Wisdom</h3>
              <p>Siberian shamans have used Amanita muscaria for millennia in sacred rituals. This ancient knowledge guides our understanding of muscimol's consciousness-expanding properties.</p>
            </div>
            <div className="education-card">
              <div className="edu-icon">🧠</div>
              <h3>Consciousness Evolution</h3>
              <p>The Stoned Ape Theory suggests psychoactive compounds catalyzed human brain development. We honor this evolutionary relationship between humans and fungi.</p>
            </div>
            <div className="education-card">
              <div className="edu-icon">📦</div>
              <h3>Modern Standards</h3>
              <p>Lab-tested muscimol content ensures consistency and safety. We bridge ancient wisdom with contemporary quality control for responsible exploration.</p>
            </div>
          </div>
        </div>

        {/* Safety Information Section */}
        <div className="safety-section">
          <h2 className="section-title">Safety & Responsibility</h2>
          <div className="safety-grid">
            <div className="safety-card">
              <div className="safety-icon">⚠️</div>
              <h3>Lab Verified</h3>
              <p>All products are third-party tested for muscimol content, heavy metals, and contaminants. Certificates available upon request.</p>
            </div>
            <div className="safety-card">
              <div className="safety-icon">🎯</div>
              <h3>Start Low</h3>
              <p>Begin with minimal doses. Amanita effects are dose-dependent. Respect the mushroom and allow time to understand your response.</p>
            </div>
            <div className="safety-card">
              <div className="safety-icon">📚</div>
              <h3>Set & Setting</h3>
              <p>Create a safe, comfortable environment. Mental preparation and proper context are essential for meaningful experiences.</p>
            </div>
            <div className="safety-card">
              <div className="safety-icon">📖</div>
              <h3>Educational Purpose</h3>
              <p>These products are sold for educational and research purposes. Not for human consumption. Not evaluated by FDA.</p>
            </div>
          </div>
          <div className="legal-disclaimer">
            <p><strong>Legal Notice:</strong> These statements have not been evaluated by the Food and Drug Administration. These products are not intended to diagnose, treat, cure, or prevent any disease. For educational purposes only.</p>
          </div>
        </div>
      </div>

      {/* Shopping Cart Sidebar */}
      {showCart && (
        <div className="cart-sidebar" data-testid="cart-sidebar">
          <div className="cart-header">
            <h2><ShoppingCart size={24} /> Your Cart</h2>
            <button onClick={() => setShowCart(false)} className="close-cart">×</button>
          </div>
          
          {cart.length === 0 ? (
            <div className="empty-cart" data-testid="empty-cart">
              <p>Your cart is empty</p>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item" data-testid={`cart-item-${item.id}`}>
                    <div className="cart-item-info">
                      <h4>{item.name}</h4>
                      <p>${item.price.toFixed(2)}</p>
                    </div>
                    <div className="cart-item-controls">
                      <button 
                        onClick={() => updateQuantity(item.id, -1)}
                        className="qty-btn"
                        data-testid={`decrease-qty-${item.id}`}
                      >
                        <Minus size={16} />
                      </button>
                      <span className="quantity">{item.quantity}</span>
                      <button 
                        onClick={() => updateQuantity(item.id, 1)}
                        className="qty-btn"
                        data-testid={`increase-qty-${item.id}`}
                      >
                        <Plus size={16} />
                      </button>
                      <button 
                        onClick={() => removeFromCart(item.id)}
                        className="remove-btn"
                        data-testid={`remove-item-${item.id}`}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="cart-footer">
                {/* Coupon Input Section */}
                <div className="coupon-section" style={{ 
                  marginBottom: '1rem', 
                  padding: '0.75rem', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '8px' 
                }}>
                  {!appliedCoupon ? (
                    <>
                      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <input
                          type="text"
                          value={couponCode}
                          onChange={(e) => {
                            setCouponCode(e.target.value.toUpperCase());
                            setCouponError('');
                          }}
                          placeholder="Enter coupon code"
                          style={{
                            flex: 1,
                            padding: '0.5rem',
                            border: couponError ? '2px solid #ef4444' : '1px solid #d1d5db',
                            borderRadius: '6px',
                            fontSize: '0.9rem'
                          }}
                          data-testid="coupon-input"
                        />
                        <button
                          onClick={handleApplyCoupon}
                          style={{
                            padding: '0.5rem 1rem',
                            backgroundColor: '#7a9053',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            fontWeight: '500'
                          }}
                          data-testid="apply-coupon-button"
                        >
                          Apply
                        </button>
                      </div>
                      {couponError && (
                        <p style={{ 
                          color: '#ef4444', 
                          fontSize: '0.85rem', 
                          margin: '0' 
                        }} data-testid="coupon-error">
                          {couponError}
                        </p>
                      )}
                    </>
                  ) : (
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center' 
                    }}>
                      <div>
                        <p style={{ 
                          margin: '0', 
                          fontSize: '0.9rem', 
                          fontWeight: '600', 
                          color: '#059669' 
                        }} data-testid="applied-coupon">
                          ✓ {appliedCoupon.code} Applied
                        </p>
                        <p style={{ 
                          margin: '0', 
                          fontSize: '0.8rem', 
                          color: '#6b7280' 
                        }}>
                          {appliedCoupon.discount_type === 'percentage' 
                            ? `${appliedCoupon.discount_value}% off` 
                            : `$${appliedCoupon.discount_value} off`}
                        </p>
                      </div>
                      <button
                        onClick={handleRemoveCoupon}
                        style={{
                          padding: '0.4rem 0.8rem',
                          backgroundColor: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.85rem'
                        }}
                        data-testid="remove-coupon-button"
                      >
                        Remove
                      </button>
                    </div>
                  )}
                </div>

                {/* Price Breakdown */}
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    marginBottom: '0.5rem',
                    fontSize: '0.95rem'
                  }}>
                    <span>Subtotal:</span>
                    <span>${getSubtotal()}</span>
                  </div>
                  {appliedCoupon && (
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      marginBottom: '0.5rem',
                      fontSize: '0.95rem',
                      color: '#059669'
                    }}>
                      <span>Discount:</span>
                      <span>-${getDiscount()}</span>
                    </div>
                  )}
                </div>

                <div className="cart-total">
                  <strong>Total:</strong>
                  <strong>${getCartTotal()}</strong>
                </div>
                <button 
                  onClick={handleCheckout}
                  className="btn btn-primary checkout-btn"
                  data-testid="checkout-button"
                >
                  Proceed to Checkout
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {showCart && <div className="cart-overlay" onClick={() => setShowCart(false)}></div>}
      
      <FloatingCoupon />

      <style>{`
        /* Sacred Shop Hero */
        .sacred-shop-hero {
          text-align: center;
          padding: 4rem 2rem 3rem;
          background: linear-gradient(135deg, rgba(255, 23, 68, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%);
        }

        .sacred-shop-hero .hero-icon-combo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .sacred-shop-hero .plus {
          font-size: 1.8rem;
          color: #ff6b8a;
          opacity: 0.8;
        }

        .sacred-shop-hero h1 {
          font-size: clamp(2.5rem, 5vw, 4rem);
          margin-bottom: 1rem;
          background: linear-gradient(135deg, #ff1744 0%, #ec4899 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .alternating-quote {
          font-family: 'Playfair Display', serif;
          font-size: 1.8rem;
          font-style: italic;
          color: #f8e8f0;
          margin-bottom: 1rem;
          min-height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: opacity 0.5s ease;
        }

        .hero-description {
          font-size: 1.15rem;
          color: #d4b5d9;
          max-width: 600px;
          margin: 0 auto;
        }

        /* Educational Section */
        .educational-section {
          max-width: 1200px;
          margin: 4rem auto;
          padding: 3rem 2rem;
          background: rgba(30, 20, 35, 0.7);
          border-radius: 20px;
          border: 1px solid rgba(255, 23, 68, 0.3);
          box-shadow: 0 10px 50px rgba(0, 0, 0, 0.7);
        }

        .section-title {
          text-align: center;
          font-size: 2.5rem;
          color: #f8e8f0;
          margin-bottom: 3rem;
          text-shadow: 0 0 20px rgba(255, 23, 68, 0.5);
        }

        .education-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
        }

        .education-card {
          background: rgba(20, 10, 25, 0.6);
          padding: 2rem;
          border-radius: 16px;
          border: 1px solid rgba(255, 23, 68, 0.2);
          transition: all 0.3s;
        }

        .education-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(255, 23, 68, 0.4);
          border-color: rgba(255, 23, 68, 0.5);
        }

        .edu-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          text-align: center;
        }

        .education-card h3 {
          font-size: 1.5rem;
          color: #ff6b8a;
          margin-bottom: 1rem;
          text-align: center;
        }

        .education-card p {
          color: #e0d5e5;
          line-height: 1.7;
          text-align: center;
        }

        /* Safety Section */
        .safety-section {
          max-width: 1200px;
          margin: 4rem auto;
          padding: 3rem 2rem;
          background: rgba(30, 20, 35, 0.7);
          border-radius: 20px;
          border: 1px solid rgba(255, 23, 68, 0.3);
          box-shadow: 0 10px 50px rgba(0, 0, 0, 0.7);
        }

        .safety-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .safety-card {
          background: rgba(20, 10, 25, 0.6);
          padding: 1.5rem;
          border-radius: 12px;
          border: 1px solid rgba(255, 23, 68, 0.2);
          transition: all 0.3s;
        }

        .safety-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(255, 23, 68, 0.3);
          border-color: rgba(255, 23, 68, 0.4);
        }

        .safety-icon {
          font-size: 2.5rem;
          margin-bottom: 1rem;
          text-align: center;
        }

        .safety-card h3 {
          font-size: 1.3rem;
          color: #ff6b8a;
          margin-bottom: 0.75rem;
          text-align: center;
        }

        .safety-card p {
          color: #e0d5e5;
          line-height: 1.6;
          font-size: 0.95rem;
          text-align: center;
        }

        .legal-disclaimer {
          background: rgba(255, 23, 68, 0.1);
          padding: 1.5rem;
          border-radius: 12px;
          border-left: 4px solid #ff1744;
          margin-top: 2rem;
        }

        .legal-disclaimer p {
          color: #e0d5e5;
          line-height: 1.7;
          font-size: 0.9rem;
          margin: 0;
        }

        .legal-disclaimer strong {
          color: #ff6b8a;
        }
      `}</style>
    </div>
  );
};

export default ShopPage;