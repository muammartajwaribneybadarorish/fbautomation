import os
import sys
import tempfile
import shutil
import socket 

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
                with open(tmp_path, 'wb') as f: f.write(src.read_bytes())
                res = _orig_push(self, tmp_path, dst, *args, **kwargs)
                try: os.remove(tmp_path)
                except: pass
                return res
            return _orig_push(self, src, dst, *args, **kwargs)
        adbutils.sync.Sync.push = _patched_push
        
    _orig_install = adbutils.AdbDevice.install
    def _patched_install(self, filepath, *args, **kwargs):
        if "nuitka_resource" in str(type(filepath)).lower() or (hasattr(filepath, 'read_bytes') and not hasattr(filepath, 'read')):
            tmp_path = os.path.join(tempfile.gettempdir(), getattr(filepath, 'name', 'temp_app.apk'))
            with open(tmp_path, 'wb') as f: f.write(filepath.read_bytes())
            res = _orig_install(self, tmp_path, *args, **kwargs)
            try: os.remove(tmp_path)
            except: pass
            return res
        return _orig_install(self, filepath, *args, **kwargs)
    adbutils.AdbDevice.install = _patched_install
except Exception as e:
    pass

import customtkinter as ctk
import uiautomator2 as u2
import threading
import time
import random
import requests
import json
import queue
import webbrowser
import re
from datetime import datetime
import subprocess
import hashlib
import urllib.parse
from tkinter import filedialog
import ctypes 
import winreg
import uuid

# ==========================================
# 🛡️ ANTI-SNIFFING & SECURITY BLOCK
# ==========================================
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

# ==========================================
# 👑 DISTRIBUTOR / PARTNER CONFIGURATION
# ==========================================
APP_TITLE = "ZENEX ADB AUTOMATIONS"
HEADER_TEXT = "⚡ ZENEX AUTOMATION PRO ⚡"
DISTRIBUTOR_NAME = "Abdullah"
TELEGRAM_USER = "abdullah_124"
TELEGRAM_LINK = "https://t.me/abdullah_124"
FOOTER_TEXT = "Developed by: Abdullah | Owner: ZENEX NETWORK"

# ==========================================
# ⚙️ GLOBAL CONFIG & PATHS
# ==========================================
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
DAEMON_LOCK = threading.Lock() # 🛑 ANTI-LAG LOCK
PROXY_LOCK = threading.Lock()  # 🛑 PREVENT DUPLICATE PROXY ASSIGNMENT FIX

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

ADB_PATH = os.path.join(CURRENT_DIR, "platform-tools", "adb.exe")
if os.path.exists(os.path.join(CURRENT_DIR, "platform-tools")):
    os.environ["PATH"] = os.path.join(CURRENT_DIR, "platform-tools") + os.pathsep + os.environ["PATH"]

LOCAL_APK_PATH = os.path.join(CURRENT_DIR, "uiautomator2", "app-uiautomator.apk")
LOCAL_TEST_APK_PATH = os.path.join(CURRENT_DIR, "uiautomator2", "app-uiautomator-test.apk") 

APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'ZenexNetwork')
if not os.path.exists(APPDATA_DIR): 
    os.makedirs(APPDATA_DIR)
    
CONFIG_FILE = os.path.join(APPDATA_DIR, 'zenex_config.json')
SUCCESS_LOG_FILE = os.path.join(APPDATA_DIR, 'success_numbers.txt')

is_running = False
GLOBAL_RUN_TOKEN = 0

valid_numbers_queue = queue.Queue()
txt_numbers_queue = queue.Queue()

# 🌐 Proxy Memory System
GLOBAL_PROXIES = []
device_current_proxy = {} 

# Separate tracking for Popups, Dead Proxies, and Live Checking
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

# ==========================================
# 🛠️ EMULATOR NAME FORMATTER FIX
# ==========================================
def format_emu_name(text):
    """Converts 127.0.0.1:5555 to emulator-5554 format visually for UI/Logs"""
    def replacer(match):
        port = int(match.group(1))
        # Default ADB mapping logic
        if port in [5555, 5557, 5559, 5561, 5563, 5565, 5567, 5569]:
            return f"emulator-{port-1}"
        return f"emulator-{port}"
    text = re.sub(r'127\.0\.0\.1:(\d+)', replacer, str(text))
    text = re.sub(r'localhost:(\d+)', replacer, text)
    return text

# ==========================================
# 🌐 CLOUD LICENSE SYSTEM & ROBUST HWID
# ==========================================
API_BASE_URL = "http://135.125.226.195:3004/api/bot"

def get_hwid():
    hwid_string = ""
    try:
        out = subprocess.check_output(["powershell", "-Command", "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"], creationflags=CREATE_NO_WINDOW, timeout=5).decode().strip()
        if out and len(out) > 10 and "FFFF" not in out:
            hwid_string = out
    except: pass
        
    if not hwid_string:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                hwid_string = winreg.QueryValueEx(key, "MachineGuid")[0]
        except: pass

    if not hwid_string:
        try:
            out = subprocess.check_output(["powershell", "-Command", "(Get-CimInstance -Class Win32_ComputerSystem).UUID"], creationflags=CREATE_NO_WINDOW, timeout=5).decode().strip()
            if out and len(out) > 10: hwid_string = out
        except: pass

    if not hwid_string:
        try: hwid_string = str(uuid.getnode())
        except: pass

    if not hwid_string or hwid_string == "0":
        uuid_file = os.path.join(APPDATA_DIR, 'sys_machine.dat')
        if os.path.exists(uuid_file):
            with open(uuid_file, 'r') as f: hwid_string = f.read().strip()
        else:
            hwid_string = str(uuid.uuid4())
            try:
                with open(uuid_file, 'w') as f: f.write(hwid_string)
            except: pass

    try: hwid_string += f"_{socket.gethostname()}"
    except: pass

    return hashlib.sha256(hwid_string.encode()).hexdigest()[:20].upper()

def check_cloud_status():
    try:
        hwid = get_hwid()
        response = requests.post(f"{API_BASE_URL}/check", json={"hwid": hwid}, timeout=10)
        return response.json()
    except Exception as e:
        return {"valid": False, "status": "ERROR", "msg": "Server Offline! Retrying..."}

def request_cloud_access(name):
    try:
        hwid = get_hwid()
        requests.post(f"{API_BASE_URL}/request", json={"hwid": hwid, "name": name}, timeout=10)
    except: 
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

    ctk.CTkLabel(lic_app, text="Your PC Hardware ID (HWID):", font=("Consolas", 12)).pack()
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
            if not name: return
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
            encoded_msg = urllib.parse.quote(f"Hello {DISTRIBUTOR_NAME},\nI have submitted an access request.\nMy HWID: {hwid}")
            webbrowser.open(f"{TELEGRAM_LINK}?text={encoded_msg}")
            
        ctk.CTkButton(dynamic_frame, text=f"💬 MESSAGE {DISTRIBUTOR_NAME} ON TELEGRAM", command=contact_admin, fg_color="#2980B9").pack(pady=15)
        ctk.CTkButton(dynamic_frame, text="🔄 REFRESH STATUS", command=check_logic, fg_color="#27AE60").pack(pady=5)

    def check_logic():
        data = check_cloud_status()
        status = data.get("status")
        
        if status == "NOT_FOUND":
            render_not_found()
            msg_lbl.configure(text="Please submit your name to get access.", text_color="#BDC3C7")
        elif status == "PENDING":
            render_pending()
            msg_lbl.configure(text=data.get("msg"), text_color="#F1C40F")
        elif status == "BLOCKED" or status == "EXPIRED":
            for widget in dynamic_frame.winfo_children(): 
                widget.destroy()
            title_lbl.configure(text="🚫 ACCESS DENIED", text_color="#E74C3C")
            msg_lbl.configure(text=data.get("msg"), text_color="#E74C3C")
            ctk.CTkButton(dynamic_frame, text="🔄 CHECK AGAIN", command=check_logic, fg_color="#7F8C8D").pack(pady=20)
        elif status == "ACTIVE" and data.get("valid") == True:
            title_lbl.configure(text="✅ ACTIVATED!", text_color="#2ECC71")
            msg_lbl.configure(text=f"Welcome! License Valid till {data.get('expiry')}", text_color="#2ECC71")
            for widget in dynamic_frame.winfo_children(): 
                widget.destroy()
            lic_app.protocol("WM_DELETE_WINDOW", lic_app.destroy) 
            lic_app.after(1500, lic_app.destroy) 
        else:
            msg_lbl.configure(text="Server Offline! Retrying...", text_color="#E74C3C")
            lic_app.after(3000, check_logic)

    lic_app.after(500, check_logic)
    lic_app.mainloop()

    final_check = check_cloud_status()
    if final_check.get("valid") == True:
        return True, final_check.get("expiry", "Unknown"), final_check.get("name", "User")
    return False, "Unknown", "User"

# ==========================================
# 📡 NUMBER HARVESTER & FILTER 
# ==========================================
def fetch_number_from_panel():
    global CURRENT_PANEL, CURRENT_API_KEY, CURRENT_RANGE
    if CURRENT_PANEL == "ZENEX NETWORK":
        url = "https://api.zenexnetwork.com/v1/getnum"
        headers = {"mapikey": CURRENT_API_KEY, "Content-Type": "application/json"}
        payload = {"range": CURRENT_RANGE, "is_national": False, "remove_plus": False}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200 and res.json().get("meta", {}).get("status") == "success":
                return res.json()["data"]["number"]
        except: 
            pass
    return None

