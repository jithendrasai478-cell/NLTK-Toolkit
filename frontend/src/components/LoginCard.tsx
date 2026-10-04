import React, { useState, useRef, useEffect } from 'react';
import { Mail, Lock, User, ArrowRight, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';
import { AuthInput } from './AuthInput';
import { loginUser, registerUser, googleLogin } from '../services/apiClient';

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (parent: HTMLElement, options: any) => void;
          prompt: (momentListener?: (notification: any) => void) => void;
          cancel: () => void;
        };
      };
    };
  }
}

interface LoginCardProps {
  initialMode?: 'login' | 'signup';
  onSuccess: (user: any) => void;
  onModeChange?: (mode: 'login' | 'signup') => void;
}

export const LoginCard: React.FC<LoginCardProps> = ({
  initialMode = 'login',
  onSuccess,
  onModeChange,
}) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isGisReady, setIsGisReady] = useState(false);
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotSent, setForgotSent] = useState(false);

  const googleBtnRef = useRef<HTMLDivElement>(null);
  const gisInitializedRef = useRef(false);
  const isGoogleLoadingRef = useRef(false);
  isGoogleLoadingRef.current = isGoogleLoading;

  const setupGIS = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID' || !window.google?.accounts?.id || !googleBtnRef.current) {
      return;
    }
    if (gisInitializedRef.current) return;
    gisInitializedRef.current = true;

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
        use_fedcm_for_prompt: false,
      });
      gisInitializedRef.current = true;

      googleBtnRef.current.innerHTML = '';
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        width: 250,
        click_listener: () => {
          setIsGoogleLoading(true);
          setGeneralError(null);
          setSuccessMessage(null);
        },
      });
      setIsGisReady(true);
    } catch (err: any) {
      console.warn('Google Identity Services init warning:', err);
    }
  };

  // Initialize Google Identity Services (GIS)
  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID') {
      return;
    }

    if (window.google?.accounts?.id) {
      setupGIS();
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          setupGIS();
        }
      }, 200);
      return () => clearInterval(interval);
    }
  }, []);

  // Detect popup closure or cancellation via window focus
  useEffect(() => {
    const handleFocus = () => {
      if (isGoogleLoadingRef.current) {
        setTimeout(() => {
          if (isGoogleLoadingRef.current) {
            setIsGoogleLoading(false);
            setGeneralError('Google sign-in was cancelled or closed.');
          }
        }, 2200);
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  const handleGoogleCredentialResponse = async (response: any) => {
    setIsGoogleLoading(true);
    setGeneralError(null);
    setSuccessMessage(null);

    try {
      if (!response || !response.credential) {
        setGeneralError('No valid Google credential received. Please try again.');
        return;
      }

      const res = await googleLogin(response.credential);
      if (res.success && res.data) {
        localStorage.setItem('nltk_token', res.data.access_token);
        localStorage.setItem('nltk_user', JSON.stringify(res.data.user));
        const displayName = res.data.user.display_name || res.data.user.username;
        setSuccessMessage(`Welcome, ${displayName}!`);
        setTimeout(() => {
          onSuccess(res.data.user);
        }, 600);
      } else {
        const errorText = res.error?.message || res.message || 'Google authentication failed on server. Please try again.';
        console.warn('Google login failed on server:', res);
        setGeneralError(errorText);
      }
    } catch (err: any) {
      console.error('Unexpected error in Google credential response:', err);
      setGeneralError('An unexpected error occurred while contacting the server. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGoogleButtonClick = () => {
    setGeneralError(null);
    setSuccessMessage(null);
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID') {
      setGeneralError('Google Client ID is not configured. Please set VITE_GOOGLE_CLIENT_ID in your .env file.');
      return;
    }

    if (!window.google?.accounts?.id) {
      setGeneralError('Google Sign-In is initializing. Please wait a moment and try again.');
      return;
    }

    if (!isGisReady) {
      setupGIS();
    }

    // Task 6: Do NOT show "Google sign-in prompt was suppressed" as a fatal error!
    // One Tap is an optional helper; suppression is normal and not a failure.
    try {
      window.google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          setIsGoogleLoading(false);
          const reason = notification.getNotDisplayedReason?.() || notification.getSkippedReason?.() || 'prompt_not_displayed';
          console.debug('Google One Tap notice (non-fatal):', reason);
        }
      });
    } catch (err: any) {
      setIsGoogleLoading(false);
      console.debug('Google prompt error (non-fatal):', err);
    }
  };

  const toggleMode = (newMode: 'login' | 'signup') => {
    setMode(newMode);
    setErrors({});
    setGeneralError(null);
    setSuccessMessage(null);
    if (onModeChange) onModeChange(newMode);
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!email.trim()) {
      newErrors.email = 'Please enter your email address.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = 'Please enter a valid email address.';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required.';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    // Signup specific validation
    if (mode === 'signup') {
      if (!username.trim()) {
        newErrors.username = 'Username is required.';
      } else if (username.trim().length < 3) {
        newErrors.username = 'Username must be at least 3 characters.';
      }

      if (password !== confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match.';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setSuccessMessage(null);

    if (!validate()) return;

    setIsLoading(true);

    try {
      if (mode === 'login') {
        const res = await loginUser(email.trim(), password);
        if (res.success && res.data) {
          localStorage.setItem('nltk_token', res.data.access_token);
          localStorage.setItem('nltk_user', JSON.stringify(res.data.user));
          setSuccessMessage(`Welcome back, ${res.data.user.username}!`);
          setTimeout(() => {
            onSuccess(res.data.user);
          }, 800);
        } else {
          setGeneralError('Invalid email or password.');
        }
      } else {
        // Register
        const regUsername = username.trim() || email.trim().split('@')[0];
        const res = await registerUser(regUsername, email.trim(), password);
        if (res.success && res.data) {
          localStorage.setItem('nltk_token', res.data.access_token);
          localStorage.setItem('nltk_user', JSON.stringify(res.data.user));
          setSuccessMessage(`Account created! Welcome to NLTK Toolkit, ${res.data.user.username}!`);
          setTimeout(() => {
            onSuccess(res.data.user);
          }, 1000);
        } else {
          setGeneralError(res.error?.message || 'Failed to create account. Please try again.');
        }
      }
    } catch (err: any) {
      setGeneralError(err.message || 'An unexpected network error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    if (provider === 'Google') {
      handleGoogleButtonClick();
      return;
    }
    setGeneralError(`${provider} authentication is coming soon in the next release! Please log in with your email or Google.`);
  };

  const handleForgotSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(forgotEmail)) return;
    setForgotSent(true);
    setTimeout(() => {
      setShowForgotModal(false);
      setForgotSent(false);
      setForgotEmail('');
    }, 2500);
  };

  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Soft Decorative Ambient Glow */}
      <div className="absolute -inset-1.5 bg-gradient-to-r from-blue-500/20 via-indigo-500/25 to-purple-500/20 rounded-[32px] blur-xl opacity-75 pointer-events-none" />

      {/* Main Glassmorphism Card */}
      <div className="relative bg-white/85 dark:bg-slate-900/85 backdrop-blur-xl border border-white/60 dark:border-slate-800/80 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-indigo-950/10 text-slate-800 dark:text-slate-100 transition-all duration-200">
        
        {/* Top Header Badge */}
        <div className="flex items-center justify-start mb-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-100 dark:border-indigo-800/70 text-indigo-600 dark:text-indigo-300 text-[11px] font-semibold">
            <Sparkles className="w-3 h-3 text-indigo-500 dark:text-indigo-400" />
            <span>Welcome to NLTK Toolkit</span>
          </div>
        </div>

        {/* Card Title & Subtitle */}
        <div className="mb-6 text-left">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <span>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</span>
            <span className="text-2xl">{mode === 'login' ? '👋' : '🚀'}</span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
            {mode === 'login'
              ? 'Sign in to continue your NLP journey'
              : 'Join developers and researchers using modern NLTK tools'}
          </p>
        </div>

        {/* Global Error Notice */}
        {generalError && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 text-xs flex items-start gap-2 animate-fadeIn text-left">
            <span className="text-sm mt-0.5">⚠️</span>
            <span className="leading-snug">{generalError}</span>
          </div>
        )}

        {/* Global Success Notice */}
        {successMessage && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn text-left font-medium">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          {mode === 'signup' && (
            <AuthInput
              id="auth-username"
              name="username"
              label="Username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. nlpdeveloper"
              icon={User}
              error={errors.username}
              required
              autoComplete="username"
              disabled={isLoading}
            />
          )}

          <AuthInput
            id="auth-email"
            name="email"
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email address"
            icon={Mail}
            error={errors.email}
            required
            autoComplete="email"
            disabled={isLoading}
          />

          <AuthInput
            id="auth-password"
            name="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            icon={Lock}
            error={errors.password}
            required
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            disabled={isLoading}
          />

          {mode === 'signup' && (
            <AuthInput
              id="auth-confirm-password"
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat your password"
              icon={Lock}
              error={errors.confirmPassword}
              required
              autoComplete="new-password"
              disabled={isLoading}
            />
          )}

          {/* Forgot Password Link (Login only) */}
          {mode === 'login' && (
            <div className="flex justify-end pt-0.5">
              <button
                type="button"
                onClick={() => setShowForgotModal(true)}
                className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:underline transition-colors cursor-pointer"
              >
                Forgot password?
              </button>
            </div>
          )}

          {/* Primary Action Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full group mt-2 py-3 sm:py-3.5 px-4 rounded-xl sm:rounded-2xl text-xs sm:text-sm font-semibold text-white bg-gradient-to-r from-[#2563EB] via-[#6366F1] to-[#8B5CF6] hover:from-[#1D4ED8] hover:via-[#4F46E5] hover:to-[#7C3AED] shadow-lg shadow-indigo-500/25 active:scale-[0.98] disabled:opacity-70 disabled:pointer-events-none transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>{mode === 'login' ? 'Signing in...' : 'Creating account...'}</span>
              </>
            ) : (
              <>
                <span>{mode === 'login' ? 'Login' : 'Create Account'}</span>
                <ArrowRight className="w-4 h-4 transition-transform duration-150 group-hover:translate-x-1" />
              </>
            )}
          </button>
        </form>

        {/* Divider: "or continue with" */}
        <div className="relative my-6 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200 dark:border-slate-800" />
          </div>
          <div className="relative bg-white/90 dark:bg-slate-900/90 px-3 text-[11px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider rounded-full backdrop-blur-xs">
            or continue with
          </div>
        </div>

        {/* Social Login Buttons: Google and GitHub */}
        <div className="grid grid-cols-2 gap-3">
          {/* Real Google Identity Services Button Container */}
          <div className="relative overflow-hidden rounded-xl sm:rounded-2xl group/google">
            <button
              type="button"
              id="google-signin-btn"
              onClick={() => handleSocialLogin('Google')}
              disabled={isLoading || isGoogleLoading}
              className="w-full flex items-center justify-center gap-2.5 py-2.5 px-3 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 shadow-2xs hover:shadow-xs active:scale-[0.98] transition-all cursor-pointer disabled:opacity-75 disabled:pointer-events-none"
            >
              {isGoogleLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-500 shrink-0" />
                  <span className="truncate">Connecting to Google...</span>
                </>
              ) : (
                <>
                  {/* Google Multicolor SVG */}
                  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.67v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.16z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.26v3.15C3.25 21.36 7.33 24 12 24z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.26C.46 8.17 0 9.99 0 12s.46 3.83 1.26 5.42l4.02-3.15z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.25 2.64 1.26 6.58l4.02 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                    />
                  </svg>
                  <span>Google</span>
                </>
              )}
            </button>

            {/* Invisible Google Identity Services Button Overlay */}
            <div
              ref={googleBtnRef}
              id="google-gis-button-wrapper"
              onClick={handleGoogleButtonClick}
              className="absolute inset-0 z-10 w-full h-full overflow-hidden cursor-pointer flex items-center justify-center transform scale-110"
              style={{
                opacity: 0.001,
                pointerEvents: (isLoading || isGoogleLoading) ? 'none' : 'auto'
              }}
              title="Sign in with Google"
            />
          </div>

          {/* GitHub Button */}
          <button
            type="button"
            onClick={() => handleSocialLogin('GitHub')}
            className="flex items-center justify-center gap-2.5 py-2.5 px-3 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 shadow-2xs hover:shadow-xs active:scale-[0.98] transition-all cursor-pointer"
          >
            {/* GitHub SVG */}
            <svg className="w-4 h-4 shrink-0 fill-current text-slate-900 dark:text-white" viewBox="0 0 24 24">
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              />
            </svg>
            <span>GitHub</span>
          </button>
        </div>

        {/* Footer: Toggle Mode */}
        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800/80 text-center">
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {mode === 'login' ? (
              <>
                <span>Don't have an account? </span>
                <button
                  type="button"
                  onClick={() => toggleMode('signup')}
                  className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:underline transition-colors cursor-pointer"
                >
                  Create an account &rarr;
                </button>
              </>
            ) : (
              <>
                <span>Already have an account? </span>
                <button
                  type="button"
                  onClick={() => toggleMode('login')}
                  className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:underline transition-colors cursor-pointer"
                >
                  Sign in &rarr;
                </button>
              </>
            )}
          </p>
        </div>

      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-fadeIn">
          <div className="relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 text-left">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Reset Password</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Enter your email address and we'll send you a password recovery link.
            </p>

            {forgotSent ? (
              <div className="my-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Reset link sent! Please check your inbox.</span>
              </div>
            ) : (
              <form onSubmit={handleForgotSubmit} className="mt-4 space-y-3">
                <AuthInput
                  id="forgot-email"
                  name="forgotEmail"
                  label="Email Address"
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  placeholder="Enter your email"
                  icon={Mail}
                  required
                />
                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowForgotModal(false)}
                    className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-full shadow-xs transition-colors cursor-pointer"
                  >
                    Send Link
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
