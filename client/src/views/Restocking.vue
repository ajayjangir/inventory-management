<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Budget Slider -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
          <span class="budget-value">${{ budget.toLocaleString() }}</span>
        </div>
        <div class="slider-container">
          <span class="slider-label">$1,000</span>
          <input
            type="range"
            v-model.number="budget"
            min="1000"
            max="50000"
            step="500"
            class="budget-slider"
          />
          <span class="slider-label">$50,000</span>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <!-- Recommended Items Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }}</h3>
          <span class="lead-time-badge">{{ t('restocking.leadTime') }}</span>
        </div>
        <div v-if="recommendedItems.length === 0" class="no-items">
          {{ t('restocking.noItems') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('demand.table.sku') }}</th>
                <th>{{ t('demand.table.itemName') }}</th>
                <th>{{ t('restocking.demandGap') }}</th>
                <th>{{ t('restocking.unitCost') }}</th>
                <th>{{ t('restocking.recommendedQty') }}</th>
                <th>{{ t('restocking.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendedItems" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.demandGap }}</td>
                <td>${{ item.unit_cost.toFixed(2) }}</td>
                <td><strong>{{ item.quantity }}</strong></td>
                <td><strong>${{ item.lineTotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Summary Bar -->
        <div v-if="recommendedItems.length > 0" class="summary-bar">
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.totalItems') }}</span>
            <span class="summary-value">{{ totalQuantity }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.totalCost') }}</span>
            <span class="summary-value">${{ totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.remaining') }}</span>
            <span class="summary-value remaining">${{ remainingBudget.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          </div>
          <button
            class="place-order-btn"
            :disabled="submitting"
            @click="placeOrder"
          >
            {{ t('restocking.placeOrder') }}
          </button>
        </div>
      </div>

      <!-- Submitted Restocking Orders -->
      <div v-if="restockingOrders.length > 0" class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.submittedOrders') }} ({{ restockingOrders.length }})</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.orderNumber') }}</th>
                <th>{{ t('restocking.items') }}</th>
                <th>{{ t('restocking.status') }}</th>
                <th>{{ t('restocking.orderDate') }}</th>
                <th>{{ t('restocking.expectedDelivery') }}</th>
                <th>{{ t('restocking.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in restockingOrders" :key="order.id">
                <td><strong>{{ order.order_number }}</strong></td>
                <td>{{ order.items.length }} {{ t('common.items') }}</td>
                <td><span class="badge warning">{{ order.status }}</span></td>
                <td>{{ formatDate(order.order_date) }}</td>
                <td>{{ formatDate(order.expected_delivery) }}</td>
                <td><strong>${{ order.total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(10000)
    const submitting = ref(false)
    const successMessage = ref('')
    const restockingOrders = ref([])

    const recommendedItems = computed(() => {
      // Calculate demand gap and filter items with positive gap
      const itemsWithGap = forecasts.value
        .map(f => ({
          item_sku: f.item_sku,
          item_name: f.item_name,
          unit_cost: f.unit_cost,
          demandGap: f.forecasted_demand - f.current_demand
        }))
        .filter(item => item.demandGap > 0)
        .sort((a, b) => b.demandGap - a.demandGap)

      // Greedily fill budget
      let remaining = budget.value
      const result = []

      for (const item of itemsWithGap) {
        if (remaining < item.unit_cost) continue
        const qty = Math.min(item.demandGap, Math.floor(remaining / item.unit_cost))
        if (qty > 0) {
          const lineTotal = qty * item.unit_cost
          result.push({
            ...item,
            quantity: qty,
            lineTotal
          })
          remaining -= lineTotal
        }
      }

      return result
    })

    const totalQuantity = computed(() => {
      return recommendedItems.value.reduce((sum, item) => sum + item.quantity, 0)
    })

    const totalCost = computed(() => {
      return recommendedItems.value.reduce((sum, item) => sum + item.lineTotal, 0)
    })

    const remainingBudget = computed(() => {
      return budget.value - totalCost.value
    })

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const loadData = async () => {
      try {
        loading.value = true
        const [forecastsData, ordersData] = await Promise.all([
          api.getDemandForecasts(),
          api.getRestockingOrders()
        ])
        forecasts.value = forecastsData
        restockingOrders.value = ordersData
      } catch (err) {
        error.value = 'Failed to load data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      try {
        submitting.value = true
        successMessage.value = ''

        const orderData = {
          items: recommendedItems.value.map(item => ({
            item_sku: item.item_sku,
            item_name: item.item_name,
            quantity: item.quantity,
            unit_cost: item.unit_cost
          })),
          total_budget: budget.value
        }

        const newOrder = await api.submitRestockingOrder(orderData)
        restockingOrders.value.push(newOrder)
        successMessage.value = t('restocking.orderPlaced')

        setTimeout(() => {
          successMessage.value = ''
        }, 5000)
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      budget,
      recommendedItems,
      totalQuantity,
      totalCost,
      remainingBudget,
      submitting,
      successMessage,
      restockingOrders,
      placeOrder,
      formatDate
    }
  }
}
</script>

<style scoped>
.budget-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
}

.slider-label {
  font-size: 0.813rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}

.budget-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.success-message {
  background: #d1fae5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 0.875rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-weight: 500;
  font-size: 0.938rem;
}

.lead-time-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e40af;
  background: #dbeafe;
  padding: 0.313rem 0.75rem;
  border-radius: 6px;
}

.no-items {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 1.25rem;
  margin-top: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.summary-value.remaining {
  color: #059669;
}

.place-order-btn {
  margin-left: auto;
  padding: 0.625rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.938rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.place-order-btn:hover {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
