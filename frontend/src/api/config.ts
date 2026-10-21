// Base URL for every backend call. Defaults to "/api", which the Vite dev
// proxy forwards to the backend. Set VITE_API_URL when the backend lives
// elsewhere, e.g. https://ecoscan-api.example.com/api.
export const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/+$/, '')