def build_browser_fingerprint():
    andro_ver = random.choice([
        '4.0.3','4.0.4','4.1.2','4.2.2','4.3','4.4.2','4.4.4',
        '5.0','5.0.2','5.1.1','6.0','6.0.1','7.0','7.1.1'
    ])
    models = [
        'SM-G900F','SM-G920F','SM-G930F','SM-G935F','SM-J320F',
        'SM-J500F','SM-J700F','SM-A300FU','SM-A500FU','SM-N910F',
        'SM-N920C','LG-H815','LG-H850','LG-D855','LG-K420',
        'XT1068','XT1092','XT1562','XT1635','E6653','F5121',
        'D6603','ALE-L21','VNS-L31','PRA-LX1'
    ]
    model = random.choice(models)

    if andro_ver.startswith('4'): 
        build_prefix = random.choice(['KOT49','KTU84','JZO54','JSS15'])
    elif andro_ver.startswith('5'): 
        build_prefix = random.choice(['LRX21','LMY47','LRX22'])
    elif andro_ver.startswith('6'): 
        build_prefix = random.choice(['MRA58','MMB29'])
    elif andro_ver.startswith('7'): 
        build_prefix = random.choice(['NRD90','NMF26'])
    else: 
        build_prefix = 'LMY47'

    build = f"{build_prefix}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(35,65)}"
    chrome_ver = f"{random.randint(35,65)}.0.{random.randint(1500,4000)}.{random.randint(40,150)}"
    base_ua = (
        f"Mozilla/5.0 (Linux; Android {andro_ver}; {model} Build/{build}) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver} Mobile Safari/537.36"
    )

    browser_list = [
        'Brave','Chrome','Edge','Firefox','Samsung','Opera',
        'UC','DuckDuckGo','Vivaldi','Yandex','Kiwi',
        'Dolphin','Mi Browser','Maxthon','Puffin'
    ]
    browser = random.choice(browser_list)

    sec_headers = {}
    if browser == 'Brave':
        sec_headers = {'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"'}
    elif browser == 'Chrome':
        sec_headers = {'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"'}
    else:
        sec_headers = {'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"'}

    screen_res = random.choice([
        '320x480','480x800','540x960','800x480','854x480',
        '960x540','720x1280','1280x720','1080x1920','1920x1080','1440x2560'
    ])

    base_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'sec-ch-ua-full-version-list': '"Chromium";v="143.0.0.0", "Not A(Brand";v="24.0.0.0"',
        'sec-ch-ua-model': f'"{model}"',
        'sec-ch-ua-platform-version': f'"{andro_ver}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': base_ua,
    }
    base_headers.update(sec_headers)
    return base_headers, screen_res, model, andro_ver

def check_fb_account(number):
    session = requests.Session()
    server = FILTER_SERVER_DOMAIN
    base_headers, screen_res, model, andro_ver = build_browser_fingerprint()
    session.cookies.update({'m_pixel_ratio': '1', 'wd': screen_res})

    try:
        first_headers = base_headers.copy()
        first_headers.update({'sec-fetch-site': 'none'})

        get_url = f"https://{server}/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0&__mmr=1&_rdr"
        r_get = session.get(get_url, headers=first_headers, timeout=15)

        try:
            lsd = re.search(r'name="lsd" value="(.*?)"', r_get.text).group(1)
        except:
            lsd = ''
        try:
            jazoest = re.search(r'name="jazoest" value="(.*?)"', r_get.text).group(1)
        except:
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

def update_stat(key, value=1):
    with stats_lock: 
        stats[key] += value
    app.after(0, update_stats_ui)

def number_harvester_thread(use_filter, platform, current_token, data_source):
    global is_running, GLOBAL_RUN_TOKEN
    log_to_filter(f"✅ Harvester Started ({platform} | Source: {data_source})", "cyan")

    while is_running and GLOBAL_RUN_TOKEN == current_token:
        use_filter = filter_var.get()
        platform = platform_var.get()
        data_source = data_source_combo.get()

        if valid_numbers_queue.qsize() < 5: 
            num = None
            if data_source == "Bulk TXT File":
                if not txt_numbers_queue.empty():
                    num = txt_numbers_queue.get()
                    app.after(0, lambda: lbl_txt_count.configure(text=f"TXT Queue: {txt_numbers_queue.qsize()}"))
                else:
                    log_to_filter("⚠ TXT File is empty! Please load more numbers.", "yellow")
                    time.sleep(3)
                    continue
            else:
                num = fetch_number_from_panel()

            if num:
                num = num.strip()
                if platform == "Instagram":
                    valid_numbers_queue.put(num)
                    update_stat("valid")
                    log_to_filter(f"✅ {num} | Direct to IG (Filter Skipped)", "cyan")
                else:
                    if use_filter:
                        update_stat("checked")
                        is_valid, reason = check_fb_account(num)
                        if is_valid:
                            valid_numbers_queue.put(num)
                            update_stat("valid")
                            log_to_filter(f"✅ {num} | {reason}", "green")
                        else:
                            update_stat("invalid")
                            log_to_filter(f"❌ {num} | {reason}", "red")
                    else:
                        valid_numbers_queue.put(num)
                        update_stat("valid")
                        log_to_filter(f"✅ {num} | Filter Disabled", "green")
            time.sleep(1)
        else: 
            time.sleep(2)

# ==========================================
# 📱 KEYBOARD HELPER
# ==========================================
def is_keyboard_shown(serial):
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    try:
        res = subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "input_method"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=3)
        if "mInputShown=true" in res.stdout:
            return True
    except:
        pass
    return False

# ==========================================
# 🔌 AUTO EMULATOR CONNECTOR (WIN 11 + ANTI LAG)
# ==========================================
def force_kill_adb():
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", "adb.exe", "/T"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=5)
        except: 
            pass

def get_connected_devices():
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    
    with DAEMON_LOCK: 
        try:
            result = subprocess.check_output([adb_cmd, "devices"], creationflags=CREATE_NO_WINDOW, timeout=5).decode("utf-8")
            raw_devices = [line.split()[0] for line in result.strip().split('\n')[1:] if 'device' in line and 'offline' not in line]
            
            if not raw_devices:
                ports = ["5554", "5555", "5556", "5557", "21503", "21513", "62001", "62025"]
                for p in ports:
                    try: subprocess.run([adb_cmd, "connect", f"127.0.0.1:{p}"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=1)
                    except: pass
                result = subprocess.check_output([adb_cmd, "devices"], creationflags=CREATE_NO_WINDOW, timeout=5).decode("utf-8")
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
                    except: 
                        pass

                if dev not in clean_devices: 
                    clean_devices.append(dev)

            if 'offline' in result and not clean_devices:
                force_kill_adb()
                time.sleep(1)
                subprocess.run([adb_cmd, "start-server"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=5)
                
                ports = ["5554", "5555", "5556", "5557", "21503", "21513", "62001", "62025"]
                for p in ports:
                    try: subprocess.run([adb_cmd, "connect", f"127.0.0.1:{p}"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=1)
                    except: pass
                
                result = subprocess.check_output([adb_cmd, "devices"], creationflags=CREATE_NO_WINDOW, timeout=5).decode("utf-8")
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
                        except: pass
                    if dev not in clean_devices: clean_devices.append(dev)

            return clean_devices
        except: 
            return []

# ==========================================
# 🔋 BACKGROUND BATTERY SIMULATOR
# ==========================================
def background_battery_simulator():
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    while True:
        time.sleep(25) 
        if not is_running: continue 
        
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
                            subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "0"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                            subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "usb", "0"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                            subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "unplug"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                            subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "3"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2) 
                            subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "level", str(start_level)], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                        except: pass
                    else:
                        state = device_battery_states[serial]
                        if current_time - state["last_update"] >= 180: 
                            if state["charging"]:
                                state["level"] += random.randint(2, 4)
                                if state["level"] >= random.randint(85, 95):
                                    state["charging"] = False
                                    try:
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "0"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "unplug"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "3"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                                    except: pass
                            else:
                                state["level"] -= 1
                                if state["level"] <= random.randint(10, 15):
                                    state["charging"] = True
                                    try:
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "ac", "1"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "usb", "1"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                                        subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "status", "2"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2) 
                                    except: pass
                            
                            state["level"] = max(5, min(100, state["level"]))
                            state["last_update"] = current_time
                            
                            try:
                                subprocess.run([adb_cmd, "-s", serial, "shell", "dumpsys", "battery", "set", "level", str(state["level"])], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=2)
                            except: pass
        except:
            pass

