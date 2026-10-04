/**
 * Centralized API Client for NLTK Toolkit Full-Stack Application.
 * Communicates with the Flask backend via /api/v1/ endpoints.
 */

const API_BASE = '/api/v1';

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data: T;
  meta?: {
    tool?: string;
    processing_time_ms?: number;
  };
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('nltk_token') : null;
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, config);
    const contentType = res.headers.get('content-type') || '';
    let json: any = null;
    let rawText = '';

    // Safely parse body based on content type
    if (contentType.toLowerCase().includes('application/json')) {
      try {
        json = await res.json();
      } catch (parseErr) {
        console.warn(`[apiClient] JSON parse error for ${endpoint}:`, parseErr);
        rawText = '';
      }
    } else {
      try {
        rawText = await res.text();
        if (rawText && rawText.trim().startsWith('{')) {
          json = JSON.parse(rawText);
        }
      } catch {
        json = null;
      }
    }

    // If server responded with a parsed JSON payload
    if (json && typeof json === 'object') {
      if (!res.ok || json.success === false) {
        const errorMsg =
          json.error?.message ||
          json.message ||
          `Server returned status ${res.status}: Request failed`;
        return {
          success: false,
          data: null as any,
          message: errorMsg,
          error: {
            code: json.error?.code || `HTTP_${res.status}`,
            message: errorMsg,
            details: json.error?.details,
          },
        };
      }
      return json as ApiResponse<T>;
    }

    // Handle non-JSON or empty response gracefully without throwing
    console.warn(`[apiClient] Received non-JSON response (HTTP ${res.status}) for ${endpoint}:`, rawText.slice(0, 200));

    let userFacingMessage = 'Could not connect to the backend server. Please verify the backend is running.';
    if (res.status === 401) {
      userFacingMessage = 'Authentication failed. Please verify your credentials and try again.';
    } else if (res.status === 403) {
      userFacingMessage = 'Access denied. You do not have permission to perform this action.';
    } else if (res.status === 404) {
      userFacingMessage = 'The requested authentication endpoint was not found on the server.';
    } else if (res.status >= 500) {
      userFacingMessage = 'Authentication server encountered a temporary issue. Please try again.';
    }

    return {
      success: false,
      data: null as any,
      message: userFacingMessage,
      error: {
        code: `HTTP_${res.status}`,
        message: userFacingMessage,
      },
    };
  } catch (err: any) {
    console.error(`[apiClient] Network request failed for ${endpoint}:`, err);
    return {
      success: false,
      data: null as any,
      message: 'Could not connect to the server. Please verify your network and that the backend is running.',
      error: {
        code: 'NETWORK_ERROR',
        message: 'Could not connect to the server. Please verify your network and that the backend is running.',
      },
    };
  }
}

// ----------------- NLP Endpoints -----------------

export async function summarizeText(text: string, lengthMode: 'short' | 'medium' | 'long' = 'medium') {
  return request('/nlp/summarize', {
    method: 'POST',
    body: JSON.stringify({ text, options: { summary_length: lengthMode } }),
  });
}

export async function analyzeSentiment(text: string) {
  return request('/nlp/sentiment', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function extractKeywords(
  text: string, 
  topN: number = 10, 
  method: 'tfidf' | 'frequency' = 'tfidf',
  corpusMode: 'single' | 'multi_doc' = 'single',
  referenceCorpus?: string[]
) {
  return request('/nlp/keywords', {
    method: 'POST',
    body: JSON.stringify({ 
      text, 
      options: { 
        top_n: topN, 
        method, 
        corpus_mode: corpusMode,
        reference_corpus: referenceCorpus 
      } 
    }),
  });
}

export async function tokenizeText(text: string, language: string = 'english') {
  return request('/nlp/tokenize', {
    method: 'POST',
    body: JSON.stringify({ text, options: { language } }),
  });
}

export async function classifyText(text: string) {
  return request('/nlp/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function translateText(text: string, sourceLang: string = 'en', targetLang: string = 'te') {
  return request('/nlp/translate', {
    method: 'POST',
    body: JSON.stringify({ text, source_language: sourceLang, target_language: targetLang }),
  });
}

export async function getSupportedLanguages() {
  return request<{ supported_languages: Array<{ code: string; name: string }>; total_languages: number }>('/languages', {
    method: 'GET',
  });
}

export async function rewriteText(text: string, mode: string = 'simplify') {
  return request('/nlp/rewrite', {
    method: 'POST',
    body: JSON.stringify({ text, options: { mode } }),
  });
}

export async function answerQuestion(passage: string, question: string) {
  return request('/nlp/qa', {
    method: 'POST',
    body: JSON.stringify({ passage, question }),
  });
}

export async function extractEntities(text: string) {
  return request('/nlp/ner', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function calculateStatistics(text: string) {
  return request('/nlp/statistics', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function calculateReadability(text: string) {
  return request('/nlp/readability', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function removeStopwords(text: string, language: string = 'english') {
  return request('/nlp/stopwords', {
    method: 'POST',
    body: JSON.stringify({ text, options: { language } }),
  });
}

export async function stemText(text: string, algorithm: string = 'porter') {
  return request('/nlp/stem', {
    method: 'POST',
    body: JSON.stringify({ text, options: { algorithm } }),
  });
}

export async function lemmatizeText(text: string) {
  return request('/nlp/lemmatize', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function tagPos(text: string) {
  return request('/nlp/pos-tag', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function generateNgrams(text: string, n: number = 2) {
  return request('/nlp/ngrams', {
    method: 'POST',
    body: JSON.stringify({ text, options: { n } }),
  });
}

export async function analyzeWordFrequency(text: string, topN: number = 10) {
  return request('/nlp/word-frequency', {
    method: 'POST',
    body: JSON.stringify({ text, options: { top_n: topN } }),
  });
}

export async function detectLanguage(text: string) {
  return request('/nlp/language-detection', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function calculateSimilarity(text1: string, text2: string) {
  return request('/nlp/similarity', {
    method: 'POST',
    body: JSON.stringify({ text1, text2 }),
  });
}

// ----------------- Learning & Samples -----------------

export async function getLearningTopics() {
  return request<{ topics: any[]; total: number }>('/learning/topics', {
    method: 'GET',
  });
}

export async function getSampleTexts() {
  return request<{ samples: Record<string, string> }>('/learning/samples', {
    method: 'GET',
  });
}

// ----------------- History Audit -----------------

export async function recordHistory(toolName: string, inputSnippet: string, outputSummary: string, ms: number) {
  return request('/history', {
    method: 'POST',
    body: JSON.stringify({
      tool_name: toolName,
      input_snippet: inputSnippet,
      output_summary: outputSummary,
      processing_time_ms: ms,
    }),
  });
}

// ----------------- Authentication Endpoints -----------------

export interface AuthUser {
  id: number;
  username: string;
  display_name?: string | null;
  email: string;
  google_id?: string | null;
  avatar_url?: string | null;
  created_at?: string;
}

export interface AuthResponse {
  user: AuthUser;
  access_token: string;
}

export async function loginUser(emailOrUsername: string, password: string) {
  return request<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: emailOrUsername, password }),
  });
}

export async function registerUser(username: string, email: string, password: string) {
  return request<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export async function googleLogin(credential: string) {
  return request<AuthResponse>('/auth/google', {
    method: 'POST',
    body: JSON.stringify({ credential }),
  });
}

export async function getCurrentUser() {
  return request<{ user: AuthUser }>('/auth/me', {
    method: 'GET',
  });
}
