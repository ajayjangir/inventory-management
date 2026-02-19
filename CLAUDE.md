# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Factory Inventory Management System — a full-stack demo app for inventory tracking, order management, demand forecasting, and spending analytics. Uses in-memory mock data (no database).

## Tech Stack

- **Frontend**: Vue 3 (Composition API) + Vite + Vue Router + Axios (port 3000)
- **Backend**: Python FastAPI + Pydantic + Uvicorn (port 8001)
- **Package Management**: npm (client), uv (server)
- **Testing**: pytest with FastAPI TestClient

## Commands

### Start/Stop Servers
```bash
./scripts/start.sh          # Start both backend and frontend
./scripts/stop.sh           # Stop both servers
```

### Manual Startup
```bash
# Backend
cd server && uv run python main.py

# Frontend
cd client && npm run dev
```

### Run Tests
```bash
cd tests && uv run pytest                                    # All tests
cd tests && uv run pytest backend/test_inventory.py -v       # Single file
cd tests && uv run pytest backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory -v  # Single test
cd tests && uv run pytest --cov=../server --cov-report=html  # With coverage
```

### Build
```bash
cd client && npm run build   # Output: client/dist/
```

## Architecture

### Backend (`server/`)

Single-file API in `main.py` — all endpoints, Pydantic models, and filtering logic live here. Data is loaded from `server/data/*.json` at startup via `mock_data.py` and held in memory.

Key patterns:
- `apply_filters()` handles warehouse/category/status filtering across endpoints
- `filter_by_month()` handles date filtering including quarter support (Q1-2025 format)
- Filter params use `'all'` as the "no filter" sentinel value
- All filter comparisons are case-insensitive for category

### Frontend (`client/src/`)

- **Views** (`views/`): Page-level components — Dashboard, Inventory, Orders, Demand, Spending, Reports
- **Components** (`components/`): Reusable UI — FilterBar, detail modals, ProfileMenu, LanguageSwitcher
- **Composables** (`composables/`): Shared state — `useFilters.js` (global filter singleton), `useAuth.js`, `useI18n.js`
- **API layer** (`api.js`): Centralized axios client, all backend calls go through here
- **i18n** (`locales/`): English and Japanese translations
- **Routing** (`main.js`): Vue Router with routes defined inline

Global filter state in `useFilters.js` is a singleton (module-level refs shared across all components). The `FilterBar` component sets filters, and views watch/use them to reload data.

### Tests (`tests/`)

Backend API tests only. Uses `conftest.py` to create a FastAPI TestClient fixture. Tests are organized by endpoint group: `test_inventory.py`, `test_dashboard.py`, `test_misc_endpoints.py`. The pytest config is in `tests/pytest.ini` — tests must be run from the `tests/` directory.

### API Endpoints

All endpoints under `/api/`. Interactive API docs at `http://localhost:8001/docs`.

- `GET /api/inventory` - Filters: warehouse, category
- `GET /api/orders` - Filters: warehouse, category, status, month
- `GET /api/dashboard/summary` - All filters
- `GET /api/demand`, `/api/backlog` - No filters
- `GET /api/spending/*` - Summary, monthly, categories, transactions

## Conventions

- Vue components use Composition API with `setup()` (not `<script setup>`)
- Scoped styles in Vue components
- Pydantic models defined in `main.py` alongside endpoints
- Filter param value `'all'` means "no filter" on both frontend and backend
- Frontend maps `selectedLocation` to `warehouse` query param in API calls
- Always document non-obvious logic changes with comments
