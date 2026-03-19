<template>
  <div>
    <!-- Mobile hamburger button -->
    <button
      v-if="isMobileView"
      class="hamburger-button"
      @click="toggleMobileSidebar"
      aria-label="Toggle menu"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>

    <!-- Backdrop for mobile -->
    <div
      v-if="isMobileView && isMobileOpen"
      class="backdrop"
      @click="closeMobileSidebar"
    ></div>

    <!-- Sidebar -->
    <aside
      class="sidebar"
      :class="{
        collapsed: effectiveCollapsed,
        'mobile-open': isMobileView && isMobileOpen
      }"
    >
      <!-- Header zone -->
      <div class="sidebar-header">
        <svg
          class="warehouse-icon"
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path d="M3 9L12 4L21 9V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V9Z" stroke="currentColor" stroke-width="2"/>
          <path d="M9 21V12H15V21" stroke="currentColor" stroke-width="2"/>
        </svg>
        <span class="app-name">InvenTrack</span>
      </div>

      <!-- Nav links zone -->
      <div class="nav-links-zone">
        <!-- MAIN Section -->
        <div class="section-label">MAIN</div>
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="3" y="3" width="6" height="6" stroke="currentColor" stroke-width="2" fill="none"/>
            <rect x="11" y="3" width="6" height="6" stroke="currentColor" stroke-width="2" fill="none"/>
            <rect x="3" y="11" width="6" height="6" stroke="currentColor" stroke-width="2" fill="none"/>
            <rect x="11" y="11" width="6" height="6" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          <span class="nav-label">{{ t('nav.overview') }}</span>
        </router-link>

        <router-link to="/inventory" class="nav-item" :class="{ active: $route.path === '/inventory' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 6L10 3L17 6V14C17 14.5304 16.7893 15.0391 16.4142 15.4142C16.0391 15.7893 15.5304 16 15 16H5C4.46957 16 3.96086 15.7893 3.58579 15.4142C3.21071 15.0391 3 14.5304 3 14V6Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M10 16V8" stroke="currentColor" stroke-width="2"/>
            <path d="M3 6L10 10L17 6" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span class="nav-label">{{ t('nav.inventory') }}</span>
        </router-link>

        <router-link to="/orders" class="nav-item" :class="{ active: $route.path === '/orders' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 3H5C3.89543 3 3 3.89543 3 5V15C3 16.1046 3.89543 17 5 17H15C16.1046 17 17 16.1046 17 15V5C17 3.89543 16.1046 3 15 3Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M7 7H13M7 10H13M7 13H10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span class="nav-label">{{ t('nav.orders') }}</span>
        </router-link>

        <!-- ANALYTICS Section -->
        <div class="section-label">ANALYTICS</div>
        <router-link to="/spending" class="nav-item" :class="{ active: $route.path === '/spending' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M10 6V10L13 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 3.5C8 3.5 9 3 10 3C11 3 12 3.5 12 3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span class="nav-label">{{ t('nav.finance') }}</span>
        </router-link>

        <router-link to="/demand" class="nav-item" :class="{ active: $route.path === '/demand' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 14L7 10L10 13L17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <path d="M13 6H17V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
          <span class="nav-label">{{ t('nav.demandForecast') }}</span>
        </router-link>

        <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 16V7M8 16V4M12 16V10M16 16V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>
          </svg>
          <span class="nav-label">Reports</span>
        </router-link>
      </div>

      <!-- Footer zone -->
      <div class="sidebar-footer">
        <button class="collapse-toggle" @click="toggleCollapse">
          <svg
            class="chevron-icon"
            :class="{ rotated: effectiveCollapsed }"
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
          >
            <path d="M12 6L8 10L12 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="nav-label">Collapse</span>
        </button>

        <div class="footer-controls">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="$emit('show-profile-details')"
            @show-tasks="$emit('show-tasks')"
          />
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

const { t } = useI18n()

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:collapsed', 'show-profile-details', 'show-tasks'])

// Responsive state
const isMobileView = ref(false)
const isTabletView = ref(false)
const isMobileOpen = ref(false)

// Effective collapsed state based on screen size
const effectiveCollapsed = computed(() => {
  if (isMobileView.value) return true
  if (isTabletView.value) return true
  return props.collapsed
})

const toggleCollapse = () => {
  if (!isMobileView.value && !isTabletView.value) {
    emit('update:collapsed', !props.collapsed)
  }
}

const toggleMobileSidebar = () => {
  isMobileOpen.value = !isMobileOpen.value
}

const closeMobileSidebar = () => {
  isMobileOpen.value = false
}

// Handle responsive behavior
const updateResponsiveState = () => {
  const width = window.innerWidth
  isMobileView.value = width < 768
  isTabletView.value = width >= 768 && width < 1024
}

let resizeObserver = null

onMounted(() => {
  updateResponsiveState()
  window.addEventListener('resize', updateResponsiveState)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateResponsiveState)
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 260px;
  background: var(--sidebar-bg);
  z-index: var(--z-sidebar);
  transition: width 0.2s ease, transform 0.2s ease;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--sidebar-border);
}

.sidebar.collapsed {
  width: 68px;
}

/* Header zone */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.warehouse-icon {
  color: var(--sidebar-text-active);
  flex-shrink: 0;
}

.app-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--sidebar-text-active);
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.15s ease;
}

.sidebar.collapsed .app-name {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

/* Nav links zone */
.nav-links-zone {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--sidebar-text);
  opacity: 0.5;
  padding: 16px 24px 8px;
  text-transform: uppercase;
  white-space: nowrap;
  transition: opacity 0.15s ease;
}

.sidebar.collapsed .section-label {
  opacity: 0;
  width: 0;
  height: 0;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 2px 8px;
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--sidebar-border);
  color: var(--sidebar-text-hover);
}

.nav-item.active {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
}

.nav-item svg {
  flex-shrink: 0;
}

.nav-label {
  opacity: 1;
  transition: opacity 0.15s ease;
  overflow: hidden;
}

.sidebar.collapsed .nav-label {
  opacity: 0;
  width: 0;
}

/* Footer zone */
.sidebar-footer {
  padding: 16px 8px;
  border-top: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.collapse-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 2px 0 12px 0;
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  width: 100%;
  font-family: inherit;
}

.collapse-toggle:hover {
  background: var(--sidebar-border);
  color: var(--sidebar-text-hover);
}

.chevron-icon {
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.footer-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Mobile */
.hamburger-button {
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 201;
  width: 48px;
  height: 48px;
  background: var(--sidebar-bg);
  border: none;
  border-radius: var(--radius-md);
  color: var(--sidebar-text-active);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
}

.hamburger-button:hover {
  background: var(--sidebar-border);
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 199;
}

/* Mobile sidebar behavior */
@media (max-width: 767px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
    width: 260px;
  }
}

/* Tablet and desktop - force collapsed on tablet */
@media (min-width: 768px) {
  .hamburger-button {
    display: none;
  }

  .backdrop {
    display: none;
  }
}
</style>
