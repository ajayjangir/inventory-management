# Restocking Module — User Guide

The Restocking module helps you replenish inventory by analyzing demand forecasts, recommending optimal quantities within your budget, and placing restocking orders.

## Accessing the Module

Click **Restocking** in the top navigation bar, or navigate to `/restocking` in your browser.

## How It Works

The module uses demand forecast data to identify items where forecasted demand exceeds current demand (the "demand gap"). It then recommends how many units to restock for each item, constrained by the budget you set.

### Algorithm

1. Demand forecasts are retrieved from the system.
2. For each item, the **demand gap** is calculated: `forecasted_demand − current_demand`.
3. Items with a positive gap are sorted by gap size (largest first).
4. Starting from the highest-gap item, the system allocates as many units as the budget allows at the item's unit cost.
5. This continues down the list until the budget is exhausted or all gaps are filled.

This greedy approach prioritizes items with the greatest supply shortfall.

## Setting a Budget

Use the **budget slider** at the top of the page to set your restocking budget:

- **Range**: $1,000 – $50,000
- **Step**: $500 increments
- **Default**: $10,000

The recommended items table updates automatically as you adjust the budget. A larger budget allows more items and higher quantities to be recommended.

## Recommended Items Table

The table displays items that the system recommends restocking, with the following columns:

| Column | Description |
|--------|-------------|
| SKU | The item's stock-keeping unit identifier |
| Item Name | Product name |
| Demand Gap | Difference between forecasted and current demand |
| Unit Cost | Cost per unit |
| Recommended Qty | Number of units recommended for restocking |
| Line Total | `Recommended Qty × Unit Cost` |

Below the table, a **summary bar** shows:

- **Total Items** — number of distinct items in the recommendation
- **Total Cost** — sum of all line totals
- **Remaining Budget** — unused portion of your budget

## Placing a Restocking Order

1. Adjust the budget slider to your desired amount.
2. Review the recommended items and quantities.
3. Click **Place Order** to submit the restocking order.

After submission:

- The order is assigned an order number (format: `RST-YYYY-NNNN`).
- Status is set to **Processing**.
- Expected delivery is set to **14 days** from the order date.
- A confirmation message appears on screen.

## Viewing Submitted Orders

Submitted restocking orders appear in two places:

### On the Restocking page

A **Submitted Restocking Orders** table at the bottom of the page shows all orders placed during the current session.

### On the Orders page

The Orders page also includes a **Submitted Restocking Orders** section alongside regular orders.

Both tables display the same information:

| Column | Description |
|--------|-------------|
| Order Number | Unique identifier (e.g., `RST-2025-0001`) |
| Items | Number of distinct items in the order |
| Status | Current order status (e.g., Processing) |
| Order Date | When the order was placed |
| Expected Delivery | Estimated delivery date (14 days from order) |
| Total Value | Total cost of the order |

## Important Notes

- **In-memory storage**: Restocking orders are stored in memory and do not persist across server restarts. All submitted orders are lost when the server is restarted.
- **Budget-constrained**: The system will never recommend spending more than your set budget. If an item's unit cost exceeds the remaining budget, it is skipped.
- **No partial units**: Only whole units are recommended — the system does not suggest fractional quantities.
- **Lead time**: All restocking orders have a fixed 14-day expected delivery window.
- **Language support**: The module is fully available in English and Japanese. Switch languages using the language selector in the navigation bar.

## API Reference

The restocking module uses two API endpoints:

### Submit a restocking order

```
POST /api/restocking-orders
```

**Request body:**

```json
{
  "items": [
    {
      "item_sku": "SKU-001",
      "item_name": "Widget Type A",
      "quantity": 50,
      "unit_cost": 12.99
    }
  ],
  "total_budget": 10000
}
```

**Response:** The created order object including order number, status, expected delivery date, and total value.

### List restocking orders

```
GET /api/restocking-orders
```

**Response:** Array of all submitted restocking orders.

Full interactive API documentation is available at `http://localhost:8001/docs` when the server is running.
