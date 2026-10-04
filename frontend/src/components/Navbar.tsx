import { useState, type ChangeEvent } from 'react';
import { Search, Sun, Moon, ArrowRight, Menu, X, User, LogOut } from 'lucide-react';
import { BrainLogo } from './BrainLogo';

interface NavbarProps {
  onSearch?: (query: string) => void;
  onGetStarted?: () => void;
  onLogin?: () => void;
  currentUser?: { username: string; email: string } | null;
  onLogout?: () => void;
  darkMode?: boolean;
  onToggleTheme?: () => void;
}

export const Navbar = ({
  onSearch,
  onGetStarted,
  onLogin,
  currentUser,
  onLogout,
  darkMode = false,
  onToggleTheme,
}: NavbarProps) => {
  const [activeTab, setActiveTab] = useState('Home');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchVal, setSearchVal] = useState('');

  const navItems = ['Home', 'Tools', 'Examples', 'Documentation', 'Resources'];

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchVal(e.target.value);
    if (onSearch) onSearch(e.target.value);
  };

  const scrollToSection = (tab: string) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
    if (tab === 'Home') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tab === 'Tools') {
      document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' });
    } else if (tab === 'Examples') {
      document.getElementById('hero-section')?.scrollIntoView({ behavior: 'smooth' });
    } else if (tab === 'Documentation' || tab === 'Resources') {
      document.getElementById('how-it-works-section')?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 dark:bg-slate-950/90 backdrop-blur-md border-b border-slate-100 dark:border-slate-800/80 transition-colors">
      <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16">
          
          {/* Left Brand Logo */}
          <div 
            onClick={() => scrollToSection('Home')}
            className="flex items-center gap-2.5 cursor-pointer group select-none"
          >
            <BrainLogo size={34} />
            <div className="flex flex-col">
              <span className="text-base font-extrabold tracking-tight text-[#1E1B4B] dark:text-white leading-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                NLTK Toolkit
              </span>
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400 tracking-normal leading-none mt-0.5">
                NLP for Everyone
              </span>
            </div>
          </div>

          {/* Desktop Center Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => {
              const isActive = activeTab === item;
              return (
                <button
                  key={item}
                  onClick={() => scrollToSection(item)}
                  className={`px-3 py-1 rounded-full text-[13px] font-medium transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-[#EEF2FF] dark:bg-indigo-950/80 text-[#4338CA] dark:text-indigo-300 font-semibold shadow-2xs'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800/60'
                  }`}
                >
                  {item}
                </button>
              );
            })}
          </nav>

          {/* Right Action Items */}
          <div className="hidden sm:flex items-center gap-3">
            {/* Search Input */}
            <div className="relative flex items-center">
              <Search className="absolute left-2.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchVal}
                onChange={handleSearchChange}
                placeholder="Search tools, examples..."
                className="w-44 lg:w-52 pl-7 pr-3 py-1.5 text-xs text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 bg-white dark:bg-slate-900 rounded-full border border-slate-200/90 dark:border-slate-800 shadow-2xs hover:border-slate-300 dark:hover:border-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-all"
              />
            </div>

            {/* Sun / Theme Toggle */}
            <button
              onClick={onToggleTheme}
              aria-label="Toggle theme"
              className="p-1.5 text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors cursor-pointer"
            >
              {darkMode ? (
                <Moon className="w-4 h-4 text-indigo-400" />
              ) : (
                <Sun className="w-4 h-4 text-slate-600" />
              )}
            </button>

            {currentUser ? (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-200 dark:border-indigo-800 text-xs font-semibold text-indigo-700 dark:text-indigo-300">
                  <User className="w-3.5 h-3.5" />
                  <span className="max-w-[100px] truncate">{currentUser.username}</span>
                </div>
                {onLogout && (
                  <button
                    onClick={onLogout}
                    title="Sign Out"
                    className="p-1.5 text-slate-400 hover:text-red-500 rounded-full hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ) : (
              <>
                <button
                  onClick={onLogin || onGetStarted}
                  className="text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-2.5 py-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors cursor-pointer"
                >
                  Sign In
                </button>
                <button
                  onClick={onGetStarted}
                  className="group inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#7C3AED] hover:from-[#5457E5] hover:to-[#6D28D9] shadow-xs active:scale-[0.98] transition-all duration-150 cursor-pointer"
                >
                  <span>Get Started</span>
                  <ArrowRight className="w-3 h-3 transition-transform duration-150 group-hover:translate-x-0.5" />
                </button>
              </>
            )}
          </div>

          {/* Mobile Hamburger Toggle */}
          <div className="flex items-center gap-2 sm:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white rounded-lg focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 pt-3 pb-4 space-y-2">
          <div className="relative flex items-center mb-2">
            <Search className="absolute left-3 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              value={searchVal}
              onChange={handleSearchChange}
              placeholder="Search tools, examples..."
              className="w-full pl-8 pr-3 py-1.5 text-xs text-slate-700 dark:text-slate-200 bg-slate-50 dark:bg-slate-900 rounded-full border border-slate-200 dark:border-slate-800"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            {navItems.map((item) => (
              <button
                key={item}
                onClick={() => scrollToSection(item)}
                className={`text-left px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  activeTab === item
                    ? 'bg-[#EEF2FF] dark:bg-indigo-950/80 text-[#4338CA] dark:text-indigo-300'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                {item}
              </button>
            ))}
          </div>
          {currentUser ? (
            <div className="flex items-center justify-between p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                <span className="text-xs font-semibold text-indigo-900 dark:text-indigo-200">{currentUser.username}</span>
              </div>
              {onLogout && (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onLogout();
                  }}
                  className="text-xs text-red-500 font-medium px-2 py-1 rounded-md hover:bg-red-50 dark:hover:bg-red-950"
                >
                  Sign Out
                </button>
              )}
            </div>
          ) : (
            <div className="flex gap-2 pt-1">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onLogin) onLogin();
                  else if (onGetStarted) onGetStarted();
                }}
                className="flex-1 py-2 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-center"
              >
                Sign In
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onGetStarted) onGetStarted();
                }}
                className="flex-1 py-2 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#7C3AED] flex items-center justify-center gap-1.5"
              >
                <span>Get Started</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
