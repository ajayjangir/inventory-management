---
name: saas-redesign
description: Redesign a Vue 3 application into a modern SaaS-style interface with
  vertical sidebar navigation, refreshed design system, consistent spacing, and a
  polished professional look. Use when transforming a top-nav layout into a sidebar layout.
---

# SaaS Redesign Skill

## Overview

This skill transforms a Vue 3 application from a traditional top-navigation layout into a modern SaaS-style interface with:

- **Vertical sidebar navigation** replacing the top nav bar
- **Full design system refresh** — cards, tables, buttons, badges, spacing, shadows, typography
- **Responsive behavior** — collapsible sidebar, mobile overlay

### Prerequisites
- App must use Vue Router with a root layout component (typically `App.vue`)
- Vue 3 with Composition API

### Delegation Rule
**All `.vue` file creation or significant modification MUST be delegated to the `vue-expert` subagent.** Pass the relevant specs from this skill document as instructions.

---

## Phase 1 — Audit (Read-Only)

Before making any changes, analyze the existing app:

1. **Read root layout component** (usually `App.vue`) — identify nav structure, sticky elements, overall layout approach
2. **Read router config** (`router/index.js` or similar) — catalog all routes, their paths, names, and display labels
3. **Scan for z-index values** — search for `position: sticky`, `position: fixed`, and any top-nav height dependencies across all `.vue` files
4. **Identify nav-area components** — profile/avatar, settings, language selector, notifications, or any other elements currently in the top nav
5. **Note existing design patterns** — color scheme, spacing conventions, font stack, component styling approach

Document findings before proceeding to implementation phases.

---

## Design System Specification

Inject these CSS custom properties into the root layout component's `<style>` block:

### Spacing Scale (8px base)
```
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
```

### Colors

**Sidebar:**
| Token | Value | Usage |
|-------|-------|-------|
| `--sidebar-bg` | `#0f172a` | Sidebar background |
| `--sidebar-border` | `#1e293b` | Borders and hover backgrounds |
| `--sidebar-active` | `#1e3a5f` | Active nav item background |
| `--sidebar-text` | `#94a3b8` | Default nav text |
| `--sidebar-text-hover` | `#e2e8f0` | Hovered nav text |
| `--sidebar-text-active` | `#ffffff` | Active nav text |

**Content area:**
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#ffffff` | Main content background |
| `--bg-secondary` | `#f8fafc` | Card backgrounds, table header bg |
| `--bg-tertiary` | `#f1f5f9` | Table headers, subtle backgrounds |

**Text:**
| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | `#0f172a` | Headings, primary text |
| `--text-secondary` | `#334155` | Body text |
| `--text-muted` | `#64748b` | Captions, placeholders |

**Borders:**
| Token | Value | Usage |
|-------|-------|-------|
| `--border-default` | `#e2e8f0` | Standard borders |
| `--border-strong` | `#cbd5e1` | Emphasized borders |

**Accent & Status:**
| Token | Value | Usage |
|-------|-------|-------|
| `--accent` | `#2563eb` | Links, primary buttons, focus rings |
| `--status-green` | `#10b981` | Success, in-stock |
| `--status-amber` | `#f59e0b` | Warning, low-stock |
| `--status-red` | `#ef4444` | Error, critical |
| `--status-blue` | `#3b82f6` | Info, pending |

### Typography
- **Font stack**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Base size**: 14px
- **Weights**: 400 (body), 500 (labels/nav), 600 (subheadings/badges), 700 (headings)

### Shadows
```
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
```

### Border Radii
```
--radius-sm: 6px;   /* buttons, badges */
--radius-md: 8px;   /* inputs, nav items */
--radius-lg: 12px;  /* cards, modals */
```

### Z-Index Layers
```
--z-content: 1;
--z-sticky: 50;
--z-sidebar: 200;
--z-dropdown: 1000;
--z-modal: 2000;
```

---

## Phase 2 — Create SidebarNav Component

Create a new `SidebarNav.vue` component (delegate to `vue-expert`):

### Structure — Three Zones

1. **Header zone** (64px height): App logo/name, bordered bottom
2. **Nav links zone** (`flex: 1`, scrollable): Route links grouped by section
3. **Footer zone**: Profile/user info (relocated from old top nav) + collapse toggle button

### Behavior

- Each nav item is a `<router-link>` with:
  - Inline SVG icon (20x20, `stroke` based, `currentColor`) — choose appropriate icons per route
  - Text label
- **Active state**: determined by `$route.path` match — uses `--sidebar-active` background and `--sidebar-text-active` color
- **`v-model:collapsed`** boolean prop — toggles sidebar between 260px (expanded) and 68px (collapsed)
- **Section grouping**: small uppercase labels (e.g., "MAIN", "ANALYTICS") separating nav groups

### Styling

- `position: fixed; top: 0; left: 0; height: 100vh`
- Background: `--sidebar-bg`
- Smooth width transition: `transition: width 0.2s ease`
- Collapsed state: text hidden via `opacity: 0; width: 0; overflow: hidden` with transition
- Nav items: `border-radius: var(--radius-md)`, horizontal padding, `margin: 2px 8px`
- Hover: background `--sidebar-border`, text `--sidebar-text-hover`

---

## Phase 3 — Transform Root Layout

Modify `App.vue` (delegate to `vue-expert`):

