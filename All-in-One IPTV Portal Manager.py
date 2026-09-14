import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import re
from datetime import datetime
from urllib.parse import urlparse
import subprocess
import hashlib
import threading
import urllib.request
from tkinter import Tk, Label, Button, Listbox, Scrollbar, Entry, Text, END, WORD, Frame, BOTH, LEFT, RIGHT, VERTICAL, X, Y, EXTENDED, Toplevel

# আপনার গুগল শিটের ওয়েব অ্যাপ লিংক
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrHGMC6d6dE7UPOILXTppRgM9Bifzejy0ofE9fNObQlyxxbgGgy1LJ5IeoMjSZcocU/exec"

# ==========================================
# 🛡️ HARDWARE ID GENERATOR
# ==========================================
def get_hardware_id():
    try:
        command = "wmic csproduct get uuid"
        uuid = subprocess.check_output(command, shell=True).decode().split('\n')[1].strip()
        return hashlib.sha256(uuid.encode()).hexdigest()[:16].upper()
    except:
        return "DEFAULT-PC-ID-001"

current_hwid = get_hardware_id()
is_activated = False

# টাস্কবার আইকনের জন্য ইউনিক AppUserModelID সেট করা (উইন্ডো তৈরির আগে)
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TapasMondal.IPTVPortalManager.App.v8")
except Exception:
    pass

# -----------------------------
# MAIN WINDOW SETUP (RESIZABLE ENABLED)
# -----------------------------

root = tk.Tk()
root.title("All-in-One IPTV Portal Manager by - Tapas Mondal")
root.geometry("620x850") 
root.config(bg="#1e1e2f")
root.resizable(True, True)

# টাইটেল বার এবং টাস্কবারের জন্য iconbitmap সেটআপ (Exe এবং লোকাল রান উভয়ক্ষেত্রের জন্য)
try:
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")
    else:
        icon_path = "icon.ico"
    root.iconbitmap(icon_path)
except Exception:
    pass

# উইন্ডোজ নেটিভ টাইটেল বারের কালার পরিবর্তন করার জন্য (উইন্ডোজ ১১)
try:
    HWND = ctypes.windll.user32.GetParent(root.winfo_id())
    COLOR = 0x5C4033  # BGR ফরম্যাটে কালার কোড (#2d2d44)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 35, ctypes.byref(ctypes.c_int(COLOR)), 4)
except Exception:
    pass

BG_COLOR = "#1e1e2f"
CARD_COLOR = "#2d2d44"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#4e73df"
BTN_COLOR = "#1cc88a"

# হেডার ফ্রেম
header_frame = tk.Frame(root, bg=ACCENT_COLOR, height=35)
header_frame.pack(fill=tk.X)

title_label = tk.Label(header_frame, text="⚡ IPTV PORTAL & DUAL M3U EDITOR MANAGER BY TAPAS ⚡", font=("Segoe UI", 9, "bold"), bg=ACCENT_COLOR, fg="white")
title_label.pack(pady=6)
# কাস্টম ট্যাব সুইচিং ফ্রেম
switch_frame = tk.Frame(root, bg=BG_COLOR)
switch_frame.pack(fill=tk.X, padx=10, pady=(4, 2))

def show_xtream_tab():
    tab_stalker.pack_forget()
    tab_m3u_editor.pack_forget()
    tab_xtream.pack(fill=tk.BOTH, expand=True)
    xtream_tab_btn.config(bg="#2c7be5", fg="white", relief=tk.SUNKEN)
    stalker_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)
    m3u_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)

def show_stalker_tab():
    tab_xtream.pack_forget()
    tab_m3u_editor.pack_forget()
    tab_stalker.pack(fill=tk.BOTH, expand=True)
    stalker_tab_btn.config(bg="#2c7be5", fg="white", relief=tk.SUNKEN)
    xtream_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)
    m3u_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)

def show_m3u_editor_tab():
    tab_xtream.pack_forget()
    tab_stalker.pack_forget()
    tab_m3u_editor.pack(fill=tk.BOTH, expand=True)
    m3u_tab_btn.config(bg="#2c7be5", fg="white", relief=tk.SUNKEN)
    xtream_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)
    stalker_tab_btn.config(bg="#3a4b60", fg="#95aac9", relief=tk.RAISED)

xtream_tab_btn = tk.Button(
    switch_frame,
    text="🌐 Xtream Codes Portal",
    font=("Segoe UI", 8, "bold"),
    bg="#2c7be5",
    fg="white",
    bd=0,
    cursor="hand2",
    command=show_xtream_tab,
)
xtream_tab_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=1)

stalker_tab_btn = tk.Button(
    switch_frame,
    text="📺 Stalker MAC Portal",
    font=("Segoe UI", 8, "bold"),
    bg="#3a4b60",
    fg="#95aac9",
    bd=0,
    cursor="hand2",
    command=show_stalker_tab,
)
stalker_tab_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=1)

m3u_tab_btn = tk.Button(
    switch_frame,
    text="📁 Dual M3U Editor",
    font=("Segoe UI", 8, "bold"),
    bg="#3a4b60",
    fg="#95aac9",
    bd=0,
    cursor="hand2",
    command=show_m3u_editor_tab,
)
m3u_tab_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=1)

container_frame = tk.Frame(root, bg=BG_COLOR)
container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 2))

tab_xtream = tk.Frame(container_frame, bg=BG_COLOR)
tab_stalker = tk.Frame(container_frame, bg=BG_COLOR)
tab_m3u_editor = tk.Frame(container_frame, bg=BG_COLOR)

# ==========================================
# 📊 GOOGLE SHEET LOGGING FUNCTION
# ==========================================
def log_to_google_sheet(portal_name, url, username, password="N/A"):
    if not GOOGLE_SCRIPT_URL or "আপনার_গুগল_শিটের" in GOOGLE_SCRIPT_URL:
        return False
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "action": "log",
        "portal_name": portal_name,
        "url": url,
        "username": username,
        "password": password,
        "mac": username if "00:1A" in username or ":" in username else "N/A",
        "login_time": current_time
    }
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Sheet logging failed: {e}")
        return False


# ==========================================
# TAB 1: XTREAM CODES
# ==========================================

live_categories = {}
vod_categories = {}
series_categories = {}
all_category_list = ["all"]
base_url_xc = ""
xc_username = ""
xc_password = ""

def create_label(parent, text):
    return tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"), bg=BG_COLOR, fg="#b0bec5")

def create_entry(parent, show_char=None):
    return tk.Entry(parent, font=("Segoe UI", 9), bg=CARD_COLOR, fg=TEXT_COLOR, insertbackground="white", relief=tk.FLAT, show=show_char)

create_label(tab_xtream, "Server URL:").pack(anchor="w", pady=(1, 0))
portal_entry = create_entry(tab_xtream)
portal_entry.pack(fill=tk.X, ipady=1, padx=2)
portal_entry.insert(0, "e.g. http://xtream.portal.com:8080")

create_label(tab_xtream, "Username:").pack(anchor="w", pady=(1, 0))
user_entry = create_entry(tab_xtream)
user_entry.pack(fill=tk.X, ipady=1, padx=2)
user_entry.insert(0, "e.g. TapasMondal")

create_label(tab_xtream, "Password:").pack(anchor="w", pady=(1, 0))
pass_entry = create_entry(tab_xtream, show_char="*")
pass_entry.pack(fill=tk.X, ipady=1, padx=2)

def filter_categories(event):
    if not is_activated:
        return
    search_text = category_search_entry.get().strip().lower()
    if not search_text:
        genre_dropdown['values'] = all_category_list
    else:
        filtered = [item for item in all_category_list if search_text in item.lower()]
        genre_dropdown['values'] = filtered
        if filtered:
            genre_dropdown.set(filtered[0])

