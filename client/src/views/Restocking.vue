<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>

      <!-- Budget Slider Card -->
      <div class="card budget-card">
        <div class="budget-card-header">
          <h3 class="card-title">{{ t('restocking.budgetSlider.label') }}</h3>
          <div class="budget-display">{{ formatCurrency(budget) }}</div>
        </div>
        <div class="slider-container">
          <input
            type="range"
            v-model.number="budget"
            :min="1000"
            :max="50000"
            :step="500"
            class="budget-slider"
          />
          <div class="slider-labels">
            <span>$1,000</span>
            <span>$50,000</span>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.summary.totalItems') }}</div>
          <div class="stat-value">{{ totalItems }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.summary.totalUnits') }}</div>
          <div class="stat-value">{{ totalUnits.toLocaleString() }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.summary.totalCost') }}</div>
          <div class="stat-value">{{ formatCurrency(totalCost) }}</div>
        </div>
        <div class="stat-card" :class="budgetRemaining < 0 ? 'danger' : 'success'">
          <div class="stat-label">{{ t('restocking.summary.budgetRemaining') }}</div>
          <div class="stat-value">{{ formatCurrency(budgetRemaining) }}</div>
        </div>
      </div>

      <!-- Recommendations Table Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendations.length }})</h3>
        </div>

        <div v-if="recommendations.length === 0" class="no-recommendations">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.demandGap') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.recommendedQty') }}</th>
                <th>{{ t('restocking.table.totalCost') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.demand_gap.toLocaleString() }}</td>
                <td>{{ formatCurrency(item.unit_cost) }}</td>
                <td>
                  <!-- Partial fill: show recommended / full gap when budget couldn't cover the entire gap -->
                  <template v-if="item.recommended_qty < item.demand_gap">
                    <span class="partial-qty">{{ item.recommended_qty.toLocaleString() }}</span><span class="full-qty-total"> / {{ item.demand_gap.toLocaleString() }}</span>
                  </template>
                  <template v-else>
                    {{ item.recommended_qty.toLocaleString() }}
                  </template>
                </td>
                <td><strong>{{ formatCurrency(item.line_total) }}</strong></td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="table-footer-row">
                <td colspan="4"></td>
                <td><strong>{{ totalUnits.toLocaleString() }}</strong></td>
                <td><strong>{{ formatCurrency(totalCost) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Place Order section — always visible inside the card -->
        <div class="order-actions">
          <span class="lead-time-note">{{ t('restocking.leadTime') }}</span>
          <button
            class="place-order-btn"
            :disabled="recommendations.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.submitting') : t('restocking.placeOrder') }}
          </button>
        </div>

        <!-- Success message -->
        <div v-if="orderResult" class="order-success">
          Order {{ orderResult.order_number }} has been placed. View it in the Orders tab.
        </div>

        <!-- Error message -->
        <div v-if="orderError" class="error" style="margin-top: 1rem;">{{ orderError }}</div>
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

    // State
    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(10000)
    const submitting = ref(false)
    const orderResult = ref(null)
    const orderError = ref(null)

    // Currency formatter — fixed USD for this business view
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    // Greedy budget allocation: sort by largest demand gap, allocate until budget is exhausted
    const recommendations = computed(() => {
      // Compute demand_gap for each forecast; keep only items with a positive gap
      const withGap = forecasts.value
        .map(f => ({ ...f, demand_gap: f.forecasted_demand - f.current_demand }))
        .filter(f => f.demand_gap > 0)

      // Sort descending by demand_gap so highest-priority items are filled first
      withGap.sort((a, b) => b.demand_gap - a.demand_gap)

      const result = []
      let remainingBudget = budget.value

      for (const item of withGap) {
        if (remainingBudget <= 0) break

        const fullCost = item.demand_gap * item.unit_cost

        if (fullCost <= remainingBudget) {
          // Full allocation: cover the entire demand gap
          result.push({
            ...item,
            recommended_qty: item.demand_gap,
            line_total: fullCost
          })
          remainingBudget -= fullCost
        } else {
          // Partial allocation: buy as many units as the budget allows
          const affordableQty = Math.floor(remainingBudget / item.unit_cost)
          if (affordableQty > 0) {
            const partialCost = affordableQty * item.unit_cost
            result.push({
              ...item,
              recommended_qty: affordableQty,
              line_total: partialCost
            })
            remainingBudget -= partialCost
          }
        }
      }

      return result
    })

    // Summary computeds derived from recommendations
    const totalItems = computed(() => recommendations.value.length)

    const totalUnits = computed(() =>
      recommendations.value.reduce((sum, item) => sum + item.recommended_qty, 0)
    )

    const totalCost = computed(() =>
      recommendations.value.reduce((sum, item) => sum + item.line_total, 0)
    )

    const budgetRemaining = computed(() => budget.value - totalCost.value)

    // Data loading
    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    // Submit restocking order to the backend
    const placeOrder = async () => {
      try {
        submitting.value = true
        orderResult.value = null
        orderError.value = null

        const orderData = {
          items: recommendations.value.map(item => ({
            item_sku: item.item_sku,
            item_name: item.item_name,
            quantity: item.recommended_qty,
            unit_cost: item.unit_cost,
            total_cost: item.line_total
          })),
          total_budget_used: totalCost.value
        }

        const result = await api.submitRestockingOrder(orderData)
        orderResult.value = result
      } catch (err) {
        orderError.value = t('restocking.orderError') + ': ' + err.message
        console.error(err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      loading,
      error,
      budget,
      submitting,
      orderResult,
      orderError,
      recommendations,
      totalItems,
      totalUnits,
      totalCost,
      budgetRemaining,
      formatCurrency,
      placeOrder
    }
  }
}
</script>

<style scoped>
/* Budget slider card — subtle blue tint to distinguish it as interactive */
.budget-card {
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
  border-color: #bfdbfe;
  margin-bottom: 1.5rem;
}

.budget-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.budget-display {
  font-size: 2rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: -0.025em;
}

/* Range slider */
.slider-container {
  padding: 0 0.5rem;
}

.budget-slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: #dbeafe;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid #ffffff;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
  transition: box-shadow 0.2s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.5);
}

.budget-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid #ffffff;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.813rem;
  color: #64748b;
  font-weight: 500;
}

/* Empty state */
.no-recommendations {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

/* Table footer totals row */
.table-footer-row td {
  border-top: 2px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.875rem;
}

/* Partial fill indicators in the Recommended Qty column */
.partial-qty {
  color: #ea580c;
  font-weight: 600;
}

.full-qty-total {
  color: #94a3b8;
  font-size: 0.813rem;
}

/* Place Order footer section */
.order-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 1rem;
}

.lead-time-note {
  color: #64748b;
  font-size: 0.875rem;
}

.place-order-btn {
  background: #2563eb;
  color: #ffffff;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
}

.place-order-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  box-shadow: none;
}

/* Success banner after order submission */
.order-success {
  margin-top: 1rem;
  padding: 0.875rem 1rem;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  border-radius: 8px;
  color: #065f46;
  font-size: 0.938rem;
  font-weight: 500;
}
</style>