1. Change root container from `flex-direction: column` to `flex-direction: row` (or equivalent layout shift)
2. **Remove the entire top navigation header block** — all its content has been relocated to sidebar or is no longer needed
3. Add `<SidebarNav v-model:collapsed="sidebarCollapsed" />` as the first child of the root container
4. Wrap remaining content (filters bar + `<router-view>`) in a `.main-area` wrapper div
5. `.main-area` styling:
   - `margin-left: 260px` (matches sidebar expanded width)
   - `transition: margin-left 0.2s ease` (syncs with sidebar collapse)
   - When `sidebarCollapsed` is true: `margin-left: 68px`
6. Add `sidebarCollapsed` ref: `const sidebarCollapsed = ref(false)`

---

## Phase 4 — Design System Refresh

Update existing component styles across the app (delegate each `.vue` file to `vue-expert`):

### Cards
- `border-radius: var(--radius-lg)` (12px)
- `box-shadow: var(--shadow-sm)`
- `border: 1px solid var(--border-default)`
- `padding: 20px`
- Optional subtle hover lift: `transform: translateY(-1px); box-shadow: var(--shadow-md)`

### Tables
- Rounded container wrapper with `overflow: hidden; border-radius: var(--radius-lg)`
- Header row: `background: var(--bg-tertiary)`, `font-size: 13px`, `font-weight: 600`, `text-transform: uppercase`, `letter-spacing: 0.025em`
- Row height: 48px comfortable spacing
- Hover row highlight: `background: var(--bg-secondary)`
- Border between rows: `1px solid var(--border-default)`

### Buttons
- `border-radius: var(--radius-sm)` (6px)
- `font-weight: 500`
- `padding: 8px 16px`
- **Primary**: `background: var(--accent)`, white text
- **Ghost/Outline**: transparent background, `border: 1px solid var(--border-default)`, `color: var(--text-secondary)`

### Badges / Status Indicators
- `border-radius: var(--radius-sm)` (6px)
- `font-size: 12px`, `font-weight: 600`
- Semantic color backgrounds at 10% opacity (e.g., green status = `rgba(16, 185, 129, 0.1)` bg with `#10b981` text)
- `padding: 4px 10px`

### Page Headers
- `font-size: 24px`, `font-weight: 700`
- `color: var(--text-primary)`
- Consistent `margin-bottom: 24px`

### Form Inputs / Selects
- `border-radius: var(--radius-md)` (8px)
- `border: 1px solid var(--border-default)`
- `padding: 8px 12px`
- Focus: `border-color: var(--accent)`, `box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1)`

### Stat / KPI Cards
- Consistent inner spacing using spacing tokens
- Optional subtle left-border accent color variant: `border-left: 3px solid var(--accent)`

---

## Phase 5 — Fix Dependencies

After the layout transformation, fix any broken dependencies:

1. **Filter bar positioning**: Change `top: 70px` (or whatever the old top-nav height was) to `top: 0` — there is no top nav above it anymore
2. **Remove orphaned CSS**: Delete any remaining top-nav CSS rules, unused nav-related classes
3. **Modal layering**: Verify modals (especially those using `<Teleport to="body">`) still render above sidebar with `z-index: var(--z-modal)` (2000)
4. **Dropdown positioning**: If any dropdown menus were positioned relative to the top nav, update their positioning context
5. **Content max-width**: Check that any `max-width` constraints on page content work correctly within the new `.main-area` context
6. **Scroll behavior**: Ensure `.main-area` scrolls independently (not the whole page including sidebar)

---

## Phase 6 — Responsive Behavior

Implement responsive breakpoints in `SidebarNav.vue` and `App.vue`:

### Breakpoints

**< 1024px (tablet):**
- Auto-collapse sidebar to 68px icon-only mode
- `.main-area` adjusts `margin-left` to 68px

**< 768px (mobile):**
- Hide sidebar completely off-screen (`transform: translateX(-100%)`)
- Show a hamburger button in a slim top bar (48px) inside `.main-area`
- Sidebar slides in as overlay on hamburger click
- Dark backdrop overlay behind sidebar (`rgba(0, 0, 0, 0.5)`)
- Tapping backdrop closes sidebar

### Implementation
- Use `matchMedia` listener in `SidebarNav` component's `onMounted`/`onUnmounted`
- CSS transitions on `width`, `margin-left`, `opacity`, `transform` — all `0.2s ease`
- Emit collapse state changes to parent so `.main-area` margin stays in sync

---

## Verification Checklist

After completing all phases, verify:

- [ ] All routes are navigable via sidebar links
- [ ] Active route is visually highlighted in sidebar
- [ ] Sidebar collapse/expand works with smooth animation
- [ ] Collapsed sidebar shows icons only (no text overflow)
- [ ] Filter bar functions correctly (no positioning issues)
- [ ] Modals and dropdowns layer properly above sidebar
- [ ] Cards have consistent border-radius, shadow, and padding
- [ ] Tables have rounded containers, styled headers, hover rows
- [ ] Badges use semantic colors with opacity backgrounds
- [ ] Buttons follow primary/ghost styling spec
- [ ] Page headers are consistent size and spacing
- [ ] Form inputs have correct border-radius and focus rings
- [ ] Responsive: sidebar auto-collapses at < 1024px
- [ ] Responsive: sidebar becomes overlay at < 768px
- [ ] No orphaned top-nav styles or dead CSS remain
- [ ] No console errors or Vue warnings
