import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import '@/App.css';
import LandingPage from '@/pages/LandingPage';
import BlogHomePage from '@/pages/BlogHomePage';
import BlogPage from '@/pages/BlogPage';
import ShopPage from '@/pages/ShopPage';
import CheckoutPage from '@/pages/CheckoutPage';
import PaymentSuccess from '@/pages/PaymentSuccess';
import PaymentCancel from '@/pages/PaymentCancel';
import Impressum from '@/pages/Impressum';
import Privacy from '@/pages/Privacy';
import Terms from '@/pages/Terms';
import AdminLogin from '@/pages/AdminLogin';
import AdminDashboard from '@/pages/AdminDashboard';
import AdminSettings from '@/pages/AdminSettings';
import AdminCoupons from '@/pages/AdminCoupons';
import AdminProducts from '@/pages/AdminProducts';
import AdminOrders from '@/pages/AdminOrders';
import CommunityProjectsPage from '@/pages/CommunityProjectsPage';
import CreateBlog from '@/pages/CreateBlog';
import EditBlog from '@/pages/EditBlog';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/blog" element={<BlogHomePage />} />
          <Route path="/blog/:id" element={<BlogPage />} />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/community" element={<CommunityProjectsPage />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/cancel" element={<PaymentCancel />} />
          <Route path="/impressum" element={<Impressum />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/shroomsadmin" element={<AdminLogin />} />
          <Route path="/shroomsadmin/dashboard" element={<AdminDashboard />} />
          <Route path="/shroomsadmin/settings" element={<AdminSettings />} />
          <Route path="/shroomsadmin/coupons" element={<AdminCoupons />} />
          <Route path="/shroomsadmin/products" element={<AdminProducts />} />
          <Route path="/shroomsadmin/orders" element={<AdminOrders />} />
          <Route path="/shroomsadmin/create" element={<CreateBlog />} />
          <Route path="/shroomsadmin/edit/:id" element={<EditBlog />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;