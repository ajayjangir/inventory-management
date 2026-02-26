"""
Tests for quarterly and monthly trend report endpoints.
"""
import pytest


class TestReportsEndpoints:
    """Test suite for /api/reports/* endpoint calculations."""

    def test_quarterly_report_fulfillment_rate_calculation(self, client):
        """Test that fulfillment_rate equals (delivered_orders / total_orders) * 100.

        The endpoint computes this in-memory. Cross-validate each quarter's
        reported rate against its own delivered_orders and total_orders fields.
        """
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected quarterly report data for 2025"

        required_fields = {
            "quarter", "total_orders", "total_revenue",
            "delivered_orders", "avg_order_value", "fulfillment_rate"
        }
        for quarter in data:
            assert required_fields <= quarter.keys(), (
                f"Quarter {quarter.get('quarter')} is missing fields: "
                f"{required_fields - quarter.keys()}"
            )

            total = quarter["total_orders"]
            delivered = quarter["delivered_orders"]
            reported_rate = quarter["fulfillment_rate"]

            assert total > 0, f"{quarter['quarter']} has zero total_orders"
            assert 0 <= delivered <= total, (
                f"{quarter['quarter']}: delivered ({delivered}) exceeds total ({total})"
            )

            expected_rate = round((delivered / total) * 100, 1)
            assert abs(reported_rate - expected_rate) < 0.01, (
                f"{quarter['quarter']} fulfillment_rate is {reported_rate}, "
                f"expected {expected_rate} ({delivered}/{total}*100)"
            )

    def test_monthly_trends_order_count_matches_orders_endpoint(self, client):
        """Test that monthly trends order_count matches the raw orders endpoint.

        /api/reports/monthly-trends aggregates orders by month. Cross-validate
        one month's order_count against a direct filtered query on /api/orders.
        """
        trends_response = client.get("/api/reports/monthly-trends")
        assert trends_response.status_code == 200

        trends = trends_response.json()
        assert isinstance(trends, list)
        assert len(trends) > 0, "Expected monthly trend data"

        # Pick the first month returned and verify its order_count
        first_month = trends[0]
        assert "month" in first_month
        assert "order_count" in first_month
        assert "revenue" in first_month

        month_str = first_month["month"]  # Format: YYYY-MM
        reported_count = first_month["order_count"]
        reported_revenue = first_month["revenue"]

        # Fetch orders for that month directly
        orders_response = client.get(f"/api/orders?month={month_str}")
        assert orders_response.status_code == 200
        month_orders = orders_response.json()

        assert reported_count == len(month_orders), (
            f"Month {month_str}: trends reports {reported_count} orders, "
            f"but /api/orders?month={month_str} returns {len(month_orders)}"
        )

        # Revenue should also match (allow floating point tolerance)
        calculated_revenue = sum(o["total_value"] for o in month_orders)
        assert abs(reported_revenue - calculated_revenue) < 0.01, (
            f"Month {month_str}: trends revenue={reported_revenue}, "
            f"calculated={calculated_revenue}"
        )
