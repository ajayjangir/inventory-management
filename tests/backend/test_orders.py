"""
Unit tests for critical backend logic: order filtering, value calculations,
status transitions, and data validation.
"""
import pytest


class TestOrderFiltering:
    """Tests for order filtering logic in apply_filters() and filter_by_month()."""

    def test_quarter_filter_returns_correct_months(self, client):
        """Q2-2025 filter should return only orders from April, May, or June 2025.

        Validates that the QUARTER_MAP expansion in filter_by_month() maps
        'Q2-2025' to the correct three-month window and excludes all others.
        """
        response = client.get("/api/orders?month=Q2-2025")
        assert response.status_code == 200

        orders = response.json()
        assert len(orders) > 0, "Q2-2025 should match at least one order"

        q2_months = {"2025-04", "2025-05", "2025-06"}
        for order in orders:
            order_month = order["order_date"][:7]  # YYYY-MM
            assert order_month in q2_months, (
                f"Order {order['order_number']} has date {order['order_date']}, "
                f"which is outside Q2-2025 (Apr-Jun 2025)"
            )

    def test_status_filter_is_case_insensitive(self, client):
        """Filtering by lowercase 'processing' should match 'Processing' orders.

        apply_filters() normalises both sides with .lower(), so case must not matter.
        """
        response_lower = client.get("/api/orders?status=processing")
        response_title = client.get("/api/orders?status=Processing")

        assert response_lower.status_code == 200
        assert response_title.status_code == 200

        orders_lower = response_lower.json()
        orders_title = response_title.json()

        # Both queries must return the same set of order IDs
        ids_lower = {o["id"] for o in orders_lower}
        ids_title = {o["id"] for o in orders_title}
        assert ids_lower == ids_title, (
            "Case-insensitive status filter should return identical results "
            "regardless of the casing supplied by the caller"
        )

        # Every returned order must have status 'Processing'
        for order in orders_title:
            assert order["status"] == "Processing"

    def test_get_nonexistent_order_returns_404(self, client):
        """Requesting an order with an unknown ID must return HTTP 404.

        Validates the HTTPException raised in get_order() and that the error
        payload contains a human-readable detail message.
        """
        response = client.get("/api/orders/nonexistent-order-id-99999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestRestockingOrderCreation:
    """Tests for the POST /api/restocking-orders endpoint value calculation."""

    def test_restocking_order_total_value_computed_correctly(self, client):
        """POST /api/restocking-orders must compute total_value = Σ(quantity × unit_cost).

        This validates the core financial calculation in create_restocking_order():
            total_value = sum(item.quantity * item.unit_cost for item in request.items)
        """
        payload = {
            "items": [
                {"item_sku": "PCB-001", "item_name": "Single Layer PCB", "quantity": 100, "unit_cost": 24.99},
                {"item_sku": "SNR-420", "item_name": "Temperature Sensor",  "quantity": 50,  "unit_cost": 8.50},
            ],
            "total_budget": 5000.0,
        }
        expected_total = (100 * 24.99) + (50 * 8.50)  # 2499.00 + 425.00 = 2924.00

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 200

        order = response.json()
        assert abs(order["total_value"] - expected_total) < 0.01, (
            f"Expected total_value={expected_total:.2f}, got {order['total_value']}"
        )

    def test_restocking_order_response_has_required_fields(self, client):
        """A newly created restocking order must include all required tracking fields.

        Validates that the order creation endpoint returns a complete record with
        the fields consumers depend on: id, order_number, status, and delivery date.
        """
        payload = {
            "items": [
                {"item_sku": "MTR-304", "item_name": "Electric Motor 5HP", "quantity": 10, "unit_cost": 350.00},
            ],
            "total_budget": 4000.0,
        }

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 200

        order = response.json()
        required_fields = ["id", "order_number", "status", "order_date", "expected_delivery", "total_value"]
        for field in required_fields:
            assert field in order, f"Restocking order response missing field: '{field}'"

        # A freshly created order must start in 'Processing' state
        assert order["status"] == "Processing"


class TestBacklogEnrichment:
    """Tests for the has_purchase_order flag computed by GET /api/backlog."""

    def test_backlog_items_always_include_has_purchase_order_flag(self, client):
        """Every backlog item returned by GET /api/backlog must have has_purchase_order.

        The endpoint enriches each backlog record by checking whether any purchase
        order references its ID.  The field must always be present and be a boolean.
        """
        response = client.get("/api/backlog")
        assert response.status_code == 200

        items = response.json()
        assert len(items) > 0, "There should be at least one backlog item"

        for item in items:
            assert "has_purchase_order" in item, (
                f"Backlog item {item.get('id')} is missing 'has_purchase_order'"
            )
            assert isinstance(item["has_purchase_order"], bool), (
                f"'has_purchase_order' must be a bool, got {type(item['has_purchase_order'])}"
            )
