# Brain Map

An interactive, MindMeister-style mind map of **system-design interview concepts** for senior software engineers — covering scalability, CAP, databases, caching, messaging, sharding, microservices, resilience, observability, and decomposition strategies.

The map is rendered with [markmap](https://markmap.js.org/) and content is driven by a single structured JSON file, so you can grow the tree without touching the frontend code.

![Tree-style mind map preview](docs/image.png)

## Quick start (Docker)

Requires Docker (with Compose v2).

```sh
docker compose up -d --build
```

Then open <http://localhost:8088>.

To stop:

```sh
docker compose down
```

## Editing the content

All map content lives in [`public/mindmap.json`](public/mindmap.json). Edit nodes, save, then rebuild:

```sh
docker compose up -d --build
```

The schema is a recursive tree of `MindNode`:

```jsonc
{
  "title": "Root title",
  "subtitle": "Optional one-liner under the title (root only)",
  "children": [
    {
      "title": "A topic",
      "note": "Optional markdown note shown as an italic child node.",
      "children": [
        { "title": "A leaf" },
        {
          "title": "A nested topic",
          "children": [{ "title": "A deeper leaf", "note": "with an explanation" }]
        }
      ]
    }
  ]
}
```

If the JSON is malformed, the app shows an error overlay instead of a blank page.

## Features

- **Color-coded branches**, smooth pan & zoom (drag the canvas, scroll to zoom).
- **Expand / collapse** any node — click the node, or use the toolbar buttons for all-at-once.
- **Fit-to-view**, manual zoom in / out.
- **Light & dark theme**, persisted in `localStorage`.
- **Schema-validated** content with a friendly error overlay on malformed JSON.

## Local development (without Docker)

```sh
npm install
npm run dev          # http://localhost:5173 with HMR
npm run build        # type-check + production bundle in dist/
```

## Project structure

```
brain-map/
├── public/
│   └── mindmap.json          ← source of truth for content
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── components/
│   │   ├── MindMap.tsx       ← markmap renderer (SVG + ref-based controls)
│   │   └── Toolbar.tsx       ← header controls
│   └── lib/
│       ├── types.ts          ← MindNode / MindMapData types
│       ├── loadData.ts       ← fetch + runtime schema validation
│       └── jsonToMarkdown.ts ← tree → markmap-compatible markdown
├── docs/
│   ├── topics.md             ← original topic outline
│   └── image.png             ← layout reference
├── Dockerfile                ← multi-stage: node build → nginx serve
├── docker-compose.yml
└── nginx.conf                ← gzip, SPA fallback, no-cache for mindmap.json
```

## How it works

1. The app fetches `/mindmap.json` and validates the shape at runtime.
2. `jsonToMarkdown()` converts the tree to nested markdown bullets.
3. `markmap-lib` parses the markdown into a node tree.
4. `markmap-view` renders that tree as an interactive SVG with built-in pan/zoom and per-node fold state.
5. Toolbar controls walk the tree to set `payload.fold` for expand-all / collapse-all and call `Markmap` instance methods for `fit()` and `rescale()`.

## Tech stack

- **Vite + React 18 + TypeScript** — fast HMR, tiny prod bundle.
- **markmap-lib + markmap-view** — markdown → interactive SVG mind map.
- **Tailwind CSS** — utility-first styling, dark mode via class.
- **nginx:alpine** — small static server for the built SPA.
