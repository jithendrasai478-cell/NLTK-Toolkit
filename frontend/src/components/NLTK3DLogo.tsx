import React, { useState, useRef } from 'react';
import {
  FileText,
  Smile,
  Network,
  ListFilter,
  Tag,
  Languages,
  MessageSquare,
  HelpCircle,
} from 'lucide-react';
import loginBrainImg from '../assets/login-3d-brain.png';

interface NlpPill {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  position: string; // Tailwind absolute position
  gradient: string;
  glowColor: string;
  delay: string;
  description: string;
}

const NLP_PILLS: NlpPill[] = [
  {
    id: 'tokenization',
    title: 'Tokenization',
    icon: FileText,
    position: 'top-[8%] left-[6%] sm:top-[10%] sm:left-[10%]',
    gradient: 'from-cyan-500/80 to-blue-600/90',
    glowColor: 'shadow-cyan-500/30',
    delay: '0s',
    description: 'Split texts into words, sentences & subwords',
  },
  {
    id: 'sentiment',
    title: 'Sentiment',
    icon: Smile,
    position: 'top-[6%] right-[8%] sm:top-[8%] sm:right-[14%]',
    gradient: 'from-purple-500/80 to-pink-500/90',
    glowColor: 'shadow-purple-500/30',
    delay: '0.6s',
    description: 'VADER & neural polarity detection',
  },
  {
    id: 'nlp',
    title: 'NLP',
    icon: MessageSquare,
    position: 'top-[26%] left-[2%] sm:top-[28%] sm:left-[5%]',
    gradient: 'from-blue-600/85 to-indigo-600/90',
    glowColor: 'shadow-blue-500/30',
    delay: '1.2s',
    description: 'Natural language processing core pipelines',
  },
  {
    id: 'classification',
    title: 'Classification',
    icon: Network,
    position: 'top-[22%] right-[2%] sm:top-[24%] sm:right-[6%]',
    gradient: 'from-indigo-600/85 to-purple-600/90',
    glowColor: 'shadow-indigo-500/30',
    delay: '1.8s',
    description: 'Multinomial Logistic Regression & topics',
  },
  {
    id: 'keywords',
    title: 'Keywords',
    icon: Tag,
    position: 'top-[42%] left-[4%] sm:top-[44%] sm:left-[8%]',
    gradient: 'from-violet-600/85 to-purple-700/90',
    glowColor: 'shadow-violet-500/30',
    delay: '0.9s',
    description: 'TF-IDF & TextRank salient keyphrases',
  },
  {
    id: 'translation',
    title: 'Translation',
    icon: Languages,
    position: 'top-[38%] right-[4%] sm:top-[40%] sm:right-[8%]',
    gradient: 'from-purple-600/85 to-pink-600/90',
    glowColor: 'shadow-purple-500/30',
    delay: '1.5s',
    description: 'Multilingual NLLB neural translation',
  },
  {
    id: 'summarization',
    title: 'Summarization',
    icon: ListFilter,
    position: 'bottom-[34%] left-[16%] sm:bottom-[36%] sm:left-[20%]',
    gradient: 'from-indigo-700/85 to-blue-700/90',
    glowColor: 'shadow-indigo-500/30',
    delay: '2.1s',
    description: 'Extractive graph centrality summaries',
  },
  {
    id: 'qa',
    title: 'Q&A',
    icon: HelpCircle,
    position: 'bottom-[32%] right-[16%] sm:bottom-[34%] right-[20%]',
    gradient: 'from-sky-500/85 to-indigo-600/90',
    glowColor: 'shadow-sky-500/30',
    delay: '0.3s',
    description: 'RoBERTa SQuAD2 extractive question answering',
  },
];