def test_xtream_account():
    global base_url_xc, xc_username, xc_password, live_categories, vod_categories, series_categories, all_category_list

    if not is_activated:
        messagebox.showerror("Locked Software", "❌ Software is not activated!\nPlease enter a valid license key below to unlock.")
        return

    url_input = portal_entry.get().strip()
    parsed = urlparse(url_input)
    base_url_xc = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else url_input.rstrip('/')
    portal_name = parsed.hostname or "Xtream Portal"

    xc_username = user_entry.get().strip()
    xc_password = pass_entry.get().strip()

    xtream_output.config(state=tk.NORMAL)
    xtream_output.delete("1.0", tk.END)
    xtream_output.insert(tk.END, "Authenticating Xtream account...\n")
    xtream_output.config(state=tk.DISABLED)

    auth_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}"

    try:
        res = requests.get(auth_url, timeout=10)
        data = res.json()
        status = data.get('user_info', {}).get('status')

        xtream_output.config(state=tk.NORMAL)
        if status == 'Active':
            xtream_output.insert(tk.END, "✔ SUCCESS: Account Active!\n")
            log_to_google_sheet(portal_name, base_url_xc, xc_username, xc_password)
            
            # 1. Live Categories
            categories_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_live_categories"
            cat_res = requests.get(categories_url, timeout=10)
            if cat_res.status_code == 200:
                cats = cat_res.json()
                if isinstance(cats, list):
                    live_categories = {str(c['category_id']): c['category_name'] for c in cats}

            # 2. VOD (Movie) Categories
            vod_cat_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_vod_categories"
            vod_cat_res = requests.get(vod_cat_url, timeout=10)
            if vod_cat_res.status_code == 200:
                vcats = vod_cat_res.json()
                if isinstance(vcats, list):
                    vod_categories = {str(c['category_id']): c['category_name'] for c in vcats}

            # 3. Series Categories
            series_cat_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_series_categories"
            series_cat_res = requests.get(series_cat_url, timeout=10)
            if series_cat_res.status_code == 200:
                scats = series_cat_res.json()
                if isinstance(scats, list):
                    series_categories = {str(c['category_id']): c['category_name'] for c in scats}

            # Combine all categories with prefixes to easily identify them
            all_category_list = ["all"]
            all_category_list += [f"[LIVE] {cid} - {cname}" for cid, cname in live_categories.items()]
            all_category_list += [f"[VOD] {cid} - {cname}" for cid, cname in vod_categories.items()]
            all_category_list += [f"[SERIES] {cid} - {cname}" for cid, cname in series_categories.items()]

            genre_dropdown['values'] = all_category_list
            genre_dropdown.set("all")

            xtream_output.insert(tk.END, "✔ Live, VOD & Series Categories Loaded!\n")
            messagebox.showinfo("Success", "Xtream Login Successful & All Categories Loaded!")
        else:
            xtream_output.insert(tk.END, "❌ FAILED: Inactive Account.\n")
            messagebox.showerror("Error", "Xtream account is not active.")
        xtream_output.config(state=tk.DISABLED)
    except Exception as e:
        xtream_output.config(state=tk.NORMAL)
        xtream_output.insert(tk.END, f"❌ Error: {str(e)}\n")
        xtream_output.config(state=tk.DISABLED)

test_btn = tk.Button(tab_xtream, text="🔍 Test Account & Get Categories", font=("Segoe UI", 8, "bold"), bg=ACCENT_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=test_xtream_account)
test_btn.pack(fill=tk.X, pady=2, ipady=2, padx=2)

xtream_output = tk.Text(tab_xtream, height=1.5, font=("Consolas", 8), bg=CARD_COLOR, fg="#00ffcc", relief=tk.FLAT, state=tk.DISABLED)
xtream_output.pack(fill=tk.X, padx=2, pady=1)

create_label(tab_xtream, "Search Category:").pack(anchor="w", pady=(1, 0))
category_search_entry = create_entry(tab_xtream)
category_search_entry.pack(fill=tk.X, ipady=1, padx=2)
category_search_entry.bind('<KeyRelease>', filter_categories)

create_label(tab_xtream, "Genre / Category (Select):").pack(anchor="w", pady=(1, 0))
genre_dropdown = ttk.Combobox(tab_xtream, font=("Segoe UI", 8), state="readonly")
genre_dropdown.pack(fill=tk.X, ipady=1, padx=2)
genre_dropdown['values'] = all_category_list
genre_dropdown.set("all")

create_label(tab_xtream, "Filename (without .m3u):").pack(anchor="w", pady=(1, 0))
filename_entry = create_entry(tab_xtream)
filename_entry.pack(fill=tk.X, ipady=1, padx=2)
filename_entry.insert(0, "xtream_playlist_by_Tapas")

def build_xtream_m3u():
    global base_url_xc, xc_username, xc_password, live_categories, vod_categories, series_categories
    
    if not is_activated:
        messagebox.showerror("Locked Software", "❌ Software is not activated!\nPlease enter a valid license key below to unlock.")
        return

    if not base_url_xc or not xc_username:
        messagebox.showerror("Error", "Please test the account first.")
        return

    try:
        genre_choice = genre_dropdown.get()
        
        target_type = "all"
        target_genre_id = "all"
        
        if genre_choice != "all" and genre_choice:
            if genre_choice.startswith("[LIVE]"):
                target_type = "live"
                target_genre_id = genre_choice.replace("[LIVE] ", "").split(" - ")[0]
            elif genre_choice.startswith("[VOD]"):
                target_type = "vod"
                target_genre_id = genre_choice.replace("[VOD] ", "").split(" - ")[0]
            elif genre_choice.startswith("[SERIES]"):
                target_type = "series"
                target_genre_id = genre_choice.replace("[SERIES] ", "").split(" - ")[0]

        filename = filename_entry.get().strip() or "xtream_playlist"
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop_dir, f"{filename}.m3u")

        count = 0
        with open(path, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')

            # 1. Live Streams
            if target_type in ["all", "live"]:
                channels_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_live_streams"
                res = requests.get(channels_url, timeout=15)
                channels = res.json()
                if isinstance(channels, list):
                    for ch in channels:
                        cat_id = str(ch.get('category_id', ''))
                        if target_type == "live" and target_genre_id != 'all' and cat_id != target_genre_id:
                            continue
                        name = ch.get('name', 'Unknown')
                        logo = ch.get('stream_icon', '')
                        group = live_categories.get(cat_id, 'Live General')
                        stream_id = ch.get('stream_id')
                        stream_url = f"{base_url_xc}/live/{xc_username}/{xc_password}/{stream_id}.ts"
                        f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Live - {group}",{name}\n{stream_url}\n')
                        count += 1

            # 2. VOD (Movies) - Fixed Extension Handling
            if target_type in ["all", "vod"]:
                vod_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_vod_streams"
                res = requests.get(vod_url, timeout=15)
                vods = res.json()
                if isinstance(vods, list):
                    for v in vods:
                        cat_id = str(v.get('category_id', ''))
                        if target_type == "vod" and target_genre_id != 'all' and cat_id != target_genre_id:
                            continue
                        name = ch_name = v.get('name', 'Unknown')
                        logo = v.get('stream_icon', '')
                        group = vod_categories.get(cat_id, 'VOD Movies')
                        stream_id = v.get('stream_id')
                        ext = v.get('container_extension', 'mp4')
                        # Correct VOD URL structure for Xtream Codes
                        stream_url = f"{base_url_xc}/movie/{xc_username}/{xc_password}/{stream_id}.{ext}"
                        f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="VOD - {group}",{name}\n{stream_url}\n')
                        count += 1

            # 3. Series - Fetching Episodes properly via get_series_info
            if target_type in ["all", "series"]:
                series_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_series"
                res = requests.get(series_url, timeout=15)
                series_list = res.json()
                if isinstance(series_list, list):
                    for s in series_list:
                        cat_id = str(s.get('category_id', ''))
                        if target_type == "series" and target_genre_id != 'all' and cat_id != target_genre_id:
                            continue
                        
                        series_id = s.get('series_id')
                        series_name = s.get('name', 'Unknown Series')
                        cover = s.get('cover', '')
                        group = series_categories.get(cat_id, 'Series')

                        # To get playable links for series, we need to fetch individual episodes using get_series_info
                        info_url = f"{base_url_xc}/player_api.php?username={xc_username}&password={xc_password}&action=get_series_info&series_id={series_id}"
                        try:
                            info_res = requests.get(info_url, timeout=10)
                            info_data = info_res.json()
                            episodes = info_data.get('episodes', {})
                            
                            for season_num, eps in episodes.items():
                                for ep in eps:
                                    ep_id = ep.get('id')
                                    ep_title = ep.get('title', 'Episode')
                                    ep_ext = ep.get('container_extension', 'mp4')
                                    
                                    # Correct Series Episode URL structure
                                    stream_url = f"{base_url_xc}/series/{xc_username}/{xc_password}/{ep_id}.{ep_ext}"
                                    display_name = f"{series_name} - S{season_num}E{ep.get('episode_num', '')} - {ep_title}"
                                    
                                    f.write(f'#EXTINF:-1 tvg-logo="{cover}" group-title="Series - {group}",{display_name}\n{stream_url}\n')
                                    count += 1
                        except Exception:
                            # Fallback if series info fails
                            pass

        messagebox.showinfo("M3U Saved", f"Successfully saved {count} streams (Live, VOD & Series) to Desktop!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate M3U: {str(e)}")
gen_btn = tk.Button(tab_xtream, text="🚀 Generate Xtream M3U Playlist", font=("Segoe UI", 9, "bold"), bg=BTN_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=build_xtream_m3u)
gen_btn.pack(fill=tk.X, pady=2, ipady=2, padx=2)

# ==========================================
# TAB 2: STALKER PORTAL
# ==========================================

stalker_base_url = ""
online_macs = []
loaded_genres = {}
loaded_vod_genres = {}
loaded_series_genres = {}
all_genre_list = ["all"]

create_label(tab_stalker, "Stalker Portal URL:").pack(anchor="w", pady=(1, 0))
stalker_url_entry = create_entry(tab_stalker)
stalker_url_entry.pack(fill=tk.X, ipady=1, padx=2)
stalker_url_entry.insert(0, "e.g. http://portal.stalker.com:8080/c/")

create_label(tab_stalker, "MAC Address:").pack(anchor="w", pady=(1, 0))
mac_entry = create_entry(tab_stalker)
mac_entry.pack(fill=tk.X, ipady=1, padx=2)
mac_entry.insert(0, "e.g. 00:1A:79:XX:XX:XX")

def filter_stalker_genres(event):
    if not is_activated:
        return
    search_text = stalker_category_search_entry.get().strip().lower()
    if not search_text:
        stalker_genre_dropdown['values'] = all_genre_list
    else:
        filtered = [item for item in all_genre_list if search_text in item.lower()]
        stalker_genre_dropdown['values'] = filtered
        if filtered:
            stalker_genre_dropdown.set(filtered[0])

def create_session(mac, base_url):
    session = requests.Session()
    session.cookies.update({'mac': mac})
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': f'{base_url}/c/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    })
    return session

