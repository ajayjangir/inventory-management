<template>
  <div class="backlog">
    <div class="page-header">
      <h2>Backlog Management</h2>
      <p>Track and resolve inventory shortages</p>
    </div>

    <div v-if="loading" class="loading">Loading backlog...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card danger">
          <div class="stat-label">High Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('high').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">Medium Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('medium').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">Low Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('low').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Backlog Items</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Backlog Items</h3>
        </div>
        <div v-if="backlogItems.length === 0" style="padding: 3rem; text-align: center;">
          <p style="font-size: 1.125rem; color: #10b981; font-weight: 600;">
            ✓ No backlog items - all orders can be fulfilled!
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>SKU</th>
                <th>Item Name</th>
                <th>Quantity Needed</th>
                <th>Quantity Available</th>
                <th>Shortage</th>
                <th>Days Delayed</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td><strong>{{ item.order_id }}</strong></td>
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ item.quantity_needed - item.quantity_available }} units short
                  </span>
                </td>
                <td>
                  <span :style="{ color: item.days_delayed > 7 ? '#ef4444' : '#f59e0b' }">
                    {{ item.days_delayed }} days
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ item.priority }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'

export default {
  name: 'Backlog',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const allBacklogItems = ref([])
    const inventoryItems = ref([])

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allBacklogItems.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allBacklogItems.value.filter(b => validSkus.has(b.item_sku))
    })

    const loadBacklog = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()

        const [backlogData, inventoryData] = await Promise.all([
          api.getBacklog(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category
          })
        ])

        allBacklogItems.value = backlogData
        inventoryItems.value = inventoryData
      } catch (err) {
        error.value = 'Failed to load backlog: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const getBacklogByPriority = (priority) => {
      return backlogItems.value.filter(item => item.priority === priority)
    }

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadBacklog()
    })

    onMounted(loadBacklog)

    return {
      loading,
      error,
      backlogItems,
      getBacklogByPriority
    }
  }
}
</script>

<style scoped>
.backlog {
  padding: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-primary, #ffffff);
  border-radius: var(--radius-lg, 12px);
  padding: 20px;
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  border: 1px solid var(--border-default, #e2e8f0);
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05));
}

.stat-card.danger {
  border-left: 3px solid var(--status-red, #ef4444);
}

.stat-card.warning {
  border-left: 3px solid var(--status-amber, #f59e0b);
}

.stat-card.info {
  border-left: 3px solid var(--status-blue, #3b82f6);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #64748b);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

.card {
  background: var(--bg-primary, #ffffff);
  border-radius: var(--radius-lg, 12px);
  padding: 20px;
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  border: 1px solid var(--border-default, #e2e8f0);
  transition: all 0.2s ease;
}

.card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05));
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin: 0;
}

.table-container {
  overflow: hidden;
  border-radius: var(--radius-lg, 12px);
  border: 1px solid var(--border-default, #e2e8f0);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--bg-tertiary, #f1f5f9);
}

th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--text-secondary, #334155);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  border-bottom: 1px solid var(--border-default, #e2e8f0);
  height: 48px;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-default, #e2e8f0);
  height: 48px;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--bg-secondary, #f8fafc);
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-sm, 6px);
  font-size: 12px;
  font-weight: 600;
}

.badge.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-red, #ef4444);
}

.badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-red, #ef4444);
}

.badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}

.badge.low {
  background: rgba(59, 130, 246, 0.1);
  color: var(--status-blue, #3b82f6);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted, #64748b);
}

.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-red, #ef4444);
  padding: 1rem;
  border-radius: var(--radius-md, 8px);
  margin: 1rem 0;
  border: 1px solid var(--border-default, #e2e8f0);
}
</style>
