import os
import sys
import re
import time
import queue
import socket
import random
import tempfile
import threading
import subprocess
import urllib.parse
import webbrowser
import requests
import customtkinter as ctk
import uiautomator2 as u2

# ==========================================
# 🚨 NUITKA UIAUTOMATOR CRASH FIX (CORE PATCH)
# ==========================================
try:
    import adbutils
    if hasattr(adbutils, 'sync') and hasattr(adbutils.sync, 'Sync'):
        _orig_push = adbutils.sync.Sync.push
        def _patched_push(self, src, dst, *args, **kwargs):
            if "nuitka_resource" in str(type(src)).lower() or (hasattr(src, 'read_bytes') and not hasattr(src, 'read')):
                tmp_path = os.path.join(tempfile.gettempdir(), getattr(src, 'name', 'temp_app.apk'))
                with open(tmp_path, 'wb') as f:
                    f.write(src.read_bytes())
                res = _orig_push(self, tmp_path, dst, *args, **kwargs)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                return res
            return _orig_push(self, src, dst, *args, **kwargs)
        adbutils.sync.Sync.push = _patched_push

    _orig_install = adbutils.AdbDevice.install
    def _patched_install(self, filepath, *args, **kwargs):
        if "nuitka_resource" in str(type(filepath)).lower() or (hasattr(filepath, 'read_bytes') and not hasattr(filepath, 'read')):
            tmp_path = os.path.join(tempfile.gettempdir(), getattr(filepath, 'name', 'temp_app.apk'))
            with open(tmp_path, 'wb') as f:
                f.write(filepath.read_bytes())
            res = _orig_install(self, tmp_path, *args, **kwargs)
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return res
        return _orig_install(self, filepath, *args, **kwargs)
    adbutils.AdbDevice.install = _patched_install
except Exception:
    pass

# Security Settings
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

# Config Constants
APP_TITLE = "ZENEX ADB AUTOMATIONS"
HEADER_TEXT = "⚡ ZENEX AUTOMATION PRO ⚡"
DISTRIBUTOR_NAME = "Abdullah"
TELEGRAM_USER = "abdullah_124"
TELEGRAM_LINK = "https://t.me/abdullah_124"
FOOTER_TEXT = "Developed by: Abdullah | Owner: ZENEX NETWORK"
API_BASE_URL = "http://135.125.226.195:3004/api/bot"

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

DAEMON_LOCK = threading.Lock()
PROXY_LOCK = threading.Lock()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False) or '__compiled__' in globals():
    CURRENT_DIR = os.path.dirname(sys.executable)
else:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

adb_binary = "adb.exe" if os.name == 'nt' else "adb"
ADB_PATH = os.path.join(CURRENT_DIR, "platform-tools", adb_binary)

if os.path.exists(os.path.join(CURRENT_DIR, "platform-tools")):
    os.environ["PATH"] = os.path.join(CURRENT_DIR, "platform-tools") + os.pathsep + os.environ["PATH"]

LOCAL_APK_PATH = os.path.join(CURRENT_DIR, "uiautomator2", "app-uiautomator.apk")
LOCAL_TEST_APK_PATH = os.path.join(CURRENT_DIR, "uiautomator2", "app-uiautomator-test.apk")

if os.name == 'nt':
    DEFAULT_DATA_DIR = os.getenv('APPDATA', CURRENT_DIR)
else:
    DEFAULT_DATA_DIR = os.path.expanduser('~/Library/Application Support')

APPDATA_DIR = os.path.join(DEFAULT_DATA_DIR, 'ZenexNetwork')
if not os.path.exists(APPDATA_DIR):
    os.makedirs(APPDATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(APPDATA_DIR, 'zenex_config.json')
SUCCESS_LOG_FILE = os.path.join(APPDATA_DIR, 'success_numbers.txt')

# System State Variables
is_running = False
GLOBAL_RUN_TOKEN = 0

valid_numbers_queue = queue.Queue()
txt_numbers_queue = queue.Queue()

GLOBAL_PROXIES = []
device_current_proxy = {}

device_popup_errors = {}
device_dead_proxy_errors = {}
device_fb_success_count = {}
device_force_proxy_change = {}
device_stopped_status = {}

stats_lock = threading.Lock()
stats = {"checked": 0, "valid": 0, "invalid": 0, "otp_sent": 0, "otp_failed": 0}

CURRENT_PANEL = "ZENEX NETWORK"
CURRENT_API_KEY = ""
CURRENT_RANGE = ""

FB_PACKAGES = ["com.facebook.lite", "com.facebook.litx", "app.kkh.pro", "com.kkh.rtx", "com.kkh.plugr", "com.facebook.orca"]
IG_PACKAGES = ["com.instagram.lite", "com.instagram.android"]

LICENSED_USER = "User"
EXPIRY_DATE = "2026-06-30"

device_handles = []
device_checkboxes_vars = {}
device_checkbox_widgets = {}
FILTER_SERVER_DOMAIN = 'm.facebook.com'
device_battery_states = {}

SUBPROCESS_EXTRA_KWARGS = {}
if os.name == 'nt':
    SUBPROCESS_EXTRA_KWARGS['creationflags'] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# ==========================================
# ⚙️ SYSTEM & ADB HELPERS
# ==========================================
def run_cmd(cmd_list, capture_output=True, text=False, timeout=None):
    kwargs = {"capture_output": capture_output, "timeout": timeout}
    if text:
        kwargs["text"] = text
    if os.name == 'nt':
        kwargs["creationflags"] = CREATE_NO_WINDOW
    return subprocess.run(cmd_list, **kwargs)

def check_output_cmd(cmd_list, timeout=None):
    kwargs = {"timeout": timeout}
    if os.name == 'nt':
        kwargs["creationflags"] = CREATE_NO_WINDOW
    return subprocess.check_output(cmd_list, **kwargs)

def get_adb_command():
    if os.path.exists(ADB_PATH):
        return ADB_PATH
    return "adb"

def format_emu_name(text):
    def replacer(match):
        port = int(match.group(1))
        if port in [5555, 5557, 5559, 5561, 5563, 5565, 5567, 5569]:
            return f"emulator-{port-1}"
        return f"emulator-{port}"
    text = re.sub(r'127\.0\.0\.1:(\d+)', replacer, str(text))
    text = re.sub(r'localhost:(\d+)', replacer, text)
    return text

def is_keyboard_shown(serial):
    adb_cmd = get_adb_command()
    try:
        res = run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "input_method"], text=True, timeout=3)
        if "mInputShown=true" in res.stdout:
            return True
    except Exception:
        pass
    return False

def force_kill_adb():
    try:
        if os.name == 'nt':
            run_cmd(["taskkill", "/F", "/IM", "adb.exe", "/T"], timeout=5)
        else:
            run_cmd(["pkill", "-f", "adb"], timeout=5)
    except Exception:
        pass

def get_connected_devices():
    adb_cmd = get_adb_command()
    with DAEMON_LOCK:
        try:
            result = check_output_cmd([adb_cmd, "devices"], timeout=5).decode("utf-8")
            raw_devices = [line.split()[0] for line in result.strip().split('\n')[1:] if 'device' in line and 'offline' not in line]

            if not raw_devices:
                ports = ["5554", "5555", "5556", "5557", "21503", "21513", "62001", "62025"]
                for p in ports:
                    try:
                        run_cmd([adb_cmd, "connect", f"127.0.0.1:{p}"], timeout=1)
                    except Exception:
                        pass
                result = check_output_cmd([adb_cmd, "devices"], timeout=5).decode("utf-8")
                raw_devices = [line.split()[0] for line in result.strip().split('\n')[1:] if 'device' in line and 'offline' not in line]

            clean_devices = []
            for dev in raw_devices:
                if not (dev.startswith("emulator-") or dev.startswith("127.0.0.1:") or dev.startswith("localhost:")):
                    continue

                if dev.startswith("127.0.0.1:") or dev.startswith("localhost:"):
                    try:
                        port = int(dev.split(":")[1])
                        if f"emulator-{port - 1}" in raw_devices or f"emulator-{port}" in raw_devices:
                            continue
                    except Exception:
                        pass

                if dev not in clean_devices:
                    clean_devices.append(dev)

            if 'offline' in result and not clean_devices:
                force_kill_adb()
                time.sleep(1)
                run_cmd([adb_cmd, "start-server"], timeout=5)

                ports = ["5554", "5555", "5556", "5557", "21503", "21513", "62001", "62025"]
                for p in ports:
                    try:
                        run_cmd([adb_cmd, "connect", f"127.0.0.1:{p}"], timeout=1)
                    except Exception:
                        pass

                result = check_output_cmd([adb_cmd, "devices"], timeout=5).decode("utf-8")
                raw_devices = [line.split()[0] for line in result.strip().split('\n')[1:] if 'device' in line and 'offline' not in line]

                clean_devices = []
                for dev in raw_devices:
                    if not (dev.startswith("emulator-") or dev.startswith("127.0.0.1:") or dev.startswith("localhost:")):
                        continue
                    if dev.startswith("127.0.0.1:") or dev.startswith("localhost:"):
                        try:
                            port = int(dev.split(":")[1])
                            if f"emulator-{port - 1}" in raw_devices or f"emulator-{port}" in raw_devices:
                                continue
                        except Exception:
                            pass
                    if dev not in clean_devices:
                        clean_devices.append(dev)

            return clean_devices
        except Exception:
            return []

