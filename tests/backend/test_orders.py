"""
Tests for orders API endpoints — status filtering, quarter-based
month filtering, and single-order retrieval.
"""
import pytest


class TestOrderEndpoints:
    """Test suite for order-related endpoints."""

    def test_filter_orders_by_status(self, client):
        """Test filtering orders by status returns only matching orders."""
        for status in ["Delivered", "Shipped", "Processing", "Backordered"]:
            response = client.get(f"/api/orders?status={status}")
            assert response.status_code == 200

            data = response.json()
            assert isinstance(data, list)

            for order in data:
                assert order["status"].lower() == status.lower(), (
                    f"Expected status '{status}', got '{order['status']}' "
                    f"for order {order['order_number']}"
                )

        # 'all' should return the same as no filter
        resp_all = client.get("/api/orders?status=all")
        resp_none = client.get("/api/orders")
        assert len(resp_all.json()) == len(resp_none.json())

    def test_filter_orders_by_quarter(self, client):
        """Test quarter-based filtering (Q1-2025 etc.) via the month param."""
        # Q1-2025 should return orders from Jan, Feb, Mar 2025
        response = client.get("/api/orders?month=Q1-2025")
        assert response.status_code == 200

        q1_orders = response.json()
        assert isinstance(q1_orders, list)

        q1_months = {"2025-01", "2025-02", "2025-03"}
        for order in q1_orders:
            order_month = order["order_date"][:7]
            assert order_month in q1_months, (
                f"Order {order['order_number']} dated {order['order_date']} "
                f"should not appear in Q1-2025"
            )

        # Verify Q1 is a strict subset — unfiltered should have more or equal
        all_orders = client.get("/api/orders").json()
        assert len(q1_orders) <= len(all_orders)

        # Single-month filter should be a subset of its quarter
        jan_orders = client.get("/api/orders?month=2025-01").json()
        jan_ids = {o["id"] for o in jan_orders}
        q1_ids = {o["id"] for o in q1_orders}
        assert jan_ids.issubset(q1_ids), (
            "January orders should be a subset of Q1 orders"
        )

    def test_get_order_by_id_and_404(self, client):
        """Test retrieving a single order by ID and 404 for missing orders."""
        # Get a valid order ID
        response = client.get("/api/orders")
        all_orders = response.json()
        assert len(all_orders) > 0

        first_order = all_orders[0]

        # Fetch by ID — should match
        response = client.get(f"/api/orders/{first_order['id']}")
        assert response.status_code == 200

        order = response.json()
        assert order["id"] == first_order["id"]
        assert order["order_number"] == first_order["order_number"]
        assert order["total_value"] == first_order["total_value"]

        # Nonexistent ID — should 404
        response = client.get("/api/orders/nonexistent-order-999")
        assert response.status_code == 404

        error = response.json()
        assert "detail" in error
        assert "not found" in error["detail"].lower()
