import os
import sys
import ctypes
import urllib.request
from tkinter import Tk, Label, Button, Listbox, Scrollbar, Entry, Text, END, WORD, filedialog, messagebox, Frame, BOTH, LEFT, RIGHT, VERTICAL, X, Y, Toplevel
from concurrent.futures import ThreadPoolExecutor, as_completed

# উইন্ডো বা প্রসেস তৈরির আগেই টাস্কবার আইকনের জন্য AppUserModelID সেট করা
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TapasMondal.AllInOneIPTVManager.App.v3")
except Exception:
    pass

class AllInOneIPTVManager:
    def __init__(self, root):
        self.root = root
        self.root.title("All-in-One IPTV Management Suite - Dual M3U Editor By Tapas")
        self.root.geometry("780x850")
        self.root.configure(bg="#1e1e2f")
        
        # টাইটেল বার এবং টাস্কবারের জন্য iconbitmap সেটআপ (Exe এবং লোকাল রান উভয়ক্ষেত্রের জন্য)
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                icon_path = "icon.ico"
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # উইন্ডোজ নেটিভ টাইটেল বারের কালার পরিবর্তন করার জন্য (উইন্ডোজ ১১)
        try:
            HWND = ctypes.windll.user32.GetParent(self.root.winfo_id())
            COLOR = 0x228B22  # BGR ফরম্যাটে কালার কোড (#2d2d44)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 35, ctypes.byref(ctypes.c_int(COLOR)), 4)
        except Exception:
            pass
        
        self.active_panel = 1
        
        # Footer Frame at the bottom
        footer_frame = Frame(root, bg="#1e1e2f")
        footer_frame.pack(side="bottom", fill=X, padx=4, pady=2)
        Label(footer_frame, text="Developed by Tapas Mondal | Mail: tapas3opl@gmail.com | Call +8801710697461", bg="#1e1e2f", fg="#888888", font=("Arial", 8, "italic")).pack(anchor="center")
        
        container = Frame(root, bg="#1e1e2f")
        container.pack(side="top", fill=BOTH, expand=True, padx=4, pady=4)
        
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        self.channels_p1 = []
        self.channels_p2 = []
        
        # Undo / Redo History Stacks
        self.history_p1 = []
        self.redo_p1 = []
        self.history_p2 = []
        self.redo_p2 = []
        
        self.drag_window = None
        self.drag_data = {"item": None, "source_p": None, "type": None, "category": None}
        
        # Editor One (Left Panel)
        self.frame_left = Frame(container, bg="#2b2b40", bd=1, relief="solid")
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.setup_editor_panel(self.frame_left, 1, "📁 M3U Playlist Editor One")
        self.frame_left.bind('<FocusIn>', lambda e: setattr(self, 'active_panel', 1))
        
        # Editor Two (Right Panel)
        self.frame_right = Frame(container, bg="#2b2b40", bd=1, relief="solid")
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.setup_editor_panel(self.frame_right, 2, "📁 M3U Playlist Editor Two")
        self.frame_right.bind('<FocusIn>', lambda e: setattr(self, 'active_panel', 2))
        
        # Global Keyboard Shortcuts Bindings (Works anywhere in the window)
        self.bind_global_shortcuts()

    def bind_global_shortcuts(self):
        self.root.bind('<Control-z>', lambda e: self.perform_undo(self.active_panel))
        self.root.bind('<Control-Z>', lambda e: self.perform_undo(self.active_panel))
        self.root.bind('<Control-y>', lambda e: self.perform_redo(self.active_panel))
        self.root.bind('<Control-Y>', lambda e: self.perform_redo(self.active_panel))
        self.root.bind('<Control-Shift-Z>', lambda e: self.perform_redo(self.active_panel))
        self.root.bind('<Control-Shift-z>', lambda e: self.perform_redo(self.active_panel))

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
        if current_chan and " [" in current_chan:
            current_chan = current_chan.split(" [")[0]

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
        if current_chan and " [" in current_chan:
            current_chan = current_chan.split(" [")[0]

        if p_num == 1 and self.redo_p1:
            self.history_p1.append([ch.copy() for ch in self.channels_p1])
            self.channels_p1 = self.redo_p1.pop()
            self.refresh_channel_view_keeping_selection(1, current_cat, current_chan)
        elif p_num == 2 and self.redo_p2:
            self.history_p2.append([ch.copy() for ch in self.channels_p2])
            self.channels_p2 = self.redo_p2.pop()
            self.refresh_channel_view_keeping_selection(2, current_cat, current_chan)

    def setup_editor_panel(self, parent_frame, p_num, title_text):
        header_frame = Frame(parent_frame, bg="#2b2b40")
        header_frame.pack(fill=X, padx=4, pady=3)
        
        Label(header_frame, text=title_text, bg="#2b2b40", fg="#4CAF50", font=("Arial", 9, "bold")).pack(side=LEFT)
        
        Button(header_frame, text="Redo ↪", command=lambda: self.perform_redo(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        Button(header_frame, text="Undo ↩", command=lambda: self.perform_undo(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        
        top_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        top_frame.pack(fill=X)
        
        Button(top_frame, text="Open", command=lambda: self.load_m3u_file(p_num), bg="#4CAF50", fg="white", font=("Arial", 8), relief="flat", padx=4, pady=1).pack(side=LEFT, padx=1)
        
        # Added M3U URL Label and Entry Box setup
        Label(top_frame, text="M3U URL:", bg="#2b2b40", fg="#FF5722", font=("Arial", 8)).pack(side=LEFT, padx=(4, 2))
        entry_url = Entry(top_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        entry_url.pack(side=LEFT, padx=2, fill=X, expand=True)
        
        Button(top_frame, text="Load", command=lambda: self.load_m3u_url(p_num), bg="#FF5722", fg="white", font=("Arial", 8), relief="flat", padx=4, pady=1).pack(side=LEFT, padx=1)
        Button(top_frame, text="Save", command=lambda: self.save_m3u(p_num), bg="#2196F3", fg="white", font=("Arial", 8), relief="flat", padx=6, pady=1).pack(side=RIGHT, padx=1)
        
        # External Player Path Setup Frame
        player_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=1)
        player_frame.pack(fill=X)
        Label(player_frame, text="Player:", bg="#2b2b40", fg="#00bcd4", font=("Arial", 8)).pack(side=LEFT, padx=(0, 4))
        entry_player = Entry(player_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        entry_player.pack(side=LEFT, fill=X, expand=True, padx=(0, 2))
        entry_player.insert(0, r"C:\Program Files\VideoLAN\VLC\vlc.exe")
        Button(player_frame, text="Browse", command=lambda: self.browse_player(p_num), bg="#607D8B", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=LEFT)

        search_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        search_frame.pack(fill=X, padx=2)
        Label(search_frame, text="Search:", bg="#2b2b40", fg="#FF9800", font=("Arial", 8)).pack(side=LEFT, padx=(0, 4))
        entry_search = Entry(search_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
        entry_search.pack(side=LEFT, fill=X, expand=True)
        entry_search.bind('<KeyRelease>', lambda e, p=p_num: self.live_auto_search(p))
        
        if p_num == 1: 
            self.entry_url1 = entry_url
            self.entry_search1 = entry_search
            self.entry_player1 = entry_player
        else: 
            self.entry_url2 = entry_url
            self.entry_search2 = entry_search
            self.entry_player2 = entry_player

        lists_frame = Frame(parent_frame, bg="#2b2b40", padx=2, pady=2)
        lists_frame.pack(fill=BOTH, expand=True)
        
        cat_frame = Frame(lists_frame, bg="#2b2b40")
        cat_frame.pack(side=LEFT, fill=Y, expand=False, padx=(0, 2))
        Label(cat_frame, text="Categories", bg="#2b2b40", fg="white", font=("Arial", 8, "bold")).pack(anchor="w")
        
        cat_listbox = Listbox(cat_frame, width=18, font=("Arial", 8), bg="#1e1e2f", fg="white", selectbackground="#4CAF50", exportselection=False, relief="solid", bd=1)
        cat_listbox.pack(side=LEFT, fill=Y, pady=2)
        cat_scroll = Scrollbar(cat_frame, orient=VERTICAL, command=cat_listbox.yview, width=12)
        cat_scroll.pack(side=RIGHT, fill=Y)
        cat_listbox.config(yscrollcommand=cat_scroll.set)
        
        cat_listbox.bind('<Button-1>', lambda e, p=p_num: self.on_cat_click(e, p))
        cat_listbox.bind('<B1-Motion>', lambda e, p=p_num: self.on_drag_motion(e))
        cat_listbox.bind('<ButtonRelease-1>', lambda e, p=p_num: self.on_cat_drop(e, p))
        cat_listbox.bind('<Delete>', lambda e, p=p_num: self.delete_selected_item(p))
        cat_listbox.bind('<BackSpace>', lambda e, p=p_num: self.delete_selected_item(p))

        chan_frame = Frame(lists_frame, bg="#2b2b40")
        chan_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        chan_top = Frame(chan_frame, bg="#2b2b40")
        chan_top.pack(fill=X)
        Label(chan_top, text="Channels", bg="#2b2b40", fg="white", font=("Arial", 8, "bold")).pack(side=LEFT)
        
        Button(chan_top, text="Delete", command=lambda: self.delete_selected_item(p_num), bg="#f44336", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        Button(chan_top, text="Del Dead", command=lambda: self.delete_dead_channels(p_num), bg="#E91E63", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        Button(chan_top, text="Play", command=lambda: self.play_in_external_player(p_num), bg="#FF9800", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        Button(chan_top, text="Check Status", command=lambda: self.check_channels_status(p_num), bg="#009688", fg="white", font=("Arial", 7), relief="flat", padx=3, pady=0).pack(side=RIGHT, padx=1)
        
        chan_listbox = Listbox(chan_frame, font=("Arial", 8), bg="#1e1e2f", fg="white", selectbackground="#4CAF50", exportselection=False, relief="solid", bd=1)
        chan_listbox.pack(side=LEFT, fill=BOTH, expand=True, pady=2)
        chan_scroll = Scrollbar(chan_frame, orient=VERTICAL, command=chan_listbox.yview, width=12)
        chan_scroll.pack(side=RIGHT, fill=Y)
        chan_listbox.config(yscrollcommand=chan_scroll.set)
        
        chan_listbox.bind('<Button-1>', lambda e, p=p_num: self.on_chan_click(e, p))
        chan_listbox.bind('<Double-Button-1>', lambda e, p=p_num: self.play_in_external_player(p))
        chan_listbox.bind('<B1-Motion>', lambda e, p=p_num: self.on_drag_motion(e))
        chan_listbox.bind('<ButtonRelease-1>', lambda e, p=p_num: self.on_chan_drop(e, p))
        chan_listbox.bind('<Delete>', lambda e, p=p_num: self.delete_selected_item(p))
        chan_listbox.bind('<BackSpace>', lambda e, p=p_num: self.delete_selected_item(p))

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
            Label(row, text=label_text, bg="#242438", fg="white", font=("Arial", 8), width=8, anchor="w").pack(side=LEFT)
            ent = Entry(row, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1)
            ent.pack(side=LEFT, fill=X, expand=True)
            return ent
            
        entry_name = add_entry_row("Name:")
        entry_group = add_entry_row("Category:")
        entry_tvgurl = add_entry_row("TVG URL:") 
        
        row4 = Frame(edit_frame, bg="#242438")
        row4.pack(fill=X, pady=1)
        Label(row4, text="URL:", bg="#242438", fg="white", font=("Arial", 8), width=8, anchor="w").pack(side=LEFT)
        text_url = Text(row4, height=2, font=("Arial", 8), bg="#1e1e2f", fg="white", insertbackground="white", relief="solid", bd=1, wrap=WORD)
        text_url.pack(side=LEFT, fill=X, expand=True)
        
        btn_row = Frame(edit_frame, bg="#242438")
        btn_row.pack(fill=X, pady=4)
        
        if p_num == 1:
            self.entry_name1, self.entry_group1, self.entry_tvgurl1, self.text_url1 = entry_name, entry_group, entry_tvgurl, text_url
            Button(btn_row, text="Add", command=lambda: self.add_new_channel(1), bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Update", command=lambda: self.update_channel(1), bg="#FF9800", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Copy to P2", command=lambda: self.copy_selection_to_other(1), bg="#9C27B0", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)
        else:
            self.entry_name2, self.entry_group2, self.entry_tvgurl2, self.text_url2 = entry_name, entry_group, entry_tvgurl, text_url
            Button(btn_row, text="Add", command=lambda: self.add_new_channel(2), bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Update", command=lambda: self.update_channel(2), bg="#FF9800", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)
            Button(btn_row, text="Copy to P1", command=lambda: self.copy_selection_to_other(2), bg="#9C27B0", fg="white", font=("Arial", 8, "bold"), relief="flat").pack(side=LEFT, fill=X, expand=True, padx=2)

    def delete_selected_item(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        cat_sel = cat_box.curselection()
        chan_sel = chan_box.curselection()
        
        if not cat_sel and not chan_sel:
            return
            
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        self.save_state_to_history(p_num)
        
        if chan_sel:
            # সুনির্দিষ্টভাবে শুধু সিলেক্ট করা ক্যাটাগরির নির্দিষ্ট চ্যানেলটিই ডিলিট হবে
            selected_chan_text = chan_box.get(chan_sel[0])
            if selected_chan_text and " [" in selected_chan_text:
                chan_name = selected_chan_text.split(" [")[0]
            else:
                chan_name = selected_chan_text
                
            new_channels = []
            removed = False
            for ch in channels:
                group = ch.get('group', 'Uncategorized')
                name = ch.get('name', '')
                # ক্যাটাগরি এবং চ্যানেলের নাম দুটোই ম্যাচ করতে হবে
                if not removed and current_cat and group == current_cat and name == chan_name:
                    removed = True
                    continue
                new_channels.append(ch)
                
            if p_num == 1:
                self.channels_p1 = new_channels
            else:
                self.channels_p2 = new_channels
                
        elif cat_sel and current_cat:
            # যদি শুধু ক্যাটাগরি সিলেক্ট করে ডিলিট করা হয়, তবে শুধু ওই ক্যাটাগরির চ্যানেলগুলোই মুছবে
            new_channels = [ch for ch in channels if ch.get('group', 'Uncategorized') != current_cat]
            if p_num == 1:
                self.channels_p1 = new_channels
            else:
                self.channels_p2 = new_channels
                
        # ভিউ রিফ্রেশ করা
        if hasattr(self, 'refresh_channel_view_keeping_selection'):
            self.refresh_channel_view_keeping_selection(p_num, current_cat, None)
        else:
            # যদি মেথডটি অন্য নামে থাকে, তবে ক্যাটাগরি ক্লিক ইভেন্ট কল করে রিফ্রেশ করুন
            if p_num == 1 and hasattr(self, 'load_channels_for_category1'):
                self.load_channels_for_category1(current_cat)
            elif p_num == 2 and hasattr(self, 'load_channels_for_category2'):
                self.load_channels_for_category2(current_cat)
    def browse_player(self, p_num):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        if file_path:
            ent = self.entry_player1 if p_num == 1 else self.entry_player2
            ent.delete(0, END)
            ent.insert(0, file_path)

    def play_in_external_player(self, p_num):
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        sel = chan_box.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a channel to play!")
            return
        c_name = chan_box.get(sel[0])
        if " [" in c_name:
            c_name = c_name.split(" [")[0]
        
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        url = ""
        for ch in channels:
            if ch['name'] == c_name:
                url = ch['url']
                break
        
        if not url:
            return
            
        player_path = self.entry_player1.get().strip() if p_num == 1 else self.entry_player2.get().strip()
        if not player_path or not os.path.exists(player_path):
            messagebox.showerror("Error", "Please select a valid external player executable path (e.g., VLC .exe)!")
            return
            
        try:
            subprocess.Popen([player_path, url])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch player: {str(e)}")

    def delete_selected_item(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        cat_sel = cat_box.curselection()
        chan_sel = chan_box.curselection()
        
        if not cat_sel and not chan_sel:
            return
            
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        from tkinter import messagebox
        
        if chan_sel:
            selected_chan_text = chan_box.get(chan_sel[0])
            if selected_chan_text and " [" in selected_chan_text:
                chan_name = selected_chan_text.split(" [")[0]
            else:
                chan_name = selected_chan_text
                
            # কনফার্মেশন পপআপ মেসেজ
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the channel '{chan_name}' from category '{current_cat}'?")
            if not confirm:
                return
                
            self.save_state_to_history(p_num)
            
            new_channels = []
            removed = False
            for ch in channels:
                group = ch.get('group', 'Uncategorized')
                name = ch.get('name', '')
                if not removed and current_cat and group == current_cat and name == chan_name:
                    removed = True
                    continue
                new_channels.append(ch)
                
            if p_num == 1:
                self.channels_p1 = new_channels
            else:
                self.channels_p2 = new_channels
                
        elif cat_sel and current_cat:
            # ক্যাটাগরির ভেতরের মোট চ্যানেল সংখ্যা গণনা করা
            cat_channels = [ch for ch in channels if ch.get('group', 'Uncategorized') == current_cat]
            count = len(cat_channels)
            
            if count == 0:
                return
                
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete all {count} channel(s) in category '{current_cat}'?")
            if not confirm:
                return
                
            self.save_state_to_history(p_num)
            
            new_channels = [ch for ch in channels if ch.get('group', 'Uncategorized') != current_cat]
            if p_num == 1:
                self.channels_p1 = new_channels
            else:
                self.channels_p2 = new_channels
                
        # ভিউ রিফ্রেশ করা
        if hasattr(self, 'refresh_channel_view_keeping_selection'):
            self.refresh_channel_view_keeping_selection(p_num, current_cat, None)
        else:
            if p_num == 1 and hasattr(self, 'load_channels_for_category1'):
                self.load_channels_for_category1(current_cat)
            elif p_num == 2 and hasattr(self, 'load_channels_for_category2'):
                self.load_channels_for_category2(current_cat)

    def delete_dead_channels(self, p_num):
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        cat_sel = cat_box.curselection()
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        if not current_cat:
            return
            
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        
        # নির্দিষ্ট ক্যাটাগরির ভেতরের ডেড চ্যানেলগুলো ফিল্টার করা
        dead_in_cat = []
        for ch in channels:
            group = ch.get('group', 'Uncategorized')
            is_dead = (ch.get('status') == 'Dead' or ch.get('is_dead') == True)
            if group == current_cat and is_dead:
                dead_in_cat.append(ch)
                
        count = len(dead_in_cat)
        if count == 0:
            from tkinter import messagebox
            messagebox.showinfo("Info", f"No dead channels found in category '{current_cat}'.")
            return
            
        from tkinter import messagebox
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete all {count} dead channel(s) in category '{current_cat}'?")
        if not confirm:
            return
            
        self.save_state_to_history(p_num)
        
        new_channels = []
        for ch in channels:
            group = ch.get('group', 'Uncategorized')
            is_dead = (ch.get('status') == 'Dead' or ch.get('is_dead') == True)
            
            if group == current_cat and is_dead:
                continue 
            new_channels.append(ch)
            
        if p_num == 1:
            self.channels_p1 = new_channels
        else:
            self.channels_p2 = new_channels
            
        if hasattr(self, 'refresh_channel_view_keeping_selection'):
            self.refresh_channel_view_keeping_selection(p_num, current_cat, None)
        else:
            if p_num == 1 and hasattr(self, 'load_channels_for_category1'):
                self.load_channels_for_category1(current_cat)
            elif p_num == 2 and hasattr(self, 'load_channels_for_category2'):
                self.load_channels_for_category2(current_cat)
    def check_channels_status(self, p_num):
        channels = self.channels_p1 if p_num == 1 else self.channels_p2
        if not channels:
            messagebox.showwarning("Warning", "No channels to check!")
            return
        
        cat_box = self.cat_listbox1 if p_num == 1 else self.cat_listbox2
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        
        cat_sel = cat_box.curselection()
        current_cat = cat_box.get(cat_sel[0]) if cat_sel else None
        
        chan_sel = chan_box.curselection()
        current_chan = chan_box.get(chan_sel[0]) if chan_sel else None
        if current_chan and " [" in current_chan:
            current_chan = current_chan.split(" [")[0]

        for ch in channels:
            ch['status'] = 'Checking...'
        self.refresh_channel_view_keeping_selection(p_num, current_cat, current_chan)
        
        def run_check():
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(self._verify_url, ch['url'], p_num): ch for ch in channels}
                for future in as_completed(futures):
                    ch = futures[future]
                    try:
                        ch['status'] = 'Active' if future.result() else 'Dead'
                    except Exception:
                        ch['status'] = 'Dead'
            
            self.root.after(0, lambda: self.refresh_channel_view_keeping_selection(p_num, current_cat, current_chan))

        import threading
        threading.Thread(target=run_check, daemon=True).start()

    def _verify_url(self, url, p_num):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'VLC/3.0.16 (Win64)'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status in [200, 206]:
                    content_type = resp.headers.get('Content-Type', '').lower()
                    if 'text/html' in content_type:
                        sample_bytes = resp.read(512).decode('utf-8', errors='ignore').lower()
                        if '<html' in sample_bytes or 'error' in sample_bytes or 'offline' in sample_bytes or 'forbidden' in sample_bytes or 'unauthorized' in sample_bytes or 'expired' in sample_bytes:
                            return False
                    return True
        except Exception:
            pass

        try:
            custom_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Icy-MetaData': '1'
            }
            req = urllib.request.Request(url, headers=custom_headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                chunk = resp.read(2048)
                if len(chunk) > 50:
                    chunk_str = chunk.decode('utf-8', errors='ignore').lower()
                    if '<html' in chunk_str and ('error' in chunk_str or 'login' in chunk_str or 'offline' in chunk_str):
                        return False
                    return True
        except Exception:
            return False

        return False

    def parse_m3u_content(self, content_lines):
        channels = []
        current_ch = {}
        for line in content_lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                current_ch = {}
                current_ch['status'] = 'Unknown'
                if 'tvg-logo="' in line:
                    start = line.find('tvg-logo="') + 10
                    end = line.find('"', start)
                    current_ch['tvg_url'] = line[start:end]
                elif 'tvg-url="' in line:
                    start = line.find('tvg-url="') + 9
                    end = line.find('"', start)
                    current_ch['tvg_url'] = line[start:end]
                elif 'tvg-id="' in line: 
                    start = line.find('tvg-id="') + 8
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
                status = ch.get('status', 'Unknown')
                display_name = f"{ch['name']} [{status}]"
                chan_box.insert(END, display_name)
                idx = chan_box.size() - 1
                if status == 'Active':
                    chan_box.itemconfig(idx, fg="#4CAF50")
                elif status == 'Dead':
                    chan_box.itemconfig(idx, fg="#f44336")
                elif status == 'Checking...':
                    chan_box.itemconfig(idx, fg="#FFEB3B")

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
                status = ch.get('status', 'Unknown')
                display_name = f"{ch['name']} [{status}]"
                chan_box.insert(END, display_name)
                idx = chan_box.size() - 1
                if status == 'Active':
                    chan_box.itemconfig(idx, fg="#4CAF50")
                elif status == 'Dead':
                    chan_box.itemconfig(idx, fg="#f44336")
                elif status == 'Checking...':
                    chan_box.itemconfig(idx, fg="#FFEB3B")

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
            channels.append({'name': name, 'group': group, 'tvg_url': tvgurl, 'url': url, 'status': 'Unknown'})
            self.refresh_channel_view_keeping_category_and_highlight(p_num, group, name)

    def update_channel(self, p_num):
        chan_box = self.chan_listbox1 if p_num == 1 else self.chan_listbox2
        sel = chan_box.curselection()
        if not sel: return
        old_name = chan_box.get(sel[0])
        if " [" in old_name:
            old_name = old_name.split(" [")[0]
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
            names = []
            for i in chan_sel:
                val = chan_box.get(i)
                if " [" in val:
                    val = val.split(" [")[0]
                names.append(val)
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
                        status = ch.get('status', 'Unknown')
                        display_name = f"{ch['name']} [{status}]"
                        chan_box.insert(END, display_name)
                        c_idx = chan_box.size() - 1
                        if status == 'Active':
                            chan_box.itemconfig(c_idx, fg="#4CAF50")
                        elif status == 'Dead':
                            chan_box.itemconfig(c_idx, fg="#f44336")
                        elif status == 'Checking...':
                            chan_box.itemconfig(c_idx, fg="#FFEB3B")
                
                if highlight_channel_name in ch_names:
                    c_idx = ch_names.index(highlight_channel_name)
                    chan_box.selection_set(c_idx)
                    chan_box.see(c_idx)
                    self.load_channel_details_by_name(p_num, highlight_channel_name)

    def refresh_channel_view_keeping_selection(self, p_num, category_name, channel_name):
        self.refresh_channel_view_keeping_category_and_highlight(p_num, category_name, channel_name)

    def create_ghost_window(self, text):
        if self.drag_window: self.drag_window.destroy()
        self.drag_window = Toplevel(self.root)
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
            self.drag_data = {"item": cat_name, "source_p": p_num, "type": "cat", "category": None}
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
                if " [" in c_name:
                    c_name = c_name.split(" [")[0]
                current_cat = cat_box.get(cat_sel[0]) if cat_sel else "General"
                self.load_channel_details_by_name(p_num, c_name)
                self.drag_data = {"item": c_name, "source_p": p_num, "type": "chan", "category": current_cat}
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
            names = []
            for i in chan_sel:
                val = chan_box.get(i)
                if " [" in val:
                    val = val.split(" [")[0]
                names.append(val)
            
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
                    f.write(f"#EXTINF:-1 tvg-logo=\"{tvg_val}\" group-title=\"{ch['group']}\",{ch['name']}\n{ch['url']}\n")
            messagebox.showinfo("Success", f"Playlist {p_num} saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = Tk()
    app = AllInOneIPTVManager(root)
    root.mainloop()