def background_battery_simulator():
    adb_cmd = get_adb_command()
    while True:
        time.sleep(25)
        if not is_running:
            continue
        try:
            devices = get_connected_devices()
            current_time = time.time()
            with DAEMON_LOCK:
                for serial in devices:
                    if serial not in device_battery_states:
                        start_level = random.randint(45, 85)
                        device_battery_states[serial] = {
                            "level": start_level,
                            "charging": False,
                            "last_update": current_time
                        }
                        try:
                            run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "0"], timeout=2)
                            run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "usb", "0"], timeout=2)
                            run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "unplug"], timeout=2)
                            run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "3"], timeout=2)
                            run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "level", str(start_level)], timeout=2)
                        except Exception:
                            pass
                    else:
                        state = device_battery_states[serial]
                        if current_time - state["last_update"] >= 180:
                            if state["charging"]:
                                state["level"] += random.randint(2, 4)
                                if state["level"] >= random.randint(85, 95):
                                    state["charging"] = False
                                    try:
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "0"], timeout=2)
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "unplug"], timeout=2)
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "3"], timeout=2)
                                    except Exception:
                                        pass
                            else:
                                state["level"] -= 1
                                if state["level"] <= random.randint(10, 15):
                                    state["charging"] = True
                                    try:
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "1"], timeout=2)
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "usb", "1"], timeout=2)
                                        run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "2"], timeout=2)
                                    except Exception:
                                        pass
                            state["level"] = max(5, min(100, state["level"]))
                            state["last_update"] = current_time
                            try:
                                run_cmd([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "level", str(state["level"])], timeout=2)
                            except Exception:
                                pass
        except Exception:
            pass

def adb_keep_alive_daemon(log_cb):
    adb_cmd = get_adb_command()
    while True:
        time.sleep(20)
        if is_running and len(device_checkboxes_vars) > 0:
            with DAEMON_LOCK:
                try:
                    result = check_output_cmd([adb_cmd, "devices"], timeout=5).decode("utf-8")
                    for serial, var in device_checkboxes_vars.items():
                        if var.get():
                            if f"{serial}\tdevice" not in result:
                                log_cb(f"[{serial}] 🔌 ADB Disconnected! Auto-reconnecting silently...", "yellow")
                                run_cmd([adb_cmd, "disconnect", serial], timeout=3)
                                time.sleep(1)
                                run_cmd([adb_cmd, "connect", serial], timeout=3)
                                try:
                                    d = u2.connect(serial)
                                    d.healthcheck()
                                except Exception:
                                    pass
                except Exception:
                    pass

def check_internet_connection(serial):
    adb_cmd = get_adb_command()
    with DAEMON_LOCK:
        try:
            res = run_cmd([adb_cmd, "-s", serial, "shell", "curl -s -I -m 5 https://google.com"], text=True, timeout=8)
            if "HTTP/" in res.stdout or "200" in res.stdout or "301" in res.stdout or "302" in res.stdout:
                return True
            res2 = run_cmd([adb_cmd, "-s", serial, "shell", "ping -c 1 -W 3 8.8.8.8"], text=True, timeout=5)
            if "1 packets transmitted, 1 received" in res2.stdout or "time=" in res2.stdout:
                return True
            return False
        except Exception:
            return False

def check_proxy_live(proxy_string):
    proxy_string = proxy_string.replace("socks5://", "").replace("http://", "").strip()
    parts = proxy_string.split(":")
    if len(parts) >= 2:
        host, port = parts[0], parts[1]
        try:
            proxy_url = f"http://{parts[2]}:{parts[3]}@{host}:{port}" if len(parts) == 4 else f"http://{host}:{port}"
            res = requests.get("http://clients3.google.com/generate_204", proxies={"http": proxy_url, "https": proxy_url}, timeout=8)
            if res.status_code in [200, 204]:
                return True
        except Exception:
            pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4.0)
            s.connect((host, int(port)))
            s.close()
            return True
        except Exception:
            pass
    return False

def live_proxy_checker_daemon(app):
    while True:
        time.sleep(10)
        if not is_running:
            continue
        devices = get_connected_devices()
        for serial in devices:
            if serial in device_checkboxes_vars and device_checkboxes_vars[serial].get():
                is_alive = check_internet_connection(serial)
                status_text = "🟢 LIVE" if is_alive else "🔴 DEAD"

                def update_ui(s=serial, t=status_text):
                    try:
                        if s in device_checkbox_widgets:
                            clean_name = format_emu_name(s)
                            device_checkbox_widgets[s].configure(text=f"📱 {clean_name} [{t}]")
                    except Exception:
                        pass
                app.after(0, update_ui)
                if not is_alive:
                    device_force_proxy_change[serial] = device_force_proxy_change.get(serial, 0) + 1
                else:
                    device_force_proxy_change[serial] = 0

