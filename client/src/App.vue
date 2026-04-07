<template>
  <div class="app-layout">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="9" height="9" rx="2" fill="#3b82f6"/>
            <rect x="16" y="3" width="9" height="9" rx="2" fill="#3b82f6" opacity="0.6"/>
            <rect x="3" y="16" width="9" height="9" rx="2" fill="#3b82f6" opacity="0.6"/>
            <rect x="16" y="16" width="9" height="9" rx="2" fill="#3b82f6" opacity="0.3"/>
          </svg>
        </div>
        <span class="logo-text">Factory IMS</span>
      </div>

      <!-- Nav Links -->
      <nav class="sidebar-nav">
        <!-- Overview -->
        <router-link to="/" :class="['nav-item', { active: isActiveRoute('/') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M3 3h6v6H3V3zm8 0h6v6h-6V3zm-8 8h6v6H3v-6zm8 0h6v6h-6v-6z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
          </svg>
          <span class="nav-label">{{ t('nav.overview') }}</span>
          <span class="nav-tooltip">{{ t('nav.overview') }}</span>
        </router-link>

        <!-- Inventory -->
        <router-link to="/inventory" :class="['nav-item', { active: isActiveRoute('/inventory') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M3 7l7-4 7 4v8l-7 4-7-4V7z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
            <path d="M10 11V19M3 7l7 4 7-4" stroke="currentColor" stroke-width="1.5" fill="none"/>
          </svg>
          <span class="nav-label">{{ t('nav.inventory') }}</span>
          <span class="nav-tooltip">{{ t('nav.inventory') }}</span>
        </router-link>

        <!-- Orders -->
        <router-link to="/orders" :class="['nav-item', { active: isActiveRoute('/orders') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M7 3h6v2H7V3z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
            <rect x="4" y="4" width="12" height="14" rx="1" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M7 9h6M7 12h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="nav-label">{{ t('nav.orders') }}</span>
          <span class="nav-tooltip">{{ t('nav.orders') }}</span>
        </router-link>

        <!-- Finance -->
        <router-link to="/spending" :class="['nav-item', { active: isActiveRoute('/spending') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M4 17V11M8 17V7M12 17V10M16 17V5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="nav-label">{{ t('nav.finance') }}</span>
          <span class="nav-tooltip">{{ t('nav.finance') }}</span>
        </router-link>

        <!-- Demand -->
        <router-link to="/demand" :class="['nav-item', { active: isActiveRoute('/demand') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M3 17l4-4 3 2 7-8" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 7h3v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
          <span class="nav-label">{{ t('nav.demandForecast') }}</span>
          <span class="nav-tooltip">{{ t('nav.demandForecast') }}</span>
        </router-link>

        <!-- Reports -->
        <router-link to="/reports" :class="['nav-item', { active: isActiveRoute('/reports') }]">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav-icon">
            <path d="M6 3h7l4 4v10a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M13 3v4h4M8 10h4M8 13h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="nav-label">Reports</span>
          <span class="nav-tooltip">Reports</span>
        </router-link>
      </nav>

      <!-- Spacer -->
      <div class="sidebar-spacer"></div>

      <!-- Profile section -->
      <div class="sidebar-profile">
        <div class="profile-avatar">{{ getInitials(currentUser.name) }}</div>
        <div class="profile-info">
          <span class="profile-name">{{ currentUser.name }}</span>
          <span class="profile-role">{{ currentUser.jobTitle }}</span>
        </div>
      </div>

      <div class="sidebar-divider"></div>

      <!-- Collapse Toggle -->
      <button class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="toggle-icon" :class="{ rotated: sidebarCollapsed }">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="toggle-label">Collapse</span>
      </button>
    </aside>

    <div class="main-panel">
      <!-- Header -->
      <header class="top-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>

      <!-- Filter Bar -->
      <FilterBar />

      <!-- Content -->
      <main class="main-content">
        <AnimatedBackground />
        <router-view v-slot="{ Component }">
          <Transition :name="transitionName" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </Transition>
        </router-view>
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { usePageTransition } from './composables/usePageTransition'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AnimatedBackground from './components/AnimatedBackground.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    AnimatedBackground
  },
  setup() {
    const { currentUser, getInitials } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const { transitionName } = usePageTransition()

    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Sidebar collapse state — persisted in localStorage
    const storedCollapsed = localStorage.getItem('sidebarCollapsed')
    const sidebarCollapsed = ref(storedCollapsed === 'true')

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
    }

    const isActiveRoute = (path) => {
      if (path === '/') {
        return route.path === '/'
      }
      return route.path === path
    }

    const pageTitleMap = {
      '/': 'Dashboard',
      '/inventory': 'Inventory',
      '/orders': 'Orders',
      '/spending': 'Finance',
      '/demand': 'Demand Forecast',
      '/reports': 'Reports'
    }

    const pageTitle = computed(() => {
      return pageTitleMap[route.path] || 'Dashboard'
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)
        if (isMockTask) {
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)
        if (mockTask) {
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      currentUser,
      getInitials,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      sidebarCollapsed,
      toggleSidebar,
      isActiveRoute,
      pageTitle,
      transitionName
    }
  }
}
</script>

