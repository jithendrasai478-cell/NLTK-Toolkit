import { Sparkles, Rocket, ArrowRight, Play } from 'lucide-react';
import hero3dScene from '../assets/hero-3d-scene.png';

interface HeroSectionProps {
  onStartExploring: () => void;
  onWatchDemo: () => void;
  onOpenCodeEditor: () => void;
}

export function HeroSection({
  onStartExploring,
  onWatchDemo,
  onOpenCodeEditor,
}: HeroSectionProps) {
  return (
    <section
      id="hero-section"
      className="relative pt-6 pb-8 md:pt-8 md:pb-12 overflow-hidden max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-4 items-center">

        {/* Left Column: Headline & Action Buttons */}
        <div className="lg:col-span-5 flex flex-col items-start text-left z-10">

          {/* Badge */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#F3E8FF]/80 dark:bg-purple-950/60 border border-purple-100/90 dark:border-purple-800/60 text-[#7C3AED] dark:text-purple-300 text-[11px] font-semibold mb-3.5">
            <Sparkles className="w-3.5 h-3.5 text-[#7C3AED] dark:text-purple-300" />
            <span>Learn &bull; Build &bull; Explore</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-[44px] font-extrabold text-[#0F172A] dark:text-white tracking-tight leading-[1.12] flex flex-col">
            <span>NLTK Toolkit</span>

            <span className="bg-gradient-to-r from-[#3B82F6] via-[#6366F1] to-[#9333EA] bg-clip-text text-transparent">
              Powerful NLP Tools
            </span>

            <span>for Everyone</span>
          </h1>

          {/* Subtitle */}
          <p className="mt-3.5 text-xs sm:text-[13px] text-slate-500 dark:text-slate-400 leading-relaxed max-w-sm sm:max-w-md font-normal">
            Explore, learn and experiment with Natural Language Processing using
            the NLTK Toolkit. From simple text analysis to advanced language
            models — all in one place.
          </p>

          {/* CTA Buttons */}
          <div className="mt-6 flex items-center gap-3 flex-wrap">

            {/* Start Exploring */}
            <button
              onClick={onStartExploring}
              className="group inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] hover:from-[#4F46E5] hover:to-[#7C3AED] shadow-md shadow-indigo-200/80 dark:shadow-indigo-950/50 active:scale-[0.98] transition-all duration-150 cursor-pointer"
            >
              <Rocket className="w-3.5 h-3.5 text-white/95" />

              <span>Start Exploring</span>

              <ArrowRight className="w-3 h-3 transition-transform duration-150 group-hover:translate-x-0.5" />
            </button>

            {/* Watch Demo */}
            <button
              onClick={onWatchDemo}
              className="group inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-slate-800 shadow-sm active:scale-[0.98] transition-all duration-150 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 text-indigo-500 fill-indigo-500 group-hover:scale-110 transition-transform" />

              <span>Watch Demo</span>
            </button>

          </div>
        </div>

        {/* Right Column: 3D Scene */}
        <div className="lg:col-span-7 relative flex justify-end items-center">
          <div
            onClick={onOpenCodeEditor}
            title="Click to interact with Python Code in NLTK"
            className="relative w-full cursor-pointer transition-transform duration-300 hover:scale-[1.008]"
          >
            <img
              src={hero3dScene}
              alt="NLTK Toolkit 3D Scene with Laptop, Code, Books, Mug, and NLP Badges"
              className="w-full h-auto object-contain select-none pointer-events-none"
            />
          </div>
        </div>

      </div>
    </section>
  );
}