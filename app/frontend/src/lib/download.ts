/**
 * Browser download helpers — no dependencies. Each function builds an object URL
 * for an anchor click, then revokes it. Safe to call from event handlers only
 * (they touch `document`), so guard for SSR is unnecessary in this SPA.
 */

/**
 * Trigger a browser download of `data` under `filename`.
 * `data` may be a Blob (used as-is) or a string (wrapped in a Blob with `mime`,
 * default `text/plain;charset=utf-8`).
 */
export function downloadBlob(filename: string, data: Blob | string, mime = 'text/plain;charset=utf-8'): void {
  const blob = data instanceof Blob ? data : new Blob([data], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

/** Download an object as pretty-printed JSON (2-space indent). */
export function downloadJSON(filename: string, obj: unknown): void {
  downloadBlob(filename, JSON.stringify(obj, null, 2), 'application/json;charset=utf-8');
}

/** Render one CSV cell, RFC-4180 quoting only when needed (comma, quote, CR, or LF). */
function csvCell(value: unknown): string {
  const text = value == null ? '' : String(value);
  if (/[",\r\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

/**
 * Convert rows to an RFC-4180 CSV string. The header is the union of all keys,
 * in first-seen order across the rows. Uses CRLF line endings per the spec.
 * An empty `rows` yields an empty string.
 */
export function toCSV(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return '';
  const headers: string[] = [];
  const seen = new Set<string>();
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      if (!seen.has(key)) {
        seen.add(key);
        headers.push(key);
      }
    }
  }
  const lines = [headers.map(csvCell).join(',')];
  for (const row of rows) {
    lines.push(headers.map((h) => csvCell(row[h])).join(','));
  }
  return lines.join('\r\n');
}

/** Build a CSV from `rows` and trigger a download under `filename`. */
export function downloadCSV(filename: string, rows: Record<string, unknown>[]): void {
  downloadBlob(filename, toCSV(rows), 'text/csv;charset=utf-8');
}
