interface BrainLogoProps {
  className?: string;
  size?: number;
  monochrome?: boolean;
}

export const BrainLogo = ({ className = '', size = 36, monochrome = false }: BrainLogoProps) => {
  return (
    <svg
      width={size}
      height={size * 0.9}
      viewBox="0 0 44 38"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`shrink-0 select-none transition-transform duration-200 group-hover:scale-105 ${className}`}
    >
      <defs>
        <linearGradient id="leftBrainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={monochrome ? "#C4B5FD" : "#8B5CF6"} />
          <stop offset="100%" stopColor={monochrome ? "#A78BFA" : "#6366F1"} />
        </linearGradient>
        <linearGradient id="rightBrainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={monochrome ? "#93C5FD" : "#3B82F6"} />
          <stop offset="100%" stopColor={monochrome ? "#60A5FA" : "#2563EB"} />
        </linearGradient>
      </defs>

      {/* Left Hemisphere: Purple outline with lobes and inner convolutions */}
      <path
        d="M 21 5 
           C 16 4, 12 7, 11 11 
           C 7 11, 4 14, 4 18 
           C 4 22, 6 24, 8 26 
           C 6 28, 6 32, 9 34 
           C 12 36, 17 35, 21 34
           Z"
        fill={monochrome ? "rgba(196, 181, 253, 0.15)" : "#F5F3FF"}
        stroke="url(#leftBrainGrad)"
        strokeWidth="2.8"
        strokeLinejoin="round"
      />
      {/* Inner folds on left */}
      <path
        d="M 12 16 C 15 16, 17 14, 19 14"
        stroke="url(#leftBrainGrad)"
        strokeWidth="2.2"
        strokeLinecap="round"
      />
      <path
        d="M 11 23 C 14 23, 16 26, 19 23"
        stroke="url(#leftBrainGrad)"
        strokeWidth="2.2"
        strokeLinecap="round"
      />
      <circle cx="16" cy="19" r="1.4" fill={monochrome ? "#C4B5FD" : "#8B5CF6"} />

      {/* Right Hemisphere: Solid vivid blue filled brain with white neural dots */}
      <path
        d="M 23 5 
           C 28 4, 32 7, 33 11 
           C 37 11, 40 14, 40 18 
           C 40 22, 38 24, 36 26 
           C 38 28, 38 32, 35 34 
           C 32 36, 27 35, 23 34
           Z"
        fill={monochrome ? "#818CF8" : "url(#rightBrainGrad)"}
      />
      {/* Sparkles & Neural dots inside right hemisphere */}
      <circle cx="28" cy="11" r="1.3" fill="#FFFFFF" opacity="0.9" />
      <circle cx="34" cy="15" r="1.2" fill="#FFFFFF" opacity="0.8" />
      <circle cx="27" cy="20" r="1.4" fill="#FFFFFF" opacity="0.9" />
      <circle cx="35" cy="24" r="1.2" fill="#FFFFFF" opacity="0.8" />
      <circle cx="30" cy="29" r="1.3" fill="#FFFFFF" opacity="0.9" />

      {/* Subtle brain stem division line */}
      <line x1="22" y1="6" x2="22" y2="33" stroke="#CBD5E1" strokeWidth="1.2" opacity={monochrome ? "0.3" : "0.5"} />
    </svg>
  );
};
