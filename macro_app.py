import threading
import time
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import ctypes
import sys
import os 
from PIL import Image, ImageTk 
import requests 
import webbrowser 

# ------------------------------------------------------------
# ⚙️ إعدادات التحديث
# ------------------------------------------------------------
APP_VERSION = "1.0.3"  # 🚨 تم تحديث رقم الإصدار هنا لنسخة المطور
# 📌📌 رابط الملف الخام لـ latest_version.json على GitHub
# هذا الرابط يشير إلى الفرع الرئيسي (main) لفحص الإصدار المستقر
UPDATE_URL = "https://raw.githubusercontent.com/saleh07mohammed-blip/JD_BOY_Macro_Final/main/latest_version.json" 
# ------------------------------------------------------------

# ------------------------------------------------------------
# 📞 إعدادات التواصل
# ------------------------------------------------------------
DISCORD_USER_ID = "358257404028125185" 
# ------------------------------------------------------------

# ------------------------------------------------------------
# 📁 دالة تحديد المسار عند التحزيم (Fix for PyInstaller)
# ------------------------------------------------------------
def resource_path(relative_path):
    """احصل على المسار المطلق للموارد، سواء في وضع التطوير أو بعد التحزيم."""
    if hasattr(sys, '_MEIPASS'):
        # إذا كان البرنامج محزماً، ابحث في المجلد المؤقت
        return os.path.join(sys._MEIPASS, relative_path)
    # إذا كان البرنامج في وضع التطوير، ابحث في المجلد الحالي
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
# ------------------------------------------------------------


