import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, json, tempfile, subprocess
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from PIL import Image, ImageTk
import requests
import webbrowser

# ---------------------- إعدادات التحديث ----------------------
CURRENT_VERSION = "100.1"
UPDATE_URL = "https://github.com/saleh07mohammed-blip/JD_BOY_Macro_Final/releases/download/100.1/JD_BOY_Macro.py"

def auto_update():
    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        tmp_file.close()

        r = requests.get(UPDATE_URL, stream=True, timeout=10)
        if r.status_code != 200:
            messagebox.showerror("تحديث", f"فشل تنزيل النسخة الجديدة. HTTP {r.status_code}")
            return

        with open(tmp_file.name, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        # مسار البرنامج الحالي
        if getattr(sys, 'frozen', False):
            current_file = sys.executable
        else:
            current_file = os.path.abspath(__file__)

        messagebox.showinfo("تحديث", f"تم تنزيل نسخة جديدة ({CURRENT_VERSION}) وسيتم التحديث الآن.")

        # استبدال النسخة القديمة
        os.remove(current_file)
        os.rename(tmp_file.name, current_file)

        # إعادة تشغيل البرنامج
        subprocess.Popen([current_file])
        sys.exit(0)

    except Exception as e:
        messagebox.showerror("تحديث", f"فشل التحديث: {e}")

# ---------------------- شاشة لودينق ----------------------
def show_splash(callback=None):
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("500x300+450+250")
    splash.configure(bg="#1e1e1e")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    logo_path = os.path.join(desktop, "JD_BOY_Macro_Final", "JD_BOY_Macro.png")

    frame_logo = tk.Frame(splash, bg="#1e1e1e")
    frame_logo.pack(expand=True)

    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((96,96))
        logo_img = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(frame_logo, image=logo_img, bg="#1e1e1e")
        lbl_logo.image = logo_img
        lbl_logo.pack(pady=10)
    else:
        lbl_logo = tk.Label(frame_logo, text="JD_BOY", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e")
        lbl_logo.pack(pady=10)

    canvas_width = 400
    canvas_height = 30
    canvas = tk.Canvas(frame_logo, width=canvas_width, height=canvas_height, bg="#333", highlightthickness=0)
    canvas.pack(pady=20)

    progress_bar = canvas.create_rectangle(0,0,0,canvas_height, fill="green", width=0)
    name_text = canvas.create_text(0, canvas_height//2, text="JD_BOY", font=("Arial", 12, "bold"), fill="white", anchor='w')

    splash.update()
    for i in range(101):
        x = int(i * canvas_width / 100)
        canvas.coords(progress_bar, 0, 0, x, canvas_height)
        canvas.coords(name_text, x-40, canvas_height//2)
        splash.update()
        time.sleep(0.02)
    splash.destroy()
    if callback:
        callback()

# ---------------------- Hotkey Recorder ----------------------
class HotkeyRecorder:
    def __init__(self, callback, label_var):
        self.callback = callback
        self.label_var = label_var
        self.recording = False
        self.listener = None

    def start(self):
        if self.recording: return
        self.recording = True
        self.label_var.set("... اضغط أي زر الآن")
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        try: k = key.char
        except: k = str(key)
        self.label_var.set(k)
        self.callback(k)
        self.recording = False
        if self.listener:
            self.listener.stop()

# ---------------------- Macro Recorder ----------------------
class MacroRecorder:
    def __init__(self):
        self.events = []
        self.recording = False
        self.start_time = None
        self.mouse_listener = None
        self.key_listener = None

    def now(self):
        return time.time() - self.start_time if self.start_time else 0

    def start(self):
        if self.recording: return
        self.events = []
        self.recording = True
        self.start_time = time.time()

        def on_move(x, y):
            if self.recording: self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'move', 'x': x, 'y': y})
        def on_click(x, y, btn, pressed):
            if self.recording: self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'click', 'x': x, 'y': y, 'button': btn.name, 'pressed': pressed})
        def on_scroll(x, y, dx, dy):
            if self.recording: self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'scroll', 'x': x, 'y': y, 'dx': dx, 'dy': dy})
        def on_press(key):
            try: k = key.char
            except: k = str(key)
            if self.recording: self.events.append({'t': self.now(), 'type': 'key', 'action': 'press', 'key': k})
        def on_release(key):
            try: k = key.char
            except: k = str(key)
            if self.recording: self.events.append({'t': self.now(), 'type': 'key', 'action': 'release', 'key': k})

        self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self.key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.mouse_listener.start()
        self.key_listener.start()

    def stop(self):
        self.recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.key_listener: self.key_listener.stop()

    def save(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def load(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            self.events = json.load(f)

# ---------------------- Macro Player ----------------------
class MacroPlayer:
    def __init__(self, events):
        self.events = events
        self.stop_event = threading.Event()
        self.pause_event = threading.Event(); self.pause_event.set()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    def play_once(self):
        start = time.time()
        for e in self.events:
            if self.stop_event.is_set(): return
            self.pause_event.wait()
            wait = (start + e['t']) - time.time()
            if wait > 0: time.sleep(wait)

            if e['type'] == 'mouse':
                if e['action'] == 'move': self.mouse.position = (e['x'], e['y'])
                elif e['action'] == 'click':
                    btn = Button.left if e['button'] == 'left' else Button.right
                    (self.mouse.press if e['pressed'] else self.mouse.release)(btn)
                elif e['action'] == 'scroll': self.mouse.scroll(e['dx'], e['dy'])
            else:
                try:
                    if e['action'] == 'press': self.keyboard.press(e['key'])
                    else: self.keyboard.release(e['key'])
                except: pass

    def stop(self): self.stop_event.set(); self.pause_event.set()
    def pause(self): self.pause_event.clear()
    def resume(self): self.pause_event.set()

# ---------------------- واجهة البرنامج ----------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("JD_BOY Macro 100.1")
        root.geometry("720x620")

        self.rec = MacroRecorder()
        self.player = None
        self.hotkeys = {'record': None, 'play': None, 'pause': None, 'resume': None, 'stop_program': None}

        self.global_listener = keyboard.Listener(on_press=self.global_hotkey)
        self.global_listener.start()

        # تبويبات Menu
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="تواصل معي", command=self.contact)
        file_menu.add_command(label="تحديث البرنامج", command=auto_update)
        file_menu.add_command(label="حول البرنامج", command=lambda: messagebox.showinfo("حول", f"JD_BOY Macro\nالإصدار: {CURRENT_VERSION}"))
        menu_bar.add_cascade(label="خيارات", menu=file_menu)
        root.config(menu=menu_bar)

        # عنوان
        ttk.Label(root, text="⚙️ JD_BOY Macro", font=("Arial", 20, "bold")).pack(pady=10)

        # اختصارات
        f = ttk.LabelFrame(root, text="🔑 اختصارات التحكم", padding=10)
        f.pack(fill='x', padx=10, pady=10)
        self._hotkey_ui(f, "زر بدء/إيقاف التسجيل", 'record', 0)
        self._hotkey_ui(f, "زر بدء التشغيل", 'play', 1)
        self._hotkey_ui(f, "زر إيقاف مؤقت", 'pause', 2)
        self._hotkey_ui(f, "زر الاستمرار", 'resume', 3)
        self._hotkey_ui(f, "إيقاف البرنامج", 'stop_program', 4)

        # أيقونة البرنامج تحت الاختصارات
        icon_path = os.path.join(os.path.expanduser("~"), "Desktop", "JD_BOY_Macro_Final", "JD_BOY_Macro.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path).resize((96,96))
            icon_img = ImageTk.PhotoImage(img)
            ttk.Label(root, image=icon_img).pack(pady=10)
            self.icon_img = icon_img
        else:
            ttk.Label(root, text="JD_BOY", font=("Arial", 14, "bold")).pack(pady=10)

        # تكرار
        repeat_frame = ttk.LabelFrame(root, text="♻️ التكرار", padding=10)
        repeat_frame.pack(fill='x', padx=10, pady=10)
        self.repeat_mode = tk.StringVar(value='none')
        ttk.Radiobutton(repeat_frame, text="مرة واحدة", variable=self.repeat_mode, value='none').grid(row=0, column=0)
        ttk.Radiobutton(repeat_frame, text="تكرار لانهائي", variable=self.repeat_mode, value='inf').grid(row=0, column=1)
        ttk.Radiobutton(repeat_frame, text="تكرار كل مدة", variable=self.repeat_mode, value='time').grid(row=1, column=0)
        ttk.Label(repeat_frame, text="المدة:").grid(row=1, column=1)
        self.repeat_value = tk.IntVar(value=5)
        ttk.Entry(repeat_frame, textvariable=self.repeat_value, width=7).grid(row=1, column=2)
        self.repeat_unit = ttk.Combobox(repeat_frame, values=["ثواني", "دقائق", "ساعات"], width=10)
        self.repeat_unit.set("ثواني")
        self.repeat_unit.grid(row=1, column=3)

        # أزرار التحكم
        b = ttk.Frame(root)
        b.pack(pady=10)
        ttk.Button(b, text="▶️ بدء التسجيل", width=20, command=self.toggle_record).grid(row=0, column=0, padx=5)
        ttk.Button(b, text="💾 حفظ", width=10, command=self.save).grid(row=0, column=1)
        ttk.Button(b, text="📂 تحميل", width=10, command=self.load).grid(row=0, column=2)
        ttk.Button(b, text="🎬 تشغيل", width=20, command=self.start_play).grid(row=1, column=0, pady=5)
        ttk.Button(b, text="⏸ إيقاف مؤقت", width=10, command=self.pause_play).grid(row=1, column=1)
        ttk.Button(b, text="▶ استمرار", width=10, command=self.resume_play).grid(row=1, column=2)
        ttk.Button(b, text="⛔ إيقاف البرنامج", width=20, command=self.stop_program).grid(row=2, column=0, pady=5)

        # سجل الأحداث
        self.log = tk.Text(root, height=12)
        self.log.pack(fill='both', padx=10, pady=10)

        # تنفيذ التحديث مباشرة عند التشغيل
        threading.Thread(target=auto_update, daemon=True).start()

    # ---------------- واجهة الاختصارات ------------------
    def _hotkey_ui(self, frame, title, name, row):
        ttk.Label(frame, text=title).grid(row=row, column=0)
        var = tk.StringVar(value="لم يتم التعيين")
        ttk.Label(frame, textvariable=var, foreground="blue").grid(row=row, column=1)
        ttk.Button(frame, text="تغيير", command=lambda:self._record_hotkey(name, var)).grid(row=row, column=2)

    def _record_hotkey(self, name, label_var):
        HotkeyRecorder(lambda k:self._set_hotkey(name, k), label_var).start()

    def _set_hotkey(self, name, key):
        self.hotkeys[name] = key

    def global_hotkey(self, key):
        try: k = key.char
        except: k = str(key)
        if k == self.hotkeys.get('record'): self.toggle_record()
        elif k == self.hotkeys.get('play'): self.start_play()
        elif k == self.hotkeys.get('pause'): self.pause_play()
        elif k == self.hotkeys.get('resume'): self.resume_play()
        elif k == self.hotkeys.get('stop_program'): self.stop_program()

    # ---------------- التسجيل ------------------
    def toggle_record(self):
        if not self.rec.recording:
            self.rec.start(); self._log("✅ بدأ التسجيل")
        else:
            self.rec.stop(); self._log("⛔ تم إيقاف التسجيل")

    # ---------------- التشغيل ------------------
    def start_play(self):
        if not self.rec.events:
            messagebox.showinfo("تنبيه", "لا يوجد تسجيل")
            return
        self._log("▶️ بدأ التشغيل")
        self.player = MacroPlayer(self.rec.events)

        def loop():
            mode = self.repeat_mode.get()
            while True:
                self.player.play_once()
                if self.player.stop_event.is_set(): break
                if mode == 'none': break
                if mode == 'time':
                    sec = self._get_repeat_seconds()
                    time.sleep(sec)

        threading.Thread(target=loop, daemon=True).start()

    def _get_repeat_seconds(self):
        v = self.repeat_value.get()
        unit = self.repeat_unit.get()
        if unit == "ثواني": return v
        if unit == "دقائق": return v * 60
        return v * 3600

    def pause_play(self):
        if self.player: self.player.pause(); self._log("⏸ تم الإيقاف المؤقت")

    def resume_play(self):
        if self.player: self.player.resume(); self._log("▶ متابعة التشغيل")

    # ---------------- حفظ/تحميل ------------------
    def save(self):
        file = tk.filedialog.asksaveasfilename(defaultextension=".json")
        if file:
            self.rec.save(file)
            self._log(f"💾 تم الحفظ: {file}")

    def load(self):
        file = tk.filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            self.rec.load(file)
            self._log(f"📂 تم تحميل الملف")

    # ---------------- سجل ------------------
    def _log(self, txt):
        self.log.insert("1.0", txt + "\n")

    # ---------------- التواصل ------------------
    def contact(self):
        discord_url = "https://discord.com/users/358257404028125185"
        webbrowser.open(discord_url)

    # ---------------- ايقاف البرنامج ------------------
    def stop_program(self):
        if self.player:
            self.player.stop()
        self.root.destroy()

# ---------------- تشغيل البرنامج ------------------
if __name__ == '__main__':
    show_splash(lambda: None)
    root = tk.Tk()
    App(root)
    root.mainloop()