def configure_super_proxy(serial, proxy_string, country_code, pkg_name, log_cb):
    adb_cmd = get_adb_command()
    try:
        log_cb(f"[{serial}] ⚙ Initiating Proxy Setup...", "cyan")
        with DAEMON_LOCK:
            run_cmd([adb_cmd, "-s", serial, "shell", "am", "force-stop", pkg_name], timeout=5)
        time.sleep(2.0)

        if country_code:
            proxy_string = re.sub(r'_zone_[a-zA-Z0-9]+', f'_zone_{country_code.upper()}', proxy_string)

        proxy_string = proxy_string.replace("socks5://", "").replace("http://", "").strip()
        parts = proxy_string.split(":")

        if len(parts) == 4:
            host, port, user, pwd = parts
        elif len(parts) == 2:
            host, port = parts
            user, pwd = "", ""
        else:
            log_cb(f"[{serial}] ❌ Invalid proxy format", "red")
            return False

        d = u2.connect(serial)
        w, h = d.window_size()
        d.app_start(pkg_name)
        time.sleep(4.0)

        if d(descriptionMatches="(?i)stop").exists(timeout=2.0) or d(textMatches="(?i)stop").exists():
            log_cb(f"[{serial}] ℹ️ Proxy was running. Stopping it to apply new IP...", "yellow")
            try:
                if d(descriptionMatches="(?i)stop").exists():
                    d(descriptionMatches="(?i)stop").click()
                else:
                    d(textMatches="(?i)stop").click()
            except Exception:
                pass
            time.sleep(2.0)

        if d(textContains="Default Profile").exists(timeout=5):
            d(textContains="Default Profile").click()
        else:
            d.click(w // 2, int(h * 0.15))
        time.sleep(1.5)

        d.click(w - 60, int(h * 0.08))
        time.sleep(2.0)

        edits = d(className="android.widget.EditText")
        if edits.count >= 3:
            edits[1].click()
            time.sleep(0.5)
            edits[1].clear_text()
            time.sleep(0.2)
            edits[1].set_text(host)
            time.sleep(0.5)

            edits[2].click()
            time.sleep(0.5)
            edits[2].clear_text()
            time.sleep(0.2)
            edits[2].set_text(port)
            time.sleep(0.5)

        d.press("back")
        time.sleep(1.0)

        if user and pwd:
            auth_none = d(textMatches="(?i)none", className="android.widget.TextView")
            if auth_none.exists(timeout=1):
                auth_none.click()
                time.sleep(1.0)
                d(textContains="Username/Password").click()
                time.sleep(1.5)

            d.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.4), 0.1)
            time.sleep(1.5)

            edits_auth = d(className="android.widget.EditText")
            if edits_auth.count >= 2:
                user_box = edits_auth[edits_auth.count - 2]
                pass_box = edits_auth[edits_auth.count - 1]

                user_box.click()
                time.sleep(0.5)
                user_box.clear_text()
                time.sleep(0.2)
                user_box.set_text(user)
                time.sleep(0.5)

                pass_box.click()
                time.sleep(0.5)
                pass_box.clear_text()
                time.sleep(0.2)
                pass_box.set_text(pwd)
                time.sleep(0.5)

        d.press("back")
        time.sleep(1.5)

        d.click(w - 60, int(h * 0.08))
        time.sleep(2.0)

        if d(className="android.widget.EditText").exists():
            d.click(w - 60, int(h * 0.08))
            time.sleep(2.0)

        if d(textMatches="(?i)start").exists(timeout=1):
            d(textMatches="(?i)start").click()
        else:
            d.click(w // 2, int(h * 0.85))

        time.sleep(3.0)

        error_ui = d(descriptionMatches="(?i).*error occured.*|.*invalid.*|.*failed.*")
        if not error_ui.exists:
            error_ui = d(textMatches="(?i).*error occured.*|.*invalid.*|.*failed.*")

        if error_ui.exists(timeout=1.0):
            log_cb(f"[{serial}] ❌ SuperProxy UI Error: Dead or Invalid Auth!", "red")
            return False

        if d(descriptionMatches="(?i)stop").exists(timeout=3.0) or d(textMatches="(?i)stop").exists():
            log_cb(f"[{serial}] ✅ Proxy Connected! (Stop verified) ({host})", "green")
            try:
                if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                    d(textMatches="(?i)(ok|allow|accept)").click()
                    time.sleep(1.0)
            except Exception:
                pass
            return True

        try:
            if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                d(textMatches="(?i)(ok|allow|accept)").click()
                time.sleep(1.0)
        except Exception:
            pass

        log_cb(f"[{serial}] ✅ Proxy Connected! ({host})", "green")
        time.sleep(2.0)
        return True

    except Exception as e:
        log_cb(f"[{serial}] ❌ Proxy Setup Error: {str(e)[:40]}", "red")
        try:
            run_cmd([adb_cmd, "disconnect", serial], timeout=3)
            time.sleep(1)
            run_cmd([adb_cmd, "connect", serial], timeout=3)
        except Exception:
            pass
        return False

def replace_dead_proxy(serial, proxy_pkg, proxy_textbox_get_func, log_cb):
    raw_text = proxy_textbox_get_func().strip()
    if not raw_text and not device_current_proxy.get(serial):
        log_cb(f"[{serial}] ⚠ Normal Mode: Auto-Proxy OFF. Skipping replacement.", "yellow")
        time.sleep(3)
        return False

    while is_running:
        valid_proxy = None
        while is_running:
            with PROXY_LOCK:
                if not GLOBAL_PROXIES:
                    if not device_stopped_status.get(serial, False):
                        log_cb(f"[{serial}] ❌ Proxy list empty! Skipping IP Replace...", "yellow")
                        device_stopped_status[serial] = True
                    time.sleep(5)
                    return False
                candidate = GLOBAL_PROXIES.pop(0)

            if check_proxy_live(candidate):
                valid_proxy = candidate
                break
            else:
                log_cb(f"[{serial}] 💀 Skipped Dead Proxy from list...", "yellow")

        if not valid_proxy:
            return False

        device_current_proxy[serial] = valid_proxy
        device_stopped_status[serial] = False
        log_cb(f"[{serial}] 🔄 Changing to new LIVE Proxy...", "yellow")

        setup_success = configure_super_proxy(serial, valid_proxy, "", proxy_pkg, log_cb)
        if setup_success:
            return True
        else:
            log_cb(f"[{serial}] ♻️ UI Error (Dead IP). Finding another...", "yellow")

    return False

def update_proxy_username_only(serial, proxy_string, pkg_name, log_cb):
    adb_cmd = get_adb_command()
    try:
        log_cb(f"[{serial}] ⏳ Waiting for ISO Update queue...", "white")
        with PROXY_LOCK:
            log_cb(f"[{serial}] ⚙ Fast Update: Changing ISO (Username only)...", "cyan")
            with DAEMON_LOCK:
                run_cmd([adb_cmd, "-s", serial, "shell", "am", "force-stop", pkg_name], timeout=5)
            time.sleep(2.0)

            proxy_string = proxy_string.replace("socks5://", "").replace("http://", "").strip()
            parts = proxy_string.split(":")

            if len(parts) == 4:
                host, port, user, pwd = parts
            else:
                return

            d = u2.connect(serial)
            w, h = d.window_size()
            d.app_start(pkg_name)
            time.sleep(4.0)

            if d(textContains="Default Profile").exists(timeout=5):
                d(textContains="Default Profile").click()
            else:
                d.click(w // 2, int(h * 0.15))
            time.sleep(1.5)

            d.click(w - 60, int(h * 0.08))
            time.sleep(2.0)

            d.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.4), 0.1)
            time.sleep(1.5)

            edits_auth = d(className="android.widget.EditText")
            if edits_auth.count >= 2:
                user_box = edits_auth[edits_auth.count - 2]
                user_box.click()
                time.sleep(0.5)
                user_box.clear_text()
                time.sleep(0.5)
                user_box.set_text(user)
                time.sleep(0.5)

            d.press("back")
            time.sleep(1.5)

            d.click(w - 60, int(h * 0.08))
            time.sleep(2.0)

            if d(className="android.widget.EditText").exists():
                d.click(w - 60, int(h * 0.08))
                time.sleep(2.0)

            if d(textMatches="(?i)start").exists(timeout=1):
                d(textMatches="(?i)start").click()
            else:
                d.click(w // 2, int(h * 0.85))
            time.sleep(3.0)

            error_ui = d(descriptionMatches="(?i).*error occured.*|.*invalid.*|.*failed.*")
            if not error_ui.exists:
                error_ui = d(textMatches="(?i).*error occured.*|.*invalid.*|.*failed.*")

            if error_ui.exists(timeout=1.0):
                log_cb(f"[{serial}] ❌ Fast Setup Failed: Credentials invalid!", "red")
                return False

            try:
                if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                    d(textMatches="(?i)(ok|allow|accept)").click()
                    time.sleep(1.0)
            except Exception:
                pass

            log_cb(f"[{serial}] ✅ Fast Proxy Updated! ISO Changed to {user}", "green")
            time.sleep(2.0)
            return True

    except Exception as e:
        log_cb(f"[{serial}] ❌ Fast Proxy Update Error: {str(e)[:40]}", "red")
        return False

def change_proxy_iso(serial, proxy_pkg, proxy_textbox_get_func, proxy_iso_list_var_get_func, log_cb, username_only=False):
    current_proxy = device_current_proxy.get(serial, "")
    raw_text = proxy_textbox_get_func().strip()

    if not raw_text and not current_proxy:
        log_cb(f"[{serial}] ⚠ Normal Mode: Auto-Proxy OFF. Skipping ISO change.", "yellow")
        return False

    if not current_proxy:
        try:
            proxies = [p.strip() for p in raw_text.split('\n') if p.strip()]
            if proxies:
                current_proxy = proxies[0]
                device_current_proxy[serial] = current_proxy
                log_cb(f"[{serial}] ⚠ Found fallback proxy from list for ISO change.", "cyan")
        except Exception:
            pass

    if not current_proxy:
        log_cb(f"[{serial}] ❌ Cannot change ISO! Proxy not found in memory.", "red")
        return False

    custom_isos = proxy_iso_list_var_get_func().replace(" ", "").split(",")
    if not custom_isos or custom_isos[0] == "":
        custom_isos = ["US", "GB", "CA", "AU", "DE"]

    new_iso = random.choice(custom_isos)
    if "_zone_" in current_proxy:
        new_proxy = re.sub(r'_zone_[a-zA-Z0-9]+', f'_zone_{new_iso}', current_proxy)
    else:
        new_proxy = current_proxy

    device_current_proxy[serial] = new_proxy
    log_cb(f"[{serial}] 🔄 Changing ISO to {new_iso}...", "cyan")

    if username_only:
        update_proxy_username_only(serial, new_proxy, proxy_pkg, log_cb)
    else:
        configure_super_proxy(serial, new_proxy, "", proxy_pkg, log_cb)
    return True

# ==========================================
# 🔐 HARDWARE ID & LICENSE SYSTEM
# ==========================================
def get_hwid():
    hwid_string = ""
    try:
        out = subprocess.check_output(["sysctl", "-n", "kern.uuid"], timeout=5).decode().strip()
        if out and len(out) > 10:
            hwid_string = out
    except Exception:
        pass

    if not hwid_string:
        try:
            cmd = "ioreg -l | grep IOPlatformSerialNumber | awk -F'\"' '{print $4}'"
            out = subprocess.check_output(cmd, shell=True, timeout=5).decode().strip()
            if out and len(out) > 5:
                hwid_string = out
        except Exception:
            pass

    if not hwid_string:
        try:
            hwid_string = str(uuid.getnode())
        except Exception:
            pass

    if not hwid_string or hwid_string == "0":
        uuid_file = os.path.join(APPDATA_DIR, 'sys_machine.dat')
        if os.path.exists(uuid_file):
            with open(uuid_file, 'r') as f:
                hwid_string = f.read().strip()
        else:
            import uuid as uuid_mod
            hwid_string = str(uuid_mod.uuid4())
            try:
                os.makedirs(APPDATA_DIR, exist_ok=True)
                with open(uuid_file, 'w') as f:
                    f.write(hwid_string)
            except Exception:
                pass

    try:
        hwid_string += f"_{socket.gethostname()}"
    except Exception:
        pass

    return hashlib.sha256(hwid_string.encode()).hexdigest()[:20].upper()

def check_cloud_status():
    try:
        hwid = get_hwid()
        response = requests.post(f"{API_BASE_URL}/check", json={"hwid": hwid}, timeout=10)
        return response.json()
    except Exception:
        return {"valid": False, "status": "ERROR", "msg": "Server Offline! Retrying..."}

def request_cloud_access(name):
    try:
        hwid = get_hwid()
        requests.post(f"{API_BASE_URL}/request", json={"hwid": hwid, "name": name}, timeout=10)
    except Exception:
        pass

def show_license_window():
    ctk.set_appearance_mode("dark")
    lic_app = ctk.CTk()
    lic_app.geometry("500x450")
    lic_app.title(f"{APP_TITLE} - Authentication")
    lic_app.protocol("WM_DELETE_WINDOW", sys.exit)

    hwid = get_hwid()

    title_lbl = ctk.CTkLabel(lic_app, text="☁️ CONNECTING TO SERVER...", font=("Consolas", 20, "bold"), text_color="#F1C40F")
    title_lbl.pack(pady=20)

    ctk.CTkLabel(lic_app, text="Your Mac Hardware ID (HWID):", font=("Consolas", 12)).pack()
    hwid_entry = ctk.CTkEntry(lic_app, width=300, justify="center", font=("Consolas", 12, "bold"))
    hwid_entry.insert(0, hwid)
    hwid_entry.configure(state="readonly")
    hwid_entry.pack(pady=5)

    dynamic_frame = ctk.CTkFrame(lic_app, fg_color="transparent")
    dynamic_frame.pack(pady=10, fill="both", expand=True)

    msg_lbl = ctk.CTkLabel(lic_app, text="", font=("Consolas", 13, "bold"))
    msg_lbl.pack(pady=10)

    def render_not_found():
        for widget in dynamic_frame.winfo_children():
            widget.destroy()
        title_lbl.configure(text="🔒 SOFTWARE NOT REGISTERED", text_color="#E74C3C")
        ctk.CTkLabel(dynamic_frame, text="Enter Your Telegram Name:", font=("Consolas", 12)).pack(pady=5)
        name_entry = ctk.CTkEntry(dynamic_frame, width=250, placeholder_text="e.g. Rahul_77")
        name_entry.pack(pady=5)

        def send_request():
            name = name_entry.get().strip()
            if not name:
                return
            msg_lbl.configure(text="⏳ Sending Request...", text_color="#F1C40F")
            lic_app.update()
            request_cloud_access(name)
            check_logic()

        ctk.CTkButton(dynamic_frame, text="📩 REQUEST ACCESS", command=send_request, fg_color="#3498DB").pack(pady=15)

    def render_pending():
        for widget in dynamic_frame.winfo_children():
            widget.destroy()
        title_lbl.configure(text="⏳ WAITING FOR APPROVAL", text_color="#F39C12")
        ctk.CTkLabel(dynamic_frame, text="Your request is pending in Admin Database.", font=("Consolas", 12)).pack(pady=5)

        def contact_admin():
            encoded_msg = urllib.parse.quote(f"Hello {DISTRIBUTOR_NAME},\nI have submitted an access request.\nHWID: {hwid}")
            webbrowser.open(f"{TELEGRAM_LINK}?text={encoded_msg}")

        ctk.CTkButton(dynamic_frame, text="💬 CONTACT DISTRIBUTOR", command=contact_admin, fg_color="#2ECC71").pack(pady=10)
        ctk.CTkButton(dynamic_frame, text="🔄 RE-CHECK STATUS", command=check_logic, fg_color="#3498DB").pack(pady=5)

    def check_logic():
        msg_lbl.configure(text="⏳ Verifying Key...", text_color="#F1C40F")
        lic_app.update()
        res = check_cloud_status()
        if res.get("valid"):
            global LICENSED_USER, EXPIRY_DATE
            LICENSED_USER = res.get("user", "Licensed User")
            EXPIRY_DATE = res.get("expiry", "Lifetime")
            lic_app.destroy()
        else:
            status = res.get("status")
            if status == "NOT_FOUND":
                render_not_found()
            elif status == "PENDING":
                render_pending()
            else:
                title_lbl.configure(text="❌ ACCESS DENIED", text_color="#E74C3C")
                msg_lbl.configure(text=res.get("msg", "Error connecting"), text_color="#E74C3C")

    lic_app.after(1000, check_logic)
    lic_app.mainloop()

# ==========================================
# 🌾 HARVESTER & ACCOUNT CHECKER LOGIC
# ==========================================
def fetch_number_from_panel():
    if CURRENT_PANEL == "ZENEX NETWORK":
        url = "https://api.zenexnetwork.com/v1/getnum"
        headers = {"mapikey": CURRENT_API_KEY, "Content-Type": "application/json"}
        payload = {"range": CURRENT_RANGE, "is_national": False, "remove_plus": False}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200 and res.json().get("meta", {}).get("status") == "success":
                return res.json()["data"]["number"]
        except Exception:
            pass
    return None

def build_browser_fingerprint():
    mac_version = random.choice(['10_15_7', '11_6_8', '12_6_9', '13_5_2', '13_6', '14_0', '14_1_1', '14_2'])
    chrome_major = random.randint(115, 125)
    chrome_ver = f"{chrome_major}.0.{random.randint(5000, 6000)}.{random.randint(100, 200)}"

    browser_list = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Brave']
    browser = random.choice(browser_list)

    if browser == 'Safari':
        base_ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    elif browser == 'Firefox':
        firefox_ver = random.randint(115, 123)
        base_ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_version}; rv:{firefox_ver}.0) Gecko/20100101 Firefox/{firefox_ver}.0"
    else:
        base_ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"

    sec_headers = {}
    if browser in ['Chrome', 'Brave', 'Edge']:
        brand_name = "Google Chrome" if browser == 'Chrome' else browser
        sec_headers = {
            'sec-ch-ua': f'"{brand_name}";v="{chrome_major}", "Chromium";v="{chrome_major}", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

    screen_res = random.choice(['1280x800', '1440x900', '1680x1050', '1728x1117', '1920x1080', '2560x1600', '3024x1964', '3456x2234'])

    base_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'sec-ch-ua-full-version-list': f'"Chromium";v="{chrome_ver}", "Not A(Brand";v="24.0.0.0"',
        'sec-ch-ua-platform-version': f'"{mac_version.replace("_", ".")}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': base_ua,
    }
    base_headers.update(sec_headers)
    return base_headers, screen_res, "MacBook", f"macOS {mac_version.replace('_', '.')}"