export const NLTK3DLogo: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [rotate, setRotate] = useState({ x: 0, y: 0 });
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setRotate({ x: x * 8, y: -y * 8 });
  };

  const handleMouseLeave = () => {
    setRotate({ x: 0, y: 0 });
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative w-full max-w-[540px] mx-auto aspect-[4/3.2] flex items-center justify-center select-none"
      style={{ perspective: '1200px' }}
    >
      {/* Dynamic 3D Scene Wrapper with Tilt Parallax */}
      <div
        className="relative w-full h-full flex items-center justify-center transition-transform duration-300 ease-out"
        style={{
          transform: `rotateY(${rotate.x}deg) rotateX(${rotate.y}deg)`,
          transformStyle: 'preserve-3d',
        }}
      >
        {/* Soft Ambient Glows behind the 3D Brain */}
        <div className="absolute top-[20%] left-[25%] w-[50%] h-[40%] bg-gradient-to-tr from-cyan-400/30 via-indigo-500/35 to-purple-500/30 rounded-full blur-3xl pointer-events-none animate-pulse-subtle" />
        <div className="absolute bottom-[25%] right-[20%] w-[35%] h-[30%] bg-purple-500/20 rounded-full blur-2xl pointer-events-none" />

        {/* Glowing Orbital Rings SVG */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none z-10 overflow-visible"
          viewBox="0 0 540 430"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="orbitGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#818CF8" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#C084FC" stopOpacity="0.4" />
            </linearGradient>
            <linearGradient id="orbitGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#A855F7" stopOpacity="0.75" />
              <stop offset="60%" stopColor="#6366F1" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.5" />
            </linearGradient>
          </defs>

          {/* Main Tilted Orbital Ellipse 1 */}
          <ellipse
            cx="270"
            cy="175"
            rx="185"
            ry="75"
            transform="rotate(-14 270 175)"
            stroke="url(#orbitGrad1)"
            strokeWidth="1.8"
            strokeDasharray="6 8"
            className="animate-[spin_45s_linear_infinite]"
            style={{ transformOrigin: '270px 175px' }}
          />

          {/* Counter Tilted Orbital Ellipse 2 */}
          <ellipse
            cx="270"
            cy="175"
            rx="170"
            ry="65"
            transform="rotate(18 270 175)"
            stroke="url(#orbitGrad2)"
            strokeWidth="1.4"
            strokeDasharray="4 6"
            className="animate-[spin_60s_linear_infinite_reverse]"
            style={{ transformOrigin: '270px 175px' }}
          />

          {/* Subtle Outer Whispering Ring */}
          <ellipse
            cx="270"
            cy="175"
            rx="210"
            ry="85"
            transform="rotate(-5 270 175)"
            stroke="rgba(192, 132, 252, 0.35)"
            strokeWidth="1"
          />

          {/* Sparkle Synapse Points on Orbits */}
          <circle cx="110" cy="140" r="3" fill="#38BDF8" className="animate-pulse" />
          <circle cx="420" cy="205" r="3.5" fill="#C084FC" className="animate-ping" style={{ animationDuration: '3s' }} />
          <circle cx="160" cy="225" r="2.5" fill="#818CF8" className="animate-pulse" />
          <circle cx="390" cy="130" r="3" fill="#38BDF8" className="animate-pulse" />
        </svg>

        {/* 3D Brain & Tech Desk Scene Image with Floating Animation */}
        <div className="relative w-full h-full flex items-center justify-center animate-float-slow">
          <img
            src={loginBrainImg}
            alt="3D Glowing NLTK Neural Brain on Tech Pedestal with Laptop and Books"
            className="w-[94%] h-auto object-contain rounded-2xl drop-shadow-[0_20px_45px_rgba(99,102,241,0.22)] select-none pointer-events-none"
          />
        </div>

        {/* Floating Interactive NLP Feature Pills */}
        {NLP_PILLS.map((pill) => {
          const Icon = pill.icon;
          const isHovered = activeTooltip === pill.id;

          return (
            <div
              key={pill.id}
              onMouseEnter={() => setActiveTooltip(pill.id)}
              onMouseLeave={() => setActiveTooltip(null)}
              onClick={() => setActiveTooltip(activeTooltip === pill.id ? null : pill.id)}
              className={`absolute ${pill.position} z-30 cursor-pointer transition-all duration-300 transform animate-float`}
              style={{
                animationDelay: pill.delay,
                transform: isHovered ? 'scale(1.1) translateZ(30px)' : 'scale(1) translateZ(10px)',
              }}
            >
              {/* Floating Glass Pill */}
              <div
                className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-gradient-to-r ${pill.gradient} text-white text-[10px] sm:text-xs font-semibold shadow-md ${pill.glowColor} border border-white/40 backdrop-blur-md hover:brightness-110 active:scale-95 transition-all duration-150`}
              >
                <Icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" />
                <span className="tracking-wide">{pill.title}</span>
              </div>

              {/* Tooltip on Hover */}
              {isHovered && (
                <div className="absolute left-1/2 -translate-x-1/2 -top-8 px-2.5 py-1 rounded-md bg-slate-900/90 text-white text-[10px] whitespace-nowrap shadow-xl border border-slate-700 pointer-events-none z-40 animate-fadeIn backdrop-blur-xs">
                  {pill.description}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
