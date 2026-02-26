<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Restocking Planner</h2>
      <p>Set a budget to restock high-demand items based on demand forecasts.</p>
    </div>

    <div v-if="loading" class="loading">Loading demand forecasts...</div>
    <div v-else-if="loadError" class="error">{{ loadError }}</div>
    <div v-else>

      <!-- Controls card -->
      <div class="card controls-card">
        <div class="controls-grid">
          <div class="control-row">
            <label class="control-label">Budget</label>
            <div class="slider-group">
              <input type="range" v-model.number="budget" :min="5000" :max="100000" :step="1000" class="budget-slider" />
              <span class="budget-value">${{ budget.toLocaleString() }}</span>
            </div>
            <span class="control-hint">$5K – $100K</span>
          </div>
          <div class="control-row">
            <label class="control-label">Lead Time</label>
            <div class="leadtime-group">
              <input type="number" v-model.number="leadTimeDays" :min="1" :max="365" class="leadtime-input" />
              <span class="leadtime-unit">days</span>
            </div>
            <span class="control-hint">Est. delivery: {{ expectedDeliveryDate }}</span>
          </div>
        </div>

        <div class="order-summary">
          <div class="summary-stats">
            <span><strong>{{ recommendations.length }}</strong> items selected</span>
            <span class="divider">|</span>
            <span>Est. cost: <strong>${{ totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></span>
            <span class="divider">|</span>
            <span>Remaining: <strong>${{ remainingBudget.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></span>
          </div>
          <button class="btn-primary" :disabled="recommendations.length === 0 || submitting" @click="placeOrder">
            {{ submitting ? 'Submitting...' : 'Place Order' }}
          </button>
        </div>
      </div>

      <!-- Success banner -->
      <div v-if="submitSuccess" class="success-banner">
        Order {{ lastOrderId }} submitted. Expected delivery: {{ lastDeliveryDate }}.
      </div>

      <!-- Error banner -->
      <div v-if="submitError" class="error">{{ submitError }}</div>

      <!-- Recommendations card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recommended Restocking ({{ recommendations.length }} items)</h3>
          <div class="budget-bar-wrap">
            <div class="budget-bar">
              <div class="budget-bar-fill" :class="budgetBarClass" :style="{ width: budgetUtilPct + '%' }"></div>
            </div>
            <span class="budget-bar-label">{{ budgetUtilPct }}% of budget used</span>
          </div>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          No items fit within the current budget. Try increasing the budget above ${{ minItemCost.toLocaleString() }}.
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Item Name</th>
                <th>Trend</th>
                <th>Demand Gap</th>
                <th>Qty to Order</th>
                <th>Unit Cost</th>
                <th>Line Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td><span :class="['badge', item.trend]">{{ item.trend }}</span></td>
                <td>{{ item.demand_gap > 0 ? '+' : '' }}{{ item.demand_gap }}</td>
                <td><strong>{{ item.quantity }}</strong></td>
                <td>${{ item.unit_cost.toFixed(2) }}</td>
                <td><strong>${{ item.line_total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="excluded.length > 0" class="excluded-section">
          <p class="excluded-title">Items excluded (insufficient budget)</p>
          <div class="excluded-list">
            <span v-for="item in excluded" :key="item.item_sku" class="excluded-chip">
              {{ item.item_sku }} — needs ${{ (item.forecasted_demand * item.unit_cost).toLocaleString() }}
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

export default {
  name: 'Restocking',
  setup() {
    const loading = ref(true)
    const loadError = ref(null)
    const forecasts = ref([])

    const budget = ref(50000)
    const leadTimeDays = ref(14)

    const submitting = ref(false)
    const submitSuccess = ref(false)
    const submitError = ref(null)
    const lastOrderId = ref('')
    const lastDeliveryDate = ref('')

    // Trend priority determines sort order: increasing items are highest priority
    const TREND_PRIORITY = { increasing: 0, stable: 1, decreasing: 2 }

    const sortedForecasts = computed(() => {
      return [...forecasts.value].sort((a, b) => {
        const trendDiff = TREND_PRIORITY[a.trend] - TREND_PRIORITY[b.trend]
        if (trendDiff !== 0) return trendDiff
        // Within the same trend tier, sort by demand gap descending
        const gapA = a.forecasted_demand - a.current_demand
        const gapB = b.forecasted_demand - b.current_demand
        return gapB - gapA
      })
    })

    // Greedy fill: include each item if its full line cost fits in the remaining budget.
    // Items are skipped (not partially filled) to keep order quantities clean.
    const recommendations = computed(() => {
      let remaining = budget.value
      const selected = []
      for (const item of sortedForecasts.value) {
        const lineCost = item.forecasted_demand * item.unit_cost
        if (lineCost <= remaining) {
          selected.push({
            item_sku: item.item_sku,
            item_name: item.item_name,
            trend: item.trend,
            demand_gap: item.forecasted_demand - item.current_demand,
            quantity: item.forecasted_demand,
            unit_cost: item.unit_cost,
            line_total: lineCost
          })
          remaining -= lineCost
        }
      }
      return selected
    })

    const excluded = computed(() => {
      const selectedSkus = new Set(recommendations.value.map(r => r.item_sku))
      return sortedForecasts.value.filter(f => !selectedSkus.has(f.item_sku))
    })

    const totalCost = computed(() => recommendations.value.reduce((sum, r) => sum + r.line_total, 0))
    const remainingBudget = computed(() => budget.value - totalCost.value)
    const budgetUtilPct = computed(() =>
      budget.value > 0 ? Math.min(100, Math.round((totalCost.value / budget.value) * 100)) : 0
    )
    const budgetBarClass = computed(() => {
      if (budgetUtilPct.value >= 90) return 'high'
      if (budgetUtilPct.value >= 60) return 'medium'
      return 'low'
    })
    const minItemCost = computed(() => {
      if (forecasts.value.length === 0) return 0
      return Math.min(...forecasts.value.map(f => f.forecasted_demand * f.unit_cost))
    })

    const expectedDeliveryDate = computed(() => {
      const d = new Date()
      d.setDate(d.getDate() + leadTimeDays.value)
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    })

    const loadForecasts = async () => {
      try {
        loading.value = true
        forecasts.value = await api.getDemandForecasts()
      } catch (err) {
        loadError.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      submitSuccess.value = false
      submitError.value = null
      submitting.value = true
      try {
        const result = await api.createRestockingOrder({
          budget: budget.value,
          lead_time_days: leadTimeDays.value,
          items: recommendations.value.map(r => ({
            item_sku: r.item_sku,
            item_name: r.item_name,
            trend: r.trend,
            quantity: r.quantity,
            unit_cost: r.unit_cost,
            line_total: r.line_total
          }))
        })
        lastOrderId.value = result.id
        lastDeliveryDate.value = result.expected_delivery_date
        submitSuccess.value = true
      } catch (err) {
        submitError.value = 'Failed to submit order: ' + (err.response?.data?.detail || err.message)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      loading, loadError,
      budget, leadTimeDays,
      recommendations, excluded,
      totalCost, remainingBudget, budgetUtilPct, budgetBarClass, minItemCost,
      expectedDeliveryDate,
      submitting, submitSuccess, submitError, lastOrderId, lastDeliveryDate,
      placeOrder
    }
  }
}
</script>

<style scoped>
.controls-card { margin-bottom: 1.25rem; }

.controls-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.control-row {
  display: grid;
  grid-template-columns: 110px 1fr auto;
  align-items: center;
  gap: 1rem;
}

.control-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.slider-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-slider {
  flex: 1;
  accent-color: #2563eb;
  cursor: pointer;
}

.budget-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 90px;
  text-align: right;
}

.leadtime-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.leadtime-input {
  width: 72px;
  padding: 0.35rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #0f172a;
  text-align: center;
}
.leadtime-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px #eff6ff;
}

.leadtime-unit {
  font-size: 0.85rem;
  color: #64748b;
}

.control-hint {
  font-size: 0.78rem;
  color: #94a3b8;
  white-space: nowrap;
}

.order-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
}

.summary-stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: #334155;
}

.divider { color: #cbd5e1; }

.btn-primary {
  padding: 0.6rem 1.5rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }

.success-banner {
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 0.875rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.budget-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.budget-bar {
  width: 160px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.budget-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.25s ease;
}
.budget-bar-fill.low    { background: #10b981; }
.budget-bar-fill.medium { background: #f59e0b; }
.budget-bar-fill.high   { background: #ef4444; }

.budget-bar-label {
  font-size: 0.78rem;
  color: #64748b;
  white-space: nowrap;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
}

.excluded-section {
  padding: 1rem 1.25rem;
  border-top: 1px solid #f1f5f9;
}

.excluded-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.6rem;
}

.excluded-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.excluded-chip {
  font-size: 0.78rem;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

/* Trend badge colors */
.badge.increasing { background: #d1fae5; color: #065f46; }
.badge.stable     { background: #dbeafe; color: #1e40af; }
.badge.decreasing { background: #fee2e2; color: #991b1b; }
</style>
