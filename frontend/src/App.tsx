import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { AgentPage } from './pages/AgentPage';
import { AdminPage } from './pages/AdminPage';
import { SuperAdminPage } from './pages/SuperAdminPage';
import './index.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/agent" element={<AgentPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/super-admin" element={<SuperAdminPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
