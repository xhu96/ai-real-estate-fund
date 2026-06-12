export interface RunSettings { engine: 'institutional' | 'screening'; llmEnabled: boolean; llmProvider: string; llmModel: string }

const KEY = 'aref.runSettings';
export const PROVIDERS = ['nvidia', 'openai', 'anthropic', 'gemini'] as const;
export const DEFAULT_MODELS: Record<string, string> = { nvidia: 'z-ai/glm-5.1', openai: 'gpt-4o-mini', anthropic: 'claude-sonnet-4-6', gemini: 'gemini-2.5-flash' };

export function loadRunSettings(): RunSettings {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { engine: 'institutional', llmEnabled: false, llmProvider: 'nvidia', llmModel: '', ...JSON.parse(raw) };
  } catch { /* fall through */ }
  return { engine: 'institutional', llmEnabled: false, llmProvider: 'nvidia', llmModel: '' };
}

export function saveRunSettings(settings: RunSettings): void {
  localStorage.setItem(KEY, JSON.stringify(settings));
}
