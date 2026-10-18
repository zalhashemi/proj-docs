---
title: Developer Guide
subtitle: "BrightCart"
version: 1.0.0
date: "2026-10-18"
author: "BrightCart team"
project: "BrightCart"
doc_id: dev-guide
confidential: false
---

BrightCart is a React 18 single-page storefront built with Vite and styled with Tailwind CSS
(`package.json`). This guide takes you from a fresh clone to a running dev server.

> [!NOTE]
> Dependencies were not installed in the environment that generated this guide, so the npm
> commands below were read from `package.json` but not executed. They are marked ⟨untested⟩.

## Prerequisites

| Tool | Version | Source |
|---|---|---|
| Node.js | 20 | `.nvmrc`, `node-version: 20` in `.github/workflows/ci.yml` |
| npm | bundled with Node 20 | CI runs `npm ci` |
| Git | any recent | — |

## Clone to running

1. Clone the repository and enter it. The remote URL is not recorded in the repo ⟨assumption⟩.

   ```bash
   git clone <repository-url> brightcart
   cd brightcart
   ```

2. Create your environment file and fill in the values:

   ```bash
   cp .env.example .env
   ```

   | Variable | Needed for |
   |---|---|
   | `VITE_API_URL` | Backend base URL used by `src/pages/Home.tsx` |
   | `VITE_SENTRY_DSN` | Error reporting (`src/main.tsx`); empty disables it |
   | `VITE_STRIPE_PUBLISHABLE_KEY` | Checkout (`src/pages/Checkout.tsx`) |

3. Install dependencies ⟨untested⟩:

   ```bash
   npm install
   ```

4. Start the dev server ⟨untested⟩:

   ```bash
   npm run dev
   ```

   Vite serves the app on `http://localhost:5173` by default ⟨assumption⟩. No port is set in the repo.

## Project structure

```text
brightcart/
├── index.html            # Vite entry; loads Poppins + Playfair Display
├── tailwind.config.js    # brand colours and font families
├── vercel.json           # SPA rewrite: every path serves /
├── public/               # logo.svg, favicon.svg
├── src/
│   ├── main.tsx          # React root + Sentry.init
│   ├── App.tsx           # routes: / and /checkout
│   ├── index.css         # Tailwind layers + CSS variables
│   ├── pages/            # Home.tsx, Checkout.tsx
│   ├── components/       # ProductCard.tsx
│   └── App.test.tsx      # Vitest + Testing Library
└── .github/workflows/ci.yml
```

## Common workflows

| Command | What it does | Tested |
|---|---|---|
| `npm run dev` | Start the Vite dev server | ⟨untested⟩ |
| `npm run build` | Type-check (`tsc -b`) and build to `dist/` | ⟨untested⟩ |
| `npm run preview` | Serve the production build locally | ⟨untested⟩ |
| `npm run lint` | ESLint over the repo | ⟨untested⟩ |
| `npm test` | Run Vitest once (`vitest run`) | ⟨untested⟩ |

### Add a page

1. Create `src/pages/<Name>.tsx`, following `src/pages/Home.tsx`.
2. Register a route in `src/App.tsx`:

   ```tsx
   <Route path="/orders" element={<Orders />} />
   ```

3. Production needs no server change: `vercel.json` already rewrites every path to `/`.

### Use the brand styles

Use the Tailwind tokens from `tailwind.config.js` rather than raw hex values:
`bg-brand`, `text-brand-700`, `font-display` (Playfair Display) and `font-sans` (Poppins).

## Testing

```bash
npm test
```

`src/App.test.tsx` has 2 tests: the home page renders, and a placeholder for the checkout
route. See [Testing Strategy](testing-strategy.md).

## Debugging tips

- Vite only exposes variables prefixed with `VITE_` to the browser. A missing value reads as
  `undefined` rather than throwing, so check `.env` first when a feature silently fails.
- Sentry starts in `src/main.tsx` with `VITE_SENTRY_DSN`. Leave it empty locally to avoid
  sending development errors.
- `loadStripe` in `src/pages/Checkout.tsx` runs at module load. An invalid publishable key
  shows up in the browser console as soon as the checkout page is imported.

## Related documents

[Architecture](architecture.md) · [User Guide](user-guide.md) · [Testing Strategy](testing-strategy.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | Repository URL | assumption | no git remote in the repo | maintainer |
| A2 | Dev server port 5173 | assumption | Vite default, not configured | frontend lead |
| A3 | npm commands work as listed | assumption | dependencies not installed during generation | frontend lead |
| Q1 | Where does the backend behind `VITE_API_URL` live? | open question | not in this repo | engineering lead |
