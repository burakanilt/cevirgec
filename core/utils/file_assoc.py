"""
Registers Çevirgeç PDF as a PDF handler for the *current user* on Windows.

Windows 10/11 do not allow applications to silently become the default handler;
we register a ProgID + "Capabilities" under HKCU (no admin rights needed) so the
app shows up in "Open with" and in Settings > Default apps, then open that
settings page so the user can confirm the choice.
"""
import os
import sys

PROG_ID = "CevirgecPDF.Document"
APP_NAME = "Çevirgeç PDF"
APP_DESCRIPTION = "Çevrimdışı PDF görüntüleyici ve dönüştürücü"
CAPABILITIES_KEY = r"Software\CevirgecPDF\Capabilities"


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_open_command() -> str:
    """Command line Windows will run when a PDF is opened with this app."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" "%1"'
    # Development mode: prefer pythonw.exe so no console window flashes.
    python = sys.executable
    pythonw = os.path.join(os.path.dirname(python), "pythonw.exe")
    if os.path.exists(pythonw):
        python = pythonw
    script = os.path.join(_project_root(), "app.py")
    return f'"{python}" "{script}" "%1"'


def get_icon_location() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}",0'
    ico = os.path.join(_project_root(), "assets", "icons", "app_icon.ico")
    return f'"{ico}",0' if os.path.exists(ico) else ""


def register_pdf_association() -> None:
    """Writes the HKCU registry entries. Raises OSError on non-Windows."""
    if sys.platform != "win32":
        raise OSError("Windows only")
    import winreg

    def set_value(path: str, name: str, value: str) -> None:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    classes = r"Software\Classes"
    command = get_open_command()
    icon = get_icon_location()

    # 1) ProgID describing how to open a PDF with us
    set_value(rf"{classes}\{PROG_ID}", "", f"PDF ({APP_NAME})")
    set_value(rf"{classes}\{PROG_ID}", "FriendlyTypeName", f"PDF ({APP_NAME})")
    if icon:
        set_value(rf"{classes}\{PROG_ID}\DefaultIcon", "", icon)
    set_value(rf"{classes}\{PROG_ID}\shell\open", "FriendlyAppName", APP_NAME)
    set_value(rf"{classes}\{PROG_ID}\shell\open\command", "", command)

    # 2) Offer the ProgID for .pdf in the "Open with" list
    set_value(rf"{classes}\.pdf\OpenWithProgids", PROG_ID, "")

    # 3) Register capabilities so we appear in Settings > Default apps
    set_value(CAPABILITIES_KEY, "ApplicationName", APP_NAME)
    set_value(CAPABILITIES_KEY, "ApplicationDescription", APP_DESCRIPTION)
    set_value(rf"{CAPABILITIES_KEY}\FileAssociations", ".pdf", PROG_ID)
    set_value(r"Software\RegisteredApplications", APP_NAME, CAPABILITIES_KEY)

    # Tell Explorer that associations changed
    try:
        import ctypes
        SHCNE_ASSOCCHANGED = 0x08000000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, 0, None, None)
    except Exception:
        pass


def open_default_apps_settings() -> None:
    if sys.platform != "win32":
        return
    try:
        # Jump straight to our app's page in Settings (Windows 11); falls back to the list.
        from urllib.parse import quote
        os.startfile(f"ms-settings:defaultapps?registeredAppUser={quote(APP_NAME)}")
    except Exception:
        try:
            os.startfile("ms-settings:defaultapps")
        except Exception:
            pass
