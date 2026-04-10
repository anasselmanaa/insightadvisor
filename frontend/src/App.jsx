import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Login from './pages/Login'
import Landing from './pages/Landing'
import Register from './pages/Register'
import Upload from './pages/Upload'
import Dashboard from './pages/Dashboard'
import Clustering from './pages/Clustering'
import Forecasting from './pages/Forecasting'
import Regression from './pages/Regression'
import Apriori from './pages/Apriori'
import Anomaly from './pages/Anomaly'
import Stock from './pages/Stock'
import AICopilot from './pages/AICopilot'
import Reports from './pages/Reports'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/landing"  element={<Landing />} />
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index                element={<Upload />} />
          <Route path="dashboard"     element={<Dashboard />} />
          <Route path="clustering"    element={<Clustering />} />
          <Route path="forecasting"   element={<Forecasting />} />
          <Route path="regression"    element={<Regression />} />
          <Route path="apriori"       element={<Apriori />} />
          <Route path="anomaly"       element={<Anomaly />} />
          <Route path="stock"         element={<Stock />} />
          <Route path="ai-copilot"    element={<AICopilot />} />
          <Route path="reports"       element={<Reports />} />
        </Route>
      </Routes>
    </>
  )
}
