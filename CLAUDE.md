# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System — Full-stack demo with Vue 3 frontend, Python FastAPI backend, and in-memory mock data (no database). Supports English and Japanese (i18n).

## Critical Tool Usage Rules

### Subagents
- **vue-expert**: **MANDATORY** for creating or significantly modifying any `.vue` file. Also use for reactivity issues, styling, and client-side functionality.
- **code-reviewer**: Use after writing significant code to review quality
- **Explore**: Use for understanding codebase structure or searching for patterns
- **general-purpose**: Use for complex multi-step tasks when other agents don't fit

### Skills
- **backend-api-test**: Use when writing or modifying tests in `tests/backend/` with pytest and FastAPI TestClient

### MCP Tools
- **ALWAYS use GitHub MCP tools** (`mcp__github__*`) for ALL GitHub operations (exception: local branches use `git checkout -b`)
- **ALWAYS use Playwright MCP tools** (`mcp__playwright__*`) for browser testing against `http://localhost:3000` (frontend) and `http://localhost:8001` (API)

## Commands

```bash
# Start everything (one command)
./scripts/start.sh          # Installs deps if needed, starts both servers in background
./scripts/stop.sh           # Stop both servers

# Backend (manual)
cd server && uv run python main.py      # Starts on port 8001

# Frontend (manual)
cd client && npm install && npm run dev  # Starts on port 3000

# Tests (from project root)
cd tests && uv run pytest -v                                    # All 51 tests
cd tests && uv run pytest backend/test_inventory.py             # Single file
cd tests && uv run pytest backend/test_orders.py::TestOrderEndpoints::test_get_all_orders  # Single test
cd tests && uv run pytest --cov=../server --cov-report=html     # Coverage report

# Frontend build
cd client && npm run build   # Production build to dist/
```

## Architecture

### Stack
- **Frontend**: Vue 3 + Composition API + Vite (port 3000), Axios for HTTP
- **Backend**: Python FastAPI + Uvicorn (port 8001), Pydantic validation
- **Data**: JSON files in `server/data/` loaded into memory at startup via `server/mock_data.py` — no persistence

### Data Flow
```
FilterBar.vue → useFilters composable (shared singleton state)
  → View watches filter refs → calls api.js with {warehouse, category, status, month}
  → api.js builds URLSearchParams (skips 'all' values)
  → FastAPI apply_filters() + filter_by_month() on in-memory data
  → Pydantic model validation → JSON response
  → Vue ref updated → computed properties derive display data
```

### Filter System
4 global filters managed by `useFilters` composable (shared across all views):
- **Time Period**: Month (`2025-01`) or quarter (`Q1-2025`, expanded server-side to 3 months)
- **Warehouse**: San Francisco, London, Tokyo
- **Category**: Circuit Boards, Sensors, Actuators, Controllers, Power Supplies
- **Order Status**: Delivered, Shipped, Processing, Backordered

Not all endpoints support all filters — inventory has no time dimension, demand/backlog have no filters.

### View Pattern
Every view follows: `useFilters()` composable → `loading/error/data` refs → `loadData()` async function → `onMounted` + `watch` on filter refs → computed properties for derived display data.

### I18n
Two locales (`client/src/locales/`): English and Japanese. Currency auto-maps by locale (USD/JPY). `useI18n` composable provides `t()` for translations with `{key}` placeholder syntax.

### Router
Defined in `client/src/main.js` with Vue Router 4 (history mode):
`/` Dashboard, `/inventory`, `/orders`, `/demand`, `/spending`, `/reports`

## API Endpoints
- `GET /api/inventory` — warehouse, category filters
- `GET /api/inventory/{item_id}`
- `GET /api/orders` — warehouse, category, status, month filters
- `GET /api/orders/{order_id}`
- `GET /api/dashboard/summary` — all filters
- `GET /api/demand` — no filters
- `GET /api/backlog` — no filters
- `GET /api/spending/summary|monthly|categories|transactions`
- `GET /api/reports/quarterly|monthly-trends`
- `POST /api/purchase-orders`, `GET /api/purchase-orders/{backlog_item_id}`
- `GET|POST|DELETE|PATCH /api/tasks` — CRUD for tasks
- Swagger docs at `http://localhost:8001/docs`

## Code Guidelines
- Always document non-obvious logic changes with comments

## Common Issues
1. Use unique keys in `v-for` (`sku`, `month`, etc.) — never use `index`
2. Validate dates before `.getMonth()` calls
3. Update Pydantic models in `server/main.py` when changing JSON data structure
4. Inventory filters don't support month (no time dimension)
5. Revenue goals: $800K/month single warehouse, $9.6M YTD all months
6. Category filtering is case-insensitive on the backend
7. Data doesn't persist — all changes lost on server restart

## Design System
- Colors: Slate/gray palette (#0f172a, #64748b, #e2e8f0)
- Status colors: green (delivered), blue (shipped), yellow (processing), red (backordered)
- Charts: Custom SVG, CSS Grid layouts
- No emojis in UI
