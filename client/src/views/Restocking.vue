<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Success Banner -->
      <div v-if="orderPlaced" class="success-banner">
        <span>{{ t('restocking.orderPlaced') }}</span>
        <button class="dismiss-btn" @click="orderPlaced = false">×</button>
      </div>

      <!-- Budget & Settings Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }} &amp; Settings</h3>
        </div>
        <div class="settings-grid">
          <div class="settings-field">
            <div class="field-label-row">
              <label class="field-label">{{ t('restocking.budget') }}</label>
              <span class="budget-display">{{ formatCurrency(budget) }}</span>
            </div>
            <input
              type="range"
              class="budget-slider"
              min="0"
              max="100000"
              step="500"
              v-model.number="budget"
            />
            <div class="slider-bounds">
              <span>$0</span>
              <span>$100,000</span>
            </div>
          </div>
          <div class="settings-field">
            <label class="field-label">{{ t('restocking.leadTime') }}</label>
            <input
              type="number"
              class="lead-time-input"
              min="1"
              max="365"
              v-model.number="leadTime"
            />
          </div>
        </div>
      </div>

      <!-- Recommendations Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
        </div>

        <!-- Budget Progress Bar -->
        <div class="budget-progress-section">
          <div class="budget-progress-labels">
            <span class="progress-label">
              {{ t('restocking.budgetUsed') }}: <strong>{{ formatCurrency(budgetUsed) }} / {{ formatCurrency(budget) }}</strong>
            </span>
            <span class="progress-remaining">
              {{ t('restocking.budgetRemaining') }}: <strong>{{ formatCurrency(budgetRemaining) }}</strong>
            </span>
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              :class="{ 'progress-warning': budgetPercent >= 90, 'progress-full': budgetPercent >= 100 }"
              :style="{ width: Math.min(budgetPercent, 100) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Recommendations Table -->
        <div v-if="recommendations.length === 0" class="no-data">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.itemName') }}</th>
                <th>{{ t('restocking.sku') }}</th>
                <th>{{ t('restocking.trend') }}</th>
                <th>{{ t('restocking.currentDemand') }}</th>
                <th>{{ t('restocking.forecastedDemand') }}</th>
                <th>{{ t('restocking.qtyToOrder') }}</th>
                <th>{{ t('restocking.unitCost') }}</th>
                <th>{{ t('restocking.totalCost') }}</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="rec in recommendations"
                :key="rec.item_sku"
                :class="{ 'row-over-budget': !rec.withinBudget }"
              >
                <td class="item-name-cell">{{ rec.item_name }}</td>
                <td><strong>{{ rec.item_sku }}</strong></td>
                <td>
                  <span :class="['badge', rec.trend]">
                    {{ t(`trends.${rec.trend}`) }}
                  </span>
                </td>
                <td>{{ rec.current_demand.toLocaleString() }}</td>
                <td><strong>{{ rec.forecasted_demand.toLocaleString() }}</strong></td>
                <td>{{ rec.qty.toLocaleString() }}</td>
                <td>{{ formatCurrency(rec.unitCost) }}</td>
                <td>{{ formatCurrency(rec.itemCost) }}</td>
                <td>
                  <span v-if="rec.withinBudget" class="badge success">
                    {{ t('restocking.withinBudget') }}
                  </span>
                  <span v-else class="badge over-budget">
                    {{ t('restocking.overBudget') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Place Order Button -->
        <div class="order-action">
          <button
            class="place-order-btn"
            :disabled="budget === 0 || withinBudgetItems.length === 0 || loading || submitting"
            @click="placeOrder"
          >
            <span v-if="submitting">Placing Order...</span>
            <span v-else>{{ t('restocking.placeOrder') }}</span>
          </button>
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

    const budget = ref(50000)
    const leadTime = ref(14)
    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const orderPlaced = ref(false)
    const forecasts = ref([])
    const skuCostMap = ref({})

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const [forecastsData, inventoryData] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory()
        ])

        const costMap = {}
        inventoryData.forEach(item => {
          costMap[item.sku] = item.unit_cost
        })

        forecasts.value = forecastsData
        skuCostMap.value = costMap
      } catch (err) {
        error.value = t('common.error') + ': ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const recommendations = computed(() => {
      const trendOrder = { increasing: 0, stable: 1, decreasing: 2 }
      const sorted = [...forecasts.value].sort((a, b) =>
        (trendOrder[a.trend] ?? 1) - (trendOrder[b.trend] ?? 1)
      )

      let runningTotal = 0
      return sorted
        .filter(f => skuCostMap.value[f.item_sku] !== undefined)
        .map(f => {
          const unitCost = skuCostMap.value[f.item_sku]
          const qty = f.forecasted_demand
          const itemCost = qty * unitCost
          const withinBudget = runningTotal + itemCost <= budget.value
          if (withinBudget) runningTotal += itemCost
          return { ...f, unitCost, qty, itemCost, withinBudget }
        })
    })

    const withinBudgetItems = computed(() =>
      recommendations.value.filter(r => r.withinBudget)
    )

    const budgetUsed = computed(() =>
      withinBudgetItems.value.reduce((sum, r) => sum + r.itemCost, 0)
    )

    const budgetRemaining = computed(() => budget.value - budgetUsed.value)

    const budgetPercent = computed(() =>
      budget.value > 0 ? (budgetUsed.value / budget.value) * 100 : 0
    )

    const formatCurrency = (value) => {
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
    }

    const placeOrder = async () => {
      const items = withinBudgetItems.value.map(r => ({
        sku: r.item_sku,
        name: r.item_name,
        quantity: r.qty,
        unit_price: r.unitCost
      }))

      submitting.value = true
      error.value = null
      try {
        await api.createRestockOrder({
          items,
          lead_time_days: leadTime.value,
          total_value: budgetUsed.value
        })

        orderPlaced.value = true
        setTimeout(() => { orderPlaced.value = false }, 5000)
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
        console.error(err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadData)

    return {
      t,
      budget,
      leadTime,
      loading,
      error,
      submitting,
      orderPlaced,
      forecasts,
      recommendations,
      withinBudgetItems,
      budgetUsed,
      budgetRemaining,
      budgetPercent,
      formatCurrency,
      placeOrder
    }
  }
}
</script>

