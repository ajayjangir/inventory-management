"""
Tests for quarterly reports calculations and backlog purchase-order
flag enrichment — critical business logic with no prior coverage.
"""
import pytest


class TestQuarterlyReports:
    """Test suite for the quarterly reports endpoint."""

    def test_quarterly_reports_calculations(self, client):
        """Test fulfillment rate and avg order value are calculated correctly."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        quarters = response.json()
        assert isinstance(quarters, list)
        assert len(quarters) > 0

        # Cross-validate against raw order data
        orders_response = client.get("/api/orders")
        all_orders = orders_response.json()

        quarter_months = {
            "Q1-2025": ["2025-01", "2025-02", "2025-03"],
            "Q2-2025": ["2025-04", "2025-05", "2025-06"],
            "Q3-2025": ["2025-07", "2025-08", "2025-09"],
            "Q4-2025": ["2025-10", "2025-11", "2025-12"],
        }

        for q_data in quarters:
            assert "quarter" in q_data
            assert "total_orders" in q_data
            assert "total_revenue" in q_data
            assert "fulfillment_rate" in q_data
            assert "avg_order_value" in q_data

            qname = q_data["quarter"]
            assert qname in quarter_months, f"Unexpected quarter: {qname}"

            # Manually count orders for this quarter
            months = quarter_months[qname]
            q_orders = [
                o for o in all_orders
                if any(m in o.get("order_date", "") for m in months)
            ]
            expected_total = len(q_orders)
            expected_revenue = sum(o["total_value"] for o in q_orders)
            expected_delivered = sum(
                1 for o in q_orders if o["status"] == "Delivered"
            )

            assert q_data["total_orders"] == expected_total
            assert abs(q_data["total_revenue"] - expected_revenue) < 0.01

            # Verify fulfillment rate = delivered / total * 100
            if expected_total > 0:
                expected_rate = round(
                    (expected_delivered / expected_total) * 100, 1
                )
                assert q_data["fulfillment_rate"] == expected_rate

                expected_avg = round(expected_revenue / expected_total, 2)
                assert q_data["avg_order_value"] == expected_avg

        # Quarters should be sorted
        quarter_names = [q["quarter"] for q in quarters]
        assert quarter_names == sorted(quarter_names)


class TestBacklogPurchaseOrderFlag:
    """Test suite for backlog purchase-order enrichment logic."""

    def test_backlog_has_purchase_order_flag(self, client):
        """Test that every backlog item includes the has_purchase_order flag."""
        response = client.get("/api/backlog")
        assert response.status_code == 200

        backlog = response.json()
        assert isinstance(backlog, list)
        assert len(backlog) > 0

        for item in backlog:
            assert "has_purchase_order" in item, (
                f"Backlog item {item['id']} missing has_purchase_order flag"
            )
            assert isinstance(item["has_purchase_order"], bool)
