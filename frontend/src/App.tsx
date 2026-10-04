import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { FeatureGrid } from './components/FeatureGrid';
import { HowItWorks } from './components/HowItWorks';
import { Footer } from './components/Footer';
import { InteractiveModal } from './components/InteractiveModal';
import { DemoModal } from './components/DemoModal';
import { LoginPage } from './components/LoginPage';
import type { FeatureItem } from './data/features';
import { featuresData } from './data/features';

export function App() {
  const [currentUser, setCurrentUser] = useState<any>(() => {
    try {
      const saved = localStorage.getItem('nltk_user');
      const token = localStorage.getItem('nltk_token');
      return (saved && token) ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [currentPath, setCurrentPath] = useState<string>(() => {
    try {
      const saved = localStorage.getItem('nltk_user');
      const token = localStorage.getItem('nltk_token');
      const isAuth = Boolean(saved && token);
      const rawPath = window.location.pathname || '/';

      if (!isAuth && rawPath !== '/login' && rawPath !== '/signup') {
        window.history.replaceState({}, '', '/login');
        return '/login';
      }
      if (isAuth && (rawPath === '/login' || rawPath === '/signup')) {
        window.history.replaceState({}, '', '/');
        return '/';
      }
      return rawPath;
    } catch {
      return '/login';
    }
  });

  const [selectedFeature, setSelectedFeature] = useState<FeatureItem | null>(null);
  const [demoOpen, setDemoOpen] = useState(false);

  const [darkMode, setDarkMode] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('nltk_theme');
      if (saved) return saved === 'dark';
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch {
      return false;
    }
  });

  // Listen to browser Back/Forward navigation & protect routes
  useEffect(() => {
    const handlePopState = () => {
      const rawPath = window.location.pathname || '/';
      const token = localStorage.getItem('nltk_token');
      const user = localStorage.getItem('nltk_user');
      const isAuth = Boolean(token && user);

      if (!isAuth && rawPath !== '/login' && rawPath !== '/signup') {
        window.history.replaceState({}, '', '/login');
        setCurrentPath('/login');
        return;
      }

      if (isAuth && (rawPath === '/login' || rawPath === '/signup')) {
        window.history.replaceState({}, '', '/');
        setCurrentPath('/');
        return;
      }

      setCurrentPath(rawPath);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Sync auth state across tabs and enforce protected routes
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'nltk_token' || e.key === 'nltk_user') {
        const token = localStorage.getItem('nltk_token');
        const user = localStorage.getItem('nltk_user');
        if (!token || !user) {
          setCurrentUser(null);
          window.history.replaceState({}, '', '/login');
          setCurrentPath('/login');
        } else {
          try {
            setCurrentUser(JSON.parse(user));
          } catch {}
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Enforce route protection whenever path or auth state changes
  useEffect(() => {
    const token = localStorage.getItem('nltk_token');
    const user = localStorage.getItem('nltk_user');
    const isAuth = Boolean(token && user && currentUser);

    if (!isAuth && currentPath !== '/login' && currentPath !== '/signup') {
      window.history.replaceState({}, '', '/login');
      setCurrentPath('/login');
    } else if (isAuth && (currentPath === '/login' || currentPath === '/signup')) {
      window.history.replaceState({}, '', '/');
      setCurrentPath('/');
    }
  }, [currentPath, currentUser]);

  // Handle section scrolling when navigating directly to sections
  useEffect(() => {
    if (currentUser) {
      if (currentPath === '/tools') {
        setTimeout(() => {
          document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } else if (currentPath === '/examples') {
        setTimeout(() => {
          document.getElementById('hero-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } else if (currentPath === '/documentation' || currentPath === '/resources') {
        setTimeout(() => {
          document.getElementById('how-it-works-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    }
  }, [currentPath, currentUser]);

  const navigate = (path: string, replace = false) => {
    try {
      if (replace) {
        window.history.replaceState({}, '', path);
      } else {
        window.history.pushState({}, '', path);
      }
    } catch {}
    setCurrentPath(path);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      try {
        localStorage.setItem('nltk_theme', 'dark');
      } catch {}
    } else {
      document.documentElement.classList.remove('dark');
      try {
        localStorage.setItem('nltk_theme', 'light');
      } catch {}
    }
  }, [darkMode]);

  const handleSearch = (query: string) => {
    if (query.trim().length > 1) {
      const match = featuresData.find(f => 
        f.title.toLowerCase().includes(query.toLowerCase()) || 
        f.description.toLowerCase().includes(query.toLowerCase())
      );
      if (match) {
        document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const handleToggleTheme = () => {
    setDarkMode(prev => !prev);
  };

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleLoginSuccess = (user: any) => {
    setCurrentUser(user);
    window.history.replaceState({}, '', '/');
    setCurrentPath('/');
    setTimeout(() => {
      document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 150);
  };

  const handleLogout = () => {
    try {
      localStorage.removeItem('nltk_token');
      localStorage.removeItem('nltk_user');
    } catch {}
    setCurrentUser(null);
    setSelectedFeature(null);
    setDemoOpen(false);
    // Immediately redirect to /login and replace history entry so Back does not show protected page
    window.history.replaceState({}, '', '/login');
    setCurrentPath('/login');
    window.scrollTo({ top: 0, behavior: 'instant' });
  };

  const handleStartExploring = () => {
    setSelectedFeature(featuresData[0]); // Open Summarize tool preview
  };

  const handleOpenCodeEditor = () => {
    setSelectedFeature(featuresData[featuresData.length - 1]); // Open More Tools / Tokenizer interactive preview
  };

  // Dedicated Login / Signup Route
  if (currentPath === '/login' || currentPath === '/signup') {
    return (
      <div className={darkMode ? 'dark' : ''}>
        <LoginPage
          initialMode={currentPath === '/signup' ? 'signup' : 'login'}
          onLoginSuccess={handleLoginSuccess}
          darkMode={darkMode}
          onToggleTheme={handleToggleTheme}
        />
      </div>
    );
  }

  // Standard Homepage Route (/)
  return (
    <div className={`min-h-screen flex flex-col bg-[#F8FAFC] dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors duration-200 ${darkMode ? 'dark' : ''}`}>
      {/* Top Navigation Bar */}
      <Navbar 
        onSearch={handleSearch}
        onGetStarted={handleGetStarted}
        onLogin={() => navigate('/login')}
        currentUser={currentUser}
        onLogout={handleLogout}
        darkMode={darkMode}
        onToggleTheme={handleToggleTheme}
      />

      {/* Main Content Area */}
      <main className="flex-grow">
        {/* Hero Section */}
        <HeroSection 
          onStartExploring={handleStartExploring}
          onWatchDemo={() => setDemoOpen(true)}
          onOpenCodeEditor={handleOpenCodeEditor}
        />

        {/* 8 Feature Cards Grid ("WHY CHOOSE US" / "Everything You Need for NLP") */}
        <FeatureGrid 
          onSelectFeature={(feature) => setSelectedFeature(feature)} 
        />

        {/* 3-step "How It Works" Section */}
        <HowItWorks />
      </main>

      {/* Footer with wave divider, brand, stats & handwriting quote */}
      <Footer />

      {/* Modals */}
      <InteractiveModal 
        feature={selectedFeature} 
        onClose={() => setSelectedFeature(null)} 
      />

      <DemoModal 
        isOpen={demoOpen} 
        onClose={() => setDemoOpen(false)} 
      />
    </div>
  );
}

export default App;
