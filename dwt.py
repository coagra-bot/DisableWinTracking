# Copyright (C) 10se1ucgo 2015-2016
#
# This file is part of DisableWinTracking.
#
# DisableWinTracking is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DisableWinTracking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DisableWinTracking.  If not, see <http://www.gnu.org/licenses/>.
import io
import json
import logging
import os
import platform
import sys
import traceback
import webbrowser
from ctypes import windll
from functools import partial

import wx
from six import u
from wx.lib.itemspicker import (
    IP_REMOVE_FROM_CHOICES,
    IP_SORT_CHOICES,
    IP_SORT_SELECTED,
    ItemsPicker,
)

import dwt_about
import dwt_i18n
import dwt_util


DEFAULT_NORMAL_DOMAINS = (
    "a-0001.a-msedge.net",
    "a-0002.a-msedge.net",
    "a-0003.a-msedge.net",
    "a-0004.a-msedge.net",
    "a-0005.a-msedge.net",
    "a-0006.a-msedge.net",
    "a-0007.a-msedge.net",
    "a-0008.a-msedge.net",
    "a-0009.a-msedge.net",
    "a-msedge.net",
    "a.ads1.msn.com",
    "a.ads2.msads.net",
    "a.ads2.msn.com",
    "a.rad.msn.com",
    "ac3.msn.com",
    "ad.doubleclick.net",
    "adnexus.net",
    "adnxs.com",
    "ads.msn.com",
    "ads1.msads.net",
    "ads1.msn.com",
    "aidps.atdmt.com",
    "aka-cdn-ns.adtech.de",
    "az361816.vo.msecnd.net",
    "az512334.vo.msecnd.net",
    "b.ads1.msn.com",
    "b.ads2.msads.net",
    "b.rad.msn.com",
    "bs.serving-sys.com",
    "c.atdmt.com",
    "c.msn.com",
    "cdn.atdmt.com",
    "cds26.ams9.msecn.net",
    "choice.microsoft.com",
    "choice.microsoft.com.nsatc.net",
    "compatexchange.cloudapp.net",
    "corp.sts.microsoft.com",
    "corpext.msitadfs.glbdns2.microsoft.com",
    "cs1.wpc.v0cdn.net",
    "db3aqu.atdmt.com",
    "df.telemetry.microsoft.com",
    "diagnostics.support.microsoft.com",
    "ec.atdmt.com",
    "feedback.microsoft-hohm.com",
    "feedback.search.microsoft.com",
    "feedback.windows.com",
    "flex.msn.com",
    "g.msn.com",
    "h1.msn.com",
    "i1.services.social.microsoft.com",
    "i1.services.social.microsoft.com.nsatc.net",
    "lb1.www.ms.akadns.net",
    "live.rads.msn.com",
    "m.adnxs.com",
    "msedge.net",
    "msnbot-65-55-108-23.search.msn.com",
    "msntest.serving-sys.com",
    "oca.telemetry.microsoft.com",
    "oca.telemetry.microsoft.com.nsatc.net",
    "pre.footprintpredict.com",
    "preview.msn.com",
    "rad.live.com",
    "rad.msn.com",
    "redir.metaservices.microsoft.com",
    "reports.wes.df.telemetry.microsoft.com",
    "schemas.microsoft.akadns.net",
    "secure.adnxs.com",
    "secure.flashtalking.com",
    "services.wes.df.telemetry.microsoft.com",
    "settings-sandbox.data.microsoft.com",
    "settings-win.data.microsoft.com",
    "sls.update.microsoft.com.akadns.net",
    "sqm.df.telemetry.microsoft.com",
    "sqm.telemetry.microsoft.com",
    "sqm.telemetry.microsoft.com.nsatc.net",
    "ssw.live.com",
    "static.2mdn.net",
    "statsfe1.ws.microsoft.com",
    "statsfe2.ws.microsoft.com",
    "telecommand.telemetry.microsoft.com",
    "telecommand.telemetry.microsoft.com.nsatc.net",
    "telemetry.appex.bing.net",
    "telemetry.microsoft.com",
    "telemetry.urs.microsoft.com",
    "v10.vortex-win.data.microsoft.com",
    "vortex-bn2.metron.live.com.nsatc.net",
    "vortex-cy2.metron.live.com.nsatc.net",
    "vortex-sandbox.data.microsoft.com",
    "vortex-win.data.metron.live.com.nsatc.net",
    "vortex-win.data.microsoft.com",
    "vortex.data.glbdns2.microsoft.com",
    "vortex.data.microsoft.com",
    "watson.live.com",
    "web.vortex.data.microsoft.com",
)