<style scoped>
.restocking {
  padding-bottom: 2rem;
}

/* Success Banner */
.success-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.938rem;
  font-weight: 500;
}

.dismiss-btn {
  background: none;
  border: none;
  color: #065f46;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 0.25rem;
  line-height: 1;
  font-weight: 700;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.dismiss-btn:hover {
  opacity: 1;
}

/* Settings */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

.settings-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.budget-display {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
  margin: 0.25rem 0;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
  transition: box-shadow 0.15s;
}

.budget-slider::-webkit-slider-thumb:hover {
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.5);
}

.budget-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
}

.slider-bounds {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #94a3b8;
}

.lead-time-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.938rem;
  color: #0f172a;
  width: 100%;
  outline: none;
  transition: border-color 0.15s;
}

.lead-time-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Budget Progress */
.budget-progress-section {
  margin-bottom: 1.25rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.budget-progress-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.625rem;
  font-size: 0.875rem;
  color: #475569;
}

.progress-remaining {
  color: #64748b;
}

.progress-track {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.progress-fill.progress-warning {
  background: #f59e0b;
}

.progress-fill.progress-full {
  background: #ef4444;
}

/* Table rows */
.row-over-budget td {
  background: #f8fafc;
  color: #94a3b8;
}

.row-over-budget td strong {
  color: #94a3b8;
}

.item-name-cell {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Over budget badge */
.badge.over-budget {
  background: #64748b;
  color: #ffffff;
}

/* No data */
.no-data {
  text-align: center;
  padding: 2.5rem;
  color: #64748b;
  font-size: 0.938rem;
}

/* Place Order */
.order-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.place-order-btn {
  padding: 0.625rem 2rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, opacity 0.2s ease;
  letter-spacing: 0.01em;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