# ------------------------------------------------------------
# 🛡️ الإطلاق بصلاحية المسؤول (Self-elevating Launcher)
# ------------------------------------------------------------
def is_admin():
    """التحقق مما إذا كان البرنامج يعمل بصلاحيات المسؤول."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # يتم تشغيل هذا الجزء فقط إذا لم يكن بصلاحيات المسؤول
    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
    else:
        executable_path = sys.executable
        script = os.path.abspath(sys.argv[0])

    try:
        if getattr(sys, 'frozen', False):
            # إعادة تشغيل الملف التنفيذي كمسؤول
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable_path, "", None, 1)
        else:
            # إعادة تشغيل ملف السكربت كمسؤول
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable_path, script, None, 1)
        sys.exit(0)
    except Exception as e:
        # إذا فشل التشغيل كمسؤول، قد يظهر البرنامج بدون صلاحيات
        pass 
# ------------------------------------------------------------


# ------------------------------------------------------------
# وظائف قفل/إلغاء قفل مدخلات الماوس (خاص بنظام Windows)
# ------------------------------------------------------------
def block_mouse_input():
    """يقوم بقفل مدخلات الماوس ولوحة المفاتيح لمنع تداخل المستخدم."""
    try:
        ctypes.windll.user32.BlockInput(True)
    except Exception as e:
        print(f"فشل قفل المدخلات: {e}")
        pass 

def unblock_mouse_input():
    """يقوم بإلغاء قفل مدخلات الماوس ولوحة المفاتيح."""
    try:
        ctypes.windll.user32.BlockInput(False)
    except Exception as e:
        print(f"فشل إلغاء قفل المدخلات: {e}")
        pass
# ------------------------------------------------------------


# ------------------------------------------------------------
# 🚀 كلاس شاشة التحميل (Splash Screen)
# ------------------------------------------------------------
class SplashApp:
    def __init__(self, master):
        self.master = master
        master.overrideredirect(True)
        
        # استخدام الدالة الجديدة لتحديد المسار 
        icon_path = resource_path('JD_BOY_Macro.ico')
        try:
            master.wm_iconbitmap(icon_path) 
        except Exception: 
            pass
            
        splash_width = 400
        splash_height = 200
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) - (splash_width // 2)
        y = (screen_height // 2) - (splash_height // 2)
        master.geometry(f'{splash_width}x{splash_height}+{x}+{y}')
        
        # 🎨 لون الخلفية: رمادي فاتح
        master.config(bg="#E0E0E0") 

        # عنصر الاسم المتراقص
        self.title_label = ttk.Label(master, text="JD_BOY", 
                  font=("Courier", 32, "bold"), 
                  foreground="#FF0000", # 🎨 لون أحمر
                  background="#E0E0E0") # 🎨 لون رمادي فاتح
        self.title_label.pack(pady=(40, 5)) 
        
        # عنصر شريط التحميل المتقاطع
        self.canvas = tk.Canvas(master, width=300, height=20, bg="#E0E0E0", highlightthickness=0) # 🎨 لون رمادي فاتح
        self.canvas.pack(pady=(5, 2))
        self.progress = 0
        self.loaded_label = None 
        
        # عنصر النسبة المئوية
        self.percent_var = tk.StringVar(value="0%")
        ttk.Label(master, textvariable=self.percent_var, 
                  font=("Arial", 10, "bold"), 
                  foreground="#FF0000", # 🎨 لون أحمر
                  background="#E0E0E0").pack(pady=(2, 5)) # 🎨 لون رمادي فاتح


        # بدء الحركة
        self.master.after(100, self.animate_title)
        self.master.after(10, self.animate_progress)
        
        # وقت الانتقال (3 ثوانٍ)
        self.master.after(3000, self.start_fade_out)

    def animate_title(self):
        """يغير تلوين حروف الاسم لتأثير التراقص"""
        if self.progress < 100: 
            current_color = self.title_label.cget("foreground")
            new_color = "#AAAAAA" if current_color == "#FF0000" else "#FF0000" # 🎨 أحمر ورمادي أغمق قليلاً
            self.title_label.config(foreground=new_color)
            self.master.after(200, self.animate_title)

    def animate_progress(self):
        """يرسم شريط تحميل متقاطع متحرك ويحدث النسبة المئوية"""
        if self.progress < 100:
            self.progress += 2
            self.percent_var.set(f"{self.progress}%") 
            self.canvas.delete("all")
            width = 300
            height = 20
            fill_width = (self.progress / 100) * width
            self.canvas.create_rectangle(0, 0, width, height, outline="#BBBBBB", fill="#DDDDDD") # 🎨 رمادي فاتح
            step = 10
            line_color = "#FF0000" # 🎨 لون أحمر
            
            for i in range(0, int(fill_width) + step, step):
                self.canvas.create_line(i + (self.progress % step), 0, i + step + (self.progress % step), height, fill=line_color, width=2)
                self.canvas.create_line(i + (self.progress % step), height, i + step + (self.progress % step), 0, fill=line_color, width=2)
            
            self.master.after(50, self.animate_progress)
        elif self.loaded_label is None:
            self.percent_var.set("100%") 
            self.canvas.delete("all")
            self.loaded_label = ttk.Label(self.master, text="... جاهز للعمل ...", 
                      font=("Arial", 10), 
                      foreground="#555555", # 🎨 لون رمادي غامق
                      background="#E0E0E0") # 🎨 لون رمادي فاتح
            self.loaded_label.pack(pady=5)


    def start_fade_out(self):
        self.alpha = 1.0
        self.fade_step = 0.1
        self.fade_out()

    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= self.fade_step
            if self.alpha < 0:
                self.alpha = 0
            self.master.attributes("-alpha", self.alpha)
            self.master.after(100, self.fade_out)
        else:
            self.master.destroy()
            main_root = tk.Tk()
            App(main_root)
            main_root.mainloop()

# ------------------------------------------------------------
# كلاس تسجيل الأزرار لتحديد الاختصارات
# ------------------------------------------------------------
class HotkeyRecorder:
    def __init__(self, callback, label_var):
        self.callback = callback
        self.label_var = label_var
        self.recording = False
        self.listener = None

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.label_var.set("... اضغط أي زر الآن")
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        try:
            k = key.char
        except:
            k = str(key)
        self.label_var.set(k)
        self.callback(k)
        self.recording = False
        if self.listener:
            self.listener.stop()

# ------------------------------------------------------------
# كلاس تسجيل الحركات
# ------------------------------------------------------------
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
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.time()

        def on_move(x, y):
            if self.recording:
                self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'move', 'x': x, 'y': y})

        def on_click(x, y, btn, pressed):
            if self.recording:
                self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'click', 'x': x, 'y': y, 'button': btn.name, 'pressed': pressed})

        def on_scroll(x, y, dx, dy):
            if self.recording:
                self.events.append({'t': self.now(), 'type': 'mouse', 'action': 'scroll', 'x': x, 'y': y, 'dx': dx, 'dy': dy})

        def on_press(key):
            try:
                k = key.char
            except:
                k = str(key)
            if self.recording:
                self.events.append({'t': self.now(), 'type': 'key', 'action': 'press', 'key': k})

        def on_release(key):
            try:
                k = key.char
            except:
                k = str(key)
            if self.recording:
                self.events.append({'t': self.now(), 'type': 'key', 'action': 'release', 'key': k})

        self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self.key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.mouse_listener.start()
        self.key_listener.start()

    def stop(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.key_listener:
            self.key_listener.stop()

    def save(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def load(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            self.events = json.load(f)

# ------------------------------------------------------------
# كلاس التشغيل
# ------------------------------------------------------------
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
                    # تحويل أسماء المفاتيح إلى كائن Key إذا لم تكن حرفاً
                    if e['action'] == 'press': 
                        if len(e['key']) > 1 and e['key'].startswith('<Key.'):
                            key_name = e['key'].split('.')[-1].split('>')[0]
                            key_to_press = getattr(Key, key_name, e['key'])
                        else:
                            key_to_press = e['key']
                        self.keyboard.press(key_to_press)
                    else: 
                        if len(e['key']) > 1 and e['key'].startswith('<Key.'):
                            key_name = e['key'].split('.')[-1].split('>')[0]
                            key_to_release = getattr(Key, key_name, e['key'])
                        else:
                            key_to_release = e['key']
                        self.keyboard.release(key_to_release)
                except Exception as ex: 
                    # هذا يضمن أن البرنامج لا يتوقف بسبب خطأ في التعامل مع مفاتيح خاصة
                    print(f"Error handling key event: {ex}")
                    pass

    def stop(self): self.stop_event.set(); self.pause_event.set()
    def pause(self): self.pause_event.clear()
    def resume(self): self.pause_event.set()


# ------------------------------------------------------------
# 🖥️ واجهة المستخدم الاحترافية (App Class)
# ------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        
        # صندوق السجلات في الأسفل (Grid Position: Row 7, Col 0-4)
        self.log = tk.Text(root, height=10)
        self.log.grid(row=7, column=0, columnspan=5, sticky='ew', padx=10, pady=(0, 10))

        # 🚨 تغيير عنوان البرنامج لتمييز الإصدار 1.0.3 (نسخة المطور)
        root.title(f"🎮 برنامج الماكرو الاحترافي - JD_BOY Edition v{APP_VERSION} (نسخة المطور)")
        root.geometry("720x620")
        
        # إعداد تخطيط Grid للنافذة الرئيسية
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.grid_columnconfigure(4, weight=1)
        
        # استخدام الدالة الجديدة لتحديد مسار الأيقونة
        icon_path = resource_path('JD_BOY_Macro.ico')
        try:
            root.wm_iconbitmap(icon_path) 
        except Exception: 
            pass 

        self.rec = MacroRecorder()
        self.player = None

        self.hotkeys = {'record': None, 'play': None, 'pause': None, 'resume': None, 'stop_all': None}

        self.global_listener = keyboard.Listener(on_press=self.global_hotkey)
        self.global_listener.start()
        
        # 1. إنشاء شريط القوائم (Menu Bar)
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="🔄 تحديث البرنامج", command=self.check_for_updates)
        
        contact_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="تواصل", menu=contact_menu)
        contact_menu.add_command(label="📞 تواصل مع المطور (JD_BOY)", command=self.open_discord_link)
        contact_menu.add_separator() 
        contact_menu.add_command(label="ℹ️ حول البرنامج", command=lambda: messagebox.showinfo("حول البرنامج", f"برنامج الماكرو الاحترافي\nالإصدار: {APP_VERSION}\nPowered by JD_BOY"))
        
        # ----------------------------------------------
        #  الصفوف العلوية للعنوان والأيقونة (Row 0, 1)
        # ----------------------------------------------

        # تحميل الأيقونة وعرضها في الـ Label
        self.app_icon = None 
        try:
            img = Image.open(resource_path('JD_BOY_Macro.ico')) 
            img = img.resize((96, 96), Image.LANCZOS) 
            self.app_icon = ImageTk.PhotoImage(img) 

            ttk.Label(root, text=" نظام الماكرو الشامل", 
                      font=("Arial", 20, "bold"),
                      image=self.app_icon, 
                      compound=tk.LEFT 
                     ).grid(row=0, column=0, columnspan=5, pady=(10, 0))
        except Exception as e:
            self._log(f"⚠️ فشل تحميل الأيقونة لعنوان الواجهة. خطأ: {e}")
            ttk.Label(root, text="⚙️ نظام الماكرو الشامل", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=5, pady=(10, 0))

        ttk.Label(root, text="Powered by JD_BOY", 
                  font=("Arial", 10), 
                  foreground="#555555").grid(row=1, column=0, columnspan=5, pady=(0, 10)) # 🎨 لون رمادي غامق

        # ----------------------------------------------
        #  إطار الاختصارات (Row 2)
        # ----------------------------------------------
        f_hotkey = ttk.LabelFrame(root, text="🔑 اختصارات التحكم", padding=10)
        f_hotkey.grid(row=2, column=0, columnspan=5, sticky='ew', padx=10, pady=10)
        
        # إعداد Grid لإطار الاختصارات (3 أعمدة)
        f_hotkey.grid_columnconfigure(0, weight=1)
        f_hotkey.grid_columnconfigure(1, weight=1)
        f_hotkey.grid_columnconfigure(2, weight=1)
        
        self._hotkey_ui(f_hotkey, "زر بدء/إيقاف التسجيل", 'record', 0)
        self._hotkey_ui(f_hotkey, "زر بدء التشغيل", 'play', 1)
        self._hotkey_ui(f_hotkey, "زر إيقاف مؤقت", 'pause', 2)
        self._hotkey_ui(f_hotkey, "زر الاستمرار", 'resume', 3)
        self._hotkey_ui(f_hotkey, "زر إيقاف التشغيل الكلي", 'stop_all', 4)
        
        # ----------------------------------------------
        #  إطار التكرار (Row 3)
        # ----------------------------------------------
        repeat_frame = ttk.LabelFrame(root, text="♻️ خيارات التكرار", padding=10)
        repeat_frame.grid(row=3, column=0, columnspan=5, sticky='ew', padx=10, pady=10)
        
        # إعداد Grid لإطار التكرار (6 أعمدة لضبط التباعد)
        repeat_frame.grid_columnconfigure(0, weight=1) 
        repeat_frame.grid_columnconfigure(1, weight=1) 
        repeat_frame.grid_columnconfigure(2, weight=1) 
        repeat_frame.grid_columnconfigure(3, weight=0) # للقيمة
        repeat_frame.grid_columnconfigure(4, weight=0) # لخانة القيمة
        repeat_frame.grid_columnconfigure(5, weight=1) # للوحدة

        self.repeat_mode = tk.StringVar(value='none')
        
        # خيار 1: مرة واحدة (بدون تكرار)
        ttk.Radiobutton(repeat_frame, text="مرة واحدة", variable=self.repeat_mode, value='none').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # خيار 2: تكرار لانهائي
        ttk.Radiobutton(repeat_frame, text="تكرار لانهائي", variable=self.repeat_mode, value='inf').grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # خيار 3: تكرار كل مدة محددة
        ttk.Radiobutton(repeat_frame, text="تكرار كل", variable=self.repeat_mode, value='time').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        
        # حقول إدخال القيمة والوحدة (في نفس سطر "تكرار كل")
        ttk.Label(repeat_frame, text="القيمة:").grid(row=0, column=3, sticky='e', padx=(10, 0))
        
        self.repeat_value = tk.IntVar(value=5)
        ttk.Entry(repeat_frame, textvariable=self.repeat_value, width=7).grid(row=0, column=4, sticky='w', padx=5)
        
        self.repeat_unit = ttk.Combobox(repeat_frame, values=["ثواني", "دقائق", "ساعات"], width=8)
        self.repeat_unit.set("ثواني")
        self.repeat_unit.grid(row=0, column=5, sticky='w', padx=5)
        
        # ----------------------------------------------
        #  إطار أزرار التحكم (Row 4, 5, 6)
        # ----------------------------------------------
        
        # الصف 4: التسجيل والحفظ والتحميل
        ttk.Button(root, text="▶️ بدء/إيقاف التسجيل", width=25, command=self.toggle_record).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Button(root, text="💾 حفظ الماكرو", width=15, command=self.save).grid(row=4, column=2, padx=5, pady=5, sticky='ew')
        ttk.Button(root, text="📂 تحميل الماكرو", width=15, command=self.load).grid(row=4, column=3, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # الصف 5: التحكم بالتشغيل
        ttk.Button(root, text="🎬 تشغيل الماكرو", width=25, command=self.start_play).grid(row=5, column=0, columnspan=2, pady=5, sticky='ew', padx=5)
        ttk.Button(root, text="⏸ إيقاف مؤقت", width=15, command=self.pause_play).grid(row=5, column=2, pady=5, sticky='ew', padx=5)
        ttk.Button(root, text="▶ استمرار التشغيل", width=15, command=self.resume_play).grid(row=5, column=3, columnspan=2, pady=5, sticky='ew', padx=5)
        
        # الصف 6: الإيقاف الكلي
        # 🎨 زر الإيقاف الكلي باللون الأحمر
        ttk.Button(root, text="⏹ إيقاف التشغيل الكلي (أمان)", style='Danger.TButton', command=self.stop_play).grid(row=6, column=0, columnspan=5, pady=10, sticky='ew', padx=10)
        
        # تحديد لون مختلف لزر الإيقاف الكلي (يتطلب إضافة ستايل)
        style = ttk.Style()
        style.configure('Danger.TButton', foreground='white', background='#FF0000', font=('Arial', 12, 'bold')) # 🎨 خلفية حمراء
        style.map('Danger.TButton',
                   background=[('active', '#CC0000')]) # 🎨 أحمر أغمق عند التفعيل


    # ---------------- دوال التحديث والـ Discord ------------------

    def check_for_updates(self):
        """يفحص ما إذا كان هناك إصدار جديد متوفر ويحمله."""
        self._log(f"⏳ فحص التحديثات... الإصدار الحالي هو: {APP_VERSION}")
        threading.Thread(target=self._run_update_check, daemon=True).start()

    def _run_update_check(self):
        try:
            response = requests.get(UPDATE_URL, timeout=5)
            response.raise_for_status()
            latest_data = response.json()
            latest_version_str = latest_data.get('version', '0.0.0').strip()
            download_url = latest_data.get('download_url')
            
            def parse_version(version_str):
                # تحويل الإصدار إلى قائمة أرقام للمقارنة (1.0.1 -> [1, 0, 1])
                return [int(x) for x in version_str.split('.')]

            app_v = parse_version(APP_VERSION.strip())
            latest_v = parse_version(latest_version_str)

            if latest_v > app_v:
                self.root.after(0, lambda: self._log(f"🎉 **تم العثور على تحديث!** الإصدار: {latest_version_str}"))
                msg = f"يجب تحديث البرنامج إلى الإصدار {latest_version_str}. هل ترغب في التحميل الآن؟"
                
                if messagebox.askyesno("تحديث البرنامج", msg):
                    self.root.after(0, lambda: self.perform_update(download_url))
                else:
                    self.root.after(0, lambda: self._log("⚠️ تم رفض التحديث. سيستمر البرنامج في العمل بالإصدار الحالي."))

            elif latest_v == app_v:
                self.root.after(0, lambda: self._log("✅ برنامجك هو أحدث إصدار."))
                
            else: 
                self.root.after(0, lambda: self._log("✅ برنامجك هو أحدث إصدار."))
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self._log(f"❌ خطأ في الاتصال بالإنترنت لفحص التحديثات: {e}"))
        except json.JSONDecodeError:
            self.root.after(0, lambda: self._log("❌ فشل قراءة ملف الإصدار. تأكد من صحة تنسيق JSON."))


    def perform_update(self, download_url):
        """يفتح رابط التحميل ويغلق البرنامج لإتاحة الفرصة للتثبيت."""
        try:
            webbrowser.open(download_url)
            self._log("✅ تم فتح رابط التحميل. يرجى تثبيت الإصدار الجديد.")
            self._log("⚠️ سيتم إغلاق البرنامج للسماح لك بتثبيت التحديث الجديد.")
            self.root.quit()
            
        except Exception as e:
            self._log(f"❌ فشل عملية التحديث: {e}")

    def open_discord_link(self):
        """يفتح ملف تعريف المستخدم الخاص بك على Discord."""
        profile_url = f"https://discord.com/users/{DISCORD_USER_ID}"
        
        try:
            webbrowser.open(profile_url)
            self._log("📞 تم فتح نافذة المتصفح لربطك بملف تعريف المستخدم الخاص بي على Discord.")
        except Exception as e:
            self._log(f"❌ فشل فتح رابط Discord. خطأ: {e}")

    # ---------------- (بقية الدوال تبقى كما هي) ------------------

    def _hotkey_ui(self, frame, title, name, row):
        # هنا ما زلنا نستخدم Grid داخل إطار الاختصارات
        ttk.Label(frame, text=title).grid(row=row, column=0, sticky='w')
        var = tk.StringVar(value="لم يتم التعيين")
        # 🎨 جعل لون الاختصار في وضع المطور باللون الأحمر لتمييزه
        ttk.Label(frame, textvariable=var, foreground="#FF0000").grid(row=row, column=1, padx=10)
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
        elif k == self.hotkeys.get('stop_all'): self.stop_play()

    def toggle_record(self):
        if not self.rec.recording:
            self.rec.start(); self._log("✅ بدأ التسجيل")
        else:
            self.rec.stop(); self._log("⛔ تم إيقاف التسجيل")

    def start_play(self):
        if not self.rec.events:
            self._log("❌ فشل التشغيل: لا يوجد تسجيل.")
            return
        
        if self.player:
            self._log("⚠️ التشغيل قيد التنفيذ بالفعل.")
            return

        self._log("▶️ بدأ التشغيل. يتم محاولة قفل مدخلات الماوس/الكيبورد.")
        
        block_mouse_input()
        time.sleep(0.1) 
        
        self.player = MacroPlayer(self.rec.events)

        def loop():
            mode = self.repeat_mode.get()
            
            try:
                while True:
                    self.player.play_once()
                    if self.player.stop_event.is_set(): break
                    if mode == 'none': break
                    if mode == 'time':
                        sec = self._get_repeat_seconds()
                        if sec <= 0:
                            self._log("❌ فشل التشغيل: يجب أن تكون قيمة التكرار بالوقت أكبر من صفر.")
                            break
                        time.sleep(sec)
            finally:
                if self.player:
                    self.player.stop() 
                    unblock_mouse_input()
                    self._log("✅ انتهى التشغيل التلقائي. تم **إلغاء قفل** المدخلات.")
                    self.player = None

        threading.Thread(target=loop, daemon=True).start()


    def _get_repeat_seconds(self):
        try:
            v = self.repeat_value.get()
        except tk.TclError:
            v = 0 # في حال كانت الخانة فارغة أو غير رقمية
            
        unit = self.repeat_unit.get()
        if unit == "ثواني": return v
        if unit == "دقائق": return v * 60
        return v * 3600

    def pause_play(self):
        if self.player: 
            self.player.pause(); 
            self._log("⏸ تم الإيقاف المؤقت")
        else:
            self._log("⚠️ لا يوجد تشغيل نشط للإيقاف المؤقت.")

    def resume_play(self):
        if self.player: 
            self.player.resume(); 
            self._log("▶ متابعة التشغيل")
        else:
            self._log("⚠️ لا يوجد تشغيل نشط للاستمرار.")

    def stop_play(self): 
        if self.player:
            self.player.stop() 
            unblock_mouse_input() 
            self._log("⏹ تم إيقاف التشغيل نهائيًا. تم **إلغاء قفل** المدخلات.")
            self.player = None
        else:
            unblock_mouse_input()
            self._log("⚠️ لا يوجد تشغيل نشط للإيقاف الكلي. تم إلغاء قفل المدخلات كإجراء أمان.")

    def save(self):
        file = filedialog.asksaveasfilename(defaultextension=".json")
        if file:
            self.rec.save(file)
            self._log(f"💾 تم الحفظ: {file}")

    def load(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            self.rec.load(file)
            self._log(f"📂 تم تحميل الملف")

    def _log(self, txt):
        self.log.insert("1.0", txt + "\n")

# ---------------- تشغيل البرنامج ------------------
if __name__ == '__main__':
    splash_root = tk.Tk()
    SplashApp(splash_root)
    splash_root.mainloop()