def check_fb_account(number):
    session = requests.Session()
    server = FILTER_SERVER_DOMAIN
    base_headers, screen_res, model, andro_ver = build_browser_fingerprint()
    session.cookies.update({'m_pixel_ratio': '2', 'wd': screen_res})

    try:
        first_headers = base_headers.copy()
        first_headers.update({'sec-fetch-site': 'none'})

        get_url = f"https://{server}/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0&__mmr=1&_rdr"
        r_get = session.get(get_url, headers=first_headers, timeout=15)

        try:
            lsd = re.search(r'name="lsd" value="(.*?)"', r_get.text).group(1)
        except Exception:
            lsd = ''
        try:
            jazoest = re.search(r'name="jazoest" value="(.*?)"', r_get.text).group(1)
        except Exception:
            jazoest = ''

        post_headers = base_headers.copy()
        post_headers.update({
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': f'https://{server}',
            'referer': f'https://{server}/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0',
            'sec-fetch-site': 'same-origin',
        })

        data = {'lsd': lsd, 'jazoest': jazoest, 'email': number, 'did_submit': 'Search'}
        post_url = (
            f"https://{server}/login/identify/"
            f"?ctx=recover&c=%2Flogin%2F&search_attempts=1"
            f"&ars=facebook_login&alternate_search=0"
            f"&show_friend_search_filtered_list=0&birth_month_search=0&city_search=0"
        )

        r_post = session.post(post_url, data=data, headers=post_headers, timeout=15, allow_redirects=True)
        resp_text = r_post.text

        if 'id="login_identify_search_error_msg"' in resp_text:
            return False, "Not Found"
        if 'action="/login/identify/?ctx=recover' in resp_text:
            return True, "Valid (Multiple)"

        return True, "Valid (Found)"
    except Exception:
        return False, "Error/Timeout"

def update_stat(key, value, app_instance, update_ui_func):
    with stats_lock:
        stats[key] += value
    app_instance.after(0, update_ui_func)

def number_harvester_thread(use_filter, platform, current_token, data_source, gui_callbacks):
    app_instance = gui_callbacks["app"]
    log_to_filter = gui_callbacks["log_to_filter"]
    update_stats_ui = gui_callbacks["update_stats_ui"]
    get_controls = gui_callbacks["get_controls"]

    log_to_filter(f"✅ Harvester Started ({platform} | Source: {data_source})", "cyan")

    while is_running and GLOBAL_RUN_TOKEN == current_token:
        c_filter, c_platform, c_data_source = get_controls()

        if valid_numbers_queue.qsize() < 5:
            num = None
            if c_data_source == "Bulk TXT File":
                if not txt_numbers_queue.empty():
                    num = txt_numbers_queue.get()
                    gui_callbacks["update_txt_count"](txt_numbers_queue.qsize())
                else:
                    log_to_filter("⚠ TXT File is empty! Please load more numbers.", "yellow")
                    time.sleep(3)
                    continue
            else:
                num = fetch_number_from_panel()

            if num:
                num = num.strip()
                if c_platform == "Instagram":
                    valid_numbers_queue.put(num)
                    update_stat("valid", 1, app_instance, update_stats_ui)
                    log_to_filter(f"✅ {num} | Direct to IG (Filter Skipped)", "cyan")
                else:
                    if c_filter:
                        update_stat("checked", 1, app_instance, update_stats_ui)
                        is_valid, reason = check_fb_account(num)
                        if is_valid:
                            valid_numbers_queue.put(num)
                            update_stat("valid", 1, app_instance, update_stats_ui)
                            log_to_filter(f"✅ {num} | {reason}", "green")
                        else:
                            update_stat("invalid", 1, app_instance, update_stats_ui)
                            log_to_filter(f"❌ {num} | {reason}", "red")
                    else:
                        valid_numbers_queue.put(num)
                        update_stat("valid", 1, app_instance, update_stats_ui)
                        log_to_filter(f"✅ {num} | Filter Disabled", "green")
            time.sleep(1)
        else:
            time.sleep(2)

# ==========================================
# 🤖 BOT AUTOMATION LOGIC (FB / IG)
# ==========================================
def get_action_delay(action_delay_val, speed_mode):
    try:
        base_delay = float(action_delay_val)
        if speed_mode == "Human":
            return base_delay + random.uniform(0.2, 0.6)
        return base_delay
    except Exception:
        return 1.0

def human_click(d, x, y, offset=7):
    try:
        rand_x = x + random.randint(-offset, offset)
        rand_y = y + random.randint(-offset, offset)
        d.click(rand_x, rand_y)
    except Exception:
        d.click(x, y)

def smart_delay(speed_mode, action_delay_val):
    time.sleep(get_action_delay(action_delay_val, speed_mode))

def handle_permissions(d):
    for _ in range(2):
        try:
            clicked = False
            if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                d(resourceId="com.google.android.gms:id/cancel").click()
                clicked = True
            elif d(textMatches="(?i)^(allow|allow all)$").exists(timeout=0.1):
                d(textMatches="(?i)^(allow|allow all)$").click()
                clicked = True
            elif d(className="android.widget.Button", textMatches="(?i).*allow.*").exists(timeout=0.1):
                d(className="android.widget.Button", textMatches="(?i).*allow.*").click()
                clicked = True
            elif d(resourceId="com.android.permissioncontroller:id/permission_allow_button").exists(timeout=0.1):
                d(resourceId="com.android.permissioncontroller:id/permission_allow_button").click()
                clicked = True
            if clicked:
                time.sleep(0.3)
        except Exception:
            pass

def grant_permissions(serial, pkg_name):
    adb_cmd = get_adb_command()
    perms = [
        "android.permission.READ_CONTACTS",
        "android.permission.WRITE_CONTACTS",
        "android.permission.READ_PHONE_STATE",
        "android.permission.CALL_PHONE",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION"
    ]
    with DAEMON_LOCK:
        for p in perms:
            try:
                subprocess.run(
                    [adb_cmd, "-s", serial, "shell", "pm", "grant", pkg_name, p],
                    capture_output=True,
                    timeout=3,
                    **SUBPROCESS_EXTRA_KWARGS
                )
            except Exception:
                pass

def type_number(d, input_box, number, speed_mode, custom_speed_str, force_paste=False):
    if input_box:
        try:
            input_box.click()
            input_box.clear_text()
        except Exception:
            pass
        time.sleep(0.1)
    else:
        for _ in range(5):
            d.press("del")
        time.sleep(0.1)

    if speed_mode == "Fastest" or force_paste:
        if input_box:
            try:
                input_box.set_text(number)
            except Exception:
                d.send_keys(number, clear=True)
        else:
            d.send_keys(number, clear=True)
        return

    try:
        speed = float(custom_speed_str)
    except Exception:
        speed = 0.08

    for char in number:
        d.send_keys(char)
        time.sleep(speed)

