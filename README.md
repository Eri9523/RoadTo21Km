# RoadTo21Km

Monorepo for the RoadTo21Km web app and Python backend.

Start with the [product specifications](specs/README.md) before making changes.

## Development

- Web: `npm install` then `npm run dev:web`
- Backend: `uv sync` then `uv run --package roadto21km-backend python -c "import api, models, services, shared"`
