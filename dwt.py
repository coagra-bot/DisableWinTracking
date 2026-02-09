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
import logging
import sys
import io
import json
import os
import platform
import traceback
import webbrowser
from ctypes import windll
from six import u

import wx
from wx.lib.itemspicker import (
    ItemsPicker,
    IP_SORT_SELECTED,
    IP_SORT_CHOICES,
    IP_REMOVE_FROM_CHOICES,
)

import dwt_about
import dwt_i18n
import dwt_util


SETTINGS_DEFAULTS = {
    "language": "en",
}
APP_SETTINGS = SETTINGS_DEFAULTS.copy()


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
    return loaded


def save_app_settings(settings):
    path = settings_path()
    data = SETTINGS_DEFAULTS.copy()
    data.update({k: v for k, v in settings.items() if k in data})
    data["language"] = dwt_i18n.normalize_language(data.get("language"))

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
        # Oh my god this is the DUMBEST THING I've ever done. (Keeping a reference to the old stdout)
        self.old_out.write(string)
        self.out.WriteText(string)


class ConsoleDialog(wx.Dialog):
    def __init__(self, old_stdout):
        tr = dwt_i18n.translate
        wx.Dialog.__init__(
            self,
            parent=wx.GetApp().TopWindow,
            title=tr("console_title"),
            size=(500, 200),
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
            size=(415, 245),
        )

        self.SetMinSize(self.GetSize())
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
        self.picked_normal = []
        self.picked_extra = []
        self.picked_ips = []

        self.service_check = wx.CheckBox(self, label=self.tr("services_label"))
        self.service_check.SetToolTip(
            self.tr("services_tooltip")
        )

        self.diagtrack_check = wx.CheckBox(self, label=self.tr("diagtrack_label"))
        self.diagtrack_check.SetToolTip(
            self.tr("diagtrack_tooltip")
        )

        # Telemetry checkbox
        self.telemetry_check = wx.CheckBox(self, label=self.tr("telemetry_label"))
        self.telemetry_check.SetToolTip(
            self.tr("telemetry_tooltip")
        )

        # HOSTS file checkbox
        self.host_check = wx.CheckBox(self, label=self.tr("host_label"))
        self.host_check.SetToolTip(
            self.tr("host_tooltip")
        )

        # Extra HOSTS checkbox
        self.extra_host_check = wx.CheckBox(self, label=self.tr("extra_host_label"))
        self.extra_host_check.SetToolTip(self.tr("extra_host_tooltip"))

        # IP block checkbox
        self.ip_check = wx.CheckBox(self, label=self.tr("ip_label"))
        self.ip_check.SetToolTip(self.tr("ip_tooltip"))

        # Windows Privacy Regs (Policy Manager)
        self.defender_check = wx.CheckBox(self, label=self.tr("defender_label"))
        # self.defender_check.SetToolTip("Modifies registry to prevent Defender collection")
        # Disable defender option until a solution is found.
        self.defender_check.SetToolTip(self.tr("defender_tooltip"))
        self.defender_check.Enable(False)

        # WifiSense checkbox
        self.wifisense_check = wx.CheckBox(self, label=self.tr("wifisense_label"))

        # OneDrive uninstall checkbox
        self.onedrive_check = wx.CheckBox(self, label=self.tr("onedrive_label"))
        self.onedrive_check.SetToolTip(self.tr("onedrive_tooltip"))

        # Xbox DVR checkbox
        self.dvr_check = wx.CheckBox(self, label=self.tr("dvr_label"))
        self.dvr_check.SetToolTip(self.tr("dvr_tooltip"))

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

        go_button = wx.Button(self, label=self.tr("go_button"))

        # Temporarily removed due to issues with not being able to restore apps properly
        # This was honestly beyond the scope of the project to begin with and shouldn't have been implemented

        """self.app_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Built-in Apps")
		stat_box = self.app_box.GetStaticBox()
		top_app_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_app_sizer = wx.BoxSizer(wx.HORIZONTAL)
		left_app_sizer = wx.BoxSizer(wx.VERTICAL)
		middle_app_sizer = wx.BoxSizer(wx.VERTICAL)
		right_app_sizer = wx.BoxSizer(wx.VERTICAL)

		# wx.CheckBox(app_box.GetStaticBox(), label="Name", name="search_name")

		wx.CheckBox(stat_box, label="3D Builder", name="3dbuilder")
		wx.CheckBox(stat_box, label="Alarms && Clocks", name="windowsalarms")
		wx.CheckBox(stat_box, label="Calendar and Mail", name="windowscommunicationsapps")
		wx.CheckBox(stat_box, label="Camera", name="windowscamera")
		wx.CheckBox(stat_box, label="Drawboard PDF", name="drawboardpdf")
		wx.CheckBox(stat_box, label="Feedback Hub", name="windowsfeedbackhub")
		wx.CheckBox(stat_box, label="Food && Drink", name="bingfoodanddrink")
		wx.CheckBox(stat_box, label="Get Office App", name="officehub")
		wx.CheckBox(stat_box, label="Get Skype App", name="skypeapp")
		wx.CheckBox(stat_box, label="Get Started App", name="getstarted")
		wx.CheckBox(stat_box, label="Groove Music", name="zunemusic")
		wx.CheckBox(stat_box, label="Health && Fitness", name="binghealthandfitness")
		wx.CheckBox(stat_box, label="Maps", name="windowsmaps")
		wx.CheckBox(stat_box, label="Messaging", name="messaging")
		wx.CheckBox(stat_box, label="Money", name="bingfinance")
		wx.CheckBox(stat_box, label="Movies && TV", name="zunevideo")
		wx.CheckBox(stat_box, label="News", name="bingnews")
		wx.CheckBox(stat_box, label="OneNote App", name="onenote")
		wx.CheckBox(stat_box, label="People", name="people")
		wx.CheckBox(stat_box, label="Phone Companion", name="windowsphone")
		wx.CheckBox(stat_box, label="Photos", name="photos")
		wx.CheckBox(stat_box, label="Reader", name="reader")
		wx.CheckBox(stat_box, label="Reading List", name="windowsreadinglist")
		wx.CheckBox(stat_box, label="Solitaire Collection", name="solitairecollection")
		wx.CheckBox(stat_box, label="Sports", name="bingsports")
		wx.CheckBox(stat_box, label="Sticky Notes", name="microsoftstickynotes")
		wx.CheckBox(stat_box, label="Sway App", name="sway")
		wx.CheckBox(stat_box, label="Travel", name="bingtravel")
		wx.CheckBox(stat_box, label="Voice Recorder", name="soundrecorder")
		wx.CheckBox(stat_box, label="Weather", name="bingweather")
		wx.CheckBox(stat_box, label="Xbox", name="xboxapp")
		remove_app_button = wx.Button(stat_box, label="Remove selected apps")
		select_all_check = wx.CheckBox(stat_box, label="Select all")

		sorted_list = sorted(stat_box.GetChildren(), key=lambda x: x.GetLabel())
		for index, item in enumerate([x for x in sorted_list if isinstance(x, wx.CheckBox) and x != select_all_check]):
			n = len(sorted_list) // 3
			if index <= n:
				left_app_sizer.Add(item, 1, wx.ALL, 1)
			elif index <= n * 2:
				middle_app_sizer.Add(item, 1, wx.ALL, 1)
			else:
				right_app_sizer.Add(item, 1, wx.ALL, 1)

		top_app_sizer.Add(left_app_sizer, 1, wx.ALL, 1)
		top_app_sizer.Add(middle_app_sizer, 1, wx.ALL, 1)
		top_app_sizer.Add(right_app_sizer, 1, wx.ALL, 1)
		button_app_sizer.Add(remove_app_button, 0, wx.ALL, 1)
		button_app_sizer.Add(select_all_check, 1, wx.ALL, 5)
		self.app_box.Add(top_app_sizer)
		self.app_box.Add(button_app_sizer)"""

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        check_sizer = wx.BoxSizer(wx.VERTICAL)
        rad_sizer = wx.BoxSizer(wx.VERTICAL)

        top_sizer.Add(top_row_sizer, 0, wx.ALL, 5)
        # top_sizer.Add(self.app_box, 0, wx.ALL, 5)
        top_row_sizer.Add(check_sizer, 0, wx.ALL)
        top_row_sizer.Add(rad_sizer, 0, wx.ALL)
        rad_sizer.Add(self.service_rad, 0, wx.ALL, 10)
        rad_sizer.Add(go_button, 0, wx.ALL ^ wx.BOTTOM | wx.ALIGN_CENTER, 10)
        rad_sizer.Add(self.mode_rad, 0, wx.ALL, 10)
        check_sizer.Add(self.service_check, 0, wx.ALL, 1)
        check_sizer.Add(self.diagtrack_check, 0, wx.ALL, 1)
        check_sizer.Add(self.telemetry_check, 0, wx.ALL, 1)
        check_sizer.Add(self.host_check, 0, wx.ALL, 1)
        check_sizer.Add(self.extra_host_check, 0, wx.ALL, 1)
        check_sizer.Add(self.ip_check, 0, wx.ALL, 1)
        check_sizer.Add(self.defender_check, 0, wx.ALL, 1)
        check_sizer.Add(self.wifisense_check, 0, wx.ALL, 1)
        check_sizer.Add(self.onedrive_check, 0, wx.ALL, 1)
        check_sizer.Add(self.dvr_check, 0, wx.ALL, 1)

        # self.Bind(wx.EVT_CHECKBOX, handler=self.select_all_apps, source=select_all_check)
        self.Bind(wx.EVT_CHECKBOX, handler=self.ip_warn, source=self.ip_check)
        self.Bind(
            wx.EVT_CHECKBOX, handler=self.hosts_warn, source=self.extra_host_check
        )
        # self.Bind(wx.EVT_BUTTON, handler=self.remove_apps, source=remove_app_button)
        self.Bind(wx.EVT_BUTTON, handler=self.go, source=go_button)

        self.SetSizer(top_sizer)

    def select_all_apps(self, event):
        # Iters through all children of the wxStaticBox of the wxStaticBoxSizer and checks/un checks all wxCheckBoxes.
        for child in self.app_box.GetStaticBox().GetChildren():
            if isinstance(child, wx.CheckBox):
                child.SetValue(event.IsChecked())

    def ip_warn(self, event):
        # Warn users about the potential side effects of the IP blocking firewall rules
        if event.IsChecked():
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
        # Warn users about the potential side effects of the extra hosts mod.
        if event.IsChecked():
            warn = wx.MessageDialog(
                parent=self,
                message=self.tr("extra_hosts_warning"),
                caption=self.tr("attention"),
                style=wx.YES_NO | wx.ICON_EXCLAMATION,
            )

            if warn.ShowModal() == wx.ID_NO:
                event.GetEventObject().SetValue(False)

            warn.Destroy()

    def go(self, event):
        if not all((self.picked_ips, self.picked_extra, self.picked_normal)):
            self.settings(event=None)

        undo = bool(self.mode_rad.GetSelection())

        if self.ip_check.IsChecked():
            dwt_util.ip_block(self.picked_ips, undo=undo)
        if self.diagtrack_check.IsChecked():
            dwt_util.clear_diagtrack()
        if self.service_check.IsChecked():
            if self.service_rad.GetSelection():
                dwt_util.delete_service("dmwappushsvc")
                dwt_util.delete_service("DiagTrack")
            else:
                dwt_util.disable_service("dmwappushsvc")
                dwt_util.disable_service("DiagTrack")
            dwt_util.services(undo=undo)
        if self.telemetry_check.IsChecked():
            dwt_util.telemetry(undo=undo)
        if self.host_check.IsChecked():
            dwt_util.host_file(self.picked_normal, undo=undo)
        if self.extra_host_check.IsChecked():
            dwt_util.host_file(self.picked_extra, undo=undo)
        if self.defender_check.IsChecked():
            dwt_util.defender(undo=undo)
        if self.wifisense_check.IsChecked():
            dwt_util.wifisense(undo=undo)
        if self.onedrive_check.IsChecked():
            dwt_util.onedrive(undo=undo)
        if self.dvr_check.IsChecked():
            dwt_util.dvr(undo=undo)
        logger.info(self.tr("done_reboot"))
        logger.info(self.tr("done_report"))
        console.Center()
        console.Show()

    def remove_apps(self, event):
        children = [
            child
            for child in self.app_box.GetStaticBox().GetChildren()
            if child.GetName() != "check"
        ]
        app_list = [
            child.GetName()
            for child in children
            if isinstance(child, wx.CheckBox) and child.IsChecked()
        ]
        dwt_util.app_manager(app_list, undo=False)

    def settings(self, event, silent=False):
        language_codes = []
        language_choice = None

        if not silent:
            dialog = wx.Dialog(
                parent=self,
                title=self.tr("settings_title"),
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            )
            sizer = wx.BoxSizer(wx.VERTICAL)
            language_row = wx.BoxSizer(wx.HORIZONTAL)
            language_codes = [code for code, _ in dwt_i18n.get_language_choices()]
            language_labels = [label for _, label in dwt_i18n.get_language_choices()]
            language_label = wx.StaticText(dialog, label=self.tr("language_label"))
            language_choice = wx.Choice(dialog, choices=language_labels)
            try:
                language_choice.SetSelection(language_codes.index(self.current_language))
            except ValueError:
                language_choice.SetSelection(0)
            language_row.Add(language_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            language_row.Add(language_choice, 1, wx.ALL | wx.EXPAND, 5)
            sizer.Add(language_row, 0, wx.EXPAND)
        else:
            dialog = self

        normal_domains = (
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

        extra_domains = (
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

        ip_addresses = (
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

        normal_domain_picker = ItemsPicker(
            dialog,
            choices=[],
            selectedLabel=self.tr("domain_picker"),
            ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES,
        )
        if self.picked_normal:
            normal_domain_picker.SetSelections(self.picked_normal)
            normal_domain_picker.SetItems(
                [
                    domain
                    for domain in normal_domains
                    if domain not in self.picked_normal
                ]
            )
        else:
            normal_domain_picker.SetSelections(normal_domains)

        extra_domain_picker = ItemsPicker(
            dialog,
            choices=[],
            selectedLabel=self.tr("extra_domain_picker"),
            ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES,
        )
        if self.picked_extra:
            extra_domain_picker.SetSelections(self.picked_extra)
            extra_domain_picker.SetItems(
                [domain for domain in extra_domains if domain not in self.picked_extra]
            )
        else:
            extra_domain_picker.SetSelections(extra_domains)

        ip_picker = ItemsPicker(
            dialog,
            choices=[],
            selectedLabel=self.tr("ip_picker"),
            ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES,
        )
        if self.picked_ips:
            ip_picker.SetSelections(self.picked_ips)
            ip_picker.SetItems([ip for ip in ip_addresses if ip not in self.picked_ips])
        else:
            ip_picker.SetSelections(ip_addresses)

        if not silent:
            sizer.Add(normal_domain_picker, 0, wx.EXPAND)
            sizer.Add(extra_domain_picker, 0, wx.EXPAND)
            sizer.Add(ip_picker, 0, wx.EXPAND)

            button_sizer = dialog.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
            if button_sizer:
                sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)

            dialog.SetSizerAndFit(sizer)

            if event is not None:
                dialog.Center()
                if dialog.ShowModal() == wx.ID_CANCEL:
                    dialog.Destroy()
                    return

            selected_language = language_codes[language_choice.GetSelection()]
            if selected_language != self.current_language:
                global APP_SETTINGS
                self.current_language = selected_language
                dwt_i18n.set_language(self.current_language)
                APP_SETTINGS["language"] = self.current_language
                save_app_settings(APP_SETTINGS)

                if event is not None:
                    info = wx.MessageDialog(
                        parent=self,
                        message=self.tr("language_changed"),
                        caption=self.tr("settings_title"),
                        style=wx.OK | wx.ICON_INFORMATION,
                    )
                    info.ShowModal()
                    info.Destroy()

            dialog.Destroy()

        self.picked_normal = normal_domain_picker.GetSelections()
        self.picked_extra = extra_domain_picker.GetSelections()
        self.picked_ips = ip_picker.GetSelections()


def setup_logging():
    global logger
    logger = logging.getLogger("dwt")
    logger.setLevel(logging.DEBUG)

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
        error_dialog = wx.MessageDialog(
            parent=wx.GetApp().GetTopWindow(),
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
    if error_dialog.ShowModal() == wx.ID_OK:
        error_dialog.Destroy()
    else:
        error_dialog.Destroy()
        sys.exit(1)


def check_elevated(silent=False):
    if not bool(windll.advpack.IsNTAdmin(0, None)):
        if silent:
            windll.shell32.ShellExecuteW(
                None,
                u"runas",
                u(sys.executable),
                u"{0} -silent".format(u(__file__)),
                None,
                1,
            )
            sys.exit(1)
        else:
            windll.shell32.ShellExecuteW(
                None, u"runas", u(sys.executable), u(__file__), None, 1
            )
        sys.exit(1)


def silent():

    setup_logging()
    check_elevated(True)

    dwt_util.clear_diagtrack()
    dwt_util.disable_service("dmwappushsvc")
    dwt_util.disable_service("DiagTrack")
    dwt_util.services(0)
    dwt_util.telemetry(0)
    # dwt_util.defender(0)
    dwt_util.wifisense(0)
    dwt_util.onedrive(0)

    logger.info("COMPLETE")


if __name__ == "__main__":
    APP_SETTINGS = load_app_settings()
    dwt_i18n.set_language(APP_SETTINGS.get("language"))

    if "-silent" in sys.argv:
        silent()
        sys.exit(0)

    wx_app = wx.App()
    frame = MainFrame()
    console = ConsoleDialog(sys.stdout)
    setup_logging()
    sys.excepthook = exception_hook
    dwt_about.update_check(None)
    frame.Show()
    wx_app.MainLoop()
