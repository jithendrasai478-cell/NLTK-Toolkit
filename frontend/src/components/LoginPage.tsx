import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { BrainLogo } from './BrainLogo';
import { NLTK3DLogo } from './NLTK3DLogo';
import { LoginCard } from './LoginCard';

interface LoginPageProps {
  onLoginSuccess?: (user: any) => void;
  darkMode?: boolean;
  onToggleTheme?: () => void;
  initialMode?: 'login' | 'signup';
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLoginSuccess,
  darkMode = false,
  onToggleTheme,
  initialMode = 'login',
}) => {
  const handleSuccess = (user: any) => {
    if (onLoginSuccess) {
      onLoginSuccess(user);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-br from-[#F8FAFC] via-[#EEF2FF] to-[#FAF5FF] dark:from-slate-950 dark:via-[#0B0F19] dark:to-[#170E2B] text-slate-800 dark:text-slate-100 transition-colors duration-200 relative overflow-hidden select-none">
      
      {/* Soft Ambient Background Glow Blobs */}
      <div className="absolute top-[-80px] left-[-80px] w-96 h-96 bg-blue-400/15 dark:bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-[20%] right-[-100px] w-[450px] h-[450px] bg-purple-400/20 dark:bg-purple-600/15 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-100px] left-[30%] w-[500px] h-[400px] bg-indigo-300/15 dark:bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Floating Ambient Light Spheres (Matching Reference Image) */}
      <div className="hidden lg:block absolute top-[15%] left-[4%] w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-300/40 to-blue-400/40 blur-xs pointer-events-none animate-float shadow-inner" />
      <div className="hidden lg:block absolute top-[28%] left-[28%] w-5 h-5 rounded-full bg-gradient-to-tr from-purple-400/50 to-pink-300/40 blur-xs pointer-events-none animate-float-slow" style={{ animationDelay: '1s' }} />
      <div className="hidden lg:block absolute bottom-[22%] left-[20%] w-6 h-6 rounded-full bg-gradient-to-tr from-cyan-400/40 to-blue-500/40 blur-xs pointer-events-none animate-float" style={{ animationDelay: '2s' }} />
      <div className="hidden lg:block absolute top-[12%] right-[42%] w-7 h-7 rounded-full bg-gradient-to-tr from-purple-400/40 to-indigo-400/40 blur-xs pointer-events-none animate-float-slow" style={{ animationDelay: '1.5s' }} />
      <div className="hidden lg:block absolute bottom-[30%] right-[3%] w-12 h-12 rounded-full bg-gradient-to-tr from-purple-300/35 to-indigo-400/35 blur-xs pointer-events-none animate-float" style={{ animationDelay: '2.5s' }} />

      {/* Top Navigation Header */}
      <header className="relative z-30 w-full max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 flex items-center justify-between">
        
        {/* Left Brand: BrainLogo + NLTK Toolkit */}
        <div className="flex items-center gap-2.5 select-none">
          <BrainLogo size={36} />
          <div className="flex flex-col text-left">
            <span className="text-base sm:text-lg font-extrabold tracking-tight text-[#1E1B4B] dark:text-white leading-tight">
              NLTK Toolkit
            </span>
            <span className="text-[10px] sm:text-[11px] font-medium text-slate-500 dark:text-slate-400 tracking-normal leading-none mt-0.5">
              NLP for Everyone
            </span>
          </div>
        </div>

        {/* Right Header Controls: Tagline & Theme Toggle */}
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="hidden sm:flex items-center text-xs font-semibold text-slate-500 dark:text-slate-400 space-x-1.5">
            <span className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Learn</span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Build</span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Explore</span>
          </div>

          <div className="hidden sm:block h-4 w-px bg-slate-200 dark:bg-slate-800" />

          {/* Theme Toggle Button */}
          {onToggleTheme && (
            <button
              onClick={onToggleTheme}
              aria-label="Toggle theme"
              className="p-2 rounded-full text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 bg-white/70 dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-800 shadow-2xs hover:shadow-xs transition-all cursor-pointer"
            >
              {darkMode ? (
                <Moon className="w-4 h-4 text-indigo-400" />
              ) : (
                <Sun className="w-4 h-4 text-amber-500" />
              )}
            </button>
          )}
        </div>
      </header>

      {/* Main Split-Screen Container */}
      <main className="relative z-20 flex-grow w-full max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 flex items-center justify-center">
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-8 xl:gap-12 items-center">
          
          {/* LEFT COLUMN: 3D Animated NLP Brain Visual + Typography */}
          <div className="lg:col-span-7 flex flex-col items-center lg:items-start text-center lg:text-left space-y-4 sm:space-y-6">
            
            {/* 3D Animated Brain Scene with Floating Pills */}
            <div className="w-full flex justify-center">
              <NLTK3DLogo />
            </div>

            {/* Typography Hierarchy matching reference */}
            <div className="max-w-xl mx-auto lg:mx-0 space-y-2">
              <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-extrabold text-slate-900 dark:text-white tracking-tight leading-[1.15]">
                <span>Turn Words into </span>
                <span className="bg-gradient-to-r from-[#2563EB] via-[#6366F1] to-[#A855F7] bg-clip-text text-transparent">
                  Insights
                </span>
              </h1>

              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-normal max-w-lg">
                Explore the power of Natural Language Processing with NLTK. Learn, build and create amazing AI solutions &mdash; all in one place.
              </p>
            </div>
          </div>

          {/* RIGHT COLUMN: Modern Glassmorphism Login Card */}
          <div className="lg:col-span-5 flex justify-center w-full">
            <LoginCard
              initialMode={initialMode}
              onSuccess={handleSuccess}
            />
          </div>

        </div>
      </main>

      {/* Footer Branding & Subtle Cursive Accent */}
      <footer className="relative z-20 w-full max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 dark:text-slate-500 gap-2">
        <div>
          &copy; {new Date().getFullYear()} NLTK Toolkit. All rights reserved.
        </div>

        {/* Decorative Handwriting/Cursive Signature from Mockup */}
        <div className="text-right font-cursive text-base sm:text-lg text-indigo-500/70 dark:text-indigo-400/60 tracking-wide select-none">
          Better Language &bull; Better Future
        </div>
      </footer>

    </div>
  );
};
