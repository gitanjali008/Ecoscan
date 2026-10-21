# EcoScan frontend

The EcoScan web app: upload or take a photo of clothing, see each item's carbon
footprint and reward points, fix anything the scan got wrong, and browse offers.
React 19 + TypeScript, Vite, Tailwind CSS v4. Mobile-first.

> For the full setup (backend, environment variables, running both together),
> see the [root README](../README.md).

## Commands

Needs Node.js 22.12+. Run from this folder:

```bash
npm install      # install dependencies
npm run dev      # http://localhost:5173, proxies /api to the backend on :8000
npm run build    # type-check (including tests) and build to dist/
npm test         # run the Vitest tests once (npm run test:watch to re-run on save)
```

Start the backend too, otherwise scans and recalculations will fail.

## Folder structure

```
src/
├── api/          the only code that talks to the backend (types, client, ApiError)
├── components/   small components, one job each; tests sit next to them
├── lib/          plain helpers: file checks, formatting, error wording
├── test/         test setup and shared fixtures
├── App.tsx       switches between the scan screen and the results
└── index.css     Tailwind and the design tokens (colours, fonts)
```