DEFAULT_EXTRA_DOMAINS = (
    "fe2.update.microsoft.com.akadns.net",
    "s0.2mdn.net",
    "statsfe2.update.microsoft.com.akadns.net",
    "survey.watson.microsoft.com",
    "view.atdmt.com",
    "watson.microsoft.com",
    "watson.ppe.telemetry.microsoft.com",
    "watson.telemetry.microsoft.com",
    "watson.telemetry.microsoft.com.nsatc.net",
    "wes.df.telemetry.microsoft.com",
    "ui.skype.com",
    "pricelist.skype.com",
    "apps.skype.com",
    "m.hotmail.com",
    "s.gateway.messenger.live.com",
)

DEFAULT_IP_ADDRESSES = (
    "2.22.61.43",
    "2.22.61.66",
    "65.39.117.230",
    "65.55.108.23",
    "23.218.212.69",
    "134.170.30.202",
    "137.116.81.24",
    "157.56.106.189",
    "204.79.197.200",
    "65.52.108.33",
    "64.4.54.254",
)

SETTINGS_DEFAULTS = {
    "language": "en",
    "preset": "balanced",
}
APP_SETTINGS = SETTINGS_DEFAULTS.copy()

RISK_LABEL_KEYS = {
    "low": "risk_low",
    "medium": "risk_medium",
}

OPTION_DEFINITIONS = (
    {
        "key": "service",
        "category": "core",
        "label_key": "services_label",
        "tooltip_key": "services_tooltip",
        "action_key": "action_services_registry",
        "risk": "medium",
    },
    {
        "key": "diagtrack",
        "category": "core",
        "label_key": "diagtrack_label",
        "tooltip_key": "diagtrack_tooltip",
        "action_key": "action_diagtrack",
        "risk": "medium",
    },
    {
        "key": "telemetry",
        "category": "core",
        "label_key": "telemetry_label",
        "tooltip_key": "telemetry_tooltip",
        "action_key": "action_telemetry",
        "risk": "low",
    },
    {
        "key": "defender",
        "category": "core",
        "label_key": "defender_label",
        "tooltip_key": "defender_tooltip",
        "action_key": "action_defender",
        "risk": "medium",
        "enabled": False,
    },
    {
        "key": "wifisense",
        "category": "core",
        "label_key": "wifisense_label",
        "tooltip_key": "wifisense_tooltip",
        "action_key": "action_wifisense",
        "risk": "low",
    },
    {
        "key": "onedrive",
        "category": "core",
        "label_key": "onedrive_label",
        "tooltip_key": "onedrive_tooltip",
        "action_key": "action_onedrive",
        "risk": "medium",
    },
    {
        "key": "dvr",
        "category": "core",
        "label_key": "dvr_label",
        "tooltip_key": "dvr_tooltip",
        "action_key": "action_dvr",
        "risk": "low",
    },
    {
        "key": "advertising_id",
        "category": "privacy_plus",
        "label_key": "advertising_id_label",
        "tooltip_key": "advertising_id_tooltip",
        "action_key": "action_advertising_id",
        "risk": "low",
    },
    {
        "key": "activity_history",
        "category": "privacy_plus",
        "label_key": "activity_history_label",
        "tooltip_key": "activity_history_tooltip",
        "action_key": "action_activity_history",
        "risk": "low",
    },
    {
        "key": "cross_device_clipboard",
        "category": "privacy_plus",
        "label_key": "cross_device_clipboard_label",
        "tooltip_key": "cross_device_clipboard_tooltip",
        "action_key": "action_cross_device_clipboard",
        "risk": "low",
    },
    {
        "key": "input_personalization",
        "category": "privacy_plus",
        "label_key": "input_personalization_label",
        "tooltip_key": "input_personalization_tooltip",
        "action_key": "action_input_personalization",
        "risk": "low",
    },
    {
        "key": "tailored_experiences",
        "category": "privacy_plus",
        "label_key": "tailored_experiences_label",
        "tooltip_key": "tailored_experiences_tooltip",
        "action_key": "action_tailored_experiences",
        "risk": "low",
    },
    {
        "key": "feedback_notifications",
        "category": "privacy_plus",
        "label_key": "feedback_notifications_label",
        "tooltip_key": "feedback_notifications_tooltip",
        "action_key": "action_feedback_notifications",
        "risk": "low",
    },
    {
        "key": "host",
        "category": "network",
        "label_key": "host_label",
        "tooltip_key": "host_tooltip",
        "action_key": "action_hosts_normal",
        "risk": "medium",
    },
    {
        "key": "extra_host",
        "category": "network",
        "label_key": "extra_host_label",
        "tooltip_key": "extra_host_tooltip",
        "action_key": "action_hosts_extra",
        "risk": "medium",
    },
    {
        "key": "ip",
        "category": "network",
        "label_key": "ip_label",
        "tooltip_key": "ip_tooltip",
        "action_key": "action_ip_block",
        "risk": "medium",
    },
)