def get_token(session, base_url, mac):
    url = f'{base_url}/portal.php?action=handshake&type=stb&token=&JsHttpRequest=1-xml'
    headers = {'Authorization': f'MAC {mac}'}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()['js']['token']
    except:
        return None

def get_genres(session, base_url, token):
    url = f'{base_url}/server/load.php?type=itv&action=get_genres&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return {g['id']: g['title'] for g in res.json()['js']}
    except:
        return {}

def get_vod_genres(session, base_url, token):
    url = f'{base_url}/server/load.php?type=vod&action=get_categories&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return {g['id']: g['title'] for g in res.json()['js']}
    except:
        return {}

def get_series_genres(session, base_url, token):
    url = f'{base_url}/server/load.php?type=series&action=get_categories&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return {g['id']: g['title'] for g in res.json()['js']}
    except:
        return {}

def get_channels(session, base_url, token):
    url = f'{base_url}/portal.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()['js']['data']
    except:
        return []

def get_vod_movies(session, base_url, token, category_id="0"):
    url = f'{base_url}/server/load.php?type=vod&action=get_ordered_list&category={category_id}&p=1&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json().get('js', {})
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"VOD Fetch Error: {e}")
        return []

def get_series_list(session, base_url, token, category_id="0"):
    url = f'{base_url}/server/load.php?type=series&action=get_ordered_list&category={category_id}&p=1&JsHttpRequest=1-xml'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json().get('js', {})
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Series Fetch Error: {e}")
        return []

def test_stalker_portal():
    global stalker_base_url, online_macs, loaded_genres, loaded_vod_genres, loaded_series_genres, all_genre_list

    if not is_activated:
        messagebox.showerror("Locked Software", "❌ Software is not activated!\nPlease enter a valid license key below to unlock.")
        return

    url_input = stalker_url_entry.get().strip()
    parsed = urlparse(url_input)
    stalker_base_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else url_input.rstrip('/')
    portal_name = parsed.hostname or "Stalker Portal"

    macs = [m.strip().upper() for m in mac_entry.get().split(",")]

    stalker_output.config(state=tk.NORMAL)
    stalker_output.delete("1.0", tk.END)
    stalker_output.insert(tk.END, "Testing MACs & Fetching Token...\n")
    stalker_output.config(state=tk.DISABLED)

    online_macs = []

    for mac in macs:
        session = create_session(mac, stalker_base_url)
        stalker_output.config(state=tk.NORMAL)
        stalker_output.insert(tk.END, f"→ {mac} ... ")
        stalker_output.config(state=tk.DISABLED)
        
        token = get_token(session, stalker_base_url, mac)

        stalker_output.config(state=tk.NORMAL)
        if token:
            stalker_output.insert(tk.END, f"✔ ONLINE\n🔑 Token: {token}\n")
            online_macs.append((mac, token, session))
            log_to_google_sheet(portal_name, stalker_base_url, mac, f"Token: {token}")
        else:
            stalker_output.insert(tk.END, "❌ OFFLINE\n")
        stalker_output.config(state=tk.DISABLED)

    if not online_macs:
        messagebox.showerror("Error", "No working MAC found.")
        return

    mac, token, session = online_macs[0]
    loaded_genres = get_genres(session, stalker_base_url, token)
    loaded_vod_genres = get_vod_genres(session, stalker_base_url, token)
    loaded_series_genres = get_series_genres(session, stalker_base_url, token)

    all_genre_list = ["all"]
    all_genre_list += [f"[LIVE] {gid} - {title}" for gid, title in loaded_genres.items()]
    all_genre_list += [f"[VOD] {gid} - {title}" for gid, title in loaded_vod_genres.items()]
    all_genre_list += [f"[SERIES] {gid} - {title}" for gid, title in loaded_series_genres.items()]

    stalker_genre_dropdown['values'] = all_genre_list
    stalker_genre_dropdown.set("all")

    total_cats = len(loaded_genres) + len(loaded_vod_genres) + len(loaded_series_genres)
    messagebox.showinfo("MAC OK", f"Using working MAC & Loaded {total_cats} Total Categories (Live, VOD, Series)!")

stalker_btn = tk.Button(tab_stalker, text="🔍 Test MAC & Get Categories", font=("Segoe UI", 8, "bold"), bg=ACCENT_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=test_stalker_portal)
stalker_btn.pack(fill=tk.X, pady=2, ipady=2, padx=2)

stalker_output = tk.Text(tab_stalker, height=2.5, font=("Consolas", 8), bg=CARD_COLOR, fg="#00ffcc", relief=tk.FLAT, state=tk.DISABLED)
stalker_output.pack(fill=tk.X, padx=2, pady=1)

create_label(tab_stalker, "Search Stalker Category:").pack(anchor="w", pady=(1, 0))
stalker_category_search_entry = create_entry(tab_stalker)
stalker_category_search_entry.pack(fill=tk.X, ipady=1, padx=2)
stalker_category_search_entry.bind('<KeyRelease>', filter_stalker_genres)

create_label(tab_stalker, "Genre / Category (Select):").pack(anchor="w", pady=(1, 0))
stalker_genre_dropdown = ttk.Combobox(tab_stalker, font=("Segoe UI", 8), state="readonly")
stalker_genre_dropdown.pack(fill=tk.X, ipady=1, padx=2)
stalker_genre_dropdown['values'] = all_genre_list
stalker_genre_dropdown.set("all")

token_frame = tk.LabelFrame(tab_stalker, text=" Token Mode ", font=("Segoe UI", 8, "bold"), bg=BG_COLOR, fg="#b0bec5", relief=tk.GROOVE, bd=1)
token_frame.pack(fill=tk.X, pady=2, ipadx=4, ipady=1)

token_var = tk.IntVar(value=1)
r1 = tk.Radiobutton(token_frame, text="Without Token", variable=token_var, value=0, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=CARD_COLOR, font=("Segoe UI", 8))
r1.pack(anchor="w", padx=6, pady=1)
r2 = tk.Radiobutton(token_frame, text="With Token", variable=token_var, value=1, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=CARD_COLOR, font=("Segoe UI", 8))
r2.pack(anchor="w", padx=6, pady=1)

create_label(tab_stalker, "Stalker Filename (without .m3u):").pack(anchor="w", pady=(1, 0))
stalker_filename_entry = create_entry(tab_stalker)
stalker_filename_entry.pack(fill=tk.X, ipady=1, padx=2)
stalker_filename_entry.insert(0, "stalker_playlist_by_Tapas")

