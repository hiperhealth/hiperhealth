// Simple API base for the frontend. Use Vite env var VITE_API_URL to override.
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function api(path){
  return `${API_BASE}${path}`;
}
