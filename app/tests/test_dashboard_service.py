import unittest
from unittest.mock import patch

from app.services import dashboard_service


def _variable_result(value="-", read_ok=True, source_timestamp=None):
    return {
        "read_ok": read_ok,
        "value_display": value,
        "source_timestamp": source_timestamp,
    }


class DashboardOpcuaSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.config = {
            "OPCUA_DASHBOARD_LINE_STATUS_LABEL": "Statut ligne",
            "OPCUA_DASHBOARD_LINE_STATUS_NODE_ID": "line-status",
            "OPCUA_DASHBOARD_CURRENT_BOX_NODE_ID": "current-box",
            "OPCUA_CURRENT_ORDER_REQUESTED_BOXES_NODE_ID": "requested-boxes",
            "OPCUA_CURRENT_ORDER_PRODUCED_BOXES_NODE_ID": "produced-boxes",
            "OPCUA_DASHBOARD_OYSTER_BAGS_NODE_ID": "oyster-bags",
            "OPCUA_DASHBOARD_SCALLOP_BAGS_NODE_ID": "scallop-bags",
        }

    @patch.object(dashboard_service, "read_configured_opcua_variables")
    def test_builds_live_production_from_opcua_values(self, read_variables):
        read_variables.return_value = [
            _variable_result("TRUE"),
            _variable_result("7", source_timestamp="2026-06-01 12:00:00"),
            _variable_result("20"),
            _variable_result("6", source_timestamp="2026-06-01 12:00:01"),
            _variable_result("4"),
            _variable_result("2"),
        ]

        snapshot = dashboard_service._read_dashboard_opcua_snapshot(self.config)
        production = dashboard_service._build_live_production(snapshot)

        self.assertEqual("Synchronise", snapshot["status_label"])
        self.assertEqual("2026-06-01 12:00:01", snapshot["source_timestamp"])
        self.assertEqual(
            {
                "numero_caisse": "7",
                "caisses_demandees": "20",
                "caisses_produites": "6",
                "sacs_huitres_consommes": "4",
                "sacs_st_jacques_consommes": "2",
            },
            production,
        )

    @patch.object(dashboard_service, "read_configured_opcua_variables")
    def test_uses_placeholder_when_live_reads_fail(self, read_variables):
        read_variables.return_value = [
            _variable_result("FALSE"),
            _variable_result(read_ok=False),
            _variable_result(read_ok=False),
            _variable_result(read_ok=False),
            _variable_result(read_ok=False),
            _variable_result(read_ok=False),
        ]

        snapshot = dashboard_service._read_dashboard_opcua_snapshot(self.config)
        production = dashboard_service._build_live_production(snapshot)

        self.assertEqual("Indisponible", snapshot["status_label"])
        self.assertEqual(
            {
                "numero_caisse": "-",
                "caisses_demandees": "-",
                "caisses_produites": "-",
                "sacs_huitres_consommes": "-",
                "sacs_st_jacques_consommes": "-",
            },
            production,
        )


if __name__ == "__main__":
    unittest.main()