def generate_stalker_m3u():
    if not is_activated:
        messagebox.showerror("Locked Software", "❌ Software is not activated!\nPlease enter a valid license key below to unlock.")
        return

    if not 'online_macs' in globals() or not online_macs:
        messagebox.showerror("Error", "Test MACs first.")
        return

    mac, token, session = online_macs[0]
    
    stalker_output.config(state=tk.NORMAL)
    stalker_output.insert(tk.END, "⏳ Fetching streams (Live, VOD, Series via API)...\n")
    stalker_output.config(state=tk.DISABLED)

    genre_choice = stalker_genre_dropdown.get()
    
    target_type = "all"
    target_genre_id = "0"
    
    if genre_choice != "all" and genre_choice:
        if genre_choice.startswith("[LIVE]"):
            target_type = "live"
            target_genre_id = genre_choice.replace("[LIVE] ", "").split(" - ")[0]
        elif genre_choice.startswith("[VOD]"):
            target_type = "vod"
            target_genre_id = genre_choice.replace("[VOD] ", "").split(" - ")[0]
        elif genre_choice.startswith("[SERIES]"):
            target_type = "series"
            target_genre_id = genre_choice.replace("[SERIES] ", "").split(" - ")[0]

    use_token = token_var.get() == 1
    filename = stalker_filename_entry.get().strip() or "stalker_playlist"
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop_dir, f"{filename}.m3u")

    clean_mac = mac.strip()
    clean_token = token.strip() if token else ''
    headers = {'Authorization': f'Bearer {clean_token}'} if clean_token else {}

    count = 0
    with open(path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')

        # 1. Live Channels
        if target_type in ["all", "live"]:
            channels = get_channels(session, stalker_base_url, clean_token)
            if isinstance(channels, list):
                for ch in channels:
                    cat_id = str(ch.get('tv_genre_id', ''))
                    if target_type == "live" and target_genre_id != '0' and cat_id != target_genre_id:
                        continue

                    name = ch.get('name', 'Unknown')
                    logo = ch.get('logo', '')
                    group = loaded_genres.get(cat_id, 'Live General')
                    cmd = ch.get('cmds', [{}])[0].get('url', '').replace('ffmpeg ', '')

                    if 'localhost' in cmd:
                        match = re.search('/ch/(\\d+)', cmd)
                        if match:
                            stream_id = match.group(1)
                            cmd = f'{stalker_base_url}/play/live.php?mac={clean_mac}&stream={stream_id}&extension=ts'
                            if use_token and clean_token:
                                cmd += f'&play_token={clean_token}'

                    if not cmd:
                        continue

                    f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Live - {group}",{name}\n{cmd}\n')
                    count += 1

        # 2. VOD (Movies) - Fixed Pagination (handles server's 28 items per page limit)
        if target_type in ["all", "vod"]:
            movies = []
            page = 1
            target_cat = target_genre_id if (target_type == "vod" and target_genre_id != "0") else "0"
            
            while page <= 50:  # পর্যাপ্ত পেজ লিমিট
                try:
                    v_url = f"{stalker_base_url.rstrip('/')}/server/load.php?type=vod&action=get_ordered_list&category={target_cat}&p={page}&JsHttpRequest=1-xml"
                    if clean_token:
                        v_url += f"&play_token={clean_token}"
                        
                    v_res = session.get(v_url, timeout=10)
                    v_json = v_res.json()
                    v_data = v_json.get('js', {})
                    
                    v_items = []
                    if isinstance(v_data, dict):
                        v_items = v_data.get('data', [])
                    elif isinstance(v_data, list):
                        v_items = v_data
                    elif isinstance(v_json, list):
                        v_items = v_json
                        
                    if not v_items:
                        break
                        
                    movies.extend(v_items)
                    # যদি আইটেম ২৮টির কম আসে তবে বুঝতে হবে এটাই শেষ পেজ
                    if len(v_items) < 10: 
                        break
                    page += 1
                except Exception:
                    break

            if isinstance(movies, list):
                for m in movies:
                    name = m.get('name', 'Unknown Movie')
                    logo = m.get('screenshot_uri', '') or m.get('cover', '')
                    group = loaded_vod_genres.get(str(m.get('cat_id', '')), 'VOD Movies')
                    
                    raw_cmd = m.get('cmd', '')
                    if not raw_cmd and 'cmds' in m:
                        raw_cmd = m['cmds'][0].get('cmd', '')

                    cmd = ""
                    if raw_cmd:
                        link_url = f"{stalker_base_url.rstrip('/')}/server/load.php?type=vod&action=create_link&cmd={requests.utils.quote(raw_cmd)}&JsHttpRequest=1-xml"
                        try:
                            link_res = session.get(link_url, timeout=5)
                            link_data = link_res.json().get('js', {})
                            if isinstance(link_data, dict):
                                cmd = link_data.get('cmd', '')
                        except Exception:
                            pass

                    if not cmd:
                        raw_id = str(m.get('id', ''))
                        movie_id = raw_id.split(':')[0].strip()
                        if movie_id:
                            cmd = f"{stalker_base_url.rstrip('/')}/play/movie.php?mac={clean_mac}&movie_id={movie_id}&extension=mp4"

                    if not cmd:
                        continue

                    cmd = cmd.replace('ffmpeg ', '').strip()
                    if use_token and clean_token and 'play_token=' not in cmd:
                        sep = '&' if '?' in cmd else '?'
                        cmd += f"{sep}play_token={clean_token}"

                    f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="VOD - {group}",{name}\n{cmd}\n')
                    count += 1

        # 3. Series - Safe Saving with Proper Episode Stream Link Extraction
        if target_type in ["all", "series"]:
            series_list = []
            page = 1
            target_series_cat = target_genre_id if (target_type == "series" and target_genre_id != "0") else "0"
            
            while page <= 50:
                try:
                    s_url = f"{stalker_base_url.rstrip('/')}/server/load.php?type=series&action=get_ordered_list&category={target_series_cat}&p={page}&JsHttpRequest=1-xml"
                    if clean_token:
                        s_url += f"&play_token={clean_token}"
                        
                    s_res = session.get(s_url, headers=headers, timeout=10)
                    s_json = s_res.json()
                    s_data = s_json.get('js', {})
                    
                    s_items = []
                    if isinstance(s_data, dict):
                        s_items = s_data.get('data', [])
                    elif isinstance(s_data, list):
                        s_items = s_data
                    elif isinstance(s_json, list):
                        s_items = s_json
                        
                    if not s_items:
                        break
                        
                    series_list.extend(s_items)
                    if len(s_items) < 10:
                        break
                    page += 1
                except Exception:
                    break

            if isinstance(series_list, list):
                for s in series_list:
                    series_id_raw = str(s.get('id', ''))
                    series_id = series_id_raw.split(':')[0].strip()
                    series_name = s.get('name', 'Unknown Series')
                    logo = s.get('screenshot_uri', '') or s.get('cover', '')
                    group = loaded_series_genres.get(str(s.get('cat_id', '')), 'Series')

                    if not series_id:
                        continue

                    info_url = f'{stalker_base_url}/server/load.php?type=series&action=get_item_the_complete_info&id={series_id}&JsHttpRequest=1-xml'
                    try:
                        info_res = session.get(info_url, headers=headers, timeout=10)
                        info_data = info_res.json().get('js', {})
                        series_ed = []
                        if isinstance(info_data, dict):
                            series_ed = info_data.get('series', []) or info_data.get('episodes', [])
                        elif isinstance(info_data, list):
                            series_ed = info_data
                        
                        if series_ed:
                            for ep in series_ed:
                                season_num = ep.get('season', '1')
                                ep_num = ep.get('episode', '1')
                                ep_title = ep.get('name', f'Episode {ep_num}')
                                
                                raw_ep_cmd = ep.get('cmd', '')
                                if not raw_ep_cmd and 'cmds' in ep:
                                    raw_ep_cmd = ep['cmds'][0].get('cmd', '')

                                ep_cmd = ""
                                # নিরাপদভাবে create_link চেষ্টা করবে, ফেল করলে ফলব্যাক হিসেবে raw_ep_cmd ব্যবহার করবে (জিরো হবে না)
                                if raw_ep_cmd:
                                    link_url = f"{stalker_base_url.rstrip('/')}/server/load.php?type=vod&action=create_link&cmd={requests.utils.quote(raw_ep_cmd)}&JsHttpRequest=1-xml"
                                    try:
                                        link_res = session.get(link_url, headers=headers, timeout=3)
                                        link_data = link_res.json().get('js', {})
                                        if isinstance(link_data, dict):
                                            ep_cmd = link_data.get('cmd', '')
                                    except Exception:
                                        pass
                                    
                                    if not ep_cmd:
                                        ep_cmd = raw_ep_cmd

                                if not ep_cmd:
                                    ep_id_raw = str(ep.get('id', ''))
                                    ep_id = ep_id_raw.split(':')[0].strip()
                                    if ep_id:
                                        ep_cmd = f"{stalker_base_url.rstrip('/')}/play/movie.php?mac={clean_mac}&movie_id={ep_id}&extension=mp4"

                                if not ep_cmd:
                                    continue

                                ep_cmd = ep_cmd.replace('ffmpeg ', '').strip()
                                if use_token and clean_token and 'play_token=' not in ep_cmd:
                                    sep = '&' if '?' in ep_cmd else '?'
                                    ep_cmd += f"{sep}play_token={clean_token}"
                                    
                                display_name = f"{series_name} - S{season_num}E{ep_num} - {ep_title}"
                                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Series - {group}",{display_name}\n{ep_cmd}\n')
                                count += 1
                        else:
                            cmd = f"{stalker_base_url.rstrip('/')}/play/movie.php?mac={clean_mac}&movie_id={series_id}&extension=mp4"
                            if use_token and clean_token and 'play_token=' not in cmd:
                                sep = '&' if '?' in cmd else '?'
                                cmd += f"{sep}play_token={clean_token}"
                            f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Series - {group}",{series_name}\n{cmd}\n')
                            count += 1
                    except Exception:
                        cmd = f"{stalker_base_url.rstrip('/')}/play/movie.php?mac={clean_mac}&movie_id={series_id}&extension=mp4"
                        if use_token and clean_token and 'play_token=' not in cmd:
                            sep = '&' if '?' in cmd else '?'
                            cmd += f"{sep}play_token={clean_token}"
                        f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Series - {group}",{series_name}\n{cmd}\n')
                        count += 1
    messagebox.showinfo("M3U Saved", f"Successfully saved {count} Stalker streams (Live, VOD & Series) to Desktop!")

stalker_gen_btn = tk.Button(tab_stalker, text="🚀 Generate Stalker M3U Playlist", font=("Segoe UI", 9, "bold"), bg=BTN_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=generate_stalker_m3u)
stalker_gen_btn.pack(fill=tk.X, pady=2, ipady=2, padx=2)
# ===============================================
# TAB 3: DUAL M3U EDITOR (INTEGRATED FULL SCRIPT)
# ===============================================

class EmbeddedM3UEditor:
    def __init__(self, parent_frame):
        self.parent = parent_frame

        self.channels_p1 = []
        self.channels_p2 = []
        
        # Undo / Redo History Stacks
        self.history_p1 = []
        self.redo_p1 = []
        self.history_p2 = []
        self.redo_p2 = []

        self.drag_window = None
        self.drag_data = {"item": None, "source_p": None, "type": None}

        container = Frame(self.parent, bg="#1e1e2f")
        container.pack(fill=BOTH, expand=True, padx=2, pady=2)
        
        # Grid weight কনফিগারেশন যাতে দুই পাশ সমানভাবে রিসাইজ হয়
        container.columnconfigure(0, weight=1, uniform="dual_editor")
        container.columnconfigure(1, weight=1, uniform="dual_editor")
        container.rowconfigure(0, weight=1)

        # Left Panel (Playlist Editor One)
        self.frame_left = Frame(container, bg="#2b2b40", bd=2, relief="groove")
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.setup_editor_panel(self.frame_left, 1, "📁 M3U Playlist Editor One")

        # Right Panel (Playlist Editor Two)
        self.frame_right = Frame(container, bg="#2b2b40", bd=2, relief="groove")
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.setup_editor_panel(self.frame_right, 2, "📁 M3U Playlist Editor Two")

        # Global Keyboard Shortcuts for Undo/Redo within this tab
        self.parent.bind_all('<Control-z>', self.trigger_undo)
        self.parent.bind_all('<Control-Z>', self.trigger_undo)
        self.parent.bind_all('<Control-Shift-z>', self.trigger_redo)
        self.parent.bind_all('<Control-Shift-Z>', self.trigger_redo)

    def save_state_to_history(self, p_num):
        if p_num == 1:
            self.history_p1.append([ch.copy() for ch in self.channels_p1])
            self.redo_p1.clear()
        else:
            self.history_p2.append([ch.copy() for ch in self.channels_p2])
            self.redo_p2.clear()

    def perform_undo(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        cat_sel = cat_box.curselection()
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        chan_sel = chan_box.curselection()
        current_chan = chan_box.get(chan_sel[0]) if chan_sel else None

        if p_num == 1 and self.history_p1:
            self.redo_p1.append([ch.copy() for ch in self.channels_p1])
            self.channels_p1 = self.history_p1.pop()
            self.refresh_channel_view_keeping_selection(1, current_cat, current_chan)
        elif p_num == 2 and self.history_p2:
            self.redo_p2.append([ch.copy() for ch in self.channels_p2])
            self.channels_p2 = self.history_p2.pop()
            self.refresh_channel_view_keeping_selection(2, current_cat, current_chan)

    def perform_redo(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        cat_sel = cat_box.curselection()
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        chan_sel = chan_box.curselection()
        current_chan = chan_box.get(chan_sel[0]) if chan_sel else None

        if p_num == 1 and self.redo_p1:
            self.history_p1.append([ch.copy() for ch in self.channels_p1])
            self.channels_p1 = self.redo_p1.pop()
            self.refresh_channel_view_keeping_selection(1, current_cat, current_chan)
        elif p_num == 2 and self.redo_p2:
            self.history_p2.append([ch.copy() for ch in self.channels_p2])
            self.channels_p2 = self.redo_p2.pop()
            self.refresh_channel_view_keeping_selection(2, current_cat, current_chan)

    def trigger_undo(self, event=None):
        try:
            focused = self.parent.focus_get()
            # ফোকাস বা উইজেট পাথ চেক করে নির্ধারণ করা হচ্ছে এটি প্যানেল ১ নাকি প্যানেল ২
            widget_str = str(focused) if focused else ""
            left_str = str(self.frame_left)
            
            # যদি ফোকাস প্যানেল ১ এর কোনো উপাদানে থাকে অথবা লিস্টবক্স ১ হয়
            if (left_str in widget_str) or ('1' in widget_str and '2' not in widget_str):
                p_num = 1
            else:
                p_num = 2
            
            # অতিরিক্ত সুরক্ষা: যদি ফোকাস নির্দিষ্টভাবে প্যানেল ১ এর লিস্টবক্সগুলোর কাছাকাছি হয়
            if hasattr(self, 'chan_listbox1') and focused in (self.chan_listbox1, self.cat_listbox1):
                p_num = 1
            elif hasattr(self, 'chan_listbox2') and focused in (self.chan_listbox2, self.cat_listbox2):
                p_num = 2

            self.perform_undo(p_num)
        except Exception as e:
            print("Trigger Undo Error:", e)

    def trigger_redo(self, event=None):
        try:
            focused = self.parent.focus_get()
            widget_str = str(focused) if focused else ""
            left_str = str(self.frame_left)
            
            if (left_str in widget_str) or ('1' in widget_str and '2' not in widget_str):
                p_num = 1
            else:
                p_num = 2
            
            if hasattr(self, 'chan_listbox1') and focused in (self.chan_listbox1, self.cat_listbox1):
                p_num = 1
            elif hasattr(self, 'chan_listbox2') and focused in (self.chan_listbox2, self.cat_listbox2):
                p_num = 2

            self.perform_redo(p_num)
        except Exception as e:
            print("Trigger Redo Error:", e)

    def setup_editor_panel(self, parent_frame, p_num, title_text):
        header_frame = Frame(parent_frame, bg="#2b2b40")
        header_frame.pack(fill=X, padx=4, pady=3)
        
        Label(header_frame, text=title_text, bg="#2b2b40", fg="#4CAF50", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        # Undo / Redo Buttons placed near Save/Top header area
        Button(header_frame, text="Redo ↪", command=lambda: self.perform_redo(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=tk.RIGHT, padx=1)
        Button(header_frame, text="Undo ↩", command=lambda: self.perform_undo(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=tk.RIGHT, padx=1)
        
        # --- PLAYER SETTINGS PANEL (Added Here) ---
        player_frame = Frame(parent_frame, bg="#242438", padx=4, pady=3, relief="solid", bd=1)
        player_frame.pack(fill=X, padx=4, pady=2)
        
        Label(player_frame, text="Player .exe:", bg="#242438", fg="#FF9800", font=("Arial", 7, "bold")).pack(side=tk.LEFT, padx=(0, 2))
        
        player_entry = Entry(player_frame, font=("Arial", 7), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        player_entry.pack(side=tk.LEFT, fill=X, expand=True, padx=2)
        
        Button(player_frame, text="Browse", command=lambda: self.browse_editor_player(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=tk.LEFT, padx=2)
        
        if p_num == 1:
            self.editor_player_entry1 = player_entry
        else:
            self.editor_player_entry2 = player_entry      
	# ------------------------------------------

        top_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        top_frame.pack(fill=X)
        
        # লাইসেন্স চেক যুক্ত করা হয়েছে (Open, Load, Save বাটনগুলোতে)
        Button(top_frame, text="Open", command=lambda: self.check_and_run(lambda: self.load_m3u_file(p_num)), bg="#4CAF50", fg="white", font=("Arial", 8), relief="flat", padx=4, pady=1).pack(side=tk.LEFT, padx=1)
        
        entry_url = Entry(top_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        entry_url.pack(side=tk.LEFT, padx=2, fill=X, expand=True)
        
        Button(top_frame, text="Load", command=lambda: self.check_and_run(lambda: self.load_m3u_url(p_num)), bg="#FF5722", fg="white", font=("Arial", 8), relief="flat", padx=4, pady=1).pack(side=tk.LEFT, padx=1)
        Button(top_frame, text="Save", command=lambda: self.check_and_run(lambda: self.save_m3u(p_num)), bg="#2196F3", fg="white", font=("Arial", 8), relief="flat", padx=6, pady=1).pack(side=tk.RIGHT, padx=1)
        
        search_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        search_frame.pack(fill=X, padx=2)
        Label(search_frame, text="Search:", bg="#2b2b40", fg="#FF9800", font=("Arial", 8)).pack(side=tk.LEFT, padx=(0, 4))
        entry_search = Entry(search_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        entry_search.pack(side=tk.LEFT, fill=X, expand=True)
        entry_search.bind('<KeyRelease>', lambda e, p=p_num: self.live_auto_search(p))
        
        if p_num == 1: 
            self.entry_url1 = entry_url
            self.entry_search1 = entry_search
        else: 
            self.entry_url2 = entry_url
            self.entry_search2 = entry_search

        lists_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        lists_frame.pack(fill=BOTH, expand=True)
        
        cat_frame = Frame(lists_frame, bg="#2b2b40")
        cat_frame.pack(side=tk.LEFT, fill=BOTH, expand=False, padx=(0, 2))
        Label(cat_frame, text="Categories", bg="#2b2b40", fg="white", font=("Arial", 8, "bold")).pack(anchor="w")
        
        cat_listbox = tk.Listbox(cat_frame, width=18, font=("Arial", 8), bg="#1e1e2f", fg="white", selectbackground="#4CAF50", exportselection=False, relief="solid", bd=1)
        cat_listbox.pack(side=tk.LEFT, fill=BOTH, expand=True, pady=2)
        cat_scroll = Scrollbar(cat_frame, orient=VERTICAL, command=cat_listbox.yview, width=12)
        cat_scroll.pack(side=tk.RIGHT, fill=Y)
        cat_listbox.config(yscrollcommand=cat_scroll.set)
        
        cat_listbox.bind('<Button-1>', lambda e, p=p_num: self.on_cat_click(e, p))
        cat_listbox.bind('<B1-Motion>', lambda e, p=p_num: self.on_drag_motion(e))
        cat_listbox.bind('<ButtonRelease-1>', lambda e, p=p_num: self.on_cat_drop(e, p))
        cat_listbox.bind('<Delete>', lambda e, p=p_num: self.check_and_run(lambda: self.delete_selected_item(p)))
        cat_listbox.bind('<BackSpace>', lambda e, p=p_num: self.check_and_run(lambda: self.delete_selected_item(p)))

        chan_frame = Frame(lists_frame, bg="#2b2b40")
        chan_frame.pack(side=tk.LEFT, fill=BOTH, expand=True)
        
        chan_top = Frame(chan_frame, bg="#2b2b40")
        chan_top.pack(fill=X)
        Label(chan_top, text="Channels", bg="#2b2b40", fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        Button(chan_top, text="Delete", command=lambda: self.check_and_run(lambda: self.delete_selected_item(p_num)), bg="#f44336", fg="white", font=("Arial", 7), relief="flat", padx=4, pady=0).pack(side=tk.RIGHT)
        
        chan_listbox = tk.Listbox(chan_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", selectbackground="#4CAF50", exportselection=False, relief="solid", bd=1)
        chan_listbox.pack(side=tk.LEFT, fill=BOTH, expand=True, pady=2)
        chan_scroll = Scrollbar(chan_frame, orient=VERTICAL, command=chan_listbox.yview, width=12)
        chan_scroll.pack(side=tk.RIGHT, fill=Y)
        chan_listbox.config(yscrollcommand=chan_scroll.set)
        
        chan_listbox.bind('<Button-1>', lambda e, p=p_num: self.on_chan_click(e, p))
        chan_listbox.bind('<B1-Motion>', lambda e, p=p_num: self.on_drag_motion(e))
        chan_listbox.bind('<ButtonRelease-1>', lambda e, p=p_num: self.on_chan_drop(e, p))
        chan_listbox.bind('<Delete>', lambda e, p=p_num: self.check_and_run(lambda: self.delete_selected_item(p)))
        chan_listbox.bind('<BackSpace>', lambda e, p=p_num: self.check_and_run(lambda: self.delete_selected_item(p)))
        
        # --- DOUBLE CLICK TO PLAY CHANNEL (Added Here) ---
        chan_listbox.bind('<Double-Button-1>', lambda e, p=p_num: self.play_selected_channel(p))

        if p_num == 1:
            self.cat_listbox1 = cat_listbox
            self.chan_listbox1 = chan_listbox
        else:
            self.cat_listbox2 = cat_listbox
            self.chan_listbox2 = chan_listbox

        edit_frame = Frame(parent_frame, bg="#242438", padx=4, pady=4, relief="solid", bd=1)
        edit_frame.pack(fill=X, pady=2)
        
        Label(edit_frame, text="Add / Edit Stream Box", bg="#242438", fg="#4CAF50", font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 2))
        
        def add_entry_row(label_text):
            row = Frame(edit_frame, bg="#242438")
            row.pack(fill=X, pady=1)
            Label(row, text=label_text, bg="#242438", fg="white", font=("Arial", 8), width=8, anchor="w").pack(side=tk.LEFT)
            ent = Entry(row, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
            ent.pack(side=tk.LEFT, fill=X, expand=True)
            return ent
            
        entry_name = add_entry_row("Name:")
        entry_group = add_entry_row("Category:")
        entry_tvgurl = add_entry_row("TVG-URL:")
        
        row4 = Frame(edit_frame, bg="#242438")
        row4.pack(fill=X, pady=1)
        Label(row4, text="URL:", bg="#242438", fg="white", font=("Arial", 8), width=8, anchor="w").pack(side=tk.LEFT)
        text_url = Text(row4, height=2, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1, wrap=WORD)
        text_url.pack(side=tk.LEFT, fill=X, expand=True)
        
        btn_row = Frame(edit_frame, bg="#242438")
        btn_row.pack(fill=X, pady=4)
        
        if p_num == 1:
            self.entry_name1, self.entry_group1, self.entry_tvgurl1, self.text_url1 = entry_name, entry_group, entry_tvgurl, text_url
            Button(btn_row, text="Add", command=lambda: self.check_and_run(lambda: self.add_new_channel(1)), bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Update", command=lambda: self.check_and_run(lambda: self.update_channel(1)), bg="#FF9800", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Copy to P2", command=lambda: self.check_and_run(lambda: self.copy_selection_to_other(1)), bg="#9C27B0", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)
        else:
            self.entry_name2, self.entry_group2, self.entry_tvgurl2, self.text_url2 = entry_name, entry_group, entry_tvgurl, text_url
            Button(btn_row, text="Add", command=lambda: self.check_and_run(lambda: self.add_new_channel(2)), bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Update", command=lambda: self.check_and_run(lambda: self.update_channel(2)), bg="#FF9800", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Copy to P1", command=lambda: self.check_and_run(lambda: self.copy_selection_to_other(2)), bg="#9C27B0", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=tk.LEFT, fill=X, expand=True, padx=2)

    # --- NEW PLAYER FUNCTIONS ---
    def browse_editor_player(self, p_num):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        if file_path:
            entry = self.editor_player_entry1 if p_num == 1 else self.editor_player_entry2
            entry.delete(0, END)
            entry.insert(0, file_path)

    def play_selected_channel(self, p_num):
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        sel = chan_box.curselection()
        if not sel:
            return
        
        channel_name = chan_box.get(sel[0])
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        channel_url = ""
        for ch in channels:
            if ch['name'] == channel_name:
                channel_url = ch.get('url', '').strip()
                break
                
        if not channel_url:
            messagebox.showwarning("Warning", "Selected channel has no valid URL!")
            return
            
        player_entry = self.editor_player_entry1 if p_num == 1 else self.editor_player_entry2
        player_path = player_entry.get().strip()
        
        try:
            if player_path and os.path.exists(player_path):
                subprocess.Popen([player_path, channel_url])
            else:
                # যদি কোনো কাস্টম প্লেয়ার পাথ দেওয়া না থাকে বা ফাইল না পাওয়া যায়, তবে সিস্টেমের ডিফল্ট অ্যাপ দিয়ে ওপেন করার চেষ্টা করবে
                if os.name == 'nt':
                    os.startfile(channel_url)
                else:
                    subprocess.call(('xdg-open', channel_url))
        except Exception as e:
            messagebox.showerror("Player Error", f"Could not play channel: {e}")
    # ----------------------------

    def check_and_run(self, func):
        # আপনার মূল কোডের is_activated ভেরিয়েবল এখানে চেক করবে
        try:
            if not is_activated:
                messagebox.showerror("Locked Software", "❌ Software is not activated!\nPlease enter a valid license key below to unlock.")
                return
        except NameError:
            pass # যদি কোনো কারণে গ্লোবাল স্কোপে is_activated আগে ডিফাইন না থাকে
        func()

    def parse_m3u_content(self, content_lines):
        channels = []
        current_ch = {}
        for line in content_lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                current_ch = {}
                if 'tvg-url="' in line:
                    start = line.find('tvg-url="') + 9
                    end = line.find('"', start)
                    current_ch['tvg_url'] = line[start:end]
                elif 'tvg-logo="' in line:
                    start = line.find('tvg-logo="') + 10
                    end = line.find('"', start)
                    current_ch['tvg_url'] = line[start:end]
                else: 
                    current_ch['tvg_url'] = ""

                if 'group-title="' in line:
                    start = line.find('group-title="') + 13
                    end = line.find('"', start)
                    current_ch['group'] = line[start:end]
                else: 
                    current_ch['group'] = "General"
                
                comma_idx = line.rfind(',')
                current_ch['name'] = line[comma_idx + 1:].strip() if comma_idx != -1 else "Unknown"
            elif line and not line.startswith('#') and current_ch:
                current_ch['url'] = line
                if not current_ch['group']: current_ch['group'] = "General"
                channels.append(current_ch)
                current_ch = {}
        return channels

    def load_m3u_file(self, p_num):
        file_path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u"), ("All Files", "*.*")])
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            channels = self.parse_m3u_content(lines)
            if p_num == 1:
                self.save_state_to_history(1)
                self.channels_p1 = channels
                self.populate_categories(1)
            else:
                self.save_state_to_history(2)
                self.channels_p2 = channels
                self.populate_categories(2)
            messagebox.showinfo("Success", f"Loaded {len(channels)} channels successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_m3u_url(self, p_num):
        url = self.entry_url1.get().strip() if p_num == 1 else self.entry_url2.get().strip()
        if not url: return
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore').splitlines()
            channels = self.parse_m3u_content(content)
            if p_num == 1:
                self.save_state_to_history(1)
                self.channels_p1 = channels
                self.populate_categories(1)
            else:
                self.save_state_to_history(2)
                self.channels_p2 = channels
                self.populate_categories(2)
            messagebox.showinfo("Success", f"Fetched {len(channels)} channels successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def populate_categories(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        cat_box.delete(0, END)
        categories = sorted(list(set(ch['group'] for ch in channels if ch['group'])))
        for cat in categories: cat_box.insert(END, cat)
        chan_box.delete(0, END)

    def live_auto_search(self, p_num):
        keyword = self.entry_search1.get().strip().lower() if p_num == 1 else self.entry_search2.get().strip().lower()
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        if not keyword:
            self.populate_categories(p_num)
            return
            
        matched_categories = sorted(list(set(ch['group'] for ch in channels if keyword in ch['group'].lower() or any(keyword in c['name'].lower() for c in channels if c['group'] == ch['group']))))
        cat_box.delete(0, END)
        for cat in matched_categories: cat_box.insert(END, cat)
            
        chan_box.delete(0, END)
        for ch in channels:
            if keyword in ch['name'].lower() or keyword in ch['group'].lower():
                chan_box.insert(END, ch['name'])

    def on_category_select(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        sel = cat_box.curselection()
        if not sel: return
        cat = cat_box.get(sel[0])
        chan_box.delete(0, END)
        for ch in channels:
            if ch['group'] == cat: 
                chan_box.insert(END, ch['name'])

    def load_channel_details_by_name(self, p_num, c_name):
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        for ch in channels:
            if ch['name'] == c_name:
                if p_num == 1:
                    self.entry_name1.delete(0, END); self.entry_name1.insert(0, ch['name'])
                    self.entry_group1.delete(0, END); self.entry_group1.insert(0, ch['group'])
                    self.entry_tvgurl1.delete(0, END); self.entry_tvgurl1.insert(0, ch.get('tvg_url', ''))
                    self.text_url1.delete("1.0", END); self.text_url1.insert("1.0", ch['url'])
                else:
                    self.entry_name2.delete(0, END); self.entry_name2.insert(0, ch['name'])
                    self.entry_group2.delete(0, END); self.entry_group2.insert(0, ch['group'])
                    self.entry_tvgurl2.delete(0, END); self.entry_tvgurl2.insert(0, ch.get('tvg_url', ''))
                    self.text_url2.delete("1.0", END); self.text_url2.insert("1.0", ch['url'])
                break

    def add_new_channel(self, p_num):
        if p_num == 1:
            name, group, tvgurl, url, channels = self.entry_name1.get().strip(), self.entry_group1.get().strip() or "General", self.entry_tvgurl1.get().strip(), self.text_url1.get("1.0", END).strip(), self.channels_p1
        else:
            name, group, tvgurl, url, channels = self.entry_name2.get().strip(), self.entry_group2.get().strip() or "General", self.entry_tvgurl2.get().strip(), self.text_url2.get("1.0", END).strip(), self.channels_p2
        if name and url:
            self.save_state_to_history(p_num)
            channels.append({'name': name, 'group': group, 'tvg_url': tvgurl, 'url': url})
            self.refresh_channel_view_keeping_category_and_highlight(p_num, group, name)

    def update_channel(self, p_num):
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        sel = chan_box.curselection()
        if not sel: return
        old_name = chan_box.get(sel[0])
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        new_group = self.entry_group1.get().strip() or "General" if p_num == 1 else self.entry_group2.get().strip() or "General"
        new_name = self.entry_name1.get().strip() if p_num == 1 else self.entry_name2.get().strip()
        new_tvgurl = self.entry_tvgurl1.get().strip() if p_num == 1 else self.entry_tvgurl2.get().strip()
        new_url = self.text_url1.get("1.0", END).strip() if p_num == 1 else self.text_url2.get("1.0", END).strip()

        self.save_state_to_history(p_num)
        for ch in channels:
            if ch['name'] == old_name:
                ch['name'], ch['group'], ch['tvg_url'], ch['url'] = new_name, new_group, new_tvgurl, new_url
                break
        self.refresh_channel_view_keeping_category_and_highlight(p_num, new_group, new_name)

    def delete_selected_item(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        chan_sel = chan_box.curselection()
        cat_sel = cat_box.curselection()
        
        if chan_sel:
            self.save_state_to_history(p_num)
            names = [chan_box.get(i) for i in chan_sel]
            current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
            
            if p_num == 1:
                self.channels_p1 = [ch for ch in self.channels_p1 if ch['name'] not in names]
            else:
                self.channels_p2 = [ch for ch in self.channels_p2 if ch['name'] not in names]
                
            self.refresh_channel_view_keeping_category_and_highlight(p_num, current_cat, None)
            
        elif cat_sel:
            cat_name = cat_box.get(cat_sel[0])
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{cat_name}' and all its channels?"):
                self.save_state_to_history(p_num)
                if p_num == 1:
                    self.channels_p1 = [ch for ch in self.channels_p1 if ch['group'] != cat_name]
                    self.populate_categories(1)
                else:
                    self.channels_p2 = [ch for ch in self.channels_p2 if ch['group'] != cat_name]
                    self.populate_categories(2)

    def refresh_channel_view_keeping_category_and_highlight(self, p_num, category_name, highlight_channel_name):
        self.populate_categories(p_num)
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        if category_name:
            cats = cat_box.get(0, END)
            if category_name in cats:
                idx = cats.index(category_name)
                cat_box.selection_set(idx)
                cat_box.see(idx)
                
                chan_box.delete(0, END)
                ch_names = []
                for ch in channels:
                    if ch['group'] == category_name:
                        ch_names.append(ch['name'])
                        chan_box.insert(END, ch['name'])
                
                if highlight_channel_name in ch_names:
                    c_idx = ch_names.index(highlight_channel_name)
                    chan_box.selection_set(c_idx)
                    chan_box.see(c_idx)
                    self.load_channel_details_by_name(p_num, highlight_channel_name)

    def refresh_channel_view_keeping_selection(self, p_num, category_name, channel_name):
        self.refresh_channel_view_keeping_category_and_highlight(p_num, category_name, channel_name)

    def create_ghost_window(self, text):
        if self.drag_window: self.drag_window.destroy()
        self.drag_window = Toplevel(self.parent)
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-alpha', 0.75)
        self.drag_window.attributes('-topmost', True)
        Label(self.drag_window, text=f" {text} ", bg="#FF9800", fg="white", font=("Arial", 8, "bold")).pack()

    def on_drag_motion(self, event):
        if self.drag_window:
            self.drag_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

    def destroy_ghost_window(self):
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None

    def on_cat_click(self, event, p_num):
        box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        idx = box.nearest(event.y)
        if idx >= 0:
            box.selection_clear(0, END); box.selection_set(idx); box.activate(idx)
            cat_name = box.get(idx)
            self.drag_data = {"item": cat_name, "source_p": p_num, "type": "cat"}
            self.create_ghost_window(cat_name)
            self.on_category_select(p_num)

    def on_cat_drop(self, event, p_num):
        self.destroy_ghost_window()
        if self.drag_data["type"] != "cat" or self.drag_data["source_p"] != p_num: return
        target_cat_box = self.cat_listbox2 if p_num == 1 else self.cat_listbox1
        bx, by, bw, bh = target_cat_box.winfo_rootx(), target_cat_box.winfo_rooty(), target_cat_box.winfo_width(), target_cat_box.winfo_height()
        
        if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
            cat_name = self.drag_data["item"]
            target_p = 2 if p_num == 1 else 1
            self.save_state_to_history(target_p)
            source_channels = self.channels_p1 if p_num == 1 else self.channels_p2
            target_channels = self.channels_p2 if p_num == 1 else self.channels_p1
            
            for ch in source_channels:
                if ch['group'] == cat_name:
                    target_channels.append(ch.copy())
            self.refresh_channel_view_keeping_category_and_highlight(target_p, cat_name, None)

    def on_chan_click(self, event, p_num):
        box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        idx = box.nearest(event.y)
        if idx >= 0:
            is_ctrl_pressed = (event.state & 0x0004) != 0
            if is_ctrl_pressed:
                if idx in box.curselection():
                    box.selection_clear(idx)
                else:
                    box.selection_set(idx)
            else:
                box.selection_clear(0, END)
                box.selection_set(idx)
                box.activate(idx)
                
            sel = box.curselection()
            cat_sel = cat_box.curselection()
            if sel:
                c_name = box.get(sel[-1])
                self.load_channel_details_by_name(p_num, c_name)
                self.drag_data = {"item": c_name, "source_p": p_num, "type": "chan"}
                self.create_ghost_window(c_name)

    def on_chan_drop(self, event, p_num):
        self.destroy_ghost_window()
        if self.drag_data["type"] != "chan" or self.drag_data["source_p"] != p_num: return
        
        target_chan_box = self.chan_listbox2 if p_num == 1 else self.chan_listbox1
        bx, by, bw, bh = target_chan_box.winfo_rootx(), target_chan_box.winfo_rooty(), target_chan_box.winfo_width(), target_chan_box.winfo_height()
        
        if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
            self.execute_drag_drop_channel(p_num)

    def execute_drag_drop_channel(self, source_p):
        target_p = 2 if source_p == 1 else 1
        chan_name = self.drag_data["item"]
        source_channels = self.channels_p1 if source_p == 1 else self.channels_p2
        target_channels = self.channels_p2 if source_p == 1 else self.channels_p1
        
        target_cat_box = self.cat_listbox2 if source_p == 1 else self.cat_listbox1
        target_cat_sel = target_cat_box.curselection()
        target_group = target_cat_box.get(target_cat_sel[0]) if target_cat_sel else "General"
        
        self.save_state_to_history(target_p)
        
        found_ch = None
        for ch in source_channels:
            if ch['name'] == chan_name:
                found_ch = ch.copy()
                break
                
        if found_ch:
            found_ch['group'] = target_group
            target_channels.append(found_ch)
            self.refresh_channel_view_keeping_category_and_highlight(target_p, target_group, found_ch['name'])

    def copy_selection_to_other(self, source_p):
        target_p = 2 if source_p == 1 else 1
        
        cat_box = self.cat_listbox1 if source_p == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if source_p == 1 else self.chan_listbox2
        
        chan_sel = chan_box.curselection()
        cat_sel = cat_box.curselection()
        
        source_channels = self.channels_p1 if source_p == 1 else self.channels_p2
        target_channels = self.channels_p2 if source_p == 1 else self.channels_p1
        
        if chan_sel:
            self.save_state_to_history(target_p)
            names = [chan_box.get(i) for i in chan_sel]
            
            target_cat_box = self.cat_listbox2 if source_p == 1 else self.cat_listbox1
            target_cat_sel = target_cat_box.curselection()
            target_group = target_cat_box.get(target_cat_sel[0]) if target_cat_sel else "General"
            
            last_copied_name = None
            for name in names:
                for ch in source_channels:
                    if ch['name'] == name:
                        new_ch = ch.copy()
                        new_ch['group'] = target_group
                        target_channels.append(new_ch)
                        last_copied_name = new_ch['name']
                        
            self.refresh_channel_view_keeping_category_and_highlight(target_p, target_group, last_copied_name)
            
        elif cat_sel:
            cat_name = cat_box.get(cat_sel[0])
            self.save_state_to_history(target_p)
            
            copied_count = 0
            for ch in source_channels:
                if ch['group'] == cat_name:
                    target_channels.append(ch.copy())
                    copied_count += 1
                    
            if copied_count > 0:
                self.refresh_channel_view_keeping_category_and_highlight(target_p, cat_name, None)
                messagebox.showinfo("Success", f"Category '{cat_name}' with {copied_count} channel(s) copied to Playlist {target_p}!")
            else:
                messagebox.showwarning("Warning", f"No channels found in category '{cat_name}'!")
        else:
            messagebox.showwarning("Warning", "Please select a Category or Channel(s) first!")

    def save_m3u(self, p_num):
        file_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U Files", "*.m3u"), ("All Files", "*.*")])
        if not file_path: return
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for ch in channels:
                    tvg_val = ch.get('tvg_url', '')
                    f.write(f"#EXTINF:-1 tvg-url=\"{tvg_val}\" group-title=\"{ch['group']}\",{ch['name']}\n{ch['url']}\n")
            messagebox.showinfo("Success", f"Playlist {p_num} saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Initialize Dual M3U Editor inside tab_m3u_editor frame
dual_m3u_app = EmbeddedM3UEditor(tab_m3u_editor)


# ==========================================
# 📺 LIVE STATUS & TERMINAL
# ==========================================

terminal_frame = tk.Frame(root, bg=CARD_COLOR, bd=1, relief=tk.SOLID)
terminal_frame.pack(fill=tk.X, padx=10, pady=(2, 2))

term_title = tk.Label(terminal_frame, text="💻 SYSTEM & ACTIVATION NOTICE", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg="#ffcc00")
term_title.pack(anchor="w", padx=6, pady=(2, 0))

status_terminal = tk.Text(terminal_frame, height=3.5, font=("Consolas", 8), bg=BG_COLOR, fg="#ff9900", relief=tk.FLAT)
status_terminal.pack(fill=tk.X, padx=4, pady=(0, 2))

initial_notice = (
    f"⚠️ Software is Unregistered / Locked!\n"
    f"• Your PC Hardware ID: {current_hwid}\n"
    f"⚠️ No internet connection!\nPlease connect to the internet to view activation instructions."
)
status_terminal.insert(tk.END, initial_notice)
status_terminal.config(state=tk.DISABLED)

def fetch_remote_notice():
    if not GOOGLE_SCRIPT_URL or "আপনার_গুগল_শিটের" in GOOGLE_SCRIPT_URL or is_activated:
        return
    try:
        payload = {
            "action": "get_notice",
            "hardware_id": current_hwid
        }
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            server_notice = res_data.get("notice")
            if server_notice and not is_activated:
                status_terminal.config(state=tk.NORMAL)
                status_terminal.delete("1.0", tk.END)
                full_text = f"⚠️ Hardware ID: {current_hwid}\n{server_notice}"
                status_terminal.insert(tk.END, full_text)
                status_terminal.config(state=tk.DISABLED)
    except Exception as e:
        print(f"Failed to fetch remote notice: {e}")

def check_startup_activation():
    global is_activated
    if not GOOGLE_SCRIPT_URL:
        return
    try:
        payload = {
            "action": "check_activation",
            "hardware_id": current_hwid
        }
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("status") == "success":
                expiry_str = res_data.get('expiry')
                try:
                    expiry_date = datetime.strptime(expiry_str.strip(), "%Y-%m-%d").date()
                    current_date = datetime.now().date()
                    
                    if current_date <= expiry_date:
                        is_activated = True
                        status_terminal.config(state=tk.NORMAL)
                        success_msg = f"🎉 Software Activated Successfully!\n• Hardware ID: {current_hwid}\n• Valid Until (Expiry Date): {expiry_str}"
                        status_terminal.delete("1.0", tk.END)
                        status_terminal.insert(tk.END, success_msg)
                        status_terminal.config(fg="#00ffcc", state=tk.DISABLED)
                        
                        license_entry.config(state=tk.NORMAL)
                        license_entry.delete(0, tk.END)
                        license_entry.insert(0, "Activated")
                        license_entry.config(state=tk.DISABLED)
                        
                        activate_btn.config(state=tk.DISABLED, bg="#555555")
                        return
                except Exception as ex:
                    print(f"Date check error: {ex}")
            
            is_activated = False
            status_terminal.config(state=tk.NORMAL)
            status_terminal.delete("1.0", tk.END)
            status_terminal.config(state=tk.DISABLED)
            threading.Thread(target=fetch_remote_notice, daemon=True).start()
            
            license_entry.config(state=tk.NORMAL)
            license_entry.delete(0, tk.END)
            license_entry.insert(0, "Enter Activation Key...")
            activate_btn.config(state=tk.NORMAL, bg="#f6c23e")
    except Exception as e:
        print(f"Startup activation check failed: {e}")
        threading.Thread(target=fetch_remote_notice, daemon=True).start()

threading.Thread(target=check_startup_activation, daemon=True).start()


# ==========================================
# 🔑 ACTIVATION & LICENSE PANEL
# ==========================================

activation_frame = tk.Frame(root, bg=CARD_COLOR, bd=1, relief=tk.SOLID)
activation_frame.pack(fill=tk.X, padx=10, pady=(0, 2))

act_title = tk.Label(activation_frame, text="🔒 SOFTWARE LICENSE & ACTIVATION", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg="#ffcc00")
act_title.pack(anchor="w", padx=6, pady=(2, 1))

act_sub_frame = tk.Frame(activation_frame, bg=CARD_COLOR)
act_sub_frame.pack(fill=tk.X, padx=6, pady=(0, 3))

license_entry = tk.Entry(act_sub_frame, font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR, insertbackground="white", relief=tk.FLAT)
license_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2, padx=(0, 4))
license_entry.insert(0, "Enter Activation Key...")

def verify_license():
    global is_activated
    key = license_entry.get().strip()
    
    if key == "" or key == "Enter Activation Key..." or key == "Activated":
        messagebox.showwarning("Warning", "Please enter a valid activation key.")
        return
    
    payload = {
        "action": "activate",
        "license_key": key,
        "hardware_id": current_hwid
    }
    
    try:
        status_terminal.config(state=tk.NORMAL)
        status_terminal.delete("1.0", tk.END)
        status_terminal.insert(tk.END, "Verifying license key & syncing hardware ID...\n")
        status_terminal.config(state=tk.DISABLED)

        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        res_data = response.json()
        
        status_terminal.config(state=tk.NORMAL)
        if res_data.get("status") == "success":
            is_activated = True  
            success_msg = f"🎉 CONGRATULATIONS! Software Activated Successfully!\nHardware ID: {current_hwid}\nExpires on: {res_data.get('expiry')}\n"
            status_terminal.insert(tk.END, success_msg)
            status_terminal.config(fg="#00ffcc")
            messagebox.showinfo("Activated", success_msg)
            
            license_entry.config(state=tk.NORMAL)
            license_entry.delete(0, tk.END)
            license_entry.insert(0, "Activated")
            license_entry.config(state=tk.DISABLED)
            
            activate_btn.config(state=tk.DISABLED, bg="#555555")
        else:
            is_activated = False
            err_msg = f"❌ Error: {res_data.get('message', 'Invalid Key!')}\n• Hardware ID: {current_hwid}\n"
            status_terminal.insert(tk.END, err_msg)
            messagebox.showerror("Activation Failed", res_data.get("message", "Invalid License Key!"))
        status_terminal.config(state=tk.DISABLED)
    except Exception as e:
        status_terminal.config(state=tk.NORMAL)
        status_terminal.insert(tk.END, f"❌ Connection Error: {str(e)}\n• Hardware ID: {current_hwid}\n")
        status_terminal.config(state=tk.DISABLED)
        messagebox.showerror("Connection Error", f"Could not connect to activation server: {str(e)}")

activate_btn = tk.Button(act_sub_frame, text="Activate Now", font=("Segoe UI", 8, "bold"), bg="#f6c23e", fg="#333333", relief=tk.FLAT, cursor="hand2", command=verify_license)
activate_btn.pack(side=tk.RIGHT, ipadx=6, ipady=2)


# -----------------------------
# DEVELOPER / COPYRIGHT FOOTER
# -----------------------------

footer_frame = tk.Frame(root, bg="#161622", height=28)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

footer_text = "Developed by Tapas Mondal | Mail: tapas3opl@gmail.com | Call +8801710697461"
footer_label = tk.Label(footer_frame, text=footer_text, font=("Segoe UI", 7, "bold"), bg="#161622", fg="#8a99ad", justify=tk.CENTER)
footer_label.pack(pady=2)

show_xtream_tab()

root.mainloop()