def log_success(number):
    try:
        from datetime import datetime
        with open(SUCCESS_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {number}\n")
    except Exception:
        pass

def init_uiautomator2_for_device(serial, log_cb):
    log_cb(f"💬 [{serial}] 🔧 Checking ATX (uiautomator2) setup...", "cyan")
    adb_cmd = get_adb_command()

    with DAEMON_LOCK:
        try:
            check_pkg = subprocess.run(
                [adb_cmd, "-s", serial, "shell", "pm", "path", "com.github.uiautomator"],
                capture_output=True,
                text=True,
                timeout=5,
                **SUBPROCESS_EXTRA_KWARGS
            )
            if "package:" not in check_pkg.stdout:
                log_cb(f"⚙️ [{serial}] ATX is missing! Auto-Installing...", "yellow")
                if os.path.exists(LOCAL_APK_PATH):
                    subprocess.run(
                        [adb_cmd, "-s", serial, "install", "-r", "-g", LOCAL_APK_PATH],
                        capture_output=True,
                        timeout=20,
                        **SUBPROCESS_EXTRA_KWARGS
                    )
                    if os.path.exists(LOCAL_TEST_APK_PATH):
                        subprocess.run(
                            [adb_cmd, "-s", serial, "install", "-r", "-g", LOCAL_TEST_APK_PATH],
                            capture_output=True,
                            timeout=20,
                            **SUBPROCESS_EXTRA_KWARGS
                        )
                    log_cb(f"✔️ [{serial}] ATX Installed successfully.", "green")
                    time.sleep(2)
                else:
                    log_cb(f"❌ [{serial}] LOCAL APK NOT FOUND! Please put app-uiautomator.apk in uiautomator2 folder.", "red")
        except Exception:
            pass

    try:
        d = u2.connect(serial)
        if d.info:
            log_cb(f"✔️ [{serial}] ATX Ready & Connected.", "green")
            d.implicitly_wait(1.0)
            return d
    except Exception as e:
        err_msg = str(e)
        log_cb(f"❌ [{serial}] Initialization Error: {err_msg[:60]}", "red")
        try:
            subprocess.run([adb_cmd, "disconnect", serial], capture_output=True, timeout=3, **SUBPROCESS_EXTRA_KWARGS)
            time.sleep(1)
            subprocess.run([adb_cmd, "connect", serial], capture_output=True, timeout=3, **SUBPROCESS_EXTRA_KWARGS)
        except Exception:
            pass

    return None

def bot_logic_ig(d, device_serial, current_token, gui_data):
    log_to_otp = gui_data["log_to_otp"]
    log_to_success = gui_data["log_to_success"]
    get_config_opts = gui_data["get_config_opts"]
    app = gui_data["app"]
    update_stats_ui = gui_data["update_stats_ui"]

    try:
        d.implicitly_wait(1.0)
        d.settings['operation_delay'] = (0.05, 0.05)
        device_handles.append(d)
    except Exception:
        return

    run_count = 0
    force_next_clear = False

    XP_CREATE_ACC = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.View[1]'
    CLASS_NUM_BOX = 'android.widget.MultiAutoCompleteTextView'
    XP_NEXT_BTN_SMART = '//*[@resource-id="com.instagram.lite:id/main_layout"]//android.view.ViewGroup[3]/android.view.View[6]'
    XP_OTP_BOX_1 = '//*[@text="_ _ _ _ _ _"]'
    XP_OTP_BOX_2 = '//*[@text="_ _ _  _ _ _"]'
    XP_POPUP_OK = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[4]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.View[1]'
    XP_POPUP_ERROR_TEXT = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[4]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.View[2]'
    XP_POPUP_ALT = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[3]/android.view.ViewGroup[3]/android.view.View[1]'
    XP_LAW_POPUP_CLOSE = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[4]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.View[1]'
    XP_DIDNT_GET_CODE = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[3]/android.view.View[6]'
    XP_RESEND_SMS = '//*[@resource-id="com.instagram.lite:id/main_layout"]/android.widget.FrameLayout[1]/android.view.ViewGroup[4]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.View[1]'

    while is_running and GLOBAL_RUN_TOKEN == current_token:
        opts = get_config_opts()
        pkg_name = opts["pkg_name"]
        speed_mode = opts["speed_mode"]
        custom_speed = opts["custom_speed"]
        clear_interval = opts["clear_interval"]
        ig_resend_limit = opts["ig_resend_limit"]

        try:
            if device_force_proxy_change.get(device_serial, 0) >= 15:
                log_to_otp(f"[{device_serial}] ❌ Background Scanner Detected Dead IP! Auto Replacing...", "red")
                if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                    continue
                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                device_force_proxy_change[device_serial] = 0
                device_dead_proxy_errors[device_serial] = 0
                continue

            try:
                app_installed = d.app_info(pkg_name) is not None
            except Exception:
                app_installed = False

            if not app_installed:
                log_to_otp(f"[{device_serial}] ❌ App '{pkg_name}' NOT installed! Skipping IP check...", "red")
                time.sleep(5)
                continue

            try:
                if force_next_clear or clear_interval == 0 or (clear_interval > 0 and run_count % clear_interval == 0):
                    log_to_otp(f"[{device_serial}] 🧹 Force Stop & App Clear", "cyan")
                    d.app_stop(pkg_name)
                    time.sleep(0.5)
                    d.app_clear(pkg_name)
                    grant_permissions(device_serial, pkg_name)
                    force_next_clear = False
                else:
                    log_to_otp(f"[{device_serial}] 🔄 Force Stop (Soft Reset)", "cyan")
                    d.app_stop(pkg_name)

                d.app_start(pkg_name)
            except Exception:
                pass

            d.app_wait(pkg_name, front=True, timeout=10.0)
            handle_permissions(d)

            log_to_otp(f"[{device_serial}] ⏳ Waiting for 'Create Account/Get started' Button...", "white")

            create_btn_found = False
            for _ in range(25):
                if not is_running or GLOBAL_RUN_TOKEN != current_token:
                    break
                try:
                    if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                        d(resourceId="com.google.android.gms:id/cancel").click()
                except Exception:
                    pass

                if pkg_name == "com.instagram.android":
                    if d.xpath('//*[@text="Create new account" or @content-desc="Create new account"]').exists:
                        try:
                            d.xpath('//*[@text="Create new account" or @content-desc="Create new account"]').click()
                        except Exception:
                            pass
                        create_btn_found = True
                        break
                    elif d.xpath('//*[@text="Get started" or @content-desc="Get started"]').exists:
                        try:
                            d.xpath('//*[@text="Get started" or @content-desc="Get started"]').click()
                        except Exception:
                            pass
                        create_btn_found = True
                        break
                    elif d(textMatches="(?i).*(create new account|create account|get started).*").exists(timeout=0.1):
                        d(textMatches="(?i).*(create new account|create account|get started).*").click()
                        create_btn_found = True
                        break
                else:
                    if d.xpath(XP_CREATE_ACC).exists:
                        try:
                            bounds = d.xpath(XP_CREATE_ACC).info['bounds']
                            human_click(d, (bounds['left'] + bounds['right']) // 2, (bounds['top'] + bounds['bottom']) // 2)
                        except Exception:
                            d.xpath(XP_CREATE_ACC).click()
                        create_btn_found = True
                        break
                    elif d(textMatches="(?i).*(create new account|create account).*").exists(timeout=0.1):
                        d(textMatches="(?i).*(create new account|create account).*").click()
                        create_btn_found = True
                        break
                time.sleep(1.0)

            if create_btn_found:
                device_dead_proxy_errors[device_serial] = 0
                log_to_otp(f"[{device_serial}] ✅ Clicked Create Account/Get started", "green")
            else:
                log_to_otp(f"[{device_serial}] ⏳ Page completely stuck! App didn't load in time.", "yellow")
                force_next_clear = True
                device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1

                iso_limit_val = opts["iso_limit"]
                if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                    log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                    if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                        continue
                    d = init_uiautomator2_for_device(device_serial, log_to_otp)
                    device_dead_proxy_errors[device_serial] = 0
                continue

            time.sleep(1.5)
            try:
                law_popup = d.xpath(XP_LAW_POPUP_CLOSE)
                if law_popup.exists or d(textMatches="(?i).*law in your area.*").exists(timeout=0.5):
                    log_to_otp(f"[{device_serial}] ❌ IG Law Restriction Popup Detected! Restarting...", "red")
                    if law_popup.exists:
                        law_popup.click()
                    force_next_clear = True
                    continue
            except Exception:
                pass

            while is_running and GLOBAL_RUN_TOKEN == current_token:
                if valid_numbers_queue.empty():
                    time.sleep(1)
                    continue

                target = valid_numbers_queue.get()
                number_submitted = False

                log_to_otp(f"\n{'='*50}", "cyan")
                log_to_otp(f"[{device_serial}] 🎯 IG TARGET: {target}", "yellow")

                try:
                    log_to_otp(f"[{device_serial}] ⏳ Waiting for Number Box...", "white")

                    if pkg_name == "com.instagram.android":
                        num_box = d(description="Mobile Number")
                        if not num_box.exists:
                            num_box = d(className="android.widget.EditText")

                        if num_box.wait(timeout=25.0):
                            device_dead_proxy_errors[device_serial] = 0
                            try:
                                if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                                    d(resourceId="com.google.android.gms:id/cancel").click()
                            except Exception:
                                pass
                            num_box.click()
                            time.sleep(0.3)
                            type_number(d, num_box, target, speed_mode, custom_speed, opts["force_paste"])
                            log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                            valid_numbers_queue.put(target)
                            log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                            force_next_clear = True

                            device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                            if device_dead_proxy_errors[device_serial] >= opts["iso_limit"]:
                                log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                    break
                                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                                device_dead_proxy_errors[device_serial] = 0
                            break
                    else:
                        num_box = d(className=CLASS_NUM_BOX)
                        if num_box.wait(timeout=15.0):
                            device_dead_proxy_errors[device_serial] = 0
                            try:
                                if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                                    d(resourceId="com.google.android.gms:id/cancel").click()
                            except Exception:
                                pass
                            num_box.click()
                            time.sleep(0.3)
                            type_number(d, num_box, target, speed_mode, custom_speed, opts["force_paste"])
                            log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                            valid_numbers_queue.put(target)
                            log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                            force_next_clear = True

                            device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                            if device_dead_proxy_errors[device_serial] >= opts["iso_limit"]:
                                log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                    break
                                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                                device_dead_proxy_errors[device_serial] = 0
                            break

                    smart_delay(speed_mode, opts["action_delay"])

                    if pkg_name == "com.instagram.android":
                        if d.xpath('//*[@text="Next" or @content-desc="Next"]').exists:
                            d.xpath('//*[@text="Next" or @content-desc="Next"]').click()
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Smart XPath)", "green")
                        elif d(text="Next").exists(timeout=0.5):
                            d(text="Next").click()
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Text)", "green")
                        else:
                            d.press("enter")
                            log_to_otp(f"[{device_serial}] ⚠ Clicked Next (By Enter)", "yellow")
                    else:
                        if d(textMatches="(?i).*(next|continue).*").exists(timeout=0.5):
                            d(textMatches="(?i).*(next|continue).*").click()
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Text)", "green")
                        elif d.xpath(XP_NEXT_BTN_SMART).exists:
                            d.xpath(XP_NEXT_BTN_SMART).click()
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Smart XPath)", "green")
                        else:
                            d.press("enter")
                            w, h = d.window_size()
                            d.click(int(w * 0.498), int(h * 0.369))
                            log_to_otp(f"[{device_serial}] ⚠ Clicked Next (By Enter/XY)", "yellow")

                    if is_keyboard_shown(device_serial):
                        d.press("back")
                        time.sleep(0.5)

                    time.sleep(2.0)
                    number_submitted = True
                    log_to_otp(f"[{device_serial}] ⏳ Scanning Page for Success/Popups...", "white")

                    otp_page_found = False
                    rate_limit_delayed = False

                    for step in range(40):
                        if not is_running or GLOBAL_RUN_TOKEN != current_token:
                            break
                        try:
                            if pkg_name == "com.instagram.android":
                                try:
                                    if d(text="Continue").exists(timeout=0.1) or d.xpath('//*[@text="Continue" or @content-desc="Continue"]').exists:
                                        try:
                                            d(text="Continue").click()
                                        except Exception:
                                            d.xpath('//*[@text="Continue" or @content-desc="Continue"]').click()
                                        log_to_otp(f"[{device_serial}] 🔄 Clicked 'Continue' (Device nearby popup)", "cyan")
                                        time.sleep(1.0)
                                except Exception:
                                    pass

                                if d(textMatches="(?i).*Enter the confirmation code.*|.*I didn’t get the code.*").exists(timeout=0.1):
                                    log_to_otp(f"[{device_serial}] ⚡ Detected OTP Page (Official)", "green")
                                    otp_page_found = True
                                    break
                                if d(textMatches="(?i).*country code.*|.*invalid.*|.*try again later.*|.*error.*|.*wait a few minutes.*").exists(timeout=0.1):
                                    log_to_otp(f"[{device_serial}] ❌ Error/Limit Detected! (Official)", "red")
                                    rate_limit_delayed = True
                                    break
                            else:
                                if d.xpath(XP_OTP_BOX_1).exists or d.xpath(XP_OTP_BOX_2).exists or d(className=CLASS_NUM_BOX, textContains="_").exists(timeout=0.1):
                                    log_to_otp(f"[{device_serial}] ⚡ Detected OTP Box (_ _ _ _ _ _)", "green")
                                    otp_page_found = True
                                    break
                                if d.xpath(XP_POPUP_OK).exists or d.xpath(XP_POPUP_ERROR_TEXT).exists or d.xpath(XP_POPUP_ALT).exists:
                                    log_to_otp(f"[{device_serial}] ⚡ Detected Blank 'Try Again' Popup!", "red")
                                    rate_limit_delayed = True
                                    break
                                if d(textContains="country code").exists(timeout=0.1) or d.xpath('//*[contains(@text, "country code")]').exists:
                                    log_to_otp(f"[{device_serial}] ❌ Invalid Number Format Detected!", "red")
                                    rate_limit_delayed = True
                                    break
                        except Exception:
                            pass
                        time.sleep(1.0)

                    if rate_limit_delayed:
                        log_to_otp(f"[{device_serial}] ❌ IG Error / Limit Detected! Clearing App...", "red")
                        try:
                            if pkg_name != "com.instagram.android":
                                if d.xpath(XP_POPUP_OK).exists:
                                    d.xpath(XP_POPUP_OK).click()
                                else:
                                    w, h = d.window_size()
                                    d.click(w // 2, int(h * 0.6))
                        except Exception:
                            pass
                        update_stat("otp_failed", 1, app, update_stats_ui)
                        force_next_clear = True

                        device_popup_errors[device_serial] = device_popup_errors.get(device_serial, 0) + 1
                        if device_popup_errors[device_serial] >= opts["iso_limit"]:
                            change_proxy_iso(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], opts["get_iso_list"], log_to_otp, username_only=True)
                            device_popup_errors[device_serial] = 0
                        break

                    elif otp_page_found:
                        device_popup_errors[device_serial] = 0
                        log_to_otp(f"[{device_serial}] ✅✅ SUCCESS IG OTP SENT: {target} ✅✅", "green")
                        log_success(target)
                        log_to_success(target)
                        update_stat("otp_sent", 1, app, update_stats_ui)

                        if ig_resend_limit <= 1:
                            log_to_otp(f"[{device_serial}] ⏳ Limit is 0/1. Waiting 4s before fast clear...", "cyan")
                            time.sleep(4.0)
                            force_next_clear = True
                            break

                        for i in range(ig_resend_limit - 1):
                            if not is_running or GLOBAL_RUN_TOKEN != current_token:
                                break
                            log_to_otp(f"[{device_serial}] ⏳ Wait for Resend ({i+1})...", "white")

                            wait_loop = 4.0
                            while wait_loop > 0 and is_running and GLOBAL_RUN_TOKEN == current_token:
                                time.sleep(0.5)
                                wait_loop -= 0.5

                            if not is_running or GLOBAL_RUN_TOKEN != current_token:
                                break

                            if pkg_name == "com.instagram.android":
                                didnt_get = d(textMatches="(?i).*I didn’t get the code.*")
                                if didnt_get.exists(timeout=1.0):
                                    didnt_get.click()
                                    log_to_otp(f"[{device_serial}] 🔄 Clicked 'I didn’t get the code'", "white")
                                    time.sleep(2.0)
                                    resend_btn = d(textMatches="(?i).*Resend confirmation code.*")
                                    if resend_btn.exists(timeout=1.0):
                                        resend_btn.click()
                                        log_to_otp(f"[{device_serial}] ✅ Clicked 'Resend confirmation code'", "cyan")
                                    else:
                                        log_to_otp(f"[{device_serial}] ❌ Couldn't find 'Resend confirmation code'", "red")
                                        break
                                else:
                                    log_to_otp(f"[{device_serial}] ❌ Couldn't find 'I didn’t get the code' button", "red")
                                    break
                            else:
                                didnt_get = d.xpath(XP_DIDNT_GET_CODE)
                                if didnt_get.exists:
                                    didnt_get.click()
                                    log_to_otp(f"[{device_serial}] 🔄 Clicked 'Didn't get code'", "white")
                                else:
                                    log_to_otp(f"[{device_serial}] ❌ Couldn't find 'Didn't get code' button", "red")
                                    break

                                time.sleep(2.0)
                                resend_sms = d.xpath(XP_RESEND_SMS)
                                if resend_sms.exists:
                                    resend_sms.click()
                                    log_to_otp(f"[{device_serial}] ✅ Clicked 'Resend SMS'", "cyan")
                                else:
                                    log_to_otp(f"[{device_serial}] ❌ Couldn't find 'Resend SMS' option", "red")
                                    break

                        log_to_otp(f"[{device_serial}] ✅ IG Flow Complete. Waiting 4s before next...", "green")
                        time.sleep(4.0)
                        force_next_clear = True
                        break
                    else:
                        if not check_internet_connection(device_serial):
                            if replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Network Too Slow / Timeout! App Clearing...", "red")

                        update_stat("otp_failed", 1, app, update_stats_ui)
                        force_next_clear = True
                        break

                except Exception as inner_e:
                    if not number_submitted:
                        valid_numbers_queue.put(target)
                        log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                    raise inner_e

            run_count += 1

        except Exception as e:
            error_msg = str(e)[:40]
            if "-32001" in error_msg or "-32002" in error_msg:
                log_to_otp(f"[{device_serial}] 🔄 CPU Lag Detected. Soft Restarting...", "yellow")
            else:
                log_to_otp(f"[{device_serial}] ❌ Error: {error_msg}", "red")
                if not check_internet_connection(device_serial):
                    if replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                        d = init_uiautomator2_for_device(device_serial, log_to_otp)
            time.sleep(2)

    if GLOBAL_RUN_TOKEN != current_token:
        log_to_otp(f"[{device_serial}] 💀 Old Thread Killed Successfully", "yellow")
    else:
        log_to_otp(f"[{device_serial}] ⚠ IG Stopped", "yellow")

