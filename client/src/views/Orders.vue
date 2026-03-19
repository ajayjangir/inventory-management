<template>
  <div class="orders">
    <div class="page-header">
      <h2>{{ t('orders.title') }}</h2>
      <p>{{ t('orders.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card success">
          <div class="stat-label">{{ t('status.delivered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Delivered').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('status.shipped') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Shipped').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('status.processing') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Processing').length }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('status.backordered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Backordered').length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('orders.allOrders') }} ({{ orders.length }})</h3>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.table.orderNumber') }}</th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">{{ t('orders.table.expectedDelivery') }}</th>
                <th class="col-value">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="col-order-number"><strong>{{ order.order_number }}</strong></td>
                <td class="col-customer">{{ translateCustomerName(order.customer) }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="(item, idx) in order.items" :key="idx" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.name) }}</span>
                        <span class="item-meta">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_price }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date">{{ formatDate(order.order_date) }}</td>
                <td class="col-date">{{ formatDate(order.expected_delivery) }}</td>
                <td class="col-value"><strong>{{ currencySymbol }}{{ order.total_value.toLocaleString() }}</strong></td>
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
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Orders',
  setup() {
    const { t, currentCurrency, translateProductName, translateCustomerName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })
    const loading = ref(true)
    const error = ref(null)
    const orders = ref([])

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const loadOrders = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()
        const fetchedOrders = await api.getOrders(filters)

        // Sort orders by order_date (earliest first)
        orders.value = fetchedOrders.sort((a, b) => {
          const dateA = new Date(a.order_date)
          const dateB = new Date(b.order_date)
          return dateA - dateB
        })
      } catch (err) {
        error.value = 'Failed to load orders: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], () => {
      loadOrders()
    })

    const getOrdersByStatus = (status) => {
      return orders.value.filter(order => order.status === status)
    }

    const getOrderStatusClass = (status) => {
      const statusMap = {
        'Delivered': 'success',
        'Shipped': 'info',
        'Processing': 'warning',
        'Backordered': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(loadOrders)

    return {
      t,
      loading,
      error,
      orders,
      getOrdersByStatus,
      getOrderStatusClass,
      formatDate,
      currencySymbol,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
/* Page header */
.page-header {
  margin-bottom: var(--space-6, 24px);
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: var(--text-primary, #0f172a);
}

.page-header p {
  color: var(--text-muted, #64748b);
  font-size: 0.875rem;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-primary, white);
  padding: var(--space-5, 20px);
  border-radius: var(--radius-lg, 12px);
  border: 1px solid var(--border-default, #e2e8f0);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  transition: all 0.2s ease;
}

.stat-card.success {
  border-left: 4px solid var(--status-green, #10b981);
}

.stat-card.info {
  border-left: 4px solid var(--status-blue, #3b82f6);
}

.stat-card.warning {
  border-left: 4px solid var(--status-amber, #f59e0b);
}

.stat-card.danger {
  border-left: 4px solid var(--status-red, #ef4444);
}

.stat-label {
  color: var(--text-muted, #64748b);
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  letter-spacing: -0.025em;
}

.stat-card.success .stat-value {
  color: var(--status-green, #10b981);
}

.stat-card.info .stat-value {
  color: var(--status-blue, #3b82f6);
}

.stat-card.warning .stat-value {
  color: var(--status-amber, #f59e0b);
}

.stat-card.danger .stat-value {
  color: var(--status-red, #ef4444);
}

/* Card styling */
.orders .card {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-default, #e2e8f0);
  border-radius: var(--radius-lg, 12px);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  padding: var(--space-5, 20px);
}

.card-header {
  padding: 0 0 var(--space-5, 20px) 0;
  border-bottom: 1px solid var(--border-default, #e2e8f0);
  margin-bottom: var(--space-5, 20px);
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin: 0;
}

/* Table styling */
.table-container {
  overflow: hidden;
  border-radius: var(--radius-lg, 12px);
  border: 1px solid var(--border-default, #e2e8f0);
}

.table-container table thead {
  background: var(--bg-tertiary, #f1f5f9);
}

.table-container table th {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  padding: 0.75rem;
  color: var(--text-secondary, #334155);
}

.table-container table tbody tr {
  height: 48px;
}

.table-container table tbody tr:hover {
  background: var(--bg-secondary, #f8fafc);
}

.table-container table td {
  padding: 0.75rem;
}

/* Fixed table layout to prevent column shifting */
.orders-table {
  table-layout: fixed;
  width: 100%;
}

/* Column widths */
.col-order-number {
  width: 130px;
}

.col-customer {
  width: 180px;
}

.col-items {
  width: 200px;
}

.col-status {
  width: 130px;
}

.col-date {
  width: 140px;
}

.col-value {
  width: 120px;
}

/* Badge styling with semantic colors */
.badge {
  border-radius: var(--radius-sm, 6px);
  font-size: 12px;
  font-weight: 600;
  padding: 0.313rem 0.75rem;
}

.badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--status-green, #10b981);
}

.badge.info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--status-blue, #3b82f6);
}

.badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--status-amber, #f59e0b);
}

.badge.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-red, #ef4444);
}

/* Items details styling */
.items-details {
  position: relative;
}

.items-summary {
  cursor: pointer;
  color: var(--status-blue, #3b82f6);
  font-weight: 500;
  list-style: none;
  user-select: none;
  display: inline-block;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.375rem;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.items-details[open] .items-summary::before {
  transform: rotate(90deg);
}

.items-summary:hover {
  color: var(--accent, #2563eb);
  text-decoration: underline;
}

/* Dropdown container */
.items-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: var(--bg-primary, white);
  border: 1px solid var(--border-default, #e2e8f0);
  border-radius: var(--radius-md, 8px);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05));
  padding: 0.75rem;
  z-index: 10;
  min-width: 300px;
  max-width: 400px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--bg-tertiary, #f1f5f9);
}

.item-entry:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
}

.item-meta {
  font-size: 13px;
  color: var(--text-muted, #64748b);
}

.loading,
.error {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted, #64748b);
}

.error {
  color: var(--status-red, #ef4444);
}
</style>