# ==========================================
# 🔌 AUTO ADB RECONNECT DAEMON
# ==========================================
def adb_keep_alive_daemon():
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    while True:
        time.sleep(20) 
        
        if is_running and len(device_checkboxes_vars) > 0:
            with DAEMON_LOCK: 
                try:
                    result = subprocess.check_output([adb_cmd, "devices"], creationflags=CREATE_NO_WINDOW, timeout=5).decode("utf-8")
                    for serial, var in device_checkboxes_vars.items():
                        if var.get(): 
                            if f"{serial}\tdevice" not in result:
                                log_to_otp(f"[{serial}] 🔌 ADB Disconnected! Auto-reconnecting silently...", "yellow")
                                subprocess.run([adb_cmd, "disconnect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
                                time.sleep(1)
                                subprocess.run([adb_cmd, "connect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
                                try:
                                    d = u2.connect(serial)
                                    d.healthcheck()
                                except: pass
                except:
                    pass

# ==========================================
# 🤖 ANDROID AUTOMATION CORE & SMART PROXY
# ==========================================
def check_internet_connection(serial):
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    with DAEMON_LOCK:
        try:
            res = subprocess.run([adb_cmd, "-s", serial, "shell", "curl -s -I -m 5 https://google.com"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=8)
            if "HTTP/" in res.stdout or "200" in res.stdout or "301" in res.stdout or "302" in res.stdout:
                return True
                
            res2 = subprocess.run([adb_cmd, "-s", serial, "shell", "ping -c 1 -W 3 8.8.8.8"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=5)
            if "1 packets transmitted, 1 received" in res2.stdout or "time=" in res2.stdout:
                return True
            return False
        except:
            return False

def check_proxy_live(proxy_string):
    proxy_string = proxy_string.replace("socks5://", "").replace("http://", "").strip()
    parts = proxy_string.split(":")
    
    if len(parts) >= 2:
        host = parts[0]
        port = parts[1]
        try:
            if len(parts) == 4:
                proxy_url = f"http://{parts[2]}:{parts[3]}@{host}:{port}"
            else:
                proxy_url = f"http://{host}:{port}"
                
            res = requests.get("http://clients3.google.com/generate_204", 
                               proxies={"http": proxy_url, "https": proxy_url}, 
                               timeout=8)
            
            if res.status_code in [200, 204]: 
                return True
        except:
            pass
            
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4.0)
            s.connect((host, int(port)))
            s.close()
            return True
        except:
            pass
                
    return False

def live_proxy_checker_daemon():
    while True:
        time.sleep(10) 
        if not is_running: continue
        
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
                    except: pass
                app.after(0, update_ui)

                if not is_alive:
                    device_force_proxy_change[serial] = device_force_proxy_change.get(serial, 0) + 1
                else:
                    device_force_proxy_change[serial] = 0

def replace_dead_proxy(serial, proxy_pkg):
    global GLOBAL_PROXIES, device_stopped_status
    
    # Check if user is even using the proxy feature
    raw_text = proxy_textbox.get("1.0", "end").strip()
    if not raw_text and not device_current_proxy.get(serial):
        log_to_otp(f"[{serial}] ⚠ Normal Mode: Auto-Proxy OFF. Skipping replacement.", "yellow")
        time.sleep(3)
        return False
    
    while is_running:
        valid_proxy = None
        while is_running:
            with PROXY_LOCK: 
                if not GLOBAL_PROXIES:
                    if not device_stopped_status.get(serial, False):
                        log_to_otp(f"[{serial}] ❌ Proxy list empty! Skipping IP Replace...", "yellow")
                        device_stopped_status[serial] = True
                    time.sleep(5)
                    return False
                candidate = GLOBAL_PROXIES.pop(0) 
                
            if check_proxy_live(candidate):
                valid_proxy = candidate
                break
            else:
                log_to_otp(f"[{serial}] 💀 Skipped Dead Proxy from list...", "yellow")
                
        if not valid_proxy:
            return False
            
        device_current_proxy[serial] = valid_proxy
        device_stopped_status[serial] = False
        log_to_otp(f"[{serial}] 🔄 Changing to new LIVE Proxy...", "yellow")
        
        setup_success = configure_super_proxy(serial, valid_proxy, "", proxy_pkg)
        if setup_success:
            return True
        else:
            log_to_otp(f"[{serial}] ♻️ UI Error (Dead IP). Finding another...", "yellow")
            
    return False

def change_proxy_iso(serial, proxy_pkg, username_only=False):
    current_proxy = device_current_proxy.get(serial, "")
    
    # Check if user is even using the proxy feature
    raw_text = proxy_textbox.get("1.0", "end").strip()
    if not raw_text and not current_proxy:
        log_to_otp(f"[{serial}] ⚠ Normal Mode: Auto-Proxy OFF. Skipping ISO change.", "yellow")
        return False
        
    if not current_proxy:
        try:
            proxies = [p.strip() for p in raw_text.split('\n') if p.strip()]
            if proxies:
                current_proxy = proxies[0]
                device_current_proxy[serial] = current_proxy
                log_to_otp(f"[{serial}] ⚠ Found fallback proxy from list for ISO change.", "cyan")
        except Exception as e:
            pass
            
    if not current_proxy:
        log_to_otp(f"[{serial}] ❌ Cannot change ISO! Proxy not found in memory.", "red")
        return False
    
    custom_isos = proxy_iso_list_var.get().replace(" ", "").split(",")
    if not custom_isos or custom_isos[0] == "":
        custom_isos = ["US", "GB", "CA", "AU", "DE"]
        
    new_iso = random.choice(custom_isos)
    if "_zone_" in current_proxy:
        new_proxy = re.sub(r'_zone_[a-zA-Z0-9]+', f'_zone_{new_iso}', current_proxy)
    else:
        new_proxy = current_proxy 
        
    device_current_proxy[serial] = new_proxy
    log_to_otp(f"[{serial}] 🔄 Changing ISO to {new_iso}...", "cyan")
    
    if username_only:
        update_proxy_username_only(serial, new_proxy, proxy_pkg)
    else:
        configure_super_proxy(serial, new_proxy, "", proxy_pkg) 
    return True

def update_proxy_username_only(serial, proxy_string, pkg_name):
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    try:
        log_to_otp(f"[{serial}] ⏳ Waiting for ISO Update queue...", "white")
        
        with PROXY_LOCK: 
            log_to_otp(f"[{serial}] ⚙ Fast Update: Changing ISO (Username only)...", "cyan")
            with DAEMON_LOCK:
                subprocess.run([adb_cmd, "-s", serial, "shell", "am", "force-stop", pkg_name], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=5)
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
                log_to_otp(f"[{serial}] ❌ Fast Setup Failed: Credentials invalid!", "red")
                return False

            try:
                if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                    d(textMatches="(?i)(ok|allow|accept)").click()
                    time.sleep(1.0)
            except:
                pass 
                
            log_to_otp(f"[{serial}] ✅ Fast Proxy Updated! ISO Changed to {user}", "green")
            time.sleep(2.0) 
            return True

    except Exception as e:
        log_to_otp(f"[{serial}] ❌ Fast Proxy Update Error: {str(e)[:40]}", "red")
        return False

def get_action_delay():
    try:
        base_delay = float(action_delay_entry.get())
        if speed_mode_var.get() == "Human":
            return base_delay + random.uniform(0.2, 0.6)
        return base_delay
    except:
        return 1.0 

def human_click(d, x, y, offset=7):
    try:
        rand_x = x + random.randint(-offset, offset)
        rand_y = y + random.randint(-offset, offset)
        d.click(rand_x, rand_y)
    except:
        d.click(x, y) 

def smart_delay(speed_mode):
    time.sleep(get_action_delay())

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
        except: 
            pass

def grant_permissions(serial, pkg_name):
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
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
                subprocess.run([adb_cmd, "-s", serial, "shell", "pm", "grant", pkg_name, p], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
            except:
                pass

def type_number(d, input_box, number, speed_mode, custom_speed_str, force_paste=False): 
    if input_box:
        try: 
            input_box.click()
            input_box.clear_text()
        except: 
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
            except:
                d.send_keys(number, clear=True)
        else:
            d.send_keys(number, clear=True)
        return

    try: 
        speed = float(custom_speed_str)
    except:
        speed = 0.08 

    for char in number:
        d.send_keys(char)
        time.sleep(speed)

def log_success(number):
    try:
        with open(SUCCESS_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {number}\n")
    except: 
        pass

def wait_for_page_state(d, speed_mode, timeout=30):
    elapsed = 0
    check_interval = 0.5
    while elapsed < timeout and is_running:
        try:
            xml = d.dump_hierarchy().lower()
            if "try another way" in xml or "another way" in xml or "get code instead" in xml or "log in another way" in xml: 
                return "bypass_page"
            if "choose a way" in xml or "send sms" in xml or "get code via sms" in xml or "phone call" in xml or "get code via email" in xml: 
                return "choose_way"
            if "enter code" in xml or "6-digit" in xml or "8-digit" in xml or "didn't get" in xml: 
                return "otp_page"
            if "enter these letters and numbers" in xml or "captcha" in xml or "robot" in xml or "before we send the code" in xml: 
                return "captcha"
            if "try again" in xml or "couldn't find" in xml or "no account found" in xml: 
                return "not_found"
            if "choose your account" in xml or "log in to another account" in xml: 
                return "multi_account"
            if "page isn't available right now" in xml or "try reloading this page" in xml or "technical error" in xml or "refresh" in xml:
                return "ip_block"
        except: 
            pass
        time.sleep(check_interval)
        elapsed += check_interval
    return "timeout"

def init_uiautomator2_for_device(serial):
    log_to_otp(f"💬 [{serial}] 🔧 Checking ATX (uiautomator2) setup...", "cyan")
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    
    with DAEMON_LOCK:
        try:
            check_pkg = subprocess.run([adb_cmd, "-s", serial, "shell", "pm", "path", "com.github.uiautomator"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=5)
            if "package:" not in check_pkg.stdout:
                log_to_otp(f"⚙️ [{serial}] ATX is missing! Auto-Installing...", "yellow")
                if os.path.exists(LOCAL_APK_PATH):
                    subprocess.run([adb_cmd, "-s", serial, "install", "-r", "-g", LOCAL_APK_PATH], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
                    if os.path.exists(LOCAL_TEST_APK_PATH):
                        subprocess.run([adb_cmd, "-s", serial, "install", "-r", "-g", LOCAL_TEST_APK_PATH], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
                    log_to_otp(f"✔️ [{serial}] ATX Installed successfully.", "green")
                    time.sleep(2)
                else:
                    log_to_otp(f"❌ [{serial}] LOCAL APK NOT FOUND! Please put app-uiautomator.apk in uiautomator2 folder.", "red")
        except Exception as e:
            pass

    try:
        d = u2.connect(serial)
        if d.info: 
            log_to_otp(f"✔️ [{serial}] ATX Ready & Connected.", "green")
            d.implicitly_wait(1.0)
            return d
    except Exception as e:
        err_msg = str(e)
        log_to_otp(f"❌ [{serial}] Initialization Error: {err_msg[:60]}", "red")
        
        try:
            subprocess.run([adb_cmd, "disconnect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
            time.sleep(1)
            subprocess.run([adb_cmd, "connect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
        except: pass
        
    return None

def background_startup_check():
    log_to_otp("🔄 Running background ADB & APK checks...", "cyan")
    devices = get_connected_devices()
    if devices:
        log_to_otp(f"✔️ ✓ Detected {len(devices)} devices", "green")
        for serial in devices:
            init_uiautomator2_for_device(serial)
        log_to_otp("✔️ Background checks completed. Ready to START.", "green")

def bot_logic_wrapper(device_serial, current_token, platform, delay_sec):
    global is_running, GLOBAL_RUN_TOKEN
    d = init_uiautomator2_for_device(device_serial)
    if not d: 
        log_to_otp(f"❌ [{device_serial}] Could not connect! Skipping this device.", "red")
        return
    
    wait_time = delay_sec
    while wait_time > 0 and is_running and GLOBAL_RUN_TOKEN == current_token:
        time.sleep(0.5)
        wait_time -= 0.5

    if is_running and GLOBAL_RUN_TOKEN == current_token:
        if platform == "Facebook":
            bot_logic_fb(d, device_serial, current_token)
        elif platform == "Instagram":
            bot_logic_ig(d, device_serial, current_token)

# ==========================================
# 📱 INSTAGRAM AUTOMATION LOGIC (LITE + OFFICIAL)
# ==========================================
def bot_logic_ig(d, device_serial, current_token):
    global is_running, device_handles, GLOBAL_RUN_TOKEN, device_popup_errors, device_dead_proxy_errors, device_force_proxy_change
    
    try:
        d.implicitly_wait(1.0) 
        d.settings['operation_delay'] = (0.05, 0.05)
        device_handles.append(d)
    except: 
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
        pkg_name = package_combo.get()
        speed_mode = speed_mode_var.get()
        custom_speed = typ_speed_entry.get()
        try: clear_interval = int(clear_interval_entry.get())
        except: clear_interval = 5
        try: ig_resend_limit = int(ig_resend_combo.get())
        except: ig_resend_limit = 3

        try:
            if device_force_proxy_change.get(device_serial, 0) >= 15: 
                log_to_otp(f"[{device_serial}] ❌ Background Scanner Detected Dead IP! Auto Replacing...", "red")
                if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                    continue 
                d = init_uiautomator2_for_device(device_serial)
                device_force_proxy_change[device_serial] = 0
                device_dead_proxy_errors[device_serial] = 0
                continue 

            # APP INSTALL CHECK
            try:
                app_installed = d.app_info(pkg_name) is not None
            except:
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
            except Exception as e:
                pass

            d.app_wait(pkg_name, front=True, timeout=10.0)
            handle_permissions(d) 

            log_to_otp(f"[{device_serial}] ⏳ Waiting for 'Create Account/Get started' Button...", "white")
            
            create_btn_found = False
            for _ in range(25): 
                if not is_running or GLOBAL_RUN_TOKEN != current_token: break
                
                try:
                    if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                        d(resourceId="com.google.android.gms:id/cancel").click()
                except: pass

                if pkg_name == "com.instagram.android":
                    if d.xpath('//*[@text="Create new account" or @content-desc="Create new account"]').exists:
                        try: d.xpath('//*[@text="Create new account" or @content-desc="Create new account"]').click()
                        except: pass
                        create_btn_found = True
                        break
                    elif d.xpath('//*[@text="Get started" or @content-desc="Get started"]').exists:
                        try: d.xpath('//*[@text="Get started" or @content-desc="Get started"]').click()
                        except: pass
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
                        except:
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
                
                try: iso_limit_val = int(iso_limit_combo.get())
                except: iso_limit_val = 3
                
                if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                    log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                    if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                        continue
                    d = init_uiautomator2_for_device(device_serial)
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
            except:
                pass

            while is_running and GLOBAL_RUN_TOKEN == current_token:
                speed_mode = speed_mode_var.get()
                custom_speed = typ_speed_entry.get()

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
                            except: pass
                            num_box.click() 
                            time.sleep(0.3)
                            type_number(d, num_box, target, speed_mode, custom_speed, force_paste_var.get()) 
                            log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                            valid_numbers_queue.put(target)
                            log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                            force_next_clear = True
                            
                            device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                            try: iso_limit_val = int(iso_limit_combo.get())
                            except: iso_limit_val = 3
                            if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                                log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                    break
                                d = init_uiautomator2_for_device(device_serial)
                                device_dead_proxy_errors[device_serial] = 0
                                
                            break 
                    else:
                        num_box = d(className=CLASS_NUM_BOX)
                        
                        if num_box.wait(timeout=15.0):
                            device_dead_proxy_errors[device_serial] = 0 
                            try:
                                if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.1):
                                    d(resourceId="com.google.android.gms:id/cancel").click()
                            except: pass
                            num_box.click() 
                            time.sleep(0.3)
                            type_number(d, num_box, target, speed_mode, custom_speed, force_paste_var.get()) 
                            log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                            valid_numbers_queue.put(target)
                            log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                            force_next_clear = True
                            
                            device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                            try: iso_limit_val = int(iso_limit_combo.get())
                            except: iso_limit_val = 3
                            if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                                log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                    break
                                d = init_uiautomator2_for_device(device_serial)
                                device_dead_proxy_errors[device_serial] = 0
                                
                            break 

                    smart_delay(speed_mode)
                    
                    next_clicked = False
                    
                    if pkg_name == "com.instagram.android":
                        if d.xpath('//*[@text="Next" or @content-desc="Next"]').exists:
                            d.xpath('//*[@text="Next" or @content-desc="Next"]').click()
                            next_clicked = True
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Smart XPath)", "green")
                        elif d(text="Next").exists(timeout=0.5):
                            d(text="Next").click()
                            next_clicked = True
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Text)", "green")
                        else:
                            d.press("enter")
                            next_clicked = True
                            log_to_otp(f"[{device_serial}] ⚠ Clicked Next (By Enter)", "yellow")
                    else:
                        if d(textMatches="(?i).*(next|continue).*").exists(timeout=0.5):
                            d(textMatches="(?i).*(next|continue).*").click()
                            next_clicked = True
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Text)", "green")
                        elif d.xpath(XP_NEXT_BTN_SMART).exists:
                            d.xpath(XP_NEXT_BTN_SMART).click()
                            next_clicked = True
                            log_to_otp(f"[{device_serial}] ✅ Clicked Next (By Smart XPath)", "green")
                        else:
                            d.press("enter")
                            w, h = d.window_size()
                            d.click(int(w * 0.498), int(h * 0.369)) 
                            next_clicked = True
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
                                        try: d(text="Continue").click()
                                        except: d.xpath('//*[@text="Continue" or @content-desc="Continue"]').click()
                                        log_to_otp(f"[{device_serial}] 🔄 Clicked 'Continue' (Device nearby popup)", "cyan")
                                        time.sleep(1.0)
                                except: pass

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
                        except:
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
                        except: pass
                        update_stat("otp_failed")
                        force_next_clear = True 
                        
                        device_popup_errors[device_serial] = device_popup_errors.get(device_serial, 0) + 1
                        try: iso_limit_val = int(iso_limit_combo.get())
                        except: iso_limit_val = 3
                        
                        if device_popup_errors[device_serial] >= iso_limit_val:
                            if change_proxy_iso(device_serial, proxy_pkg_entry.get().strip(), username_only=True):
                                pass
                            device_popup_errors[device_serial] = 0 
                            
                        break
                        
                    elif otp_page_found:
                        device_popup_errors[device_serial] = 0 
                        
                        log_to_otp(f"[{device_serial}] ✅✅ SUCCESS IG OTP SENT: {target} ✅✅", "green")
                        log_success(target)
                        log_to_success(target)
                        update_stat("otp_sent")
                        
                        if ig_resend_limit <= 1:
                            log_to_otp(f"[{device_serial}] ⏳ Limit is 0/1. Waiting 4s before fast clear...", "cyan")
                            time.sleep(4.0)
                            force_next_clear = True 
                            break
                        
                        for i in range(ig_resend_limit - 1): 
                            if not is_running or GLOBAL_RUN_TOKEN != current_token: break
                            log_to_otp(f"[{device_serial}] ⏳ Wait for Resend ({i+1})...", "white")
                            
                            wait_loop = 4.0
                            while wait_loop > 0 and is_running and GLOBAL_RUN_TOKEN == current_token:
                                time.sleep(0.5)
                                wait_loop -= 0.5
                                
                            if not is_running or GLOBAL_RUN_TOKEN != current_token: break
                            
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
                            if replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                d = init_uiautomator2_for_device(device_serial)
                        else:
                            log_to_otp(f"[{device_serial}] ❌ Network Too Slow / Timeout! App Clearing...", "red")
                            
                        update_stat("otp_failed")
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
                    if replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                        d = init_uiautomator2_for_device(device_serial)
            time.sleep(2)

    if GLOBAL_RUN_TOKEN != current_token:
        log_to_otp(f"[{device_serial}] 💀 Old Thread Killed Successfully", "yellow")
    else:
        log_to_otp(f"[{device_serial}] ⚠ IG Stopped", "yellow")
        
# ==========================================
# 📱 FACEBOOK AUTOMATION LOGIC
# ==========================================
def bot_logic_fb(d, device_serial, current_token):
    global is_running, device_handles, GLOBAL_RUN_TOKEN, device_fb_success_count, device_popup_errors, device_dead_proxy_errors, device_force_proxy_change
    try:
        d.implicitly_wait(1.0) 
        d.settings['operation_delay'] = (0.2, 0.2)
        device_handles.append(d)
    except: 
        return

    run_count = 0 
    force_next_clear = False 

    while is_running and GLOBAL_RUN_TOKEN == current_token:
        pkg_name = package_combo.get()
        speed_mode = speed_mode_var.get()
        custom_speed = typ_speed_entry.get()
        skip_timer = timer_var.get()
        skip_captcha = captcha_var.get()
        double_otp = double_otp_var.get()
        try: clear_interval = int(clear_interval_entry.get())
        except: clear_interval = 5
        try: page_timeout = int(page_timeout_entry.get())
        except: page_timeout = 40

        try:
            if device_force_proxy_change.get(device_serial, 0) >= 15: 
                log_to_otp(f"[{device_serial}] ❌ Background Scanner Detected Dead IP! Auto Replacing...", "red")
                if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                    continue 
                d = init_uiautomator2_for_device(device_serial)
                device_force_proxy_change[device_serial] = 0
                device_dead_proxy_errors[device_serial] = 0
                continue 

            # APP INSTALL CHECK
            try:
                app_installed = d.app_info(pkg_name) is not None
            except:
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

            # ==========================================
            # 🛡️ MESSENGER / FB IP SEC ERROR DETECTION (STARTUP)
            # ==========================================
            try:
                if d(textMatches="(?i).*page isn't available right now.*|.*technical error.*|.*try reloading this page.*|.*refresh.*").exists(timeout=2.0):
                    log_to_otp(f"[{device_serial}] ❌ 'Page isn't available' (IP Block) Detected! Clearing App...", "red")
                    force_next_clear = True
                    device_popup_errors[device_serial] = device_popup_errors.get(device_serial, 0) + 1
                    
                    try: iso_limit_val = int(iso_limit_combo.get())
                    except: iso_limit_val = 3
                    
                    if device_popup_errors[device_serial] >= iso_limit_val:
                        log_to_otp(f"[{device_serial}] ❌ IP Blocked {device_popup_errors[device_serial]} times! Replacing proxy...", "red")
                        if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                            continue
                        d = init_uiautomator2_for_device(device_serial)
                        device_popup_errors[device_serial] = 0
                    continue
            except Exception as e:
                pass
            # ==========================================

            btn_forgot = d(textMatches="(?i).*forgot.*")
            if btn_forgot.wait(timeout=25.0): 
                device_dead_proxy_errors[device_serial] = 0 
                try:
                    try:
                        if d(resourceId="com.google.android.gms:id/cancel").exists(timeout=0.5):
                            d(resourceId="com.google.android.gms:id/cancel").click()
                    except: pass
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
                try: iso_limit_val = int(iso_limit_combo.get())
                except: iso_limit_val = 3
                
                if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                    log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                    if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                        continue
                    d = init_uiautomator2_for_device(device_serial)
                    device_dead_proxy_errors[device_serial] = 0
                
                continue

            while is_running and GLOBAL_RUN_TOKEN == current_token:
                speed_mode = speed_mode_var.get()
                custom_speed = typ_speed_entry.get()
                skip_timer = timer_var.get()
                skip_captcha = captcha_var.get()
                double_otp = double_otp_var.get()

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
                        except: pass
                        type_number(d, input_box, target, speed_mode, custom_speed, force_paste_var.get()) 
                        log_to_otp(f"[{device_serial}] ✅ Typed Number", "green")
                    else:
                        log_to_otp(f"[{device_serial}] ❌ Page didn't load. Restarting...", "red")
                        valid_numbers_queue.put(target)
                        log_to_otp(f"[{device_serial}] ♻️ Number saved back to Queue", "cyan")
                        force_next_clear = True
                        
                        device_dead_proxy_errors[device_serial] = device_dead_proxy_errors.get(device_serial, 0) + 1
                        try: iso_limit_val = int(iso_limit_combo.get())
                        except: iso_limit_val = 3
                        if device_dead_proxy_errors[device_serial] >= iso_limit_val:
                            log_to_otp(f"[{device_serial}] ❌ Dead IP Detected (MB Finished)! Replacing proxy...", "red")
                            if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                break
                            d = init_uiautomator2_for_device(device_serial)
                            device_dead_proxy_errors[device_serial] = 0
                        break 

                    smart_delay(speed_mode)
                    
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
                        update_stat("otp_failed")
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
                            except:
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
                                if not is_running or GLOBAL_RUN_TOKEN != current_token: break
                                
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
                                    target_y = (t+b)//2
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
                                    update_stat("otp_sent")
                                    flow_success = True
                                    
                                    fb_limit_val = fb_success_iso_combo.get()
                                    if fb_limit_val != "Never":
                                        try: limit_int = int(fb_limit_val)
                                        except: limit_int = 99999
                                        if device_fb_success_count[device_serial] >= limit_int:
                                            log_to_otp(f"[{device_serial}] 🔄 Target Success Reached ({limit_int}). Auto Changing ISO...", "cyan")
                                            change_proxy_iso(device_serial, proxy_pkg_entry.get().strip(), username_only=True)
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
                                        except: pass
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
                                human_click(d, d.window_size()[0]//2, int(d.window_size()[1]*0.35))
                            time.sleep(1.0) 
                            steps_taken += 1
                            continue

                        elif page_state == "not_found":
                            log_to_otp(f"[{device_serial}] ❌ Error or Not Found", "red")
                            if d(textMatches="(?i)try again").exists: 
                                d(textMatches="(?i)try again").click()
                                update_stat("otp_failed")
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
                                    except: pass
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
                            
                            try: iso_limit_val = int(iso_limit_combo.get())
                            except: iso_limit_val = 3
                            
                            if device_popup_errors[device_serial] >= iso_limit_val:
                                log_to_otp(f"[{device_serial}] ❌ IP Blocked {device_popup_errors[device_serial]} times! Replacing proxy...", "red")
                                if not replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                    action_after_scan = "restart_app"
                                    break
                                d = init_uiautomator2_for_device(device_serial)
                                device_popup_errors[device_serial] = 0
                            action_after_scan = "restart_app"
                            break

                        else: 
                            if not check_internet_connection(device_serial):
                                if replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                                    d = init_uiautomator2_for_device(device_serial)
                            else:
                                log_to_otp(f"[{device_serial}] ❌ Timeout/Stuck", "red")
                                
                            action_after_scan = "restart_app"
                            break

                    if not flow_success and action_after_scan == "restart_app":
                        update_stat("otp_failed")

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
                    if replace_dead_proxy(device_serial, proxy_pkg_entry.get().strip()):
                        d = init_uiautomator2_for_device(device_serial)
            time.sleep(2)

    if GLOBAL_RUN_TOKEN != current_token:
        log_to_otp(f"[{device_serial}] 💀 FB Old Thread Killed", "yellow")
    else:
        log_to_otp(f"[{device_serial}] ⚠ FB Stopped", "yellow")

# ==========================================
# 🌐 IP / PROXY AUTOMATION LOGIC
# ==========================================
def configure_super_proxy(serial, proxy_string, country_code, pkg_name):
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    try:
        log_to_otp(f"[{serial}] ⚙ Initiating Proxy Setup...", "cyan")
        
        with DAEMON_LOCK:
            subprocess.run([adb_cmd, "-s", serial, "shell", "am", "force-stop", pkg_name], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=5)
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
            log_to_otp(f"[{serial}] ❌ Invalid proxy format", "red")
            return False

        d = u2.connect(serial)
        w, h = d.window_size()
        
        d.app_start(pkg_name)
        time.sleep(4.0)

        if d(descriptionMatches="(?i)stop").exists(timeout=2.0) or d(textMatches="(?i)stop").exists():
            log_to_otp(f"[{serial}] ℹ️ Proxy was running. Stopping it to apply new IP...", "yellow")
            try:
                if d(descriptionMatches="(?i)stop").exists():
                    d(descriptionMatches="(?i)stop").click()
                else:
                    d(textMatches="(?i)stop").click()
            except: pass
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
            log_to_otp(f"[{serial}] ❌ SuperProxy UI Error: Dead or Invalid Auth!", "red")
            return False

        if d(descriptionMatches="(?i)stop").exists(timeout=3.0) or d(textMatches="(?i)stop").exists():
            log_to_otp(f"[{serial}] ✅ Proxy Connected! (Stop verified) ({host})", "green")
            try:
                if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                    d(textMatches="(?i)(ok|allow|accept)").click()
                    time.sleep(1.0)
            except:
                pass 
            return True

        try:
            if d(textMatches="(?i)(ok|allow|accept)").exists(timeout=2):
                d(textMatches="(?i)(ok|allow|accept)").click()
                time.sleep(1.0)
        except:
            pass 
            
        log_to_otp(f"[{serial}] ✅ Proxy Connected! ({host})", "green")
        time.sleep(2.0)
        return True

    except Exception as e:
        log_to_otp(f"[{serial}] ❌ Proxy Setup Error: {str(e)[:40]}", "red")
        try:
            subprocess.run([adb_cmd, "disconnect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
            time.sleep(1)
            subprocess.run([adb_cmd, "connect", serial], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=3)
        except: pass
        return False

def proxy_logic_wrapper(serial, country_code, pkg_name, delay_sec):
    global is_running, GLOBAL_PROXIES, device_current_proxy
    wait_time = delay_sec
    while wait_time > 0 and is_running:
        time.sleep(0.5)
        wait_time -= 0.5
        
    if not is_running: return

    while is_running:
        log_to_otp(f"[{serial}] 🔍 Finding a LIVE proxy from list...", "white")
        valid_proxy = None
        
        while is_running:
            with PROXY_LOCK:
                if not GLOBAL_PROXIES:
                    log_to_otp(f"[{serial}] ❌ Proxy list empty!", "red")
                    return
                candidate = GLOBAL_PROXIES.pop(0)
            
            if check_proxy_live(candidate):
                valid_proxy = candidate
                break
            else:
                log_to_otp(f"[{serial}] 💀 Skipping dead proxy...", "yellow")

        if not is_running or not valid_proxy:
            return

        device_current_proxy[serial] = valid_proxy
        setup_success = configure_super_proxy(serial, valid_proxy, country_code, pkg_name)
        if setup_success:
            return 
        else:
            log_to_otp(f"[{serial}] ♻️ Setup failed (UI Error). Trying next proxy...", "yellow")

def monitor_proxy_threads(threads):
    global is_running
    for t in threads: 
        t.join()
    log_to_otp("✅ All Proxy setups completed.", "green")
    is_running = False
    
    app.after(1000, lambda: threading.Thread(target=refresh_adb, daemon=True).start())
    app.after(1000, update_ui_state)

def load_proxy_txt():
    filepath = filedialog.askopenfilename(title="Select Proxies List", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        proxy_textbox.delete("1.0", "end")
        proxy_textbox.insert("1.0", "\n".join(lines))
        log_to_otp(f"📂 Loaded {len(lines)} Proxies for setup.", "cyan")
        save_all() 

def clear_proxy_txt():
    global GLOBAL_PROXIES, device_current_proxy
    proxy_textbox.delete("1.0", "end")
    GLOBAL_PROXIES.clear()
    device_current_proxy.clear()
    log_to_otp("🗑️ Proxy list and memory cleared.", "yellow")
    save_all() 

def start_proxy_setup():
    global is_running, GLOBAL_RUN_TOKEN, GLOBAL_PROXIES, device_current_proxy, device_popup_errors, device_dead_proxy_errors
    
    selected_devices = [serial for serial, var in device_checkboxes_vars.items() if var.get()]
    
    if not selected_devices: 
        log_to_otp("❌ No devices selected from the list!", "red")
        return

    proxy_text = proxy_textbox.get("1.0", "end").strip()
    if not proxy_text: 
        log_to_otp("❌ Please paste or load proxies in the text box!", "red")
        return

    proxies = [p.strip() for p in proxy_text.split('\n') if p.strip()]
    GLOBAL_PROXIES = proxies.copy()
    
    country_code = proxy_country_entry.get().strip()
    pkg_name = proxy_pkg_entry.get().strip()

    GLOBAL_RUN_TOKEN += 1 
    is_running = True
    update_ui_state() 
    save_all()

    threads = []
    for idx, serial in enumerate(selected_devices):
        device_popup_errors[serial] = 0
        device_dead_proxy_errors[serial] = 0
        
        delay = idx * 6.0 
        t = threading.Thread(target=proxy_logic_wrapper, args=(serial, country_code, pkg_name, delay), daemon=True)
        threads.append(t)
        t.start()
        
    threading.Thread(target=monitor_proxy_threads, args=(threads,), daemon=True).start()

# ==========================================
# 🖥 UI CODE & APP LAUNCHER
# ==========================================
ctk.set_appearance_mode("dark")
app = ctk.CTk()

myappid = 'zenex.adb.automations.1.0'
try: 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: 
    pass

app.geometry("850x880")
app.title(APP_TITLE)

icon_path = resource_path("logo.ico")
if os.path.exists(icon_path):
    try: 
        app.iconbitmap(icon_path)
    except: 
        pass

proxy_iso_list_var = ctk.StringVar(value="US, GB, CA, AU, DE, FR")

server_data = check_cloud_status()
if server_data.get("valid") and server_data.get("status") == "ACTIVE":
    EXPIRY_DATE = server_data.get("expiry")
    LICENSED_USER = server_data.get("name", "User")
else:
    is_valid, EXPIRY_DATE, LICENSED_USER = show_license_window()
    if not is_valid: 
        sys.exit()

def get_time(): 
    return datetime.now().strftime("[%H:%M:%S]")

def log_to_filter(msg, color="white"):
    msg = format_emu_name(msg) # LOG FIX
    def update():
        filter_term.configure(state="normal")
        filter_term.insert("end", f"{get_time()} {msg}\n", color)
        filter_term.see("end")
        filter_term.configure(state="disabled")
    app.after(0, update)

def log_to_otp(msg, color="white"):
    msg = format_emu_name(msg) # LOG FIX
    def update():
        otp_term.configure(state="normal")
        if any(x in msg for x in ["🎯", "=", "✔️", "⚙", "✅", "🔋", "💀", "🔄", "♻️", "🗑️"]): 
            otp_term.insert("end", f"{msg}\n", color)
        else: 
            otp_term.insert("end", f"{get_time()} {msg}\n", color)
        otp_term.see("end")
        otp_term.configure(state="disabled")
    app.after(0, update)

def log_to_success(number):
    def update():
        success_term.configure(state="normal")
        success_term.insert("end", f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {number}\n", "green")
        success_term.see("end")
        success_term.configure(state="disabled")
    app.after(0, update)

def clear_logs():
    def clear_ui():
        filter_term.configure(state="normal")
        filter_term.delete("1.0", "end")
        filter_term.configure(state="disabled")
        
        otp_term.configure(state="normal")
        otp_term.delete("1.0", "end")
        otp_term.configure(state="disabled")
    app.after(0, clear_ui)
    
    def clear_worker():
        global device_handles
        pkg = package_combo.get()
        for d in device_handles:
            try: 
                d.app_clear(pkg)
                d.press("home")
                log_to_otp(f"✅ App Cleared on {d.serial}", "green")
            except: 
                pass
        threading.Thread(target=background_startup_check, daemon=True).start()
    threading.Thread(target=clear_worker, daemon=True).start()

def refresh_adb():
    log_to_otp("🔄 Resetting ADB Server (Fixing Proxy Drop)...", "yellow")
    adb_cmd = ADB_PATH if os.path.exists(ADB_PATH) else "adb"
    
    with DAEMON_LOCK:
        try:
            force_kill_adb()
            subprocess.run([adb_cmd, "start-server"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=5)
            time.sleep(2)
            
            ports = ["5554", "5555", "5556", "5557", "21503", "21513", "62001", "62025"]
            for p in ports:
                try: subprocess.run([adb_cmd, "connect", f"127.0.0.1:{p}"], capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=1)
                except: pass
        except: 
            pass
        
    devices = get_connected_devices()
    if devices: 
        log_to_otp(f"✔️ ✓ Detected {len(devices)} devices", "green")
    else: 
        log_to_otp("❌ No devices found", "red")
        
    threading.Thread(target=populate_proxy_devices_worker, daemon=True).start()
    threading.Thread(target=background_startup_check, daemon=True).start()

def update_stats_ui():
    lbl_checked.configure(text=str(stats['checked']))
    lbl_valid.configure(text=str(stats['valid']))
    lbl_queue.configure(text=str(valid_numbers_queue.qsize()))
    lbl_otp_sent.configure(text=str(stats['otp_sent']))
    lbl_otp_failed.configure(text=str(stats['otp_failed']))

def save_all():
    data = {
        "panel": CURRENT_PANEL, 
        "api_key": CURRENT_API_KEY, 
        "range": CURRENT_RANGE, 
        "package": package_combo.get(), 
        "speed_mode": speed_mode_var.get(), 
        "action_delay": action_delay_entry.get(),
        "clear_interval": clear_interval_entry.get(),
        "typ_speed": typ_speed_entry.get(), 
        "force_paste": force_paste_var.get(),
        "page_timeout": page_timeout_entry.get(),
        "use_filter": filter_var.get(), 
        "skip_timer": timer_var.get(), 
        "skip_captcha": captcha_var.get(), 
        "double_otp": double_otp_var.get(), 
        "platform": platform_var.get(), 
        "ig_resend": ig_resend_combo.get(),
        "iso_limit": iso_limit_combo.get(),
        "fb_success_iso": fb_success_iso_combo.get(), 
        "iso_list": proxy_iso_list_var.get(),
        "data_source": data_source_combo.get(), 
        "proxy_pkg": proxy_pkg_entry.get(),
        "proxy_list": proxy_textbox.get("1.0", "end").strip(),
        "device_current_proxy": device_current_proxy
    }
    with open(CONFIG_FILE, "w") as f: 
        json.dump(data, f)

def load_configs():
    global CURRENT_PANEL, CURRENT_API_KEY, CURRENT_RANGE, device_current_proxy
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                CURRENT_PANEL = data.get("panel", "ZENEX NETWORK")
                CURRENT_API_KEY = data.get("api_key", "")
                CURRENT_RANGE = data.get("range", "")
                lbl_current_range.configure(text=f"{CURRENT_PANEL} | {CURRENT_RANGE}")
                
                p_val = data.get("platform", "Facebook")
                platform_var.set(p_val)
                saved_pkg = data.get("package", "com.facebook.lite")
                
                change_platform(p_val)
                
                if p_val != "IP Setup": 
                    package_combo.set(saved_pkg) 
                
                speed_mode_var.set(data.get("speed_mode", "Normal"))
                
                action_delay_entry.delete(0, "end")
                action_delay_entry.insert(0, data.get("action_delay", "1.0"))

                clear_interval_entry.delete(0, "end")
                clear_interval_entry.insert(0, data.get("clear_interval", "5"))
                
                typ_speed_entry.delete(0, "end")
                typ_speed_entry.insert(0, data.get("typ_speed", "0.08"))

                force_paste_var.set(data.get("force_paste", False)) 
                
                page_timeout_entry.delete(0, "end")
                page_timeout_entry.insert(0, data.get("page_timeout", "40"))
                
                filter_var.set(data.get("use_filter", True))
                timer_var.set(data.get("skip_timer", True))
                captcha_var.set(data.get("skip_captcha", True))
                double_otp_var.set(data.get("double_otp", False))
                
                ig_resend_combo.set(data.get("ig_resend", "3"))
                iso_limit_combo.set(data.get("iso_limit", "3"))
                fb_success_iso_combo.set(data.get("fb_success_iso", "Never")) 
                proxy_iso_list_var.set(data.get("iso_list", "US, GB, CA, AU, DE, FR"))
                
                data_source_combo.set(data.get("data_source", "API (Zenex)"))
                
                proxy_pkg_entry.delete(0, "end")
                proxy_pkg_entry.insert(0, data.get("proxy_pkg", "com.scheler.superproxy"))
                
                p_list = data.get("proxy_list", "")
                if p_list:
                    proxy_textbox.delete("1.0", "end")
                    proxy_textbox.insert("1.0", p_list)
                    
                device_current_proxy.clear()
                device_current_proxy.update(data.get("device_current_proxy", {}))
                
        except Exception as e:
            try:
                os.remove(CONFIG_FILE)
            except:
                pass

def on_speed_mode_change(choice):
    action_delay_entry.delete(0, "end")
    if choice == "Fastest": 
        action_delay_entry.insert(0, "0.3")
    elif choice == "Normal": 
        action_delay_entry.insert(0, "1.0") 
    elif choice == "Human": 
        action_delay_entry.insert(0, "1.5")

def open_api():
    popup = ctk.CTkToplevel(app)
    popup.geometry("450x320")
    popup.title("API Setup")
    popup.attributes("-topmost", True)
    
    ctk.CTkLabel(popup, text="📡 API & RANGE SETUP", font=("Consolas", 16, "bold"), text_color="#3498DB").pack(pady=15)
    
    panel_combo = ctk.CTkComboBox(popup, values=["ZENEX NETWORK"], width=350)
    panel_combo.set(CURRENT_PANEL)
    panel_combo.pack(padx=20, pady=5)
    
    ctk.CTkLabel(popup, text="API KEY:", font=("Consolas", 10)).pack(anchor="w", padx=50)
    api_inp = ctk.CTkEntry(popup, width=350, show="*")
    api_inp.insert(0, CURRENT_API_KEY)
    api_inp.pack(padx=20, pady=2)
    
    ctk.CTkLabel(popup, text="RANGE (Live Update):", font=("Consolas", 10)).pack(anchor="w", padx=50)
    range_inp = ctk.CTkEntry(popup, width=350)
    range_inp.insert(0, CURRENT_RANGE)
    range_inp.pack(padx=20, pady=2)
    
    def save():
        global CURRENT_PANEL, CURRENT_API_KEY, CURRENT_RANGE
        CURRENT_PANEL = panel_combo.get()
        CURRENT_API_KEY = api_inp.get()
        CURRENT_RANGE = range_inp.get()
        
        lbl_current_range.configure(text=f"{CURRENT_PANEL} | {CURRENT_RANGE}")
        save_all()
        
        with valid_numbers_queue.mutex:
            valid_numbers_queue.queue.clear()
        
        if is_running:
            log_to_filter(f"🔄 Range Updated to: {CURRENT_RANGE}. Old queue wiped!", "yellow")
            log_to_otp(f"🔄 Live Range Changed to: {CURRENT_RANGE}. Fetching new numbers...", "yellow")
            
        popup.destroy()
        
    ctk.CTkButton(popup, text="SAVE CONFIG", command=save, fg_color="#3498DB").pack(pady=15)

def load_txt_file():
    filepath = filedialog.askopenfilename(title="Select Numbers List", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f: 
            lines = [line.strip() for line in f if line.strip()]
            
        with txt_numbers_queue.mutex:
            txt_numbers_queue.queue.clear()
            
        with valid_numbers_queue.mutex:
            valid_numbers_queue.queue.clear()
            
        for num in lines: 
            txt_numbers_queue.put(num)
            
        lbl_txt_count.configure(text=f"TXT Queue: {len(lines)}")
        log_to_filter(f"📂 Successfully loaded {len(lines)} numbers. Old queue wiped!", "cyan")

def start_bot():
    global is_running, device_handles, GLOBAL_RUN_TOKEN, device_fb_success_count, device_popup_errors, device_dead_proxy_errors, device_force_proxy_change, device_stopped_status, GLOBAL_PROXIES
    save_all()
    
    proxy_text = proxy_textbox.get("1.0", "end").strip()
    if proxy_text and not GLOBAL_PROXIES:
        GLOBAL_PROXIES = [p.strip() for p in proxy_text.split('\n') if p.strip()]
    
    data_source = data_source_combo.get()
    if data_source == "API (Zenex)":
        if not CURRENT_API_KEY or not CURRENT_RANGE: 
            log_to_otp("❌ Setup API & Range first", "red")
            return
    else:
        if txt_numbers_queue.empty(): 
            log_to_otp("❌ Please Load a TXT file first!", "red")
            return

    devices = get_connected_devices()
    if not devices: 
        log_to_otp("❌ No devices found!", "red")
        return

    GLOBAL_RUN_TOKEN += 1 
    current_token = GLOBAL_RUN_TOKEN

    is_running = True
    update_ui_state()
    device_handles = []
    
    for serial in devices:
        device_fb_success_count[serial] = 0
        device_popup_errors[serial] = 0
        device_dead_proxy_errors[serial] = 0
        device_force_proxy_change[serial] = 0
        device_stopped_status[serial] = False 
    
    platform = platform_var.get()
    
    threading.Thread(target=number_harvester_thread, args=(None, platform, current_token, data_source), daemon=True).start()

    for index, serial in enumerate(devices): 
        delay = index * 4 
        threading.Thread(target=bot_logic_wrapper, args=(serial, current_token, platform, delay), daemon=True).start()

def stop_bot():
    global is_running
    is_running = False
    update_ui_state()
    log_to_otp("⚠ Stopping...", "yellow")

def update_ui_state():
    if is_running: 
        btn_start.configure(state="disabled", fg_color="#1F618D")
        btn_stop.configure(state="normal", fg_color="#C0392B")
        btn_start_proxy.configure(state="disabled", fg_color="#1F618D")
        btn_stop_proxy.configure(state="normal", fg_color="#C0392B")
    else: 
        btn_start.configure(state="normal", fg_color="#2980B9")
        btn_stop.configure(state="disabled", fg_color="#641E16")
        btn_start_proxy.configure(state="normal", fg_color="#27AE60")
        btn_stop_proxy.configure(state="disabled", fg_color="#641E16")

def populate_proxy_devices_worker():
    devices = get_connected_devices()
    def update_ui():
        global device_checkboxes_vars, device_checkbox_widgets
        for widget in device_scroll_frame.winfo_children():
            widget.destroy()
            
        device_checkboxes_vars.clear()
        device_checkbox_widgets.clear() 
        
        if not devices:
            ctk.CTkLabel(device_scroll_frame, text="No devices found", text_color="red").pack(pady=5)
            return
            
        for serial in devices:
            var = ctk.BooleanVar(value=True) 
            clean_name = format_emu_name(serial)
            chk = ctk.CTkCheckBox(device_scroll_frame, text=f"📱 {clean_name}", variable=var, fg_color="#27AE60")
            chk.pack(anchor="w", padx=10, pady=2)
            device_checkboxes_vars[serial] = var
            device_checkbox_widgets[serial] = chk 
    app.after(0, update_ui)

def populate_proxy_devices():
    threading.Thread(target=populate_proxy_devices_worker, daemon=True).start()

def change_platform(choice):
    if choice == "IP Setup":
        main_config_frame.pack_forget()
        proxy_config_frame.pack(fill="both", expand=True)
        populate_proxy_devices() 
    else:
        proxy_config_frame.pack_forget()
        main_config_frame.pack(fill="both", expand=True)
        if choice == "Facebook":
            package_combo.configure(values=FB_PACKAGES)
            if package_combo.get() not in FB_PACKAGES: 
                package_combo.set(FB_PACKAGES[0])
        elif choice == "Instagram":
            package_combo.configure(values=IG_PACKAGES)
            if package_combo.get() not in IG_PACKAGES: 
                package_combo.set(IG_PACKAGES[0])

# ==========================================
# ✅ UI DESIGN
# ==========================================
license_frame = ctk.CTkFrame(app, fg_color="#0D1B2A", corner_radius=0, height=30)
license_frame.pack(fill="x")

ctk.CTkLabel(license_frame, text=f"LICENSE: Active | Expiry: {EXPIRY_DATE} | User: {LICENSED_USER}", font=("Consolas", 12, "bold"), text_color="#3498DB").pack(pady=2)

header_frame = ctk.CTkFrame(app, fg_color="#0a0a0a", corner_radius=0, height=50)
header_frame.pack(fill="x")

ctk.CTkLabel(header_frame, text=HEADER_TEXT, font=("Consolas", 20, "bold"), text_color="#00FFCC").pack(side="left", padx=20, pady=10)

main_container = ctk.CTkFrame(app, fg_color="transparent")
main_container.pack(fill="both", expand=True, padx=10, pady=5)

sidebar = ctk.CTkFrame(main_container, width=280, corner_radius=5, fg_color="#121212")
sidebar.pack(side="left", fill="y", padx=(0, 10))
sidebar.pack_propagate(False)

platform_var = ctk.StringVar(value="Facebook")
platform_seg = ctk.CTkSegmentedButton(sidebar, values=["Facebook", "Instagram", "IP Setup"], variable=platform_var, selected_color="#E1306C", command=change_platform)
platform_seg.pack(padx=15, pady=(10, 2), fill="x")

dynamic_container = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
dynamic_container.pack(fill="both", expand=True)

main_config_frame = ctk.CTkFrame(dynamic_container, fg_color="transparent")
proxy_config_frame = ctk.CTkFrame(dynamic_container, fg_color="transparent")

# 🔹 VIEW 1: FB & IG
ctk.CTkLabel(main_config_frame, text="Configuration", font=("Consolas", 13, "bold"), text_color="#3498DB").pack(pady=2)

ctk.CTkLabel(main_config_frame, text="Data Source:", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
data_source_combo = ctk.CTkComboBox(main_config_frame, values=["API (Zenex)", "Bulk TXT File"], fg_color="#1e1e1e")
data_source_combo.pack(padx=15, pady=1, fill="x")

btn_source_frame = ctk.CTkFrame(main_config_frame, fg_color="transparent")
btn_source_frame.pack(pady=2, padx=15, fill="x")

btn_api = ctk.CTkButton(btn_source_frame, text="🌐 Setup API", command=open_api, fg_color="#8E44AD", font=("Consolas", 10, "bold"), width=110, height=25)
btn_api.pack(side="left", padx=(0, 5))

btn_txt = ctk.CTkButton(btn_source_frame, text="📂 Load TXT", command=load_txt_file, fg_color="#2E86C1", font=("Consolas", 10, "bold"), width=110, height=25)
btn_txt.pack(side="right")

lbl_current_range = ctk.CTkLabel(main_config_frame, text="Range: None", font=("Consolas", 10), text_color="#F4D03F")
lbl_current_range.pack(pady=0)

lbl_txt_count = ctk.CTkLabel(main_config_frame, text="TXT Queue: 0", font=("Consolas", 10), text_color="#2ECC71")
lbl_txt_count.pack(pady=0)

ctk.CTkLabel(main_config_frame, text="App Package:", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
package_combo = ctk.CTkComboBox(main_config_frame, values=FB_PACKAGES, fg_color="#1e1e1e")
package_combo.pack(padx=15, pady=1, fill="x")

ctk.CTkLabel(main_config_frame, text="Bot Speed Mode (Fastest = Copy/Paste):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
speed_mode_var = ctk.StringVar(value="Normal")
speed_seg = ctk.CTkSegmentedButton(main_config_frame, values=["Fastest", "Normal", "Human"], variable=speed_mode_var, command=on_speed_mode_change, selected_color="#3498DB")
speed_seg.pack(padx=15, pady=1, fill="x")

delay_clear_frame = ctk.CTkFrame(main_config_frame, fg_color="transparent")
delay_clear_frame.pack(fill="x", padx=15, pady=(2,0))

delay_frame = ctk.CTkFrame(delay_clear_frame, fg_color="transparent")
delay_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
ctk.CTkLabel(delay_frame, text="Action Delay (Secs):", font=("Consolas", 10)).pack(anchor="w")
action_delay_entry = ctk.CTkEntry(delay_frame, fg_color="#1e1e1e", height=25)
action_delay_entry.insert(0, "1.0")
action_delay_entry.pack(fill="x")

clear_frame = ctk.CTkFrame(delay_clear_frame, fg_color="transparent")
clear_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
ctk.CTkLabel(clear_frame, text="Clear App After (Runs):", font=("Consolas", 10)).pack(anchor="w")
clear_interval_entry = ctk.CTkEntry(clear_frame, fg_color="#1e1e1e", height=25)
clear_interval_entry.insert(0, "5")
clear_interval_entry.pack(fill="x")

ctk.CTkLabel(main_config_frame, text="Custom Type Speed:", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))

typ_speed_frame = ctk.CTkFrame(main_config_frame, fg_color="transparent")
typ_speed_frame.pack(padx=15, pady=1, fill="x")

typ_speed_entry = ctk.CTkEntry(typ_speed_frame, fg_color="#1e1e1e", height=25, width=120)
typ_speed_entry.pack(side="left")

force_paste_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(typ_speed_frame, text="Force Copy/Paste", variable=force_paste_var, fg_color="#3498DB", checkbox_width=18, checkbox_height=18, font=("Consolas", 10)).pack(side="left", padx=10)

ctk.CTkLabel(main_config_frame, text="Page Load Timeout (Secs):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
page_timeout_entry = ctk.CTkEntry(main_config_frame, fg_color="#1e1e1e", height=25)
page_timeout_entry.pack(padx=15, pady=1, fill="x")
page_timeout_entry.insert(0, "40")

filter_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(main_config_frame, text="Enable Number Filter", variable=filter_var, fg_color="#3498DB", checkbox_width=18, checkbox_height=18).pack(anchor="w", padx=15, pady=1)

timer_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(main_config_frame, text="Skip SMS Timer", variable=timer_var, fg_color="#3498DB", checkbox_width=18, checkbox_height=18).pack(anchor="w", padx=15, pady=1)

captcha_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(main_config_frame, text="Skip Captcha Process", variable=captcha_var, fg_color="#3498DB", checkbox_width=18, checkbox_height=18).pack(anchor="w", padx=15, pady=1)

double_otp_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(main_config_frame, text="Request FB Double OTP", variable=double_otp_var, fg_color="#2ECC71", checkbox_width=18, checkbox_height=18).pack(anchor="w", padx=15, pady=1)

ctk.CTkLabel(main_config_frame, text="IG Resend Times (0 for instant clear):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
ig_resend_combo = ctk.CTkComboBox(main_config_frame, values=["0", "1", "2", "3", "4", "5"], fg_color="#1e1e1e", height=25)
ig_resend_combo.pack(padx=15, pady=1, fill="x")
ig_resend_combo.set("3")

ctk.CTkLabel(main_config_frame, text="Block Popup Limit (Change ISO):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
iso_limit_combo = ctk.CTkComboBox(main_config_frame, values=["1", "2", "3", "4", "5", "6"], fg_color="#1e1e1e", height=25)
iso_limit_combo.pack(padx=15, pady=1, fill="x")
iso_limit_combo.set("3")

ctk.CTkLabel(main_config_frame, text="Change ISO after FB Success (Target):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(2,0))
fb_success_iso_combo = ctk.CTkComboBox(main_config_frame, values=["Never", "1", "2", "3", "5", "10", "15", "20"], fg_color="#1e1e1e", height=25)
fb_success_iso_combo.pack(padx=15, pady=1, fill="x")
fb_success_iso_combo.set("Never")

btn_frame = ctk.CTkFrame(main_config_frame, fg_color="transparent")
btn_frame.pack(pady=5, fill="x")

btn_start = ctk.CTkButton(btn_frame, text="▶ START", command=start_bot, fg_color="#2980B9", width=115, height=30, font=("Consolas", 11, "bold"))
btn_start.grid(row=0, column=0, padx=5, pady=2)

btn_stop = ctk.CTkButton(btn_frame, text="⏹ STOP", command=stop_bot, fg_color="#C0392B", state="disabled", width=115, height=30, font=("Consolas", 11, "bold"))
btn_stop.grid(row=0, column=1, padx=5, pady=2)

btn_clear = ctk.CTkButton(btn_frame, text="🗑 CLEAR", command=lambda: threading.Thread(target=clear_logs, daemon=True).start(), fg_color="#7F8C8D", width=115, height=30, font=("Consolas", 11, "bold"))
btn_clear.grid(row=1, column=0, padx=5, pady=2)

btn_refresh = ctk.CTkButton(btn_frame, text="🔄 REFRESH", command=lambda: threading.Thread(target=refresh_adb, daemon=True).start(), fg_color="#D68910", text_color="black", width=115, height=30, font=("Consolas", 11, "bold"))
btn_refresh.grid(row=1, column=1, padx=5, pady=2)

# 🔹 VIEW 2: PROXY SETUP
ctk.CTkLabel(proxy_config_frame, text="PROXY CONFIGURATION", font=("Consolas", 13, "bold"), text_color="#27AE60").pack(pady=(5, 5))

ctk.CTkLabel(proxy_config_frame, text="Select Devices to Setup:", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(0, 2))
device_scroll_frame = ctk.CTkScrollableFrame(proxy_config_frame, height=80, fg_color="#1e1e1e")
device_scroll_frame.pack(padx=15, pady=2, fill="x")
ctk.CTkButton(proxy_config_frame, text="🔄 Refresh Device List", command=lambda: threading.Thread(target=populate_proxy_devices_worker, daemon=True).start(), fg_color="#7F8C8D", height=20, font=("Consolas", 10)).pack(pady=(2, 10))

ctk.CTkLabel(proxy_config_frame, text="Proxy App Package Name:", font=("Consolas", 10)).pack(anchor="w", padx=15)
proxy_pkg_entry = ctk.CTkEntry(proxy_config_frame, fg_color="#1e1e1e", height=25)
proxy_pkg_entry.insert(0, "com.scheler.superproxy")
proxy_pkg_entry.pack(padx=15, pady=2, fill="x")

ctk.CTkLabel(proxy_config_frame, text="Country ISO Code (Optional):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(5,0))
proxy_country_entry = ctk.CTkEntry(proxy_config_frame, fg_color="#1e1e1e", height=25, placeholder_text="e.g. US, UK")
proxy_country_entry.pack(padx=15, pady=2, fill="x")

ctk.CTkLabel(proxy_config_frame, text="Custom ISO List (Comma separated):", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(5,0))
proxy_iso_list_entry = ctk.CTkEntry(proxy_config_frame, fg_color="#1e1e1e", height=25, textvariable=proxy_iso_list_var)
proxy_iso_list_entry.pack(padx=15, pady=2, fill="x")

ctk.CTkLabel(proxy_config_frame, text="Paste Proxies or Load TXT File:", font=("Consolas", 10)).pack(anchor="w", padx=15, pady=(5,0))

proxy_btn_top_frame = ctk.CTkFrame(proxy_config_frame, fg_color="transparent")
proxy_btn_top_frame.pack(padx=15, pady=(0, 2), fill="x")

ctk.CTkButton(proxy_btn_top_frame, text="📄 LOAD TXT", command=load_proxy_txt, fg_color="#8E44AD", hover_color="#9B59B6", height=25, font=("Consolas", 10, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 5))
ctk.CTkButton(proxy_btn_top_frame, text="🗑 CLEAR", command=clear_proxy_txt, fg_color="#C0392B", hover_color="#922B21", height=25, font=("Consolas", 10, "bold")).pack(side="right", expand=True, fill="x", padx=(5, 0))

proxy_textbox = ctk.CTkTextbox(proxy_config_frame, fg_color="#1e1e1e", height=150, font=("Consolas", 10))
proxy_textbox.pack(padx=15, pady=2, fill="both", expand=True)

proxy_btn_frame = ctk.CTkFrame(proxy_config_frame, fg_color="transparent")
proxy_btn_frame.pack(pady=10, fill="x")

btn_start_proxy = ctk.CTkButton(proxy_btn_frame, text="▶ SETUP PROXIES", command=start_proxy_setup, fg_color="#27AE60", width=115, height=30, font=("Consolas", 11, "bold"))
btn_start_proxy.grid(row=0, column=0, padx=(15, 5), pady=2)

btn_stop_proxy = ctk.CTkButton(proxy_btn_frame, text="⏹ STOP", command=stop_bot, fg_color="#C0392B", state="disabled", width=115, height=30, font=("Consolas", 11, "bold"))
btn_stop_proxy.grid(row=0, column=1, padx=5, pady=2)

main_config_frame.pack(fill="both", expand=True)

# ----------------------------------------------------
# 🔹 STATS AND LOG CONSOLE
# ----------------------------------------------------
right_area = ctk.CTkFrame(main_container, fg_color="transparent")
right_area.pack(side="right", fill="both", expand=True)

stats_container = ctk.CTkFrame(right_area, fg_color="transparent")
stats_container.pack(fill="x", pady=(0, 10))

def create_stat_card(parent, title, color):
    card = ctk.CTkFrame(parent, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color=color)
    card.pack(side="left", fill="x", expand=True, padx=3)
    
    ctk.CTkLabel(card, text=title, font=("Consolas", 10, "bold"), text_color="#A9CCE3").pack(pady=(5,0))
    
    lbl_val = ctk.CTkLabel(card, text="0", font=("Consolas", 18, "bold"), text_color=color)
    lbl_val.pack(pady=(0,5))
    
    return lbl_val

lbl_checked = create_stat_card(stats_container, "TOTAL", "#3498DB")
lbl_valid = create_stat_card(stats_container, "VALID", "#F1C40F")
lbl_queue = create_stat_card(stats_container, "QUEUE", "#9B59B6")
lbl_otp_sent = create_stat_card(stats_container, "SENT", "#2ECC71")
lbl_otp_failed = create_stat_card(stats_container, "FAILED", "#E74C3C")

ctk.CTkLabel(right_area, text="LIVE CONSOLE", font=("Courier custom", 13, "bold"), text_color="#00FF00").pack(anchor="w", padx=5)

tabview = ctk.CTkTabview(right_area, fg_color="#121212", segmented_button_fg_color="#0a0a0a", segmented_button_selected_color="#3498DB")
tabview.pack(fill="both", expand=True)

tab_otp = tabview.add("Execution")
tab_filter = tabview.add("Filter")
tab_success = tabview.add("Success")

otp_term = ctk.CTkTextbox(tab_otp, state="disabled", fg_color="#000000", font=("Courier New", 11, "bold"))
otp_term.pack(fill="both", expand=True, padx=5, pady=5)

filter_term = ctk.CTkTextbox(tab_filter, state="disabled", fg_color="#000000", font=("Courier New", 11, "bold"))
filter_term.pack(fill="both", expand=True, padx=5, pady=5)

success_term = ctk.CTkTextbox(tab_success, state="disabled", fg_color="#000000", font=("Courier New", 11, "bold"))
success_term.pack(fill="both", expand=True, padx=5, pady=5)

for term in [filter_term, otp_term, success_term]:
    term.tag_config("green", foreground="#00FF00")
    term.tag_config("red", foreground="#FF4C4C")
    term.tag_config("yellow", foreground="#FFFF00")
    term.tag_config("white", foreground="#FFFFFF")
    term.tag_config("cyan", foreground="#00FFFF")

footer = ctk.CTkButton(app, text=FOOTER_TEXT, fg_color="transparent", text_color="#3498DB", hover_color="#121212", font=("Consolas", 10, "underline"), height=20, command=lambda: webbrowser.open_new(TELEGRAM_LINK))
footer.pack(pady=2)

load_configs()
threading.Thread(target=background_startup_check, daemon=True).start()

threading.Thread(target=background_battery_simulator, daemon=True).start()
threading.Thread(target=adb_keep_alive_daemon, daemon=True).start()

threading.Thread(target=live_proxy_checker_daemon, daemon=True).start()

def on_closing():
    save_all()
    app.destroy()
    sys.exit(0)

app.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    app.mainloop()