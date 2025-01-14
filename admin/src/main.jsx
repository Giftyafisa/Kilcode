import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import CodeAnalyzerApp from './pages/CodeAnalyzer/App'
import './index.css'

// Determine which app to render based on the route
const isCodeAnalyzerRoute = window.location.pathname.startsWith('/code-analyzer');
const AppComponent = isCodeAnalyzerRoute ? CodeAnalyzerApp : App;

// Initialize the appropriate app
if (isCodeAnalyzerRoute) {
  console.log('Initializing Code Analyzer Portal');
  import('./styles/tailwind.css');
  import('./styles/toast.css');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppComponent />
  </React.StrictMode>,
) 