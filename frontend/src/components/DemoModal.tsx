import { X, Play, CheckCircle2, ExternalLink } from 'lucide-react';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const VIDEO_ID = 'X2vAabgKiuM';

export const DemoModal = ({ isOpen, onClose }: DemoModalProps) => {
  if (!isOpen) return null;

  const handleBackdropClick = () => {
    onClose();
  };

  const handleVideoClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();
  };

  const handleOpenYouTube = () => {
    window.open(
      `https://www.youtube.com/watch?v=${VIDEO_ID}`,
      '_blank',
      'noopener,noreferrer'
    );
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-3 sm:p-5 md:p-8 animate-fadeIn"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="demo-modal-title"
    >
      <div
        className="relative flex w-full max-w-5xl max-h-[95vh] flex-col overflow-hidden rounded-2xl sm:rounded-3xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100"
        onClick={handleVideoClick}
      >
        {/* Header */}
        <div className="flex shrink-0 items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 px-4 sm:px-6 py-3.5 sm:py-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400">
              <Play className="h-4 w-4 fill-current" />
            </div>

            <div className="min-w-0">
              <h3
                id="demo-modal-title"
                className="truncate text-sm sm:text-base font-bold text-slate-900 dark:text-white"
              >
                NLTK Toolkit Quick Tour
              </h3>

              <p className="hidden sm:block text-[11px] text-slate-500 dark:text-slate-400">
                Natural Language Processing with Python & NLTK
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close demo"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200 cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto">
          <div className="p-4 sm:p-6 md:p-7 space-y-5">

            {/* Video */}
            <div className="overflow-hidden rounded-xl sm:rounded-2xl bg-black shadow-xl ring-1 ring-slate-200 dark:ring-slate-800">
              <div className="relative aspect-video w-full">
                <iframe
                  className="absolute inset-0 h-full w-full"
                  src={`https://www.youtube.com/embed/${VIDEO_ID}?rel=0`}
                  title="Natural Language Processing NLP Tutorial with Python and NLTK"
                  loading="lazy"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                />
              </div>
            </div>

            {/* Video Information */}
            <div className="space-y-1">
              <h4 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                Natural Language Processing with Python & NLTK
              </h4>

              <p className="text-xs sm:text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                Learn the fundamentals of Natural Language Processing and
                understand how NLTK can be used to process and analyze human
                language.
              </p>
            </div>

            {/* Topics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div className="flex items-start gap-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 p-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  Tokenization, stopwords and text preprocessing
                </span>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 p-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  Stemming and lemmatization
                </span>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 p-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  POS tagging and Named Entity Recognition
                </span>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 p-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  N-grams, classification and NLP workflows
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex shrink-0 flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/90 px-4 sm:px-6 py-3.5 sm:py-4">
          <button
            type="button"
            onClick={handleOpenYouTube}
            className="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Open on YouTube
          </button>

          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center justify-center rounded-full bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700 active:scale-[0.98] cursor-pointer"
          >
            Got it, explore tools!
          </button>
        </div>
      </div>
    </div>
  );
};