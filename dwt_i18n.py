# Copyright (C) 10se1ucgo 2015-2016
#
# This file is part of DisableWinTracking.

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Espanol",
}

_DEFAULT_LANG = "en"
_CURRENT_LANG = _DEFAULT_LANG

_TRANSLATIONS = {
    "en": {
        "app_title": "Disable Windows 10 Tracking",
        "console_title": "Console Output",
        "report_issue": "Report an issue",
        "menu_file": "&File",
        "menu_help": "&Help",
        "menu_settings": "&Settings",
        "menu_settings_help": "DWT settings",
        "menu_about": "&About",
        "menu_about_help": "About DWT",
        "menu_licenses": "&Licenses",
        "menu_licenses_help": "Open-source licenses",
        "services_label": "Services",
        "services_tooltip": "Disables or deletes tracking services. Choose option in 'Service Method'",
        "diagtrack_label": "Clear DiagTrack log",
        "diagtrack_tooltip": "Clears Diagnostic Tracking log and prevents modification to it. Cannot be undone automatically.",
        "telemetry_label": "Telemetry",
        "telemetry_tooltip": "Sets 'AllowTelemetry' to 0. On non-Enterprise OS editions, requires HOSTS file modification.",
        "host_label": "Block tracking domains",
        "host_tooltip": "Adds known tracking domains to HOSTS file. Required to disable Telemetry",
        "extra_host_label": "Block even more tracking domains",
        "extra_host_tooltip": "For the paranoid. Adds extra domains to the HOSTS file.\nMay cause issues with Skype, Dr. Watson, Hotmail and/or Error Reporting.",
        "ip_label": "Block tracking IP addresses",
        "ip_tooltip": "Blocks known tracking IP addresses with Windows Firewall.",
        "defender_label": "Windows Defender collection",
        "defender_tooltip": "Disabled due to limitations set by Windows kernel.",
        "wifisense_label": "WifiSense",
        "onedrive_label": "Uninstall OneDrive",
        "onedrive_tooltip": "Uninstalls OneDrive from your computer and removes it from Explorer.",
        "dvr_label": "Disable Xbox DVR",
        "dvr_tooltip": "Disable Xbox DVR feature to increase FPS in games",
        "service_method_label": "Service Method",
        "service_disable": "Disable",
        "service_delete": "Delete",
        "service_disable_tooltip": "Simply disables the services. This can be undone.",
        "service_delete_tooltip": "Deletes the services completely. This cannot be undone.",
        "mode_label": "Mode",
        "mode_privacy": "Privacy",
        "mode_revert": "Revert",
        "mode_privacy_tooltip": "Applies the selected settings.",
        "mode_revert_tooltip": "Reverts the selected settings.",
        "go_button": "Go!",
        "attention": "Attention!",
        "ip_warning": "This option could potentially disable Microsoft Licensing traffic and thus certain games and apps may cease to work, such as Forza or Gears of War.",
        "extra_hosts_warning": "This option could potentially disable one or more of the following services:\n\nSkype, Hotmail, Dr. Watson and/or Error Reporting. Continue?",
        "settings_title": "Settings",
        "language_label": "Language",
        "language_changed": "Language has been updated. Restart the app to fully apply all UI texts.",
        "domain_picker": "Domains to be blocked",
        "extra_domain_picker": "Extra domains to be blocked",
        "ip_picker": "IP addresses to be blocked",
        "done_reboot": "Done. It's recommended that you reboot as soon as possible for the full effect.",
        "done_report": "If you feel something didn't work properly, please press the 'Report an issue' button and follow the directions",
        "log_file_error": "Could not create log file, errors will not be recorded!",
        "error_title": "ERROR!",
        "exception_msg": "An error has occurred!\n\n{error}",
        "exception_ignore": "Ignore",
        "exception_quit": "Quit",
        "about_name": "Disable Windows 10 Tracking",
        "about_description": "A tool to disable tracking in Windows 10",
        "about_website": "GitHub repository",
        "licenses_title": "Licenses",
        "licenses_intro": "DisableWinTracking uses a number of open source software. The following are the licenses for these software.",
        "licenses_wx": "DisableWinTracking uses wxWidgets and wxPython. Their license is below\nMore info at https://www.wxwidgets.org/about/",
        "licenses_pywin": "DisableWinTracking uses PyWin32. Its license is below.",
        "update_title": "DWT Update",
        "update_message": "DWT {version} is now available!\nGo to download page?",
    },
    "es": {
        "app_title": "Deshabilitar rastreo de Windows 10",
        "console_title": "Salida de consola",
        "report_issue": "Reportar un problema",
        "menu_file": "&Archivo",
        "menu_help": "&Ayuda",
        "menu_settings": "&Configuracion",
        "menu_settings_help": "Configuracion de DWT",
        "menu_about": "&Acerca de",
        "menu_about_help": "Acerca de DWT",
        "menu_licenses": "&Licencias",
        "menu_licenses_help": "Licencias de codigo abierto",
        "services_label": "Servicios",
        "services_tooltip": "Deshabilita o elimina servicios de rastreo. Elige una opcion en 'Metodo de servicio'",
        "diagtrack_label": "Limpiar log de DiagTrack",
        "diagtrack_tooltip": "Limpia el log de seguimiento diagnostico e impide su modificacion. No se puede deshacer automaticamente.",
        "telemetry_label": "Telemetria",
        "telemetry_tooltip": "Establece 'AllowTelemetry' en 0. En ediciones que no son Enterprise, requiere modificar el archivo HOSTS.",
        "host_label": "Bloquear dominios de rastreo",
        "host_tooltip": "Agrega dominios de rastreo conocidos al archivo HOSTS. Necesario para deshabilitar Telemetria",
        "extra_host_label": "Bloquear aun mas dominios de rastreo",
        "extra_host_tooltip": "Para los paranoicos. Agrega dominios extra al archivo HOSTS.\nPuede causar problemas con Skype, Dr. Watson, Hotmail y/o Error Reporting.",
        "ip_label": "Bloquear direcciones IP de rastreo",
        "ip_tooltip": "Bloquea direcciones IP de rastreo conocidas con el firewall de Windows.",
        "defender_label": "Recoleccion de Windows Defender",
        "defender_tooltip": "Deshabilitado por limitaciones impuestas por el kernel de Windows.",
        "wifisense_label": "WifiSense",
        "onedrive_label": "Desinstalar OneDrive",
        "onedrive_tooltip": "Desinstala OneDrive de tu equipo y lo quita del Explorador.",
        "dvr_label": "Deshabilitar Xbox DVR",
        "dvr_tooltip": "Deshabilita Xbox DVR para aumentar FPS en juegos",
        "service_method_label": "Metodo de servicio",
        "service_disable": "Deshabilitar",
        "service_delete": "Eliminar",
        "service_disable_tooltip": "Simplemente deshabilita los servicios. Se puede deshacer.",
        "service_delete_tooltip": "Elimina los servicios por completo. No se puede deshacer.",
        "mode_label": "Modo",
        "mode_privacy": "Privacidad",
        "mode_revert": "Revertir",
        "mode_privacy_tooltip": "Aplica la configuracion seleccionada.",
        "mode_revert_tooltip": "Revierte la configuracion seleccionada.",
        "go_button": "Aplicar",
        "attention": "Atencion!",
        "ip_warning": "Esta opcion podria bloquear trafico de licenciamiento de Microsoft y algunos juegos o apps podrian dejar de funcionar, como Forza o Gears of War.",
        "extra_hosts_warning": "Esta opcion podria deshabilitar uno o mas de los siguientes servicios:\n\nSkype, Hotmail, Dr. Watson y/o Error Reporting. Continuar?",
        "settings_title": "Configuracion",
        "language_label": "Idioma",
        "language_changed": "El idioma fue actualizado. Reinicia la aplicacion para aplicar todos los textos de la interfaz.",
        "domain_picker": "Dominios a bloquear",
        "extra_domain_picker": "Dominios extra a bloquear",
        "ip_picker": "Direcciones IP a bloquear",
        "done_reboot": "Listo. Se recomienda reiniciar el equipo lo antes posible para aplicar todos los cambios.",
        "done_report": "Si algo no funciono correctamente, presiona 'Reportar un problema' y sigue las instrucciones",
        "log_file_error": "No se pudo crear el archivo de log, los errores no quedaran registrados!",
        "error_title": "ERROR!",
        "exception_msg": "Ha ocurrido un error!\n\n{error}",
        "exception_ignore": "Ignorar",
        "exception_quit": "Salir",
        "about_name": "Deshabilitar rastreo de Windows 10",
        "about_description": "Herramienta para deshabilitar rastreo en Windows 10",
        "about_website": "Repositorio en GitHub",
        "licenses_title": "Licencias",
        "licenses_intro": "DisableWinTracking usa varios componentes de software libre. A continuacion se muestran sus licencias.",
        "licenses_wx": "DisableWinTracking usa wxWidgets y wxPython. Su licencia se muestra abajo\nMas info en https://www.wxwidgets.org/about/",
        "licenses_pywin": "DisableWinTracking usa PyWin32. Su licencia se muestra abajo.",
        "update_title": "Actualizacion de DWT",
        "update_message": "DWT {version} ya esta disponible!\nIr a la pagina de descarga?",
    },
}


def normalize_language(language):
    return language if language in SUPPORTED_LANGUAGES else _DEFAULT_LANG


def set_language(language):
    global _CURRENT_LANG
    _CURRENT_LANG = normalize_language(language)


def get_language():
    return _CURRENT_LANG


def get_language_choices():
    return [(code, label) for code, label in SUPPORTED_LANGUAGES.items()]


def translate(key, language=None, **kwargs):
    lang = normalize_language(language or _CURRENT_LANG)
    text = _TRANSLATIONS.get(lang, {}).get(key)
    if text is None:
        text = _TRANSLATIONS[_DEFAULT_LANG].get(key, key)

    if kwargs:
        return text.format(**kwargs)

    return text
