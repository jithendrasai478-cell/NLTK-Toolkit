import { useState, useEffect } from 'react';
import { 
  X, 
  Sparkles, 
  Copy, 
  Check, 
  ArrowRight, 
  Play, 
  Download, 
  Clock, 
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import type { FeatureItem } from '../data/features';
import {
  summarizeText,
  analyzeSentiment,
  extractKeywords,
  tokenizeText,
  classifyText,
  translateText,
  rewriteText,
  answerQuestion,
  recordHistory
} from '../services/apiClient';

interface InteractiveModalProps {
  feature: FeatureItem | null;
  onClose: () => void;
}

export const InteractiveModal = ({ feature, onClose }: InteractiveModalProps) => {
  const [inputVal, setInputVal] = useState(feature?.sampleInput || '');
  const [questionVal, setQuestionVal] = useState('When was NLTK created?');
  const [outputVal, setOutputVal] = useState(feature?.sampleOutput || '');
  const [isProcessing, setIsProcessing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [processingTime, setProcessingTime] = useState<number | null>(null);

  // Settings
  const [targetLang, setTargetLang] = useState('te');
  const [rewriteMode, setRewriteMode] = useState('simplify');
  const [summaryMode, setSummaryMode] = useState<'short' | 'medium' | 'long'>('medium');
  const [keywordsCorpusMode, setKeywordsCorpusMode] = useState<'single' | 'multi_doc'>('single');

  useEffect(() => {
    if (feature) {
      setInputVal(feature.sampleInput || '');
      setOutputVal(feature.sampleOutput || '');
      setErrorMsg(null);
      setProcessingTime(null);
    }
  }, [feature]);

  if (!feature) return null;

  const handleProcess = async () => {
    if (!inputVal.trim()) {
      setErrorMsg('Please enter text to process.');
      return;
    }

    setIsProcessing(true);
    setErrorMsg(null);

    try {
      let res: any;
      if (feature.id === 'summarize') {
        res = await summarizeText(inputVal, summaryMode);
        if (res.success) {
          const d = res.data;
          let out = `Summary (${d.summary_sentence_count} of ${d.original_sentence_count} sentences, ${d.percentage_reduction}% reduction):\n\n${d.summary}`;
          if (d.key_takeaways && d.key_takeaways.length > 0) {
            out += `\n\nKey Insights / Takeaways:\n` + d.key_takeaways.map((t: string) => `• ${t}`).join('\n');
          }
          if (d.technique || d.provider) {
            out += `\n\nMethod: ${d.technique || d.provider}`;
          }
          setOutputVal(out);
        }
      } else if (feature.id === 'sentiment') {
        res = await analyzeSentiment(inputVal);
        if (res.success) {
          const d = res.data;
          setOutputVal(
            `Sentiment: ${d.label.toUpperCase()} (${d.tone})\n` +
            `Compound Score: ${d.scores.compound > 0 ? '+' : ''}${d.scores.compound} (Scale: -1.0 to +1.0)\n\n` +
            `Positivity: ${d.score_percentages.positive}%\n` +
            `Neutrality: ${d.score_percentages.neutral}%\n` +
            `Negativity: ${d.score_percentages.negative}%\n\n` +
            `Note: ${d.explanation.disclaimer}`
          );
        }
      } else if (feature.id === 'keywords') {
        res = await extractKeywords(inputVal, 8, 'tfidf', keywordsCorpusMode);
        if (res.success) {
          const d = res.data;
          const isMultiDoc = d.corpus_mode === 'multi_doc';
          const lines = d.keywords.map((k: any) => {
            const dfInfo = isMultiDoc && k.doc_frequency ? ` [wt: ${k.score}] [DF: ${k.doc_frequency}/${k.corpus_size}]` : ` [weight: ${k.score}]`;
            return `#${k.rank}  ${k.keyword.padEnd(21)}${dfInfo} (${k.type || 'keyword'})`;
          });
          let out = `Extracted Keywords & Keyphrases (${d.method_used.toUpperCase()} Ranking - ${isMultiDoc ? 'Multi-Doc Corpus Mode' : 'Single Document Mode'}):\n\n` + lines.join('\n');
          if (d.hashtag_format?.length) {
            out += `\n\nHashtags:\n${d.hashtag_format.join(' ')}`;
          }
          if (d.note) {
            out += `\n\nNote: ${d.note}`;
          }
          setOutputVal(out);
        }
      } else if (feature.id === 'rewrite') {
        res = await rewriteText(inputVal, rewriteMode);
        if (res.success) {
          const d = res.data;
          setOutputVal(
            `Style Mode: ${d.mode_used.toUpperCase()}\n` +
            `Word Count: ${d.original_word_count} -> ${d.rewritten_word_count} words\n\n` +
            `"${d.rewritten_text}"\n\n` +
            `Notice: ${d.notice}`
          );
        }
      } else if (feature.id === 'translate') {
        res = await translateText(inputVal, 'en', targetLang);
        if (res.success) {
          const d = res.data;
          setOutputVal(
            `Target Language: ${d.target_language_name}\n` +
            `Provider: ${d.provider}\n\n` +
            `${d.translated_text}`
          );
        }
      } else if (feature.id === 'classify') {
        res = await classifyText(inputVal);
        if (res.success) {
          const d = res.data;
          const probLines = d.category_probabilities.map(
            (c: any) => {
              const formattedPct = typeof c.percentage === 'number' ? c.percentage.toFixed(1) : c.percentage;
              return `• ${c.category.padEnd(18)} : ${formattedPct.padStart(5)}%`;
            }
          );
          let extra = `\n\nModel: ${d.model_info?.algorithm || 'Multinomial Logistic Regression + TF-IDF'}`;
          if (d.warning) {
            extra += `\n\nNotice: ${d.warning}`;
          }
          if (d.confidence_note) {
            extra += `\n\nConfidence Note: ${d.confidence_note}`;
          }
          setOutputVal(
            `Predicted Topic: ${d.predicted_category.toUpperCase()} (Confidence: ${d.confidence_tier})\n\n` +
            `Category Distribution:\n` +
            probLines.join('\n') +
            extra
          );
        }
      } else if (feature.id === 'qa') {
        res = await answerQuestion(inputVal, questionVal);
        if (res.success) {
          const d = res.data;
          setOutputVal(
            `Question: ${d.question}\n` +
            `Confidence: ${d.confidence_label} (${d.confidence})\n\n` +
            `Extracted Answer:\n"${d.answer}"\n\n` +
            `Method: ${d.method}`
          );
        }
      } else {
        // More Tools -> Tokenize
        res = await tokenizeText(inputVal, 'english');
        if (res.success) {
          const d = res.data;
          const tokensFormatted = JSON.stringify(d.tokens, null, 2);
          const sentsBlock = d.function_name === 'sent_tokenize' && d.sentences
            ? `Sentences List:\n${JSON.stringify(d.sentences, null, 2)}\n\n`
            : '';
          setOutputVal(
            `Input Text:\n${d.input_text || inputVal}\n\n` +
            `Processing Method:\n${d.processing_method || 'NLTK word_tokenize'}\n\n` +
            `Library Used:\n${d.library_used || 'NLTK'}\n\n` +
            `Token Count:\n${d.token_count}\n\n` +
            `Sentence Count:\n${d.sentence_count}\n\n` +
            `Character Count:\n${d.character_count}\n\n` +
            sentsBlock +
            `Tokens List:\n${tokensFormatted}`
          );
        }
      }

      if (res && res.success) {
        const ms = res.meta?.processing_time_ms || 12;
        setProcessingTime(ms);
        // Record non-blocking audit trail
        recordHistory(feature.id, inputVal.slice(0, 100), (res.data?.summary || res.data?.label || 'Processed').slice(0, 100), ms);
      } else {
        setErrorMsg(res?.error?.message || 'Processing failed. Please check input text.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred while communicating with the server.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(outputVal);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([outputVal], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nltk_${feature.id}_result.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-xs p-4 animate-fadeIn">
      <div 
        className="relative w-full max-w-xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 overflow-hidden max-h-[90vh] flex flex-col text-slate-800 dark:text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 sm:py-5 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/90 shrink-0">
          <div className="flex items-center gap-3">
            <div className={`w-9 h-9 rounded-full flex items-center justify-center ${feature.colorBg} ${feature.colorText} dark:bg-opacity-20`}>
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {feature.title}
                </h3>
                {processingTime !== null && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200/60 dark:border-emerald-800/60 px-2 py-0.5 rounded-full">
                    <Clock className="w-2.5 h-2.5" />
                    {processingTime}ms
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {feature.description}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 sm:p-6 space-y-4 overflow-y-auto flex-grow">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-900/60 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Context Options for specific tools */}
          {feature.id === 'translate' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Target Language
              </label>
              <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="w-full text-xs p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 font-medium text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-400/20"
              >
                <option value="te">Telugu (తెలుగు) — Regional Indian Language</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                <option value="ml">Malayalam (മലയാളം)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="ur">Urdu (اردو)</option>
                <option value="fr">French (Français)</option>
                <option value="es">Spanish (Español)</option>
                <option value="de">German (Deutsch)</option>
                <option value="ja">Japanese (日本語)</option>
                <option value="zh">Chinese (中文)</option>
              </select>
            </div>
          )}

          {feature.id === 'rewrite' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Rewriting Mode
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['simplify', 'formal', 'informal', 'shorten', 'expand', 'paraphrase'] as const).map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setRewriteMode(m)}
                    className={`py-1.5 px-2 rounded-lg text-xs font-semibold capitalize transition-all cursor-pointer ${
                      rewriteMode === m
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          )}

          {feature.id === 'summarize' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Summary Length
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['short', 'medium', 'long'] as const).map((len) => (
                  <button
                    key={len}
                    type="button"
                    onClick={() => setSummaryMode(len)}
                    className={`py-1.5 px-2 rounded-lg text-xs font-semibold capitalize transition-all cursor-pointer ${
                      summaryMode === len
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    {len}
                  </button>
                ))}
              </div>
            </div>
          )}

          {feature.id === 'keywords' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                TF-IDF Evaluation Mode
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setKeywordsCorpusMode('single')}
                  className={`py-1.5 px-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    keywordsCorpusMode === 'single'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  Single Document (Baseline DF)
                </button>
                <button
                  type="button"
                  onClick={() => setKeywordsCorpusMode('multi_doc')}
                  className={`py-1.5 px-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    keywordsCorpusMode === 'multi_doc'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  Multi-Doc Corpus (Test Mode)
                </button>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">
                {keywordsCorpusMode === 'single'
                  ? 'Evaluates document independently. Single occurrences naturally share identical DF=1 / IDF=1.0.'
                  : 'Evaluates against a reference corpus (N=6). Term weights naturally vary based on real Document Frequency (DF).'}
              </p>
            </div>
          )}

          {feature.id === 'qa' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Question to Ask Passage
              </label>
              <input
                type="text"
                value={questionVal}
                onChange={(e) => setQuestionVal(e.target.value)}
                placeholder="What would you like to ask?"
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-400 font-sans"
              />
            </div>
          )}

          {/* Input text area */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                {feature.id === 'qa' ? 'Reference Passage' : 'Input Text'}
              </label>
              <span className="text-[11px] text-slate-400 dark:text-slate-500">
                {inputVal.length} chars
              </span>
            </div>
            <textarea
              rows={3}
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              className="w-full text-xs sm:text-sm p-3 rounded-xl border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400/20 focus:border-indigo-400 bg-slate-50/70 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 resize-none font-sans"
              placeholder="Enter text to process..."
            />
          </div>

          {/* Action trigger row */}
          <div className="flex items-center justify-between pt-0.5">
            <span className="text-[11px] text-slate-400 dark:text-slate-500">
              Live Flask REST API (/api/v1/nlp)
            </span>
            <button
              onClick={handleProcess}
              disabled={isProcessing}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-xs active:scale-95 transition-all cursor-pointer disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3 h-3 fill-white" />
                  <span>Run {feature.title}</span>
                </>
              )}
            </button>
          </div>

          {/* Output text area */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Output Result
              </label>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium cursor-pointer"
                >
                  <Download className="w-3 h-3" />
                  <span>Export</span>
                </button>
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium cursor-pointer"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 dark:bg-slate-950 text-slate-100 border border-slate-800/80 font-mono text-xs whitespace-pre-wrap leading-relaxed shadow-inner max-h-48 overflow-y-auto">
              {outputVal}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-slate-50 dark:bg-slate-900/90 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0">
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Real Python NLTK / Scikit-learn Pipeline
          </span>
          <button
            onClick={onClose}
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center gap-1 cursor-pointer"
          >
            <span>Close Window</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