def bot_logic_fb(d, device_serial, current_token, gui_data):
    log_to_otp = gui_data["log_to_otp"]
    log_to_success = gui_data["log_to_success"]
    get_config_opts = gui_data["get_config_opts"]
    app = gui_data["app"]
    update_stats_ui = gui_data["update_stats_ui"]

    try:
        d.implicitly_wait(1.0)
        d.settings['operation_delay'] = (0.2, 0.2)
        device_handles.append(d)
    except Exception:
        return

    run_count = 0
    force_next_clear = False

    while is_running and GLOBAL_RUN_TOKEN == current_token:
        opts = get_config_opts()
        pkg_name = opts["pkg_name"]
        speed_mode = opts["speed_mode"]
        custom_speed = opts["custom_speed"]
        skip_timer = opts["skip_timer"]
        skip_captcha = opts["skip_captcha"]
        double_otp = opts["double_otp"]
        clear_interval = opts["clear_interval"]
        page_timeout = opts["page_timeout"]

        try:
            if device_force_proxy_change.get(device_serial, 0) >= 15:
                log_to_otp(f"[{device_serial}] ❌ Background Scanner Detected Dead IP! Auto Replacing...", "red")
                if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                    continue
                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                device_force_proxy_change[device_serial] = 0
                device_dead_proxy_errors[device_serial] = 0
                continue

            try:
                app_installed = d.app_info(pkg_name) is not None
            except Exception:
                app_installed = False

            if not app_installed:
                log_to_otp(f"[{device_serial}] ❌ App '{pkg_name}' NOT installed! Skipping IP check...", "red")
                time.sleep(5)
                continue

            try:
                display_run = run_count % clear_interval if clear_interval > 0 else 0

                if force_next_clear or clear_interval == 0 or (clear_interval > 0 and run_count % clear_interval == 0):
                    log_to_otp(f"[{device_serial}] 🧹 App Clear (Run: {display_run}/{clear_interval})", "cyan")
                    d.app_stop(pkg_name)
                    time.sleep(0.5)
                    d.app_clear(pkg_name)
                    grant_permissions(device_serial, pkg_name)
                    force_next_clear = False
                else:
                    log_to_otp(f"[{device_serial}] 🔄 Soft Reset (Run: {display_run}/{clear_interval})", "cyan")
                    d.app_stop(pkg_name)

                d.app_start(pkg_name)
                time.sleep(2.0)
            except Exception as e:
                if "-32001" in str(e) or "-32002" in str(e):
                    time.sleep(2)
                    continue

            d.app_wait(pkg_name, front=True, timeout=5.0)
            handle_permissions(d)

            try:
                if d(textMatches="(?i).*page isn't available right now.*|.*technical error.*|.*try reloading this page.*|.*refresh.*").exists(timeout=2.0):
                    log_to_otp(f"[{device_serial}] ❌ 'Page isn't available' (IP Block) Detected! Clearing App...", "red")
                    force_next_clear = True
                    device_popup_errors[device_serial] = device_popup_errors.get(device_serial, 0) + 1

                    if device_popup_errors[device_serial] >= opts["iso_limit"]:
                        log_to_otp(f"[{device_serial}] ❌ IP Blocked {device_popup_errors[device_serial]} times! Replacing proxy...", "red")
                        if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                            continue
                        d = init_uiautomator2_for_device(device_serial, log_to_otp)
                        device_popup_errors[device_serial] = 0
                    continue
            except Exception:
                pass

            btn_forgot = d(textMatches="(?i).*forgot.*")
            if btn_forgot.wait(timeout=25.0):
                device_dead_proxy_errors[device_serial] = 0
                try:
                    try:
                        if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.5):
                            d(resourceId="com.google.android.gms:id/cancel").click()
                    except Exception:
                        pass
                    btn_forgot.click()
                    log_to_otp(f"[{device_serial}] 🔄 Clicked Forgot, checking permissions...", "cyan")
                    time.sleep(1.0)
                    handle_permissions(d)
                except Exception as e:
                    if "-32002" in str(e):
                        continue
            else:
                log_to_otp(f"[{device_serial}] ⏳ Page completely stuck! App didn't load in time.", "yellow")
                force_next_clear = True
                device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1

                if device_dead_proxy_errors[device_serial] >= opts["iso_limit"]:
                    log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                    if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                        continue
                    d = init_uiautomator2_for_device(device_serial, log_to_otp)
                    device_dead_proxy_errors[device_serial] = 0
                continue

            while is_running and GLOBAL_RUN_TOKEN == current_token:
                if valid_numbers_queue.empty():
                    time.sleep(1)
                    continue

                target = valid_numbers_queue.get()
                number_submitted = False

                log_to_otp(f"\n{'='*50}", "cyan")
                log_to_otp(f"[{device_serial}] 🎯 FB TARGET: {target}", "yellow")

                try:
                    last_2 = target.strip()[-2:]

                    if d(textMatches="(?i).*enter code.*|.*we sent a code.*|.*confirm your account.*").exists(timeout=1.0):
                        log_to_otp(f"[{device_serial}] ❌ Stuck on OTP Page! App Reset Required.", "red")
                        valid_numbers_queue.put(target)
                        log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                        force_next_clear = True
                        break

                    if d(textMatches="(?i)allow").exists(timeout=0.1):
                        d(textMatches="(?i)allow").click()

                    input_box = d(className="android.widget.EditText")
                    if input_box.wait(timeout=25.0):
                        device_dead_proxy_errors[device_serial] = 0
                        try:
                            if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                                d(resourceId="com.google.android.gms:id/cancel").click()
                        except Exception:
                            pass
                        type_number(d, input_box, target, speed_mode, custom_speed, opts["force_paste"])
                        log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                    else:
                        log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                        valid_numbers_queue.put(target)
                        log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                        force_next_clear = True

                        device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                        if device_dead_proxy_errors[device_serial] >= opts["iso_limit"]:
                            log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                            if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                break
                            d = init_uiautomator2_for_device(device_serial, log_to_otp)
                            device_dead_proxy_errors[device_serial] = 0
                        break

                    smart_delay(speed_mode, opts["action_delay"])

                    clicked_cont = False
                    for btn_txt in ["Continue", "continue", "Find Account", "find account"]:
                        if d(text=btn_txt).exists(timeout=0.5):
                            d(text=btn_txt).click()
                            clicked_cont = True
                            break
                        elif d(description=btn_txt).exists(timeout=0.5):
                            d(description=btn_txt).click()
                            clicked_cont = True
                            break

                    if clicked_cont:
                        log_to_otp(f"[{device_serial}] ✅ Proceeding...", "green")

                    time.sleep(1.0)
                    number_submitted = True

                    if d(textMatches="(?i)try again").exists(timeout=1.0):
                        log_to_otp(f"[{device_serial}] ❌ 'Try Again' Popup. Finding next...", "yellow")
                        d(textMatches="(?i)try again").click()
                        update_stat("otp_failed", 1, app, update_stats_ui)
                        time.sleep(0.5)
                        continue

                    steps_taken = 0
                    flow_success = False
                    action_after_scan = "restart_app"

                    while steps_taken < 6 and is_running and GLOBAL_RUN_TOKEN == current_token:
                        log_to_otp(f"[{device_serial}] ⏳ Scanning Page (Timeout: {page_timeout}s)...", "white")

                        page_state = "timeout"
                        elapsed = 0
                        while elapsed < page_timeout and is_running and GLOBAL_RUN_TOKEN == current_token:
                            try:
                                xml = d.dump_hierarchy().lower()
                                if "enter these letters and numbers" in xml or "captcha" in xml or "robot" in xml or "before we send the code" in xml:
                                    page_state = "captcha"
                                    break
                                if "page isn't available right now" in xml or "try reloading this page" in xml or "technical error" in xml or "refresh" in xml:
                                    page_state = "ip_block"
                                    break
                                if "try another way" in xml or "another way" in xml or "get code instead" in xml or "log in another way" in xml:
                                    page_state = "bypass_page"
                                    break
                                if "choose a way" in xml or "send sms" in xml or "get code via sms" in xml or "phone call" in xml or "get code via email" in xml:
                                    page_state = "choose_way"
                                    break
                                if "enter code" in xml or "6-digit" in xml or "8-digit" in xml or "didn't get" in xml:
                                    page_state = "otp_page"
                                    break
                                if "try again" in xml or "couldn't find" in xml or "no account found" in xml:
                                    page_state = "not_found"
                                    break
                                if "choose your account" in xml or "log in to another account" in xml:
                                    page_state = "multi_account"
                                    break
                            except Exception:
                                pass
                            time.sleep(0.5)
                            elapsed += 0.5

                        if page_state == "bypass_page":
                            btn_try = d(textMatches="(?i).*try another way.*|.*another way.*|.*get code instead.*|.*log in another way.*")
                            if btn_try.exists(timeout=1.0):
                                btn_try.click()
                                log_to_otp(f"[{device_serial}] 🔄 Bypassing Email/WA", "cyan")
                                btn_try.wait_gone(timeout=10.0)
                                time.sleep(2.0)
                                steps_taken += 1
                                continue
                            else:
                                action_after_scan = "restart_app"
                                break

                        elif page_state == "choose_way":
                            log_to_otp(f"[{device_serial}] ⚡ Smart Checking for SMS (*{last_2})...", "cyan")

                            number_found = False
                            target_y = -1
                            target_bounds = None

                            for search_step in range(int(page_timeout)):
                                if not is_running or GLOBAL_RUN_TOKEN != current_token:
                                    break

                                see_more_btn = d(textMatches="(?i)^(see more|see all)$")
                                if not see_more_btn.exists:
                                    see_more_btn = d(descriptionMatches="(?i)^(see more|see all)$")

                                if see_more_btn.exists(timeout=0.1):
                                    see_more_btn.click()
                                    log_to_otp(f"[{device_serial}] 👁 Expanded 'See more'", "cyan")
                                    time.sleep(1.0)

                                xml_dump = d.dump_hierarchy().lower()
                                valid_nodes = []

                                for match in re.finditer(r'<node[^>]+(?:text|content-desc)="([^"]+)"[^>]+bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml_dump):
                                    text_val = match.group(1)
                                    l, t, r, b = map(int, match.groups()[1:])

                                    if last_2 in text_val:
                                        if "whatsapp" not in text_val.lower() and "call" not in text_val.lower() and "password" not in text_val.lower() and "@" not in text_val and "email" not in text_val.lower():
                                            height = b - t
                                            if t > 150 and height < 250:
                                                valid_nodes.append((l, t, r, b))

                                if valid_nodes:
                                    valid_nodes.sort(key=lambda x: x[1])
                                    l, t, r, b = valid_nodes[-1]
                                    target_y = (t + b) // 2
                                    target_bounds = (l, t, r, b)
                                    number_found = True
                                    break

                                if search_step % 3 == 0 and search_step > 0:
                                    w, h = d.window_size()
                                    d.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 0.1)
                                    log_to_otp(f"[{device_serial}] 🔄 Scrolling down to find SMS (*{last_2})...", "white")

                                time.sleep(1.0)

                            if not number_found or target_y == -1:
                                log_to_otp(f"[{device_serial}] ❌ Valid SMS (*{last_2}) not found! Soft Reset.", "red")
                                action_after_scan = "restart_app"
                                break

                            w, h = d.window_size()
                            human_click(d, int(w * 0.12), target_y)
                            time.sleep(0.3)
                            l, t, r, b = target_bounds
                            human_click(d, (l + r) // 2, target_y)

                            log_to_otp(f"[{device_serial}] ✅ Selected Guaranteed SMS (*{last_2})", "green")
                            time.sleep(0.5)

                            timer_found = False
                            xml_dump_timer = d.dump_hierarchy().lower()
                            if "sms" in xml_dump_timer:
                                for match in re.finditer(r'<node[^>]+(?:text|content-desc)="[^"]*(\d{1,2}:\d{2})[^"]*"[^>]+bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml_dump_timer):
                                    t_bound = int(match.group(3))
                                    if t_bound > 150:
                                        timer_found = True
                                        break

                            if timer_found:
                                if skip_timer:
                                    log_to_otp(f"[{device_serial}] ⏱ True Timer Detected -> Fast Skip!", "red")
                                    action_after_scan = "restart_app"
                                    break
                                else:
                                    log_to_otp(f"[{device_serial}] ⏱ True Timer Detected -> Waiting...", "yellow")
                                    wait_start = time.time()
                                    timer_cleared = False
                                    while time.time() - wait_start < 120 and is_running and GLOBAL_RUN_TOKEN == current_token:
                                        time.sleep(3)
                                        safe_timer = False
                                        for match in re.finditer(r'<node[^>]+bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', d.dump_hierarchy().lower()):
                                            t_bound = int(match.group(2))
                                            if t_bound > 150 and re.search(r'\b\d{1,2}:\d{2}\b', match.group(0)):
                                                safe_timer = True
                                                break
                                        if not safe_timer:
                                            timer_cleared = True
                                            break
                                    if not timer_cleared:
                                        action_after_scan = "restart_app"
                                        break
                                    log_to_otp(f"[{device_serial}] ✅ Timer Finished!", "green")

                            btn_send_clicked = False
                            btn_cont = d(textMatches="(?i)^(continue|send|next)$")
                            if btn_cont.exists(timeout=0.5):
                                btn_cont.click()
                                btn_send_clicked = True
                            else:
                                for b_text in ["Continue", "continue", "Send", "send", "Next", "next"]:
                                    if d(text=b_text).exists(timeout=0.1):
                                        d(text=b_text).click()
                                        btn_send_clicked = True
                                        break

                            if not btn_send_clicked:
                                human_click(d, w // 2, int(h * 0.90))
                                btn_send_clicked = True

                            if btn_send_clicked:
                                log_to_otp(f"[{device_serial}] ✅ Clicked Continue (Fast)", "green")

                                if d(textMatches="(?i).*enter code.*|.*we sent.*|.*didn't get.*|.*try again.*").wait(timeout=15.0):
                                    device_popup_errors[device_serial] = 0
                                    device_fb_success_count[device_serial] = device_fb_success_count.get(device_serial, 0) + 1

                                    log_to_otp(f"[{device_serial}] ✅✅ SUCCESS FB OTP SENT: {target} ✅✅", "green")
                                    log_success(target)
                                    log_to_success(target)
                                    update_stat("otp_sent", 1, app, update_stats_ui)
                                    flow_success = True

                                    fb_limit_val = opts["fb_success_iso"]
                                    if fb_limit_val != "Never":
                                        try:
                                            limit_int = int(fb_limit_val)
                                        except Exception:
                                            limit_int = 99999
                                        if device_fb_success_count[device_serial] >= limit_int:
                                            log_to_otp(f"[{device_serial}] 🔄 Target Success Reached ({limit_int}). Auto Changing ISO...", "cyan")
                                            change_proxy_iso(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], opts["get_iso_list"], log_to_otp, username_only=True)
                                            device_fb_success_count[device_serial] = 0

                                    if double_otp:
                                        log_to_otp(f"[{device_serial}] ⏳ Double OTP: Waiting 1.5s...", "cyan")
                                        time.sleep(1.5)
                                        try:
                                            btn_didnt_get = d(textMatches="(?i).*didn't get.*|.*get code again.*")
                                            if btn_didnt_get.exists(timeout=2):
                                                btn_didnt_get.click()
                                                log_to_otp(f"[{device_serial}] 🔄 Clicked 'Didn't get code'", "white")
                                                time.sleep(1.5)

                                                btn_send_again = d(textMatches="(?i).*send sms again.*")
                                                if btn_send_again.exists(timeout=1.5):
                                                    btn_send_again.click()
                                                    log_to_otp(f"[{device_serial}] ✅ Clicked 'Send SMS again'", "cyan")
                                                else:
                                                    log_to_otp(f"[{device_serial}] 🔄 Sending 2nd OTP instantly...", "cyan")
                                                    btn_cont_2 = d(className="android.widget.Button", textMatches="(?i)^(continue|send|next)$")
                                                    if btn_cont_2.exists(timeout=1.0):
                                                        btn_cont_2.click()
                                                    else:
                                                        human_click(d, w // 2, int(h * 0.88))
                                        except Exception:
                                            pass
                                    time.sleep(4.0)
                                    action_after_scan = "restart_app"
                                    break
                                else:
                                    log_to_otp(f"[{device_serial}] ❌ Stuck on Continue. Soft Reset.", "red")
                                    action_after_scan = "restart_app"
                                    break

                        elif page_state == "multi_account":
                            profiles = d(className="android.view.ViewGroup", clickable=True)
                            if profiles.exists:
                                profiles[0].click()
                            else:
                                human_click(d, d.window_size()[0] // 2, int(d.window_size()[1] * 0.35))
                            time.sleep(1.0)
                            steps_taken += 1
                            continue

                        elif page_state == "not_found":
                            log_to_otp(f"[{device_serial}] ❌ Error or Not Found", "red")
                            if d(textMatches="(?i)try again").exists:
                                d(textMatches="(?i)try again").click()
                                update_stat("otp_failed", 1, app, update_stats_ui)
                                action_after_scan = "continue_loop"
                                break
                            else:
                                action_after_scan = "restart_app"
                                break

                        elif page_state == "captcha":
                            if skip_captcha:
                                log_to_otp(f"[{device_serial}] 🚫 Skip Captcha is ON. App Clearing...", "red")
                                action_after_scan = "restart_app"
                                break
                            else:
                                log_to_otp(f"[{device_serial}] ⏸ Captcha Found! Waiting 40s to solve manually...", "yellow")
                                captcha_cleared = False
                                wait_time = 0

                                while wait_time < 40 and is_running and GLOBAL_RUN_TOKEN == current_token:
                                    try:
                                        xml_dump = d.dump_hierarchy().lower()
                                        if "enter these letters and numbers" not in xml_dump and "captcha" not in xml_dump and "before we send the code" not in xml_dump:
                                            captcha_cleared = True
                                            break
                                    except Exception:
                                        pass
                                    time.sleep(1.0)
                                    wait_time += 1

                                if captcha_cleared:
                                    log_to_otp(f"[{device_serial}] ✅ Captcha Bypassed! Scanning next page...", "green")
                                    steps_taken += 1
                                    continue
                                else:
                                    log_to_otp(f"[{device_serial}] ❌ Captcha not solved in 40s! App Clearing...", "red")
                                    action_after_scan = "restart_app"
                                    break

                        elif page_state == "otp_page":
                            log_to_otp(f"[{device_serial}] ⚠ Forced Non-SMS OTP Page! Finding bypass...", "yellow")
                            btn_try = d(textMatches="(?i).*try another way.*|.*another way.*|.*get code instead.*|.*log in another way.*")
                            if btn_try.exists(timeout=1.0):
                                btn_try.click()
                                btn_try.wait_gone(timeout=10.0)
                                time.sleep(2.0)
                                steps_taken += 1
                                continue
                            else:
                                w, h = d.window_size()
                                human_click(d, w // 2, int(h * 0.85))
                                time.sleep(2.0)
                                steps_taken += 1
                                continue

                        elif page_state == "ip_block":
                            log_to_otp(f"[{device_serial}] ❌ 'Page isn't available' (IP Block) Detected in flow!", "red")
                            force_next_clear = True
                            device_popup_errors[device_serial] = device_popup_errors.get(device_serial, 0) + 1

                            if device_popup_errors[device_serial] >= opts["iso_limit"]:
                                log_to_otp(f"[{device_serial}] ❌ IP Blocked {device_popup_errors[device_serial]} times! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                    action_after_scan = "restart_app"
                                    break
                                d = init_uiautomator2_for_device(device_serial, log_to_otp)
                                device_popup_errors[device_serial] = 0
                            action_after_scan = "restart_app"
                            break

                        else:
                            if not check_internet_connection(device_serial):
                                if replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                                    d = init_uiautomator2_for_device(device_serial, log_to_otp)
                            else:
                                log_to_otp(f"[{device_serial}] ❌ Timeout/Stuck", "red")

                            action_after_scan = "restart_app"
                            break

                    if not flow_success and action_after_scan == "restart_app":
                        update_stat("otp_failed", 1, app, update_stats_ui)

                    run_count += 1

                    if action_after_scan == "continue_loop":
                        continue
                    elif action_after_scan == "restart_app":
                        break

                except Exception as inner_e:
                    if not number_submitted:
                        valid_numbers_queue.put(target)
                        log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                    raise inner_e

        except Exception as e:
            error_msg = str(e)[:40]
            if "-32001" in error_msg or "-32002" in error_msg:
                log_to_otp(f"[{device_serial}] 🔄 CPU Lag Detected. Soft Restarting...", "yellow")
            else:
                log_to_otp(f"[{device_serial}] ❌ Error: {error_msg}", "red")
                if not check_internet_connection(device_serial):
                    if replace_dead_proxy(device_serial, opts["proxy_pkg"], opts["get_proxy_txt"], log_to_otp):
                        d = init_uiautomator2_for_device(device_serial, log_to_otp)
            time.sleep(2)

    if GLOBAL_RUN_TOKEN != current_token:
        log_to_otp(f"[{device_serial}] 💀 FB Old Thread Killed", "yellow")
    else:
        log_to_otp(f"[{device_serial}] ⚠ FB Stopped", "yellow")

def bot_logic_wrapper(device_serial, current_token, platform, delay_sec, gui_data):
    d = init_uiautomator2_for_device(device_serial, gui_data["log_to_otp"])
    if not d:
        gui_data["log_to_otp"](f"❌ [{device_serial}] Could not connect! Skipping this device.", "red")
        return

    wait_time = delay_sec
    while wait_time > 0 and is_running and GLOBAL_RUN_TOKEN == current_token:
        time.sleep(0.5)
        wait_time -= 0.5

    if is_running and GLOBAL_RUN_TOKEN == current_token:
        if platform == "Facebook":
            bot_logic_fb(d, device_serial, current_token, gui_data)
        elif platform == "Instagram":
            bot_logic_ig(d, device_serial, current_token, gui_data)

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # Authenticate via cloud license
    show_license_window()
    
    # Start background threads
    threading.Thread(target=background_battery_simulator, daemon=True).start()