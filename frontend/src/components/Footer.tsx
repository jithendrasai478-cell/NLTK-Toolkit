import { GraduationCap, Users, Star, ArrowUp } from 'lucide-react';
import { BrainLogo } from './BrainLogo';

export const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <footer className="relative w-full mt-6 overflow-hidden">
      {/* Organic Curved Wave Transition matching reference */}
      <div className="w-full leading-none -mb-[1px]">
        <svg
          viewBox="0 0 1440 80"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-12 sm:h-16 md:h-20"
          preserveAspectRatio="none"
        >
          {/* Lavender light wave 1 */}
          <path
            d="M0,45 C280,10 520,70 800,35 C1080,5 1320,60 1440,30 L1440,80 L0,80 Z"
            fill="#E9D5FF"
            fillOpacity="0.45"
          />
          {/* Violet wave 2 */}
          <path
            d="M0,55 C320,20 640,65 960,35 C1200,10 1360,50 1440,40 L1440,80 L0,80 Z"
            fill="#7C3AED"
            fillOpacity="0.3"
          />
          {/* Deep Navy/Purple Base */}
          <path
            d="M0,65 C340,30 680,75 1020,45 C1240,25 1380,55 1440,50 L1440,80 L0,80 Z"
            fill="#110B29"
          />
        </svg>
      </div>

      {/* Main Dark Footer Area */}
      <div className="bg-[#110B29] text-white pt-1 pb-6 sm:pb-7">
        <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-5 md:gap-4">
            
            {/* Left Brand info */}
            <div className="flex items-center gap-2.5">
              <BrainLogo size={32} monochrome />
              <div className="flex flex-col">
                <span className="text-sm sm:text-base font-extrabold tracking-tight text-white leading-tight">
                  NLTK Toolkit
                </span>
                <span className="text-[10px] font-medium text-slate-400 tracking-normal leading-none mt-0.5">
                  NLP for Everyone
                </span>
              </div>
            </div>

            {/* Center Stats */}
            <div className="flex items-center gap-5 sm:gap-7 lg:gap-8">
              {/* Stat 1: 50+ Tools & Examples */}
              <div className="flex items-center gap-2">
                <div className="p-1 rounded-md bg-white/5 text-indigo-300">
                  <GraduationCap className="w-4 h-4" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs sm:text-[13px] font-bold text-white leading-none">50+</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 leading-none">Tools & Examples</span>
                </div>
              </div>

              {/* Stat 2: 10K+ Happy Learners */}
              <div className="flex items-center gap-2">
                <div className="p-1 rounded-md bg-white/5 text-purple-300">
                  <Users className="w-4 h-4" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs sm:text-[13px] font-bold text-white leading-none">10K+</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 leading-none">Happy Learners</span>
                </div>
              </div>

              {/* Stat 3: 4.9/5 User Satisfaction */}
              <div className="flex items-center gap-2">
                <div className="p-1 rounded-md bg-white/5 text-amber-300">
                  <Star className="w-3.5 h-3.5 fill-amber-300" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs sm:text-[13px] font-bold text-white leading-none">4.9/5</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 leading-none">User Satisfaction</span>
                </div>
              </div>
            </div>

            {/* Right: Handwriting quote and Scroll to top button */}
            <div className="flex items-center gap-3">
              <span className="font-cursive text-slate-300 text-base sm:text-lg font-medium tracking-wide">
                Better Language Better Tomorrow ♡
              </span>

              {/* Scroll to Top Circle Button */}
              <button
                onClick={scrollToTop}
                aria-label="Scroll to top"
                className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-all duration-150 cursor-pointer hover:scale-105 active:scale-95"
              >
                <ArrowUp className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>
        </div>
      </div>
    </footer>
  );
};
