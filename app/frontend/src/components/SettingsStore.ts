export interface RunSettings {
  engine: 'institutional' | 'screening';
  llmEnabled: boolean;
  llmProvider: string;
  llmModel: string;
  llmApiKey: string;   // optional GUI override; blank = use the server .env key
  llmBaseUrl: string;  // optional GUI override; blank = provider default / .env
}

const KEY = 'aref.runSettings';
export const PROVIDERS = ['nvidia', 'openai', 'anthropic', 'gemini'] as const;
export const DEFAULT_MODELS: Record<string, string> = { nvidia: 'meta/llama-3.1-8b-instruct', openai: 'gpt-4o-mini', anthropic: 'claude-sonnet-4-6', gemini: 'gemini-2.5-flash' };

const DEFAULTS: RunSettings = { engine: 'institutional', llmEnabled: false, llmProvider: 'nvidia', llmModel: '', llmApiKey: '', llmBaseUrl: '' };

export function loadRunSettings(): RunSettings {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch { /* fall through */ }
  return { ...DEFAULTS };
}

export function saveRunSettings(settings: RunSettings): void {
  localStorage.setItem(KEY, JSON.stringify(settings));
}
