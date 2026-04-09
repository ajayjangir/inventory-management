<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Restocking Planner</h2>
      <p>Set a budget and get prioritized restocking recommendations based on demand forecasts.</p>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="orderSuccess" class="success-state card">
      <div class="success-content">
        <div class="success-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="success-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3>Order Placed Successfully</h3>
        <p class="success-order-number">Order <strong>{{ orderNumber }}</strong> has been submitted.</p>
        <div class="success-actions">
          <router-link to="/orders" class="btn-primary">View in Orders</router-link>
          <button class="btn-secondary" @click="resetForm">Place Another Order</button>
        </div>
      </div>
    </div>
    <div v-else>
      <!-- Budget Section -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">Budget</h3>
          <span class="budget-display">{{ formatCurrency(budget) }}</span>
        </div>
        <div class="budget-slider-wrap">
          <span class="slider-label">$1,000</span>
          <input
            type="range"
            class="budget-slider"
            :min="1000"
            :max="50000"
            :step="500"
            v-model.number="budget"
          />
          <span class="slider-label">$50,000</span>
        </div>
        <div class="budget-meta">
          <span>Remaining: <strong :class="{ 'over-budget': remainingBudget < 0 }">{{ formatCurrency(remainingBudget) }}</strong></span>
        </div>
      </div>

      <!-- Recommendations Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recommended Items ({{ recommendations.length }})</h3>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          No items with positive demand gap found.
        </div>
        <div v-else class="table-container">
          <table class="restocking-table">
            <thead>
              <tr>
                <th class="col-sku">SKU</th>
                <th class="col-name">Item Name</th>
                <th class="col-gap">Demand Gap</th>
                <th class="col-trend">Trend</th>
                <th class="col-cost">Cost / Unit</th>
                <th class="col-qty">Qty</th>
                <th class="col-total">Line Total</th>
                <th class="col-include">Include</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in recommendations"
                :key="item.id"
                :class="{ 'row-excluded': !item.included }"
              >
                <td class="col-sku"><strong>{{ item.sku }}</strong></td>
                <td class="col-name">{{ item.name }}</td>
                <td class="col-gap">{{ item.demandGap }}</td>
                <td class="col-trend">
                  <span :class="['badge', trendBadgeClass(item.trend)]">{{ item.trend }}</span>
                </td>
                <td class="col-cost">{{ formatCurrency(item.unitCost) }}</td>
                <td class="col-qty">
                  <input
                    type="number"
                    class="qty-input"
                    :min="0"
                    :max="item.demandGap"
                    v-model.number="item.qty"
                    :disabled="!item.included"
                    @change="clampQty(item)"
                  />
                </td>
                <td class="col-total">
                  <strong>{{ formatCurrency(item.qty * item.unitCost) }}</strong>
                </td>
                <td class="col-include">
                  <input type="checkbox" v-model="item.included" class="include-checkbox" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Bar -->
      <div class="summary-bar card">
        <div class="summary-stats">
          <div class="summary-stat">
            <span class="summary-label">Items Selected</span>
            <span class="summary-value">{{ selectedItemsCount }}</span>
          </div>
          <div class="summary-stat">
            <span class="summary-label">Total Cost</span>
            <span class="summary-value">{{ formatCurrency(totalCost) }}</span>
          </div>
          <div class="summary-stat">
            <span class="summary-label">Remaining Budget</span>
            <span class="summary-value" :class="{ 'over-budget': remainingBudget < 0 }">{{ formatCurrency(remainingBudget) }}</span>
          </div>
        </div>
        <button
          class="btn-primary place-order-btn"
          :disabled="selectedItemsCount === 0 || remainingBudget < 0 || placing"
          @click="placeOrder"
        >
          {{ placing ? 'Placing Order...' : 'Place Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'

export default {
  name: 'Restocking',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const placing = ref(false)
    const orderSuccess = ref(false)
    const orderNumber = ref(null)

    const budget = ref(10000)
    const forecasts = ref([])
    const recommendations = ref([])

    // --- Helpers ---

    const formatCurrency = (value) => {
      return '$' + Math.round(value).toLocaleString('en-US')
    }

    const trendBadgeClass = (trend) => {
      if (trend === 'increasing') return 'success'
      if (trend === 'stable') return 'info'
      if (trend === 'decreasing') return 'warning'
      return 'info'
    }

    const clampQty = (item) => {
      if (item.qty < 0) item.qty = 0
      if (item.qty > item.demandGap) item.qty = item.demandGap
    }

    // --- Algorithm ---

    const buildRecommendations = () => {
      // 1. Filter forecasts with positive demand gap
      const eligible = forecasts.value
        .filter(f => f.forecasted_demand > f.current_demand)
        .map(f => {
          const demandGap = f.forecasted_demand - f.current_demand
          const unitCost = f.forecasted_demand
          const priorityScore = demandGap * (f.trend === 'increasing' ? 1.5 : 1.0)
          return {
            id: f.id,
            sku: f.item_sku,
            name: f.item_name,
            trend: f.trend,
            demandGap,
            unitCost,
            priorityScore
          }
        })

      // 2. Sort descending by priorityScore
      eligible.sort((a, b) => b.priorityScore - a.priorityScore)

      // 3. Greedy budget allocation
      let remaining = budget.value
      const result = eligible.map(item => {
        const qty = Math.min(Math.floor(remaining / item.unitCost), item.demandGap)
        if (qty > 0) {
          remaining -= qty * item.unitCost
        }
        return {
          ...item,
          qty: Math.max(qty, 0),
          included: qty > 0
        }
      })

      recommendations.value = result
    }

    // --- Computed ---

    const selectedItems = computed(() => {
      return recommendations.value.filter(item => item.included && item.qty > 0)
    })

    const selectedItemsCount = computed(() => selectedItems.value.length)

    const totalCost = computed(() => {
      return selectedItems.value.reduce((sum, item) => sum + item.qty * item.unitCost, 0)
    })

    const remainingBudget = computed(() => budget.value - totalCost.value)

    // --- Watch ---

    watch(budget, () => {
      buildRecommendations()
    })

    // --- Data Loading ---

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        forecasts.value = await api.getDemandForecasts()
        buildRecommendations()
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    // --- Actions ---

    const placeOrder = async () => {
      if (selectedItemsCount.value === 0 || remainingBudget.value < 0) return
      placing.value = true
      error.value = null
      try {
        const orderData = {
          items: selectedItems.value.map(item => ({
            sku: item.sku,
            name: item.name,
            quantity: item.qty,
            unit_price: item.unitCost
          })),
          total_value: totalCost.value
        }
        const response = await api.createRestockingOrder(orderData)
        orderNumber.value = response.order_number || response.id || 'RST-' + Date.now()
        orderSuccess.value = true
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
        console.error(err)
      } finally {
        placing.value = false
      }
    }

    const resetForm = () => {
      orderSuccess.value = false
      orderNumber.value = null
      budget.value = 10000
      buildRecommendations()
    }

    onMounted(() => loadData())

    return {
      loading,
      error,
      placing,
      orderSuccess,
      orderNumber,
      budget,
      recommendations,
      selectedItemsCount,
      totalCost,
      remainingBudget,
      formatCurrency,
      trendBadgeClass,
      clampQty,
      placeOrder,
      resetForm
    }
  }
}
</script>

<style scoped>
.restocking {
  padding: 2rem;
}

/* Budget Card */
.budget-card .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.budget-display {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0 0.75rem;
}

.slider-label {
  font-size: 0.813rem;
  color: #64748b;
  white-space: nowrap;
}

.budget-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
  transition: background 0.15s;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #2563eb;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

.budget-meta {
  font-size: 0.875rem;
  color: #64748b;
}

.over-budget {
  color: #ef4444 !important;
}

/* Table */
.restocking-table {
  table-layout: fixed;
  width: 100%;
}

.col-sku    { width: 120px; }
.col-name   { width: auto; }
.col-gap    { width: 110px; }
.col-trend  { width: 120px; }
.col-cost   { width: 110px; }
.col-qty    { width: 100px; }
.col-total  { width: 120px; }
.col-include { width: 80px; text-align: center; }

.row-excluded {
  opacity: 0.45;
}

.qty-input {
  width: 72px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #f8fafc;
  text-align: center;
}

.qty-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
}

.qty-input:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
}

.include-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

/* Summary Bar */
.summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
}

.summary-stats {
  display: flex;
  gap: 2.5rem;
  flex-wrap: wrap;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

/* Buttons */
.btn-primary {
  display: inline-block;
  padding: 0.625rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-block;
  padding: 0.625rem 1.5rem;
  background: white;
  color: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.btn-secondary:hover {
  background: #eff6ff;
}

.place-order-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

/* Success State */
.success-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 320px;
}

.success-content {
  text-align: center;
  max-width: 420px;
}

.success-icon-wrap {
  width: 64px;
  height: 64px;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem;
}

.success-icon {
  width: 32px;
  height: 32px;
  color: #059669;
}

.success-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.success-order-number {
  color: #64748b;
  margin-bottom: 1.75rem;
  font-size: 0.9375rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>
