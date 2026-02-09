import logging
import unittest
from unittest.mock import patch

import dwt


class SilentProfilePlanTests(unittest.TestCase):
    def test_apply_plan_contains_expected_actions(self):
        names = [name for name, _ in dwt.get_silent_profile_actions(undo=False)]

        self.assertIn("clear_diagtrack", names)
        self.assertIn("disable_service_dmwappushsvc", names)
        self.assertIn("disable_service_diagtrack", names)
        self.assertIn("advertising_id", names)
        self.assertIn("activity_history", names)
        self.assertIn("cross_device_clipboard", names)
        self.assertIn("input_personalization", names)
        self.assertIn("tailored_experiences", names)
        self.assertIn("feedback_notifications", names)

    def test_revert_plan_is_symmetric_and_skips_non_revertable(self):
        names = [name for name, _ in dwt.get_silent_profile_actions(undo=True)]

        self.assertNotIn("clear_diagtrack", names)
        self.assertNotIn("disable_service_dmwappushsvc", names)
        self.assertNotIn("disable_service_diagtrack", names)

        self.assertIn("services", names)
        self.assertIn("telemetry", names)
        self.assertIn("wifisense", names)
        self.assertIn("onedrive", names)
        self.assertIn("dvr", names)
        self.assertIn("advertising_id", names)
        self.assertIn("activity_history", names)
        self.assertIn("cross_device_clipboard", names)
        self.assertIn("input_personalization", names)
        self.assertIn("tailored_experiences", names)
        self.assertIn("feedback_notifications", names)


class SilentProfileExecutionTests(unittest.TestCase):
    @patch("dwt.dwt_util.feedback_notifications")
    @patch("dwt.dwt_util.tailored_experiences")
    @patch("dwt.dwt_util.input_personalization")
    @patch("dwt.dwt_util.cross_device_clipboard")
    @patch("dwt.dwt_util.activity_history")
    @patch("dwt.dwt_util.advertising_id")
    @patch("dwt.dwt_util.dvr")
    @patch("dwt.dwt_util.onedrive")
    @patch("dwt.dwt_util.wifisense")
    @patch("dwt.dwt_util.telemetry")
    @patch("dwt.dwt_util.services")
    @patch("dwt.dwt_util.disable_service")
    @patch("dwt.dwt_util.clear_diagtrack")
    def test_run_silent_profile_apply(
        self,
        clear_diagtrack,
        disable_service,
        services,
        telemetry,
        wifisense,
        onedrive,
        dvr,
        advertising_id,
        activity_history,
        cross_device_clipboard,
        input_personalization,
        tailored_experiences,
        feedback_notifications,
    ):
        dwt.logger = logging.getLogger("dwt.tests")

        dwt.run_silent_profile(undo=False)

        clear_diagtrack.assert_called_once_with()
        disable_service.assert_any_call("dmwappushsvc")
        disable_service.assert_any_call("DiagTrack")
        services.assert_called_once_with(undo=False)
        telemetry.assert_called_once_with(undo=False)
        wifisense.assert_called_once_with(undo=False)
        onedrive.assert_called_once_with(undo=False)
        dvr.assert_called_once_with(undo=False)
        advertising_id.assert_called_once_with(undo=False)
        activity_history.assert_called_once_with(undo=False)
        cross_device_clipboard.assert_called_once_with(undo=False)
        input_personalization.assert_called_once_with(undo=False)
        tailored_experiences.assert_called_once_with(undo=False)
        feedback_notifications.assert_called_once_with(undo=False)

    @patch("dwt.dwt_util.feedback_notifications")
    @patch("dwt.dwt_util.tailored_experiences")
    @patch("dwt.dwt_util.input_personalization")
    @patch("dwt.dwt_util.cross_device_clipboard")
    @patch("dwt.dwt_util.activity_history")
    @patch("dwt.dwt_util.advertising_id")
    @patch("dwt.dwt_util.dvr")
    @patch("dwt.dwt_util.onedrive")
    @patch("dwt.dwt_util.wifisense")
    @patch("dwt.dwt_util.telemetry")
    @patch("dwt.dwt_util.services")
    @patch("dwt.dwt_util.disable_service")
    @patch("dwt.dwt_util.clear_diagtrack")
    def test_run_silent_profile_revert(
        self,
        clear_diagtrack,
        disable_service,
        services,
        telemetry,
        wifisense,
        onedrive,
        dvr,
        advertising_id,
        activity_history,
        cross_device_clipboard,
        input_personalization,
        tailored_experiences,
        feedback_notifications,
    ):
        dwt.logger = logging.getLogger("dwt.tests")

        dwt.run_silent_profile(undo=True)

        clear_diagtrack.assert_not_called()
        disable_service.assert_not_called()
        services.assert_called_once_with(undo=True)
        telemetry.assert_called_once_with(undo=True)
        wifisense.assert_called_once_with(undo=True)
        onedrive.assert_called_once_with(undo=True)
        dvr.assert_called_once_with(undo=True)
        advertising_id.assert_called_once_with(undo=True)
        activity_history.assert_called_once_with(undo=True)
        cross_device_clipboard.assert_called_once_with(undo=True)
        input_personalization.assert_called_once_with(undo=True)
        tailored_experiences.assert_called_once_with(undo=True)
        feedback_notifications.assert_called_once_with(undo=True)


if __name__ == "__main__":
    unittest.main()
