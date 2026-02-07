import os
import tempfile
import unittest
from unittest.mock import mock_open, patch

import dwt_util


class ServicesTests(unittest.TestCase):
    @patch("dwt_util.set_registry")
    def test_services_privacy_sets_disabled_start(self, set_registry):
        dwt_util.services(undo=False)
        registry_keys = set_registry.call_args.args[0]
        self.assertEqual(registry_keys["dmwappushsvc"][4], 4)
        self.assertEqual(registry_keys["DiagTrack"][4], 4)

    @patch("dwt_util.set_registry")
    def test_services_revert_restores_manual_start(self, set_registry):
        dwt_util.services(undo=True)
        registry_keys = set_registry.call_args.args[0]
        self.assertEqual(registry_keys["dmwappushsvc"][4], 3)
        self.assertEqual(registry_keys["DiagTrack"][4], 3)


class OneDriveTests(unittest.TestCase):
    @patch("dwt_util.os.path.isfile", return_value=False)
    @patch("dwt_util.set_registry")
    @patch("dwt_util.is_64bit", return_value=True)
    def test_onedrive_privacy_values(self, _, set_registry, __):
        with patch.dict(dwt_util.os.environ, {"SYSTEMROOT": "C:\\Windows"}, clear=False):
            dwt_util.onedrive(undo=False)

        registry_keys = set_registry.call_args.args[0]
        self.assertEqual(registry_keys["FileSync"][4], 1)
        self.assertEqual(registry_keys["ListPin"][4], 0)
        self.assertEqual(registry_keys["ListPin64Bit"][4], 0)

    @patch("dwt_util.os.path.isfile", return_value=False)
    @patch("dwt_util.set_registry")
    @patch("dwt_util.is_64bit", return_value=True)
    def test_onedrive_revert_values(self, _, set_registry, __):
        with patch.dict(dwt_util.os.environ, {"SYSTEMROOT": "C:\\Windows"}, clear=False):
            dwt_util.onedrive(undo=True)

        registry_keys = set_registry.call_args.args[0]
        self.assertEqual(registry_keys["FileSync"][4], 0)
        self.assertEqual(registry_keys["ListPin"][4], 1)
        self.assertEqual(registry_keys["ListPin64Bit"][4], 1)


class ProcessAndDiagtrackTests(unittest.TestCase):
    @patch("dwt_util.subprocess_handler", return_value=(1, b"", b"failure"))
    @patch("dwt_util.logger")
    def test_ip_block_logs_failure_on_non_zero(self, logger, _):
        dwt_util.ip_block(["1.2.3.4"], undo=False)
        logger.exception.assert_called_once()
        logger.critical.assert_called_once()

    @patch("dwt_util.subprocess_handler", return_value=(0, b"", b""))
    def test_clear_diagtrack_uses_correct_service_name(self, subprocess_handler):
        with patch.dict(dwt_util.os.environ, {"SYSTEMDRIVE": "C:"}, clear=False):
            with patch("builtins.open", mock_open()):
                dwt_util.clear_diagtrack()

        commands = [call.args[0] for call in subprocess_handler.call_args_list]
        self.assertIn("sc delete dmwappushsvc", commands)


class HostsFileTests(unittest.TestCase):
    def _run_host_file(self, hosts_content, entries, undo):
        with tempfile.TemporaryDirectory() as temp_dir:
            system_root = os.path.join(temp_dir, "Windows")
            hosts_dir = os.path.join(system_root, "System32", "drivers", "etc")
            os.makedirs(hosts_dir, exist_ok=True)
            hosts_path = os.path.join(hosts_dir, "hosts")
            with open(hosts_path, "w", encoding="utf-8") as hosts:
                hosts.write(hosts_content)

            with patch.dict(dwt_util.os.environ, {"SYSTEMROOT": system_root}, clear=False):
                self.assertTrue(dwt_util.host_file(entries, undo=undo))

            with open(hosts_path, "r", encoding="utf-8") as hosts:
                return hosts.read().splitlines()

    def test_host_file_add_does_not_duplicate(self):
        lines = self._run_host_file(
            "127.0.0.1 localhost\n0.0.0.0 example.com\n",
            ["example.com", "new.example.com"],
            undo=False,
        )
        self.assertEqual(lines.count("0.0.0.0 example.com"), 1)
        self.assertEqual(lines.count("0.0.0.0 new.example.com"), 1)

    def test_host_file_undo_matches_exact_entries(self):
        lines = self._run_host_file(
            "0.0.0.0 example.com\n0.0.0.0 example.com.bad\n",
            ["example.com"],
            undo=True,
        )
        self.assertNotIn("0.0.0.0 example.com", lines)
        self.assertIn("0.0.0.0 example.com.bad", lines)


if __name__ == "__main__":
    unittest.main()
