<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Inventory Restocking</h2>
      <p>Set your budget and view AI-recommended items to restock based on demand forecasts</p>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Budget Control Card -->
      <div class="card budget-card">
        <h3 class="card-title">Set Restocking Budget</h3>
        <div class="budget-display">{{ formatCurrency(budget) }}</div>
        <div class="budget-controls">
          <button @click="decreaseBudget" :disabled="budget <= 0" class="budget-btn">- $5,000</button>
          <input
            type="range"
            v-model.number="budget"
            min="0"
            max="100000"
            step="1000"
            class="budget-slider"
          />
          <button @click="increaseBudget" :disabled="budget >= 100000" class="budget-btn">+ $5,000</button>
        </div>
      </div>

      <!-- Recommendations Card -->
      <div class="card recommendations-card">
        <div class="card-header">
          <h3 class="card-title">Recommended Items ({{ recommendations.length }})</h3>
          <div class="total-cost-badge">
            Total Cost: <strong>{{ formatCurrency(totalCost) }}</strong>
          </div>
        </div>
        <div v-if="recommendations.length === 0" class="no-data">
          <p>Increase budget to see recommendations</p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>Item Name</th>
                <th>SKU</th>
                <th>Current Demand</th>
                <th>Forecasted Demand</th>
                <th>Unit Cost</th>
                <th>Qty to Order</th>
                <th>Line Total</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in recommendations"
                :key="item.sku"
                :class="{ 'high-priority': item.is_high_priority }"
              >
                <td><strong>{{ item.item_name }}</strong></td>
                <td>{{ item.sku }}</td>
                <td>{{ item.current_demand }}</td>
                <td>
                  <span :class="['demand-badge', item.trend]">
                    {{ item.forecasted_demand }}
                  </span>
                </td>
                <td>{{ formatCurrency(item.unit_cost) }}</td>
                <td><strong>{{ item.quantity }}</strong></td>
                <td><strong>{{ formatCurrency(item.line_total) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action Button -->
      <div class="actions">
        <button
          @click="placeOrder"
          :disabled="recommendations.length === 0 || submitting"
          class="place-order-btn"
        >
          {{ submitting ? 'Placing Order...' : 'Place Restocking Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const router = useRouter()
    const { currentCurrency } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)

    const budget = ref(50000)
    const demandForecasts = ref([])
    const inventoryItems = ref([])

    const formatCurrency = (value) => {
      if (currentCurrency.value === 'JPY') {
        return `¥${Math.round(value).toLocaleString()}`
      }
      return `$${value.toLocaleString()}`
    }

    // Calculate recommendations based on budget
    const recommendations = computed(() => {
      if (!demandForecasts.value.length || !inventoryItems.value.length) {
        return []
      }

      // Sort demand forecasts by forecasted_demand DESC
      const sortedForecasts = [...demandForecasts.value].sort(
        (a, b) => b.forecasted_demand - a.forecasted_demand
      )

      const recs = []
      let remainingBudget = budget.value

      for (const forecast of sortedForecasts) {
        // Find matching inventory item to get unit_cost
        const invItem = inventoryItems.value.find(item => item.sku === forecast.item_sku)

        if (!invItem || !invItem.unit_cost) continue

        const unitCost = invItem.unit_cost
        const maxQuantity = Math.floor(remainingBudget / unitCost)

        if (maxQuantity > 0) {
          const quantity = maxQuantity
          const lineTotal = quantity * unitCost
          const isHighPriority = forecast.forecasted_demand > forecast.current_demand * 1.2

          recs.push({
            sku: forecast.item_sku,
            item_name: forecast.item_name,
            current_demand: forecast.current_demand,
            forecasted_demand: forecast.forecasted_demand,
            trend: forecast.trend,
            unit_cost: unitCost,
            quantity: quantity,
            line_total: lineTotal,
            is_high_priority: isHighPriority
          })

          remainingBudget -= lineTotal
        }

        // Stop if budget exhausted
        if (remainingBudget <= 0) break
      }

      return recs
    })

    const totalCost = computed(() => {
      return recommendations.value.reduce((sum, item) => sum + item.line_total, 0)
    })

    const increaseBudget = () => {
      if (budget.value < 100000) {
        budget.value = Math.min(budget.value + 5000, 100000)
      }
    }

    const decreaseBudget = () => {
      if (budget.value > 0) {
        budget.value = Math.max(budget.value - 5000, 0)
      }
    }

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null

        const [forecasts, inventory] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory()
        ])

        demandForecasts.value = forecasts
        inventoryItems.value = inventory
      } catch (err) {
        error.value = 'Failed to load data: ' + err.message
        console.error('Load error:', err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (recommendations.value.length === 0) return

      try {
        submitting.value = true
        error.value = null

        const orderData = {
          budget: budget.value,
          recommended_items: recommendations.value.map(item => ({
            sku: item.sku,
            quantity: item.quantity,
            unit_cost: item.unit_cost,
            item_name: item.item_name
          }))
        }

        await api.createRestockingOrder(orderData)

        // Navigate to orders page to see the submitted order
        router.push('/orders')
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
        console.error('Place order error:', err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadData)

    return {
      loading,
      error,
      budget,
      recommendations,
      totalCost,
      increaseBudget,
      decreaseBudget,
      placeOrder,
      formatCurrency,
      submitting
    }
  }
}
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.5rem;
  text-align: center;
}

.budget-display {
  font-size: 3rem;
  font-weight: 700;
  color: #2563eb;
  margin: 1.5rem 0;
  letter-spacing: -0.025em;
}

.budget-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.budget-btn {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.budget-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.budget-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
}

.budget-slider {
  flex: 1;
  max-width: 400px;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 4px;
  outline: none;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.budget-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.budget-slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.recommendations-card {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-cost-badge {
  font-size: 1.125rem;
  color: #0f172a;
}

.total-cost-badge strong {
  color: #2563eb;
}

.no-data {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
  font-size: 1rem;
}

.high-priority {
  background: #fef3c7 !important;
}

.demand-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 600;
}

.demand-badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.demand-badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.demand-badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.place-order-btn {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.place-order-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
