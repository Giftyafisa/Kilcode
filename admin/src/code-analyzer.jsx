import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './pages/CodeAnalyzer/App';
import { CodeAnalyzerAuthProvider } from './context/CodeAnalyzerAuthContext';
import './index.css';
import './styles/tailwind.css';
import './styles/toast.css';

// Initialize any required services or configurations
const init = () => {
  console.log('Code Analyzer Portal initialized');
};

init();

// Create root element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the app
root.render(
  <React.StrictMode>
    <BrowserRouter basename="/code-analyzer">
      <CodeAnalyzerAuthProvider>
        <Toaster 
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <App />
      </CodeAnalyzerAuthProvider>
    </BrowserRouter>
  </React.StrictMode>
); 