<style>
:root {
  --sidebar-bg: #0c111d;
  --sidebar-hover: rgba(255,255,255,0.04);
  --sidebar-active: rgba(59,130,246,0.08);
  --sidebar-text: #8896ab;
  --sidebar-text-active: #ffffff;
  --sidebar-accent: #3b82f6;
  --sidebar-divider: rgba(255,255,255,0.06);
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --header-height: 56px;
  --content-bg: #f1f5f9;
  --surface: #ffffff;
  --border: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --accent: #3b82f6;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--content-bg);
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ─── App Layout ─────────────────────────────────────────── */

.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ─── Sidebar ─────────────────────────────────────────────── */

.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: linear-gradient(180deg, #0c111d 0%, #111827 50%, #0c111d 100%);
  background-size: 100% 200%;
  animation: sidebar-gradient 8s ease infinite;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 200;
  overflow: hidden;
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              min-width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
  min-width: var(--sidebar-collapsed-width);
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid var(--sidebar-divider);
  min-height: 72px;
  overflow: hidden;
  flex-shrink: 0;
}

.logo-mark {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.15s ease;
  letter-spacing: -0.01em;
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  pointer-events: none;
}

/* Nav */
.sidebar-nav {
  padding: 12px 0;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 2px 10px;
  border-radius: 8px;
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
  position: relative;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: #c8d3e0;
}

.nav-item.active {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
  border-left-color: var(--sidebar-accent);
}

.nav-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.nav-label {
  opacity: 1;
  transition: opacity 0.15s ease;
  overflow: hidden;
}

.sidebar.collapsed .nav-label {
  opacity: 0;
  width: 0;
  pointer-events: none;
}

/* Tooltip shown when collapsed */
.nav-tooltip {
  display: none;
  position: absolute;
  left: calc(var(--sidebar-collapsed-width) + 8px);
  top: 50%;
  transform: translateY(-50%);
  background: #1e293b;
  color: #f1f5f9;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 6px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 300;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.nav-tooltip::before {
  content: '';
  position: absolute;
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-right-color: #1e293b;
}

.sidebar.collapsed .nav-item:hover .nav-tooltip {
  display: block;
}

/* Spacer */
.sidebar-spacer {
  flex: 1;
}

/* Profile */
.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  overflow: hidden;
}

.profile-avatar {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  opacity: 1;
  transition: opacity 0.15s ease;
}

.sidebar.collapsed .profile-info {
  opacity: 0;
  width: 0;
  pointer-events: none;
}

.profile-name {
  font-size: 0.813rem;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-role {
  font-size: 0.75rem;
  color: var(--sidebar-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Divider */
.sidebar-divider {
  height: 1px;
  background: var(--sidebar-divider);
  margin: 0 16px;
}

/* Collapse toggle */
.sidebar-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  background: none;
  border: none;
  color: var(--sidebar-text);
  cursor: pointer;
  font-size: 0.813rem;
  font-weight: 500;
  transition: color 0.15s ease;
  width: 100%;
  text-align: left;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  color: #c8d3e0;
}

.toggle-icon {
  flex-shrink: 0;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.toggle-label {
  opacity: 1;
  transition: opacity 0.15s ease;
  white-space: nowrap;
}

.sidebar.collapsed .toggle-label {
  opacity: 0;
  width: 0;
  pointer-events: none;
}

/* ─── Main Panel ─────────────────────────────────────────── */

.main-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
}

.app-layout:has(.sidebar.collapsed) .main-panel {
  margin-left: var(--sidebar-collapsed-width);
}

/* ─── Top Header ─────────────────────────────────────────── */

.top-header {
  height: var(--header-height);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ─── Main Content ───────────────────────────────────────── */

.main-content {
  flex: 1;
  padding: 24px;
  background: var(--content-bg);
}

/* ─── Global Component Styles ────────────────────────────── */

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.25rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.3s ease,
              border-color 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-6px) scale(1.02);
  border-color: #cbd5e1;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.625rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: #ea580c;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.danger .stat-value {
  color: #dc2626;
}

.stat-card.info .stat-value {
  color: #2563eb;
}

.card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  border: 1px solid var(--border);
  margin-bottom: 1.25rem;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8fafc;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: #475569;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 0.5rem 0.75rem;
  border-top: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.2s ease, transform 0.2s ease;
}

tbody tr:hover {
  background: #f0f7ff;
  transform: translateX(4px);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
  font-size: 0.938rem;
  animation: loading-pulse 1.5s ease-in-out infinite;
}

.loading::after {
  content: '';
  animation: loading-dots 1.5s steps(4, end) infinite;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}

/* ─── Route Transitions ─────────────────────────────────── */

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.97);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-60px) scale(0.97);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-60px) scale(0.97);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(60px) scale(0.97);
}

/* ─── Badge Pulse Animations ────────────────────────────── */

.badge.danger {
  animation: pulse-danger 2s ease-in-out infinite;
}

.badge.warning {
  animation: pulse-warning 2.5s ease-in-out infinite;
}

@keyframes pulse-danger {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
}

@keyframes pulse-warning {
  0%, 100% { box-shadow: 0 0 0 0 rgba(234, 88, 12, 0.3); }
  50% { box-shadow: 0 0 0 5px rgba(234, 88, 12, 0); }
}

/* ─── Loading Animation ─────────────────────────────────── */

@keyframes loading-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

@keyframes loading-dots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
}

/* ─── Sidebar Gradient ──────────────────────────────────── */

@keyframes sidebar-gradient {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 0% 100%; }
}

/* ─── Nav Active Indicator ──────────────────────────────── */

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px;
  height: 60%;
  background: var(--sidebar-accent);
  border-radius: 0 2px 2px 0;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-item.active::before {
  transform: translateY(-50%) scaleY(1);
}
</style>
