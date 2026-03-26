#"bold"：粗體 "italic"：斜體 "underline"：底線 "overstrike"：刪除線

import customtkinter as ctk
import subprocess
import os
import json
from datetime import datetime

# ==============================
# 設定區
# ==============================
SCRIPTS = {
    "recorder": "memory_observer.py",      # 錄影機
    "build_db": "build_strategy_db.py",    # 資料庫轉換 & 分析
    "inspect": "inspect_db.py",            # 資料庫檢視
    "spawn": "remote_spawn.py",            # 生產小兵
    "dance": "dance_creep.py",             # 跳舞測試 
}

CONFIG_FILE = "strategy_config.json"

# 外觀設定
ctk.set_appearance_mode("dark")   # "light", "dark", "外觀，system 的背景與文字的底色。"
ctk.set_default_color_theme("blue")   # "blue", "green", "主題色，按鈕、進度條、拉桿等元件的「主色調」"

class App(ctk.CTk):
    def __init__(self):#初始化UI
        super().__init__()

        self.title("Screeps AI 指揮中心 🚀")
        self.geometry("560x730")
        self.minsize(700, 730)
        self.resizable(True, True)
        
        # RL 策略偏向預設
        self.rl_mode = ctk.StringVar(value="自動")
        
        self.create_widgets()
        self.load_strategy_config()

    def load_strategy_config(self):#啟動時讀取已有策略設定檔
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            mode = config_data.get("rl_strategy_mode", "自動")
            updated_at = config_data.get("updated_at", "未記錄")

            self.rl_mode.set(mode)

            if hasattr(self, "strategy_status_label"):
                self.strategy_status_label.configure(
                    text=f"目前套用策略偏向：{self.rl_mode.get()} \n 更新於：({updated_at})"
                )

            if hasattr(self, "status_label"):
                self.status_label.configure(
                    text=f"已載入策略設定：{self.rl_mode.get()}"
                )

            self.write_log(f"[完成] 已載入策略設定：{self.rl_mode.get()}")

        except Exception as e:
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"❌ 讀取設定失敗：{e}")
            self.write_log(f"[錯誤] 讀取設定失敗: {e}")

    def create_widgets(self):  # 視窗建立
        # ===== 頂部標題 =====
        header = ctk.CTkLabel(
            self,
            text="Overmind 戰略訓練系統",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(20, 10))

        sub_header = ctk.CTkLabel(
            self,
            text="Screeps AI Command Center",
            font=ctk.CTkFont(size=13),
            text_color="gray70"
        )
        sub_header.pack(pady=(0, 15))

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)   # 左側
        content_frame.grid_columnconfigure(1, weight=0)   # 右側不要跟著拉伸

        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right_frame = ctk.CTkFrame(content_frame, width=300, corner_radius=12)
        right_frame.grid(row=0, column=1, sticky="ns")
        right_frame.grid_propagate(False)

        # ===== 左側分頁容器 =====
        self.tabview = ctk.CTkTabview(left_frame)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("RL 策略設定")
        self.tabview.add("資料與控制")

        self.build_strategy_tab(self.tabview.tab("RL 策略設定"))
        self.build_main_tab(self.tabview.tab("資料與控制"))

        # ===== 右側固定日誌 =====
        self.build_log_panel(right_frame)

        # ===== 底部狀態列 =====
        self.status_label = ctk.CTkLabel(
            self,
            text="系統就緒",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.pack(pady=(5, 10))

    def build_main_tab(self, parent):
        # ---------- 區塊 1：數據蒐集 ----------
        frame_data = ctk.CTkFrame(parent, corner_radius=12)
        frame_data.pack(fill="x", padx=10, pady=(15, 10))

        title_data = ctk.CTkLabel(
            frame_data,
            text="🎥 數據蒐集 (Data Collection)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_data.pack(anchor="w", padx=15, pady=(12, 8))

        btn_record = ctk.CTkButton(
            frame_data,
            text="啟動錄影機 (Observer)",
            height=42,
            command=lambda: self.run_script(SCRIPTS["recorder"])
        )
        btn_record.pack(fill="x", padx=15, pady=(0, 15))

        # ---------- 區塊 2：數據處理 ----------
        frame_process = ctk.CTkFrame(parent, corner_radius=12)
        frame_process.pack(fill="x", padx=10, pady=10)

        title_process = ctk.CTkLabel(
            frame_process,
            text="🧠 數據處理 (Data Processing)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_process.pack(anchor="w", padx=15, pady=(12, 8))

        btn_build = ctk.CTkButton(
            frame_process,
            text="1. 轉換並分析資料庫 (Build DB)",
            height=42,
            command=lambda: self.run_script(SCRIPTS["build_db"])
        )
        btn_build.pack(fill="x", padx=15, pady=(0, 8))

        btn_inspect = ctk.CTkButton(
            frame_process,
            text="2. 檢視資料庫內容 (Inspect DB)",
            height=42,
            command=lambda: self.run_script(SCRIPTS["inspect"])
        )
        btn_inspect.pack(fill="x", padx=15, pady=(0, 15))

        # ---------- 區塊 3：實驗控制 ----------
        frame_control = ctk.CTkFrame(parent, corner_radius=12)
        frame_control.pack(fill="x", padx=10, pady=10)

        title_control = ctk.CTkLabel(
            frame_control,
            text="🎮 實驗控制 (Control)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_control.pack(anchor="w", padx=15, pady=(12, 8))

        btn_spawn = ctk.CTkButton(
            frame_control,
            text="遠端生產 RL_Bot",
            height=42,
            command=lambda: self.run_script(SCRIPTS["spawn"])
        )
        btn_spawn.pack(fill="x", padx=15, pady=(0, 8))

        btn_dance = ctk.CTkButton(
            frame_control,
            text="跳舞測試 (Dance Test)",
            height=42,
            command=lambda: self.run_script(SCRIPTS["dance"])
        )
        btn_dance.pack(fill="x", padx=15, pady=(0, 15))

        # ---------- 補充說明 ----------
        note = ctk.CTkLabel(
            parent,
            text="點擊按鈕後會開啟獨立 CMD 視窗執行腳本",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        note.pack(pady=(10, 0))

    def build_strategy_tab(self, parent):

        # ---------- 策略選擇區 ----------
        frame_strategy = ctk.CTkFrame(parent, corner_radius=12)
        frame_strategy.pack(fill="x", padx=10, pady=(15, 10))

        title_strategy = ctk.CTkLabel(
            frame_strategy,
            text="⚙️ RL 策略偏向調整",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_strategy.pack(anchor="w", padx=15, pady=(12, 8))

        info = ctk.CTkLabel(
            frame_strategy,
            text="選擇目前的策略模式：",
            font=ctk.CTkFont(size=14)
        )
        info.pack(anchor="w", padx=15, pady=(0, 8))

        self.radio_attack = ctk.CTkRadioButton(
            frame_strategy,
            text="進攻",
            variable=self.rl_mode,
            value="進攻",
        )
        self.radio_attack.pack(anchor="w", padx=20, pady=5)

        self.radio_defense = ctk.CTkRadioButton(
            frame_strategy,
            text="防守",
            variable=self.rl_mode,
            value="防守",
        )
        self.radio_defense.pack(anchor="w", padx=20, pady=5)

        self.radio_economy = ctk.CTkRadioButton(
            frame_strategy,
            text="發展",
            variable=self.rl_mode,
            value="發展",
        )
        self.radio_economy.pack(anchor="w", padx=20, pady=5)

        self.radio_auto = ctk.CTkRadioButton(
            frame_strategy,
            text="自動",
            variable=self.rl_mode,
            value="自動",
        )
        self.radio_auto.pack(anchor="w", padx=20, pady=5)

        self.strategy_status_label = ctk.CTkLabel(
            frame_strategy,
            text=f"目前套用策略偏向：{self.rl_mode.get()}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4EA1FF",
            justify="left",
            anchor="w",
            wraplength=320
        )
        self.strategy_status_label.pack(anchor="w", padx=15, pady=(12, 10))

        btn_apply = ctk.CTkButton(
            frame_strategy,
            text="套用策略設定",
            height=42,
            command=self.apply_strategy
        )
        btn_apply.pack(fill="x", padx=15, pady=(0, 15))

        # ---------- 模式說明區 ----------
        self.mode_desc = {
            "進攻": "偏向主動擴張、壓制敵方與強化戰術推進。",
            "防守": "偏向基地穩定、防禦部署、敵襲應對與資產保護。",
            "發展": "偏向經濟成長、資源採集、建設升級與長期發展。",
            "自動": "由系統依局勢自動切換適合的策略模式。"
        }

        # 滑鼠懸停事件
        self.radio_attack.bind("<Enter>", lambda e: self.show_mode_desc("進攻"))
        self.radio_attack.bind("<Leave>", lambda e: self.clear_mode_desc())

        self.radio_defense.bind("<Enter>", lambda e: self.show_mode_desc("防守"))
        self.radio_defense.bind("<Leave>", lambda e: self.clear_mode_desc())

        self.radio_economy.bind("<Enter>", lambda e: self.show_mode_desc("發展"))
        self.radio_economy.bind("<Leave>", lambda e: self.clear_mode_desc())

        self.radio_auto.bind("<Enter>", lambda e: self.show_mode_desc("自動"))
        self.radio_auto.bind("<Leave>", lambda e: self.clear_mode_desc())

        frame_desc = ctk.CTkFrame(parent, corner_radius=12)
        frame_desc.pack(fill="both", expand=True, padx=10, pady=10)

        title_desc = ctk.CTkLabel(
            frame_desc,
            text="📘 模式說明",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_desc.pack(anchor="w", padx=15, pady=(12, 8))

        self.desc_label = ctk.CTkLabel(
            frame_desc,
            text="將滑鼠移到策略選項上，可查看模式說明。",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=300
        )
        self.desc_label.pack(fill="x", anchor="w", padx=20, pady=(0, 15))

    def build_log_panel(self, parent):  # 固定右側日誌區
        log_title = ctk.CTkLabel(
            parent,
            text="系統日誌",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        log_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.log_textbox = ctk.CTkTextbox(parent)
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.log_textbox.insert("end", "系統啟動完成\n")
        self.log_textbox.configure(state="disabled")

        btn_clear_log = ctk.CTkButton(
            parent,
            text="清除日誌",
            height=40,
            command=self.clear_log
        )
        btn_clear_log.pack(fill="x", padx=15, pady=(0, 15))
    
    def write_log(self, message): #日誌寫入
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"

        if hasattr(self, "log_textbox"):
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", full_message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        if hasattr(self, "status_label"):
            self.status_label.configure(text=message)

        print(full_message)

    def clear_log(self): #日誌清除
        if hasattr(self, "log_textbox"):
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("end", "日誌已清除\n")
            self.log_textbox.configure(state="disabled")

    def show_mode_desc(self, mode): #模式說明顯示更改
        self.desc_label.configure(
            text=f"{mode}：{self.mode_desc.get(mode, '')}"
        )

    def clear_mode_desc(self): #模式說明顯示預設
        self.desc_label.configure(
            text="將滑鼠移到策略選項上，可查看模式說明。"
        )

    def apply_strategy(self): #套用策略設定觸發
        selected_mode = self.rl_mode.get()

        #dict 方便 json
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        config_data = {
            "rl_strategy_mode": selected_mode,
            "updated_at": current_time,
        }

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)

            self.strategy_status_label.configure(
                text=f"目前套用策略偏向：{selected_mode} \n 更新於：({current_time})"
            )
            self.status_label.configure(
                text=f"✅ 已套用並寫入 {CONFIG_FILE}：{selected_mode}"
            )
            self.write_log(f"[完成] 已套用 RL 策略偏向: {selected_mode}")

        except Exception as e:
            self.status_label.configure(text=f"❌ 寫入設定失敗：{e}")
            self.write_log(f"[錯誤] 寫入設定失敗: {e}")

    def run_script(self, script_name):
        """啟動新的 CMD 視窗執行 Python 腳本"""
        if not os.path.exists(script_name):
            msg = f"[錯誤] 找不到檔案: {script_name}"
            self.status_label.configure(text=msg)
            self.write_log(msg)
            return

        msg = f"正在啟動: {script_name}"
        self.status_label.configure(text=msg)
        self.write_log(msg)

        cmd_command = f'start cmd /k "python {script_name}"'
        subprocess.Popen(cmd_command, shell=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()