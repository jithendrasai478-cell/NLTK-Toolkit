import { 
  Brain, 
  Smile, 
  Tag, 
  PenLine, 
  Languages, 
  LayoutGrid, 
  FileText, 
  Code2, 
  ArrowRight 
} from 'lucide-react';
import type { FeatureItem } from '../data/features';
import { featuresData } from '../data/features';

interface FeatureGridProps {
  onSelectFeature: (feature: FeatureItem) => void;
}

export const FeatureGrid = ({ onSelectFeature }: FeatureGridProps) => {
  const getIcon = (iconName: FeatureItem['iconName']) => {
    const iconProps = { className: "w-4 h-4", strokeWidth: 2.2 };
    switch (iconName) {
      case 'brain':
        return <Brain {...iconProps} />;
      case 'smile':
        return <Smile {...iconProps} />;
      case 'tag':
        return <Tag {...iconProps} />;
      case 'pen':
        return <PenLine {...iconProps} />;
      case 'translate':
        return <Languages {...iconProps} />;
      case 'grid':
        return <LayoutGrid {...iconProps} />;
      case 'file':
        return <FileText {...iconProps} />;
      case 'code':
        return <Code2 {...iconProps} />;
      default:
        return <Brain {...iconProps} />;
    }
  };

  return (
    <section id="features-section" className="relative py-8 md:py-10 max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8">
      {/* Section Header */}
      <div className="text-center max-w-2xl mx-auto mb-7">
        {/* Pill Badge */}
        <div className="inline-flex items-center justify-center px-3 py-0.5 rounded-full bg-[#E0F2FE] dark:bg-sky-950/70 text-[#0284C7] dark:text-sky-300 dark:border dark:border-sky-800/60 text-[10px] font-bold uppercase tracking-wider mb-2">
          WHY CHOOSE US
        </div>
        
        {/* Heading */}
        <h2 className="text-xl sm:text-2xl md:text-[26px] font-extrabold text-[#0F172A] dark:text-white tracking-tight">
          Everything You Need for NLP
        </h2>
        
        {/* Subtitle */}
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 font-normal">
          Simple tools. Powerful features. Built for learners, researchers and developers.
        </p>
      </div>

      {/* 8 Feature Cards Grid (4 columns x 2 rows) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-3.5">
        {featuresData.map((feature) => (
          <div
            key={feature.id}
            onClick={() => onSelectFeature(feature)}
            className="group relative bg-white dark:bg-slate-900/90 rounded-2xl px-4 py-3.5 border border-slate-100/90 dark:border-slate-800 shadow-2xs hover:shadow-md hover:border-indigo-200/90 dark:hover:border-indigo-500/50 transition-all duration-200 flex items-center justify-between cursor-pointer"
          >
            {/* Left: Icon & Text content */}
            <div className="flex items-center gap-3 min-w-0 pr-1">
              {/* Icon in colored circle */}
              <div 
                className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 transition-transform duration-200 group-hover:scale-105 ${feature.colorBg} ${feature.colorText} dark:bg-opacity-20`}
              >
                {getIcon(feature.iconName)}
              </div>

              {/* Title & Desc */}
              <div className="min-w-0">
                <h3 className="text-xs sm:text-[13px] font-bold text-[#0F172A] dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors leading-tight">
                  {feature.title}
                </h3>
                <p className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-snug line-clamp-2">
                  {feature.description}
                </p>
              </div>
            </div>

            {/* Right: Circular Arrow CTA Button */}
            <div className="shrink-0">
              <div className="w-6 h-6 rounded-full border border-slate-200/90 dark:border-slate-700 flex items-center justify-center text-slate-400 dark:text-slate-400 group-hover:border-indigo-500 dark:group-hover:border-indigo-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 group-hover:bg-indigo-50/80 dark:group-hover:bg-indigo-950/60 transition-all duration-150">
                <ArrowRight className="w-3 h-3 transition-transform duration-150 group-hover:translate-x-0.5" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
