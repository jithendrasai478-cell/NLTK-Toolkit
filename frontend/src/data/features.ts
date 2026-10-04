export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  iconName: 'brain' | 'smile' | 'tag' | 'pen' | 'translate' | 'grid' | 'file' | 'code';
  colorBg: string;
  colorText: string;
  iconBgLight: string;
  badgeText?: string;
  sampleInput?: string;
  sampleOutput?: string;
}

export const featuresData: FeatureItem[] = [
  {
    id: 'summarize',
    title: 'Summarize',
    description: 'Get concise summaries from long text.',
    iconName: 'brain',
    colorBg: 'bg-purple-100',
    colorText: 'text-purple-600',
    iconBgLight: 'hover:border-purple-200',
    sampleInput: 'Natural language processing (NLP) is an interdisciplinary subfield of computer science and artificial intelligence. The ultimate objective is to read, decipher, understand, and make sense of human languages in a manner that is valuable. Modern neural models and transformers now allow automated systems to perform sentiment analysis, translation, and text summarization with unprecedented accuracy.',
    sampleOutput: 'Natural language processing (NLP) enables computers to understand human languages and execute translation, sentiment analysis, and summarization with high accuracy.',
  },
  {
    id: 'sentiment',
    title: 'Sentiment Analysis',
    description: 'Detect emotion and tone in text.',
    iconName: 'smile',
    colorBg: 'bg-emerald-100',
    colorText: 'text-emerald-600',
    iconBgLight: 'hover:border-emerald-200',
    sampleInput: 'The NLTK toolkit makes natural language processing so incredibly accessible and enjoyable!',
    sampleOutput: 'Positive (Score: 0.96) • Emotion: Joy, Enthusiasm',
  },
  {
    id: 'keywords',
    title: 'Keywords',
    description: 'Find important keywords and key phrases.',
    iconName: 'tag',
    colorBg: 'bg-rose-100',
    colorText: 'text-rose-500',
    iconBgLight: 'hover:border-rose-200',
    sampleInput: 'Machine learning algorithms analyze large text corpora to extract meaningful patterns and linguistic structures.',
    sampleOutput: '#MachineLearning, #Algorithms, #TextCorpora, #Patterns, #Linguistics',
  },
  {
    id: 'rewrite',
    title: 'Rewrite',
    description: 'Improve, simplify or change your writing style.',
    iconName: 'pen',
    colorBg: 'bg-sky-100',
    colorText: 'text-sky-600',
    iconBgLight: 'hover:border-sky-200',
    sampleInput: 'It is imperative that we utilize all available algorithmic methodologies to optimize computational throughput.',
    sampleOutput: 'We must use the best algorithms to speed up our system.',
  },
  {
    id: 'translate',
    title: 'Translate',
    description: 'Convert between multiple languages.',
    iconName: 'translate',
    colorBg: 'bg-amber-100',
    colorText: 'text-amber-600',
    iconBgLight: 'hover:border-amber-200',
    sampleInput: 'Natural Language Processing is amazing!',
    sampleOutput: 'Le traitement du langage naturel est formidable ! (FR)\n¡El procesamiento del lenguaje natural es increíble! (ES)',
  },
  {
    id: 'classify',
    title: 'Classify',
    description: 'Categorize text into custom labels.',
    iconName: 'grid',
    colorBg: 'bg-teal-100',
    colorText: 'text-teal-600',
    iconBgLight: 'hover:border-teal-200',
    sampleInput: 'Tesla announces new autonomous driving neural network architecture with end-to-end vision processing.',
    sampleOutput: 'Category: Technology / AI (Confidence: 98.4%)',
  },
  {
    id: 'qa',
    title: 'Q&A',
    description: 'Ask questions and get accurate answers.',
    iconName: 'file',
    colorBg: 'bg-indigo-100',
    colorText: 'text-indigo-600',
    iconBgLight: 'hover:border-indigo-200',
    sampleInput: 'Context: NLTK was created in 2001 by Steven Bird and Edward Loper at the University of Pennsylvania.\nQuestion: When was NLTK created?',
    sampleOutput: 'Answer: 2001 (by Steven Bird and Edward Loper at the University of Pennsylvania).',
  },
  {
    id: 'more-tools',
    title: 'More Tools',
    description: 'Explore additional NLP utilities and examples.',
    iconName: 'code',
    colorBg: 'bg-slate-100',
    colorText: 'text-slate-600',
    iconBgLight: 'hover:border-slate-300',
    sampleInput: 'word_tokenize("Let\'s tokenize this sentence!")',
    sampleOutput: 'Tokens: ["Let", "\'s", "tokenize", "this", "sentence", "!"]\nPOS Tags: [("Let", "VB"), ("\'s", "POS"), ...]',
  },
];