OPTION_INDEX = {option["key"]: option for option in OPTION_DEFINITIONS}

PRESET_BALANCED = {
    "service": True,
    "diagtrack": True,
    "telemetry": True,
    "defender": False,
    "wifisense": True,
    "onedrive": True,
    "dvr": True,
    "advertising_id": True,
    "activity_history": True,
    "cross_device_clipboard": True,
    "input_personalization": True,
    "tailored_experiences": True,
    "feedback_notifications": True,
    "host": False,
    "extra_host": False,
    "ip": False,
}


def settings_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            base_dir = os.path.join(appdata, "DisableWinTracking")
    else:
        base_dir = os.path.join(os.path.expanduser("~"), ".disablewintracking")

    try:
        os.makedirs(base_dir, exist_ok=True)
    except OSError:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

    return os.path.join(base_dir, "settings.json")


def load_app_settings():
    loaded = SETTINGS_DEFAULTS.copy()
    path = settings_path()

    try:
        with open(path, "r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)
            if isinstance(data, dict):
                loaded.update({k: v for k, v in data.items() if k in loaded})
    except (OSError, IOError, ValueError):
        pass

    loaded["language"] = dwt_i18n.normalize_language(loaded.get("language"))
    loaded["preset"] = loaded.get("preset") if loaded.get("preset") in (
        "balanced",
        "custom",
    ) else "balanced"
    return loaded


def save_app_settings(settings):
    path = settings_path()
    data = SETTINGS_DEFAULTS.copy()
    data.update({k: v for k, v in settings.items() if k in data})
    data["language"] = dwt_i18n.normalize_language(data.get("language"))
    if data.get("preset") not in ("balanced", "custom"):
        data["preset"] = "balanced"

    try:
        with open(path, "w", encoding="utf-8") as settings_file:
            json.dump(data, settings_file, indent=2, sort_keys=True)
    except (OSError, IOError):
        pass


class RedirectText(io.StringIO):
    def __init__(self, console, old_stdout):
        super(RedirectText, self).__init__()
        self.out = console
        self.old_out = old_stdout

    def write(self, string):
        self.old_out.write(string)
        self.out.WriteText(string)


class ConsoleDialog(wx.Dialog):
    def __init__(self, old_stdout):
        tr = dwt_i18n.translate
        wx.Dialog.__init__(
            self,
            parent=wx.GetApp().TopWindow,
            title=tr("console_title"),
            size=(680, 280),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        console_box = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sys.stdout = RedirectText(console_box, old_stdout)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        console_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        report_button = wx.FindWindowById(wx.ID_CANCEL, self)
        report_button.SetLabel(tr("report_issue"))

        console_sizer.Add(
            console_box, 1, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_TOP, 5
        )

        top_sizer.Add(console_sizer, 1, wx.ALL | wx.EXPAND, 5)
        top_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_LEFT, 5)

        self.Bind(wx.EVT_CLOSE, handler=lambda x: sys.exit(0))
        self.Bind(wx.EVT_BUTTON, handler=lambda x: sys.exit(0), id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, source=report_button, handler=self.submit_issue)
        self.SetSizer(top_sizer)

    def submit_issue(self, event):
        webbrowser.open_new_tab(
            "https://github.com/Potencial/DisableWinTracking/issues/new"
        )


class MainFrame(wx.Frame):
    def __init__(self):
        tr = dwt_i18n.translate
        super(MainFrame, self).__init__(
            parent=wx.GetApp().GetTopWindow(),
            title=tr("app_title"),
            size=(860, 630),
        )

        self.SetMinSize((820, 580))
        panel = MainPanel(self)

        file_menu = wx.Menu()
        settings = file_menu.Append(
            wx.ID_SETUP, tr("menu_settings"), tr("menu_settings_help")
        )

        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ABOUT, tr("menu_about"), tr("menu_about_help"))
        licenses = help_menu.Append(
            wx.ID_ANY, tr("menu_licenses"), tr("menu_licenses_help")
        )

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, tr("menu_file"))
        menu_bar.Append(help_menu, tr("menu_help"))
        self.SetMenuBar(menu_bar)

        check_elevated()

        self.SetIcon(wx.Icon(sys.executable, wx.BITMAP_TYPE_ICO))
        self.Bind(wx.EVT_MENU, lambda x: dwt_about.about_dialog(self), about)
        self.Bind(wx.EVT_MENU, panel.settings, settings)
        self.Bind(wx.EVT_MENU, lambda x: dwt_about.Licenses(self), licenses)
        self.Layout()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)
        self.parent = parent
        self.tr = dwt_i18n.translate
        self.current_language = dwt_i18n.get_language()
        self.current_preset = APP_SETTINGS.get("preset", "balanced")

        self.picked_normal = list(DEFAULT_NORMAL_DOMAINS)
        self.picked_extra = list(DEFAULT_EXTRA_DOMAINS)
        self.picked_ips = list(DEFAULT_IP_ADDRESSES)

        self.option_checkboxes = {}
        self._applying_preset = False
        self.preset_codes = ["balanced", "custom"]

        self._build_ui()
        self.apply_preset(self.current_preset)
        self.refresh_network_summary()

    def _build_ui(self):
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.BoxSizer(wx.HORIZONTAL)
        preset_label = wx.StaticText(self, label=self.tr("preset_label"))
        self.preset_choice = wx.Choice(
            self,
            choices=[self.tr("preset_balanced"), self.tr("preset_custom")],
        )
        reset_button = wx.Button(self, label=self.tr("reset_button"))
        settings_button = wx.Button(self, label=self.tr("configure_lists_button"))

        header.Add(preset_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        header.Add(self.preset_choice, 0, wx.ALL, 5)
        header.Add(reset_button, 0, wx.ALL, 5)
        header.AddStretchSpacer(1)
        header.Add(settings_button, 0, wx.ALL, 5)

        self.notebook = wx.Notebook(self)
        self.core_tab = self._build_core_tab()
        self.privacy_plus_tab = self._build_privacy_plus_tab()
        self.network_tab = self._build_network_tab()

        self.notebook.AddPage(self.core_tab, self.tr("tab_core"))
        self.notebook.AddPage(self.privacy_plus_tab, self.tr("tab_privacy_plus"))
        self.notebook.AddPage(self.network_tab, self.tr("tab_network"))

        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.service_rad = wx.RadioBox(
            self,
            label=self.tr("service_method_label"),
            choices=(self.tr("service_disable"), self.tr("service_delete")),
        )
        self.service_rad.SetItemToolTip(
            item=0, text=self.tr("service_disable_tooltip")
        )
        self.service_rad.SetItemToolTip(
            item=1, text=self.tr("service_delete_tooltip")
        )

        self.mode_rad = wx.RadioBox(
            self,
            label=self.tr("mode_label"),
            choices=(self.tr("mode_privacy"), self.tr("mode_revert")),
        )
        self.mode_rad.SetItemToolTip(item=0, text=self.tr("mode_privacy_tooltip"))
        self.mode_rad.SetItemToolTip(item=1, text=self.tr("mode_revert_tooltip"))

        go_button = wx.Button(self, label=self.tr("go_button"), size=(140, 44))

        controls_sizer.Add(self.service_rad, 0, wx.ALL, 8)
        controls_sizer.Add(self.mode_rad, 0, wx.ALL, 8)
        controls_sizer.AddStretchSpacer(1)
        controls_sizer.Add(go_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)

        top_sizer.Add(header, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        top_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 8)
        top_sizer.Add(controls_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.SetSizer(top_sizer)

        self.Bind(wx.EVT_CHOICE, self.on_preset_changed, self.preset_choice)
        self.Bind(wx.EVT_BUTTON, self.reset_selections, reset_button)
        self.Bind(wx.EVT_BUTTON, self.settings, settings_button)
        self.Bind(wx.EVT_BUTTON, self.go, go_button)

    def _build_core_tab(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for option_key in (
            "service",
            "diagtrack",
            "telemetry",
            "defender",
            "wifisense",
            "onedrive",
            "dvr",
        ):
            sizer.Add(self._create_option_checkbox(panel, OPTION_INDEX[option_key]), 0, wx.ALL, 4)

        panel.SetSizer(sizer)
        return panel

    def _build_privacy_plus_tab(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        intro = wx.StaticText(panel, label=self.tr("privacy_plus_intro"))
        sizer.Add(intro, 0, wx.ALL, 6)

        for option_key in (
            "advertising_id",
            "activity_history",
            "cross_device_clipboard",
            "input_personalization",
            "tailored_experiences",
            "feedback_notifications",
        ):
            sizer.Add(self._create_option_checkbox(panel, OPTION_INDEX[option_key]), 0, wx.ALL, 4)

        panel.SetSizer(sizer)
        return panel

    def _build_network_tab(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for option_key in ("host", "extra_host", "ip"):
            sizer.Add(self._create_option_checkbox(panel, OPTION_INDEX[option_key]), 0, wx.ALL, 4)

        self.network_summary = wx.StaticText(panel, label="")
        configure_button = wx.Button(panel, label=self.tr("configure_lists_button"))

        sizer.AddSpacer(10)
        sizer.Add(self.network_summary, 0, wx.ALL, 4)
        sizer.Add(configure_button, 0, wx.ALL, 4)

        self.Bind(wx.EVT_BUTTON, self.settings, configure_button)

        panel.SetSizer(sizer)
        return panel

    def _create_option_checkbox(self, parent, option):
        checkbox = wx.CheckBox(parent, label=self.tr(option["label_key"]))
        checkbox.option_key = option["key"]
        checkbox.SetToolTip(self.tr(option["tooltip_key"]))
        if not option.get("enabled", True):
            checkbox.Enable(False)

        self.option_checkboxes[option["key"]] = checkbox
        self.Bind(wx.EVT_CHECKBOX, self.on_option_toggled, checkbox)
        return checkbox

    def on_option_toggled(self, event):
        checkbox = event.GetEventObject()
        option_key = checkbox.option_key

        if option_key == "ip" and checkbox.IsChecked():
            self.ip_warn(event)
        elif option_key == "extra_host" and checkbox.IsChecked():
            self.hosts_warn(event)

        if not self._applying_preset:
            self.set_preset("custom")

        self.refresh_network_summary()

    def on_preset_changed(self, event):
        preset = self.preset_codes[self.preset_choice.GetSelection()]
        self.apply_preset(preset)

    def set_preset(self, preset):
        self.current_preset = preset
        APP_SETTINGS["preset"] = preset
        save_app_settings(APP_SETTINGS)
        self.preset_choice.SetSelection(self.preset_codes.index(preset))

    def apply_preset(self, preset):
        if preset not in self.preset_codes:
            preset = "balanced"

        if preset == "balanced":
            target_state = PRESET_BALANCED
        else:
            target_state = {key: False for key in self.option_checkboxes}

        self._applying_preset = True
        for key, checkbox in self.option_checkboxes.items():
            checkbox.SetValue(bool(target_state.get(key, False)))
        self._applying_preset = False

        self.set_preset(preset)
        self.refresh_network_summary()

    def reset_selections(self, event):
        self.apply_preset("custom")

    def refresh_network_summary(self):
        self.network_summary.SetLabel(
            self.tr(
                "network_selection_summary",
                domains=len(self.picked_normal),
                extra=len(self.picked_extra),
                ips=len(self.picked_ips),
            )
        )

    def ip_warn(self, event):
        warn = wx.MessageDialog(
            parent=self,
            message=self.tr("ip_warning"),
            caption=self.tr("attention"),
            style=wx.YES_NO | wx.ICON_EXCLAMATION,
        )

        if warn.ShowModal() == wx.ID_NO:
            event.GetEventObject().SetValue(False)
        warn.Destroy()

    def hosts_warn(self, event):
        warn = wx.MessageDialog(
            parent=self,
            message=self.tr("extra_hosts_warning"),
            caption=self.tr("attention"),
            style=wx.YES_NO | wx.ICON_EXCLAMATION,
        )

        if warn.ShowModal() == wx.ID_NO:
            event.GetEventObject().SetValue(False)
        warn.Destroy()

    def _add_action(self, actions, label_key, risk, func):
        actions.append((self.tr(label_key), risk, func))

    def build_actions(self, undo):
        selected = {
            key: checkbox.IsChecked()
            for key, checkbox in self.option_checkboxes.items()
            if checkbox.IsEnabled()
        }
        actions = []

        if selected.get("service"):
            if not undo:
                if self.service_rad.GetSelection() == 1:
                    self._add_action(
                        actions,
                        "action_service_delete_dmw",
                        "medium",
                        partial(dwt_util.delete_service, "dmwappushsvc"),
                    )
                    self._add_action(
                        actions,
                        "action_service_delete_diag",
                        "medium",
                        partial(dwt_util.delete_service, "DiagTrack"),
                    )
                else:
                    self._add_action(
                        actions,
                        "action_service_disable_dmw",
                        "medium",
                        partial(dwt_util.disable_service, "dmwappushsvc"),
                    )
                    self._add_action(
                        actions,
                        "action_service_disable_diag",
                        "medium",
                        partial(dwt_util.disable_service, "DiagTrack"),
                    )
            self._add_action(
                actions,
                OPTION_INDEX["service"]["action_key"],
                OPTION_INDEX["service"]["risk"],
                partial(dwt_util.services, undo=undo),
            )

        if selected.get("diagtrack") and not undo:
            self._add_action(
                actions,
                OPTION_INDEX["diagtrack"]["action_key"],
                OPTION_INDEX["diagtrack"]["risk"],
                dwt_util.clear_diagtrack,
            )

        if selected.get("telemetry"):
            self._add_action(
                actions,
                OPTION_INDEX["telemetry"]["action_key"],
                OPTION_INDEX["telemetry"]["risk"],
                partial(dwt_util.telemetry, undo=undo),
            )

        if selected.get("host"):
            self._add_action(
                actions,
                OPTION_INDEX["host"]["action_key"],
                OPTION_INDEX["host"]["risk"],
                partial(dwt_util.host_file, self.picked_normal, undo=undo),
            )

        if selected.get("extra_host"):
            self._add_action(
                actions,
                OPTION_INDEX["extra_host"]["action_key"],
                OPTION_INDEX["extra_host"]["risk"],
                partial(dwt_util.host_file, self.picked_extra, undo=undo),
            )

        if selected.get("ip"):
            self._add_action(
                actions,
                OPTION_INDEX["ip"]["action_key"],
                OPTION_INDEX["ip"]["risk"],
                partial(dwt_util.ip_block, self.picked_ips, undo=undo),
            )

        if selected.get("defender"):
            self._add_action(
                actions,
                OPTION_INDEX["defender"]["action_key"],
                OPTION_INDEX["defender"]["risk"],
                partial(dwt_util.defender, undo=undo),
            )

        if selected.get("wifisense"):
            self._add_action(
                actions,
                OPTION_INDEX["wifisense"]["action_key"],
                OPTION_INDEX["wifisense"]["risk"],
                partial(dwt_util.wifisense, undo=undo),
            )

        if selected.get("onedrive"):
            self._add_action(
                actions,
                OPTION_INDEX["onedrive"]["action_key"],
                OPTION_INDEX["onedrive"]["risk"],
                partial(dwt_util.onedrive, undo=undo),
            )

        if selected.get("dvr"):
            self._add_action(
                actions,
                OPTION_INDEX["dvr"]["action_key"],
                OPTION_INDEX["dvr"]["risk"],
                partial(dwt_util.dvr, undo=undo),
            )

        for privacy_key in (
            "advertising_id",
            "activity_history",
            "cross_device_clipboard",
            "input_personalization",
            "tailored_experiences",
            "feedback_notifications",
        ):
            if selected.get(privacy_key):
                self._add_action(
                    actions,
                    OPTION_INDEX[privacy_key]["action_key"],
                    OPTION_INDEX[privacy_key]["risk"],
                    partial(getattr(dwt_util, privacy_key), undo=undo),
                )

        return actions

    def confirm_actions(self, actions, undo):
        mode_name = self.tr("mode_revert") if undo else self.tr("mode_privacy")
        lines = [self.tr("action_summary_mode", mode=mode_name), ""]
        for label, risk, _ in actions:
            lines.append(
                "- [{risk}] {label}".format(
                    risk=self.tr(RISK_LABEL_KEYS[risk]),
                    label=label,
                )
            )

        message = "{header}\n\n{items}".format(
            header=self.tr("action_summary_prompt"),
            items="\n".join(lines),
        )

        dialog = wx.MessageDialog(
            parent=self,
            message=message,
            caption=self.tr("action_summary_title"),
            style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )
        accepted = dialog.ShowModal() == wx.ID_YES
        dialog.Destroy()
        return accepted

    def execute_actions(self, actions):
        failures = 0
        progress = wx.ProgressDialog(
            self.tr("apply_progress_title"),
            self.tr("apply_progress_start"),
            maximum=len(actions),
            parent=self,
            style=(
                wx.PD_APP_MODAL
                | wx.PD_ELAPSED_TIME
                | wx.PD_REMAINING_TIME
                | wx.PD_AUTO_HIDE
            ),
        )

        for index, (label, _, action) in enumerate(actions, start=1):
            progress.Update(
                index - 1,
                self.tr(
                    "apply_progress_running",
                    current=index,
                    total=len(actions),
                    action=label,
                ),
            )
            try:
                result = action()
                if result is False:
                    failures += 1
                    logger.warning("Action reported failure: %s", label)
            except Exception:
                failures += 1
                logger.exception("Action failed: %s", label)

        progress.Update(len(actions), self.tr("apply_progress_done", failures=failures))
        progress.Destroy()
        return failures

    def go(self, event):
        undo = bool(self.mode_rad.GetSelection())
        actions = self.build_actions(undo=undo)

        if not actions:
            info = wx.MessageDialog(
                self,
                self.tr("action_summary_empty"),
                self.tr("action_summary_title"),
                style=wx.OK | wx.ICON_INFORMATION,
            )
            info.ShowModal()
            info.Destroy()
            return

        if not self.confirm_actions(actions, undo=undo):
            return

        failures = self.execute_actions(actions)

        logger.info(self.tr("done_reboot"))
        logger.info(self.tr("done_report"))
        if failures:
            logger.warning(self.tr("execution_failures", failures=failures))

        console.Center()
        console.Show()

    def _create_picker(self, dialog, selected_label, all_items, current_selected):
        picker = ItemsPicker(
            dialog,
            choices=[],
            selectedLabel=selected_label,
            ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES,
        )

        selected_items = list(current_selected) if current_selected else list(all_items)
        selected_set = set(selected_items)
        picker.SetSelections(selected_items)
        picker.SetItems([item for item in all_items if item not in selected_set])
        return picker

    def settings(self, event=None):
        dialog = wx.Dialog(
            parent=self,
            title=self.tr("settings_title"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        sizer = wx.BoxSizer(wx.VERTICAL)

        language_codes = [code for code, _ in dwt_i18n.get_language_choices()]
        language_labels = [label for _, label in dwt_i18n.get_language_choices()]

        language_row = wx.BoxSizer(wx.HORIZONTAL)
        language_label = wx.StaticText(dialog, label=self.tr("language_label"))
        language_choice = wx.Choice(dialog, choices=language_labels)
        try:
            language_choice.SetSelection(language_codes.index(self.current_language))
        except ValueError:
            language_choice.SetSelection(0)

        language_row.Add(language_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        language_row.Add(language_choice, 1, wx.ALL | wx.EXPAND, 5)

        normal_picker = self._create_picker(
            dialog,
            self.tr("domain_picker"),
            DEFAULT_NORMAL_DOMAINS,
            self.picked_normal,
        )
        extra_picker = self._create_picker(
            dialog,
            self.tr("extra_domain_picker"),
            DEFAULT_EXTRA_DOMAINS,
            self.picked_extra,
        )
        ip_picker = self._create_picker(
            dialog,
            self.tr("ip_picker"),
            DEFAULT_IP_ADDRESSES,
            self.picked_ips,
        )

        sizer.Add(language_row, 0, wx.EXPAND)
        sizer.Add(normal_picker, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(extra_picker, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(ip_picker, 0, wx.EXPAND | wx.ALL, 2)

        button_sizer = dialog.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        if button_sizer:
            sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)

        dialog.SetSizerAndFit(sizer)
        dialog.Center()

        if dialog.ShowModal() == wx.ID_CANCEL:
            dialog.Destroy()
            return

        self.picked_normal = normal_picker.GetSelections()
        self.picked_extra = extra_picker.GetSelections()
        self.picked_ips = ip_picker.GetSelections()
        self.refresh_network_summary()

        selected_language = language_codes[language_choice.GetSelection()]
        if selected_language != self.current_language:
            self.current_language = selected_language
            dwt_i18n.set_language(self.current_language)
            APP_SETTINGS["language"] = self.current_language
            save_app_settings(APP_SETTINGS)

            info = wx.MessageDialog(
                parent=self,
                message=self.tr("language_changed"),
                caption=self.tr("settings_title"),
                style=wx.OK | wx.ICON_INFORMATION,
            )
            info.ShowModal()
            info.Destroy()

        dialog.Destroy()


def setup_logging():
    global logger
    logger = logging.getLogger("dwt")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )

    stdout_log = logging.StreamHandler(sys.stdout)
    stdout_log.setLevel(logging.DEBUG)
    stdout_log.setFormatter(formatter)
    logger.addHandler(stdout_log)

    try:
        file_log = logging.FileHandler(filename="dwt.log")
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(formatter)
        logger.addHandler(file_log)
    except (OSError, IOError):
        app = wx.GetApp()
        parent = app.GetTopWindow() if app else None
        error_dialog = wx.MessageDialog(
            parent=parent,
            message=dwt_i18n.translate("log_file_error"),
            caption=dwt_i18n.translate("error_title"),
            style=wx.OK | wx.ICON_ERROR,
        )
        error_dialog.ShowModal()
        error_dialog.Destroy()
        logger.exception("Could not create log file.")

    logger.info(
        "Python {version} on {platform}".format(
            version=sys.version, platform=sys.platform
        )
    )
    logger.info(platform.uname())
    logger.info("DisableWinTracking version {v}".format(v=dwt_about.__version__))


def exception_hook(error, value, trace):
    error_message = "".join(traceback.format_exception(error, value, trace))
    logger.critical(error_message)

    error_dialog = wx.MessageDialog(
        parent=wx.GetApp().GetTopWindow(),
        message=dwt_i18n.translate("exception_msg", error=error_message),
        caption=dwt_i18n.translate("error_title"),
        style=wx.OK | wx.CANCEL | wx.ICON_ERROR,
    )
    error_dialog.SetOKCancelLabels(
        dwt_i18n.translate("exception_ignore"), dwt_i18n.translate("exception_quit")
    )

    if error_dialog.ShowModal() != wx.ID_OK:
        error_dialog.Destroy()
        sys.exit(1)
    error_dialog.Destroy()


def check_elevated(silent=False, revert=False):
    if bool(windll.advpack.IsNTAdmin(0, None)):
        return

    args = u(__file__)
    if silent:
        args = u("{0} {1}").format(
            u(__file__),
            u("-silent-revert") if revert else u("-silent"),
        )

    windll.shell32.ShellExecuteW(None, u("runas"), u(sys.executable), args, None, 1)
    sys.exit(1)


def get_silent_profile_actions(undo=False):
    actions = []

    if not undo:
        actions.extend(
            [
                ("clear_diagtrack", dwt_util.clear_diagtrack),
                (
                    "disable_service_dmwappushsvc",
                    partial(dwt_util.disable_service, "dmwappushsvc"),
                ),
                ("disable_service_diagtrack", partial(dwt_util.disable_service, "DiagTrack")),
            ]
        )

    actions.extend(
        [
            ("services", partial(dwt_util.services, undo=undo)),
            ("telemetry", partial(dwt_util.telemetry, undo=undo)),
            ("wifisense", partial(dwt_util.wifisense, undo=undo)),
            ("onedrive", partial(dwt_util.onedrive, undo=undo)),
            ("dvr", partial(dwt_util.dvr, undo=undo)),
            ("advertising_id", partial(dwt_util.advertising_id, undo=undo)),
            ("activity_history", partial(dwt_util.activity_history, undo=undo)),
            (
                "cross_device_clipboard",
                partial(dwt_util.cross_device_clipboard, undo=undo),
            ),
            (
                "input_personalization",
                partial(dwt_util.input_personalization, undo=undo),
            ),
            ("tailored_experiences", partial(dwt_util.tailored_experiences, undo=undo)),
            (
                "feedback_notifications",
                partial(dwt_util.feedback_notifications, undo=undo),
            ),
        ]
    )

    return actions


def run_silent_profile(undo=False):
    for action_name, action in get_silent_profile_actions(undo=undo):
        logger.info("Silent profile: running %s", action_name)
        try:
            result = action()
            if result is False:
                logger.warning("Silent profile action reported failure: %s", action_name)
        except Exception:
            logger.exception("Silent profile action failed: %s", action_name)


def silent(undo=False):
    setup_logging()
    check_elevated(silent=True, revert=undo)
    run_silent_profile(undo=undo)
    logger.info("COMPLETE" if not undo else "REVERT COMPLETE")


if __name__ == "__main__":
    APP_SETTINGS = load_app_settings()
    dwt_i18n.set_language(APP_SETTINGS.get("language"))

    if "-silent-revert" in sys.argv:
        silent(undo=True)
        sys.exit(0)

    if "-silent" in sys.argv:
        silent(undo=False)
        sys.exit(0)

    wx_app = wx.App()
    frame = MainFrame()
    console = ConsoleDialog(sys.stdout)
    setup_logging()
    sys.excepthook = exception_hook
    dwt_about.update_check(None)
    frame.Show()
    wx_app.MainLoop()
