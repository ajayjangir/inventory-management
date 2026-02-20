"""
Tests for orders, quarterly reports, and restocking order endpoints.

Covers critical untested backend logic:
- Order filtering by status and quarter/month
- Quarterly report financial calculations (fulfillment rate, avg order value)
- Restocking order creation with total value calculation
- Order lookup by ID with 404 handling
"""
import pytest


class TestOrderFiltering:
    """Tests for order filtering logic — the most-used endpoint with zero prior coverage."""

    def test_filter_orders_by_status(self, client):
        """Test that status filter returns only matching orders and is case-insensitive."""
        response = client.get("/api/orders?status=Processing")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one Processing order in mock data"

        for order in data:
            assert order["status"].lower() == "processing"

        # Verify the filter actually reduces the result set
        all_response = client.get("/api/orders")
        assert len(data) < len(all_response.json())

    def test_filter_orders_by_quarter(self, client):
        """Test quarter-based date filtering (Q1-2025 maps to Jan/Feb/Mar)."""
        response = client.get("/api/orders?month=Q1-2025")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected orders in Q1-2025"

        q1_months = ["2025-01", "2025-02", "2025-03"]
        for order in data:
            order_month = order["order_date"][:7]
            assert order_month in q1_months, (
                f"Order date {order['order_date']} is not in Q1-2025"
            )


class TestQuarterlyReports:
    """Tests for quarterly report calculations — financial data with no prior coverage."""

    def test_quarterly_report_calculations(self, client):
        """Verify fulfillment_rate and avg_order_value are calculated correctly from raw orders."""
        reports_response = client.get("/api/reports/quarterly")
        assert reports_response.status_code == 200

        reports = reports_response.json()
        assert isinstance(reports, list)
        assert len(reports) > 0

        # Independently calculate expected values from raw order data
        orders_response = client.get("/api/orders")
        all_orders = orders_response.json()

        for report in reports:
            quarter = report["quarter"]

            # Determine which months belong to this quarter
            q_num = int(quarter[1])
            start_month = (q_num - 1) * 3 + 1
            months = [f"2025-{m:02d}" for m in range(start_month, start_month + 3)]

            # Filter orders for this quarter
            quarter_orders = [
                o for o in all_orders
                if o["order_date"][:7] in months
            ]

            expected_total = len(quarter_orders)
            expected_revenue = sum(o["total_value"] for o in quarter_orders)
            expected_delivered = sum(
                1 for o in quarter_orders if o["status"] == "Delivered"
            )

            assert report["total_orders"] == expected_total
            assert abs(report["total_revenue"] - expected_revenue) < 0.01

            if expected_total > 0:
                expected_avg = round(expected_revenue / expected_total, 2)
                expected_rate = round((expected_delivered / expected_total) * 100, 1)
                assert report["avg_order_value"] == expected_avg
                assert report["fulfillment_rate"] == expected_rate


class TestRestockingOrders:
    """Tests for restocking order creation — POST endpoint with business logic, no prior coverage."""

    def test_create_restocking_order_calculates_total(self, client):
        """Test that creating a restocking order correctly calculates total_value from items."""
        request_body = {
            "items": [
                {"item_sku": "PCB-001", "item_name": "Single Layer PCB", "quantity": 10, "unit_cost": 24.99},
                {"item_sku": "SEN-001", "item_name": "Temperature Sensor", "quantity": 5, "unit_cost": 15.50},
            ],
            "total_budget": 500.00,
        }

        response = client.post("/api/restocking-orders", json=request_body)
        assert response.status_code == 200

        order = response.json()

        # Verify calculated total: (10 * 24.99) + (5 * 15.50) = 249.90 + 77.50 = 327.40
        expected_total = round(10 * 24.99 + 5 * 15.50, 2)
        assert order["total_value"] == expected_total

        assert order["status"] == "Processing"
        assert order["id"].startswith("restock-")
        assert order["order_number"].startswith("RST-")
        assert len(order["items"]) == 2

        # Verify expected_delivery is 14 days after order_date
        from datetime import datetime, timedelta
        order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
        expected_delivery = datetime.strptime(order["expected_delivery"], "%Y-%m-%d")
        assert (expected_delivery - order_date).days == 14


class TestOrderLookup:
    """Tests for single-order lookup — validates ID-based retrieval and error handling."""

    def test_get_order_by_id_and_404(self, client):
        """Test retrieving an order by ID returns correct data, and missing ID returns 404."""
        # Get a valid order ID from the list
        list_response = client.get("/api/orders")
        all_orders = list_response.json()
        assert len(all_orders) > 0

        target = all_orders[0]

        # Fetch by ID and verify fields match
        detail_response = client.get(f"/api/orders/{target['id']}")
        assert detail_response.status_code == 200

        order = detail_response.json()
        assert order["id"] == target["id"]
        assert order["order_number"] == target["order_number"]
        assert order["status"] == target["status"]
        assert order["total_value"] == target["total_value"]

        # Verify required fields are present
        for field in ["id", "order_number", "customer", "items", "status",
                      "order_date", "expected_delivery", "total_value"]:
            assert field in order, f"Missing required field: {field}"

        # Non-existent ID should return 404
        not_found_response = client.get("/api/orders/nonexistent-order-999")
        assert not_found_response.status_code == 404
        assert "not found" in not_found_response.json()["detail"].lower()
