import { Laptop, Code2, Sparkles, ArrowRight } from 'lucide-react';

export const HowItWorks = () => {
  const steps = [
    {
      stepNumber: '1',
      badgeBg: 'bg-[#38BDF8]',
      icon: <Laptop className="w-4 h-4 text-sky-600 dark:text-sky-400" />,
      iconBoxBg: 'bg-sky-50 dark:bg-sky-950/60 border border-sky-100 dark:border-sky-800/60',
      title: 'Choose a Tool',
      description: 'Select from a variety of NLP tools based on your needs.',
    },
    {
      stepNumber: '2',
      badgeBg: 'bg-[#A855F7]',
      icon: <Code2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />,
      iconBoxBg: 'bg-purple-50 dark:bg-purple-950/60 border border-purple-100 dark:border-purple-800/60',
      title: 'Enter Your Text',
      description: 'Input your text or upload your data.',
    },
    {
      stepNumber: '3',
      badgeBg: 'bg-[#34D399]',
      icon: <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />,
      iconBoxBg: 'bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-100 dark:border-emerald-800/60',
      title: 'Get Results',
      description: 'View, analyze and explore the results instantly.',
    },
  ];

  return (
    <section id="how-it-works-section" className="relative py-8 md:py-10 max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-center">
        {/* Left Side: Tag, Heading, Description */}
        <div className="lg:col-span-4 flex flex-col items-start">
          <div className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-[#EEF2FF] dark:bg-indigo-950/70 text-[#4F46E5] dark:text-indigo-300 dark:border dark:border-indigo-800/60 text-[10px] font-bold tracking-wider uppercase mb-1">
            GET STARTED IN 3 STEPS
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] dark:text-white tracking-tight">
            How It Works
          </h2>
          <p className="mt-1 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 leading-relaxed max-w-xs">
            Start using NLTK Toolkit in minutes. No complex setup required — just explore and build!
          </p>
        </div>

        {/* Right Side: 3 Connected Steps */}
        <div className="lg:col-span-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sm:gap-2">
          {steps.map((step, idx) => (
            <div key={step.stepNumber} className="flex-1 flex items-center gap-3 w-full sm:w-auto">
              <div className="flex-1 flex flex-col items-start group">
                {/* Header row: Number badge + Icon container */}
                <div className="flex items-center gap-2 mb-2">
                  {/* Number circular badge */}
                  <div className={`w-4 h-4 rounded-full ${step.badgeBg} text-white font-bold text-[10px] flex items-center justify-center shrink-0`}>
                    {step.stepNumber}
                  </div>
                  {/* Icon box */}
                  <div className={`p-1.5 rounded-lg ${step.iconBoxBg} shrink-0`}>
                    {step.icon}
                  </div>
                </div>

                {/* Step Title */}
                <h4 className="text-xs sm:text-[13px] font-bold text-[#0F172A] dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {step.title}
                </h4>

                {/* Step Subtitle */}
                <p className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-snug max-w-[190px]">
                  {step.description}
                </p>
              </div>

              {/* Arrow connector */}
              {idx < steps.length - 1 && (
                <div className="hidden sm:flex items-center justify-center px-2 text-slate-300 dark:text-slate-600">
                  <ArrowRight className="w-3.5 h-3.5 text-slate-300 dark:text-slate-600" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
