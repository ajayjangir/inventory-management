<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Restocking Planner</h2>
      <p>Set a budget, review recommended items, and place a restocking order.</p>
    </div>

    <!-- Success State -->
    <div v-if="orderResult" class="card success-card">
      <div class="success-content">
        <div class="success-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="24" r="24" fill="#d1fae5"/>
            <path d="M14 24l8 8 12-14" stroke="#059669" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="success-details">
          <h3>Order Submitted</h3>
          <p>
            Order <strong>{{ orderResult.order_number }}</strong> has been placed.
            Expected delivery in {{ orderResult.lead_time_days }} days
            ({{ formatDate(orderResult.expected_delivery) }}).
          </p>
          <div class="success-meta">
            <span class="badge success">{{ orderResult.status }}</span>
            <span class="success-total">Total value: ${{ orderResult.total_value.toLocaleString() }}</span>
          </div>
        </div>
      </div>
      <button class="btn btn-secondary" @click="resetForm">Place Another Order</button>
    </div>

    <!-- Main Form -->
    <template v-else>
      <!-- Budget Slider Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Set Budget</h3>
          <span class="budget-display">{{ formatCurrency(budget) }}</span>
        </div>

        <div class="slider-section">
          <div class="slider-labels">
            <span>$0</span>
            <span>$50,000</span>
          </div>
          <input
            type="range"
            class="budget-slider"
            min="0"
            max="50000"
            step="1000"
            v-model.number="budget"
          />
        </div>

        <div class="budget-summary" v-if="!loadingRecs && recommendations.length > 0">
          <div class="budget-item">
            <span class="budget-label">Budget</span>
            <span class="budget-value">{{ formatCurrency(budget) }}</span>
          </div>
          <div class="budget-item">
            <span class="budget-label">Allocated</span>
            <span class="budget-value warning-text">{{ formatCurrency(selectedTotalCost) }}</span>
          </div>
          <div class="budget-item">
            <span class="budget-label">Remaining</span>
            <span class="budget-value" :class="remainingBudget < 0 ? 'danger-text' : 'success-text'">
              {{ formatCurrency(remainingBudget) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Recommendations Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recommended Items</h3>
          <div class="header-actions" v-if="!loadingRecs && recommendations.length > 0">
            <button class="btn btn-text" @click="selectAll">Select All</button>
            <button class="btn btn-text" @click="deselectAll">Deselect All</button>
          </div>
        </div>

        <div v-if="loadingRecs" class="loading">Loading recommendations...</div>
        <div v-else-if="recsError" class="error">{{ recsError }}</div>
        <div v-else-if="recommendations.length === 0" class="empty-state">
          No recommendations available for this budget. Try increasing the budget.
        </div>
        <div v-else>
          <div class="table-container">
            <table class="recs-table">
              <thead>
                <tr>
                  <th class="col-check"></th>
                  <th class="col-name">Item Name</th>
                  <th class="col-sku">SKU</th>
                  <th class="col-trend">Trend</th>
                  <th class="col-qty">Forecasted Qty</th>
                  <th class="col-unit">Unit Cost</th>
                  <th class="col-total">Total Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in recommendations"
                  :key="item.sku"
                  :class="{ 'row-unchecked': !selectedSkus.has(item.sku) }"
                >
                  <td class="col-check">
                    <input
                      type="checkbox"
                      :checked="selectedSkus.has(item.sku)"
                      @change="toggleItem(item.sku)"
                    />
                  </td>
                  <td class="col-name"><strong>{{ item.name }}</strong></td>
                  <td class="col-sku"><code>{{ item.sku }}</code></td>
                  <td class="col-trend">
                    <span :class="['badge', trendClass(item.trend)]">{{ item.trend }}</span>
                  </td>
                  <td class="col-qty">{{ item.forecasted_demand.toLocaleString() }}</td>
                  <td class="col-unit">${{ item.unit_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
                  <td class="col-total"><strong>${{ item.total_cost.toLocaleString() }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="order-footer">
            <div class="selection-summary">
              {{ selectedCount }} of {{ recommendations.length }} items selected
              &mdash; {{ formatCurrency(selectedTotalCost) }} total
            </div>
            <button
              class="btn btn-primary"
              :disabled="selectedCount === 0 || submitting"
              @click="placeOrder"
            >
              {{ submitting ? 'Placing Order...' : 'Place Order' }}
            </button>
          </div>

          <div v-if="orderError" class="error order-error">{{ orderError }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { currentCurrency } = useI18n()

    // Budget state
    const budget = ref(25000)

    // Recommendations state
    const recommendations = ref([])
    const loadingRecs = ref(false)
    const recsError = ref(null)

    // Selection state: Set of selected SKUs
    const selectedSkus = ref(new Set())

    // Order submission state
    const submitting = ref(false)
    const orderError = ref(null)
    const orderResult = ref(null)

    // Debounce timer handle
    let debounceTimer = null

    const loadRecommendations = async () => {
      loadingRecs.value = true
      recsError.value = null
      try {
        const data = await api.getRestockingRecommendations(budget.value)
        recommendations.value = data.recommendations || []
        // Default: all items selected
        selectedSkus.value = new Set(recommendations.value.map(item => item.sku))
      } catch (err) {
        recsError.value = 'Failed to load recommendations: ' + (err.response?.data?.detail || err.message)
        recommendations.value = []
        selectedSkus.value = new Set()
      } finally {
        loadingRecs.value = false
      }
    }

    // Watch budget with 300ms debounce
    watch(budget, () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        loadRecommendations()
      }, 300)
    }, { immediate: true })

    // Computed: total cost of selected items
    const selectedTotalCost = computed(() => {
      return recommendations.value
        .filter(item => selectedSkus.value.has(item.sku))
        .reduce((sum, item) => sum + item.total_cost, 0)
    })

    const remainingBudget = computed(() => budget.value - selectedTotalCost.value)

    const selectedCount = computed(() => selectedSkus.value.size)

    const selectedItems = computed(() => {
      return recommendations.value
        .filter(item => selectedSkus.value.has(item.sku))
        .map(item => ({
          sku: item.sku,
          name: item.name,
          quantity: item.forecasted_demand,
          unit_cost: item.unit_cost,
          total_cost: item.total_cost
        }))
    })

    const toggleItem = (sku) => {
      const next = new Set(selectedSkus.value)
      if (next.has(sku)) {
        next.delete(sku)
      } else {
        next.add(sku)
      }
      selectedSkus.value = next
    }

    const selectAll = () => {
      selectedSkus.value = new Set(recommendations.value.map(item => item.sku))
    }

    const deselectAll = () => {
      selectedSkus.value = new Set()
    }

    const trendClass = (trend) => {
      const map = {
        increasing: 'success',
        stable: 'stable',
        decreasing: 'info'
      }
      return map[trend?.toLowerCase()] || 'stable'
    }

    const formatCurrency = (value) => {
      if (currentCurrency.value === 'JPY') {
        return '¥' + Math.round(value).toLocaleString()
      }
      return '$' + value.toLocaleString()
    }

    const formatDate = (dateString) => {
      const d = new Date(dateString)
      if (isNaN(d.getTime())) return dateString
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    }

    const placeOrder = async () => {
      if (selectedCount.value === 0 || submitting.value) return
      submitting.value = true
      orderError.value = null
      try {
        const result = await api.createRestockingOrder({
          items: selectedItems.value,
          budget: budget.value
        })
        orderResult.value = result
      } catch (err) {
        orderError.value = 'Failed to place order: ' + (err.response?.data?.detail || err.message)
      } finally {
        submitting.value = false
      }
    }

    const resetForm = () => {
      orderResult.value = null
      orderError.value = null
      budget.value = 25000
      // loadRecommendations will be triggered by the watch
    }

    return {
      budget,
      recommendations,
      loadingRecs,
      recsError,
      selectedSkus,
      submitting,
      orderError,
      orderResult,
      selectedTotalCost,
      remainingBudget,
      selectedCount,
      toggleItem,
      selectAll,
      deselectAll,
      trendClass,
      formatCurrency,
      formatDate,
      placeOrder,
      resetForm
    }
  }
}
</script>

<style scoped>
.restocking {
  padding: 0;
}

/* Budget slider */
.budget-display {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.slider-section {
  padding: 0.75rem 0 1rem;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.813rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.budget-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #2563eb;
  transition: box-shadow 0.2s;
}

.budget-slider::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #2563eb;
}

/* Budget summary row */
.budget-summary {
  display: flex;
  gap: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 0.5rem;
}

.budget-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.budget-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.budget-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.warning-text { color: #ea580c; }
.success-text { color: #059669; }
.danger-text  { color: #dc2626; }

/* Table */
.recs-table {
  table-layout: fixed;
  width: 100%;
}

.col-check { width: 44px; }
.col-name  { width: 220px; }
.col-sku   { width: 120px; }
.col-trend { width: 110px; }
.col-qty   { width: 130px; }
.col-unit  { width: 110px; }
.col-total { width: 120px; }

.row-unchecked td {
  opacity: 0.45;
}

code {
  font-family: 'SF Mono', 'Fira Code', 'Fira Mono', monospace;
  font-size: 0.813rem;
  color: #475569;
}

/* Header actions */
.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Order footer */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0.75rem 0;
  border-top: 1px solid #e2e8f0;
  margin-top: 0.5rem;
}

.selection-summary {
  font-size: 0.875rem;
  color: #64748b;
}

.order-error {
  margin-top: 0.75rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #f1f5f9;
  color: #0f172a;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-text {
  background: transparent;
  color: #2563eb;
  padding: 0.25rem 0.625rem;
  font-size: 0.813rem;
}

.btn-text:hover {
  background: #eff6ff;
}

/* Empty state */
.empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

/* Success card */
.success-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.success-content {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
}

.success-icon {
  flex-shrink: 0;
}

.success-details h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.375rem;
}

.success-details p {
  color: #475569;
  font-size: 0.938rem;
  margin-bottom: 0.75rem;
}

.success-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.success-total {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}
</style>
