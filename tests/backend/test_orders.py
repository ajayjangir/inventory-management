"""
Tests for orders API endpoints — filtering by month, quarter, and status.
"""
import pytest


class TestOrdersEndpoints:
    """Test suite for orders endpoint filtering logic."""

    def test_orders_filter_by_specific_month(self, client):
        """Test that month filter returns only orders from that calendar month.

        The filter_by_month function does a substring match on order_date using
        the 'YYYY-MM' prefix. Verifies no orders from other months leak through.
        """
        target_month = "2025-03"
        response = client.get(f"/api/orders?month={target_month}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one order in March 2025"

        for order in data:
            assert target_month in order["order_date"], (
                f"Order {order['order_number']} has order_date "
                f"'{order['order_date']}' but should be in {target_month}"
            )

    def test_orders_filter_by_quarter_expands_correctly(self, client):
        """Test that Q1-2025 filter returns orders from January, February, and March only.

        QUARTER_MAP in main.py maps 'Q1-2025' → ['2025-01', '2025-02', '2025-03'].
        Verifies the expansion works and no Q2+ orders are included.
        """
        response = client.get("/api/orders?month=Q1-2025")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected orders in Q1-2025"

        q1_months = {"2025-01", "2025-02", "2025-03"}
        for order in data:
            order_month = order["order_date"][:7]  # Extract YYYY-MM
            assert order_month in q1_months, (
                f"Order {order['order_number']} with date '{order['order_date']}' "
                f"should not appear in Q1-2025 results"
            )

        # Confirm all three Q1 months are represented (data covers full year)
        months_found = {order["order_date"][:7] for order in data}
        assert months_found == q1_months, (
            f"Expected all of Q1 months {q1_months}, got {months_found}"
        )

    def test_orders_filter_by_status_delivered(self, client):
        """Test that status=Delivered filter returns only Delivered orders.

        apply_filters() does a case-insensitive status comparison.
        Verifies Processing and Backordered orders are excluded.
        """
        response = client.get("/api/orders?status=Delivered")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected Delivered orders in dataset"

        for order in data:
            assert order["status"].lower() == "delivered", (
                f"Order {order['order_number']} has status '{order['status']}', "
                f"expected 'Delivered'"
            )

        # Cross-check: filtered count must be less than total order count
        all_response = client.get("/api/orders")
        all_data = all_response.json()
        assert len(data) < len(all_data), (
            "Delivered-only results should be a subset of all orders"
        )
