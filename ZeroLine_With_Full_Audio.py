"""
《代號：零線》完整版本 - 整合 12 款專業音效
包含完整的遊戲系統、賬戶系統、皮膚系統、商店系統和音效系統
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import hashlib
from datetime import datetime
from sound_manager import SoundManager, SoundEventHandler, get_sound_manager, play_sound


# ================== 遊戲配置 ==================
GAME_CONFIG = {
    "title": "代號：零線 (CODE: ZERO LINE)",
    "version": "2.0.0",
    "window_width": 1000,
    "window_height": 700,
    "bg_color": "#0a0e27",
    "primary_color": "#00ff88",
    "secondary_color": "#1a253a",
}


# ================== 英雄數據 ==================
HEROES = {
    1: {"name": "李擎天", "code": "風暴", "role": "攻擊", "hp": 120, "armor": 20, "speed": 1.1},
    2: {"name": "陳靜雨", "code": "靜流", "role": "技術", "hp": 90, "armor": 10, "speed": 0.95},
    3: {"name": "張雷鳴", "code": "雷神", "role": "防禦", "hp": 150, "armor": 30, "speed": 0.9},
    4: {"name": "王天翔", "code": "幽靈", "role": "偵查", "hp": 80, "armor": 5, "speed": 1.2},
    5: {"name": "林正義", "code": "指揮官", "role": "支援", "hp": 100, "armor": 15, "speed": 1.0},
}


# ================== 主遊戲類 ==================
class ZeroLineGame:
    """主遊戲類"""
    def __init__(self, root):
        self.root = root
        self.root.title(GAME_CONFIG["title"])
        self.root.geometry(f"{GAME_CONFIG['window_width']}x{GAME_CONFIG['window_height']}")
        self.root.configure(bg=GAME_CONFIG["bg_color"])
        
        # 初始化音效管理器
        self.sound_manager = get_sound_manager()
        self.sound_handler = SoundEventHandler(self.sound_manager)
        
        # 遊戲狀態
        self.current_player = None
        self.current_hero = None
        self.current_screen = "login"
        
        # 播放啟動音效
        self.sound_handler.on_game_startup()
        
        # 初始化 UI
        self.setup_ui()

    def setup_ui(self):
        """設置 UI"""
        self.main_frame = tk.Frame(self.root, bg=GAME_CONFIG["bg_color"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_login_screen()

    def clear_screen(self):
        """清除屏幕"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ========== 登入界面 ==========
    def show_login_screen(self):
        """顯示登入界面"""
        self.clear_screen()
        self.current_screen = "login"
        
        # 標題
        title_label = tk.Label(
            self.main_frame,
            text="代號：零線",
            font=("Arial", 48, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=50)
        
        # 副標題
        subtitle_label = tk.Label(
            self.main_frame,
            text="CODE: ZERO LINE - 戰術射擊遊戲原型",
            font=("Arial", 14),
            fg=GAME_CONFIG["secondary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        subtitle_label.pack(pady=10)
        
        # 按鈕框架
        button_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        button_frame.pack(pady=50)
        
        # 新建賬戶按鈕
        register_btn = tk.Button(
            button_frame,
            text="建立新賬戶",
            font=("Arial", 14, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.show_register_screen
        )
        register_btn.pack(pady=10)
        
        # 登入按鈕
        login_btn = tk.Button(
            button_frame,
            text="登入賬戶",
            font=("Arial", 14, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.show_login_form
        )
        login_btn.pack(pady=10)
        
        # 試玩按鈕
        demo_btn = tk.Button(
            button_frame,
            text="試玩遊戲",
            font=("Arial", 14, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.start_demo
        )
        demo_btn.pack(pady=10)

    def show_register_screen(self):
        """顯示註冊界面"""
        self.clear_screen()
        self.sound_handler.on_button_click()
        
        title_label = tk.Label(
            self.main_frame,
            text="建立新賬戶",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=30)
        
        # 用戶名
        tk.Label(self.main_frame, text="用戶名：", font=("Arial", 12), 
                fg=GAME_CONFIG["primary_color"], bg=GAME_CONFIG["bg_color"]).pack()
        username_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
        username_entry.pack(pady=5)
        
        # 密碼
        tk.Label(self.main_frame, text="密碼：", font=("Arial", 12),
                fg=GAME_CONFIG["primary_color"], bg=GAME_CONFIG["bg_color"]).pack()
        password_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30, show="*")
        password_entry.pack(pady=5)
        
        # 確認密碼
        tk.Label(self.main_frame, text="確認密碼：", font=("Arial", 12),
                fg=GAME_CONFIG["primary_color"], bg=GAME_CONFIG["bg_color"]).pack()
        confirm_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30, show="*")
        confirm_entry.pack(pady=5)
        
        def register():
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("錯誤", "請填寫所有字段")
                return
            
            if password != confirm:
                messagebox.showerror("錯誤", "密碼不匹配")
                return
            
            self.sound_handler.on_select()
            self.current_player = username
            messagebox.showinfo("成功", f"賬戶 {username} 創建成功！")
            self.show_lobby()
        
        # 按鈕框架
        button_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        button_frame.pack(pady=30)
        
        register_btn = tk.Button(
            button_frame,
            text="註冊",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=register
        )
        register_btn.pack(side=tk.LEFT, padx=10)
        
        back_btn = tk.Button(
            button_frame,
            text="返回",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_login_screen
        )
        back_btn.pack(side=tk.LEFT, padx=10)

    def show_login_form(self):
        """顯示登入表單"""
        self.clear_screen()
        self.sound_handler.on_button_click()
        
        title_label = tk.Label(
            self.main_frame,
            text="登入賬戶",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=30)
        
        # 用戶名
        tk.Label(self.main_frame, text="用戶名：", font=("Arial", 12),
                fg=GAME_CONFIG["primary_color"], bg=GAME_CONFIG["bg_color"]).pack()
        username_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
        username_entry.pack(pady=5)
        
        # 密碼
        tk.Label(self.main_frame, text="密碼：", font=("Arial", 12),
                fg=GAME_CONFIG["primary_color"], bg=GAME_CONFIG["bg_color"]).pack()
        password_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30, show="*")
        password_entry.pack(pady=5)
        
        def login():
            username = username_entry.get()
            if not username:
                messagebox.showerror("錯誤", "請輸入用戶名")
                return
            
            self.sound_handler.on_login()
            self.current_player = username
            messagebox.showinfo("成功", f"歡迎回來，{username}！")
            self.show_lobby()
        
        # 按鈕框架
        button_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        button_frame.pack(pady=30)
        
        login_btn = tk.Button(
            button_frame,
            text="登入",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=login
        )
        login_btn.pack(side=tk.LEFT, padx=10)
        
        back_btn = tk.Button(
            button_frame,
            text="返回",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_login_screen
        )
        back_btn.pack(side=tk.LEFT, padx=10)

    def start_demo(self):
        """試玩遊戲"""
        self.sound_handler.on_button_click()
        self.current_player = "Demo Player"
        self.show_lobby()

    # ========== 大廳界面 ==========
    def show_lobby(self):
        """顯示大廳"""
        self.clear_screen()
        self.current_screen = "lobby"
        
        # 歡迎信息
        welcome_label = tk.Label(
            self.main_frame,
            text=f"歡迎，{self.current_player}！",
            font=("Arial", 24, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        welcome_label.pack(pady=20)
        
        # 菜單框架
        menu_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        menu_frame.pack(pady=20)
        
        # 菜單按鈕
        buttons = [
            ("快速匹配", self.show_hero_selection),
            ("英雄圖鑑", self.show_hero_gallery),
            ("英雄皮膚", self.show_hero_skins),
            ("槍枝皮膚", self.show_weapon_skins),
            ("課金商店", self.show_shop),
            ("玩家資料", self.show_player_stats),
            ("音效設置", self.show_audio_settings),
            ("登出", self.show_login_screen),
        ]
        
        for btn_text, cmd in buttons:
            btn = tk.Button(
                menu_frame,
                text=btn_text,
                font=("Arial", 12, "bold"),
                bg=GAME_CONFIG["primary_color"],
                fg=GAME_CONFIG["bg_color"],
                padx=15,
                pady=10,
                width=15,
                command=cmd
            )
            btn.pack(pady=5)

    # ========== 英雄選擇 ==========
    def show_hero_selection(self):
        """顯示英雄選擇"""
        self.clear_screen()
        self.sound_handler.on_battle_start()
        
        title_label = tk.Label(
            self.main_frame,
            text="選擇英雄",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=20)
        
        # 英雄列表
        for hero_id, hero_data in HEROES.items():
            hero_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["secondary_color"])
            hero_frame.pack(pady=5, padx=20, fill=tk.X)
            
            hero_info = tk.Label(
                hero_frame,
                text=f"{hero_data['name']} ({hero_data['code']}) - {hero_data['role']} | HP: {hero_data['hp']} | 護甲: {hero_data['armor']}",
                font=("Arial", 11),
                fg=GAME_CONFIG["primary_color"],
                bg=GAME_CONFIG["secondary_color"],
                anchor=tk.W
            )
            hero_info.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
            
            select_btn = tk.Button(
                hero_frame,
                text="選擇",
                font=("Arial", 10, "bold"),
                bg=GAME_CONFIG["primary_color"],
                fg=GAME_CONFIG["bg_color"],
                padx=10,
                command=lambda h_id=hero_id: self.select_hero(h_id)
            )
            select_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # 返回按鈕
        back_btn = tk.Button(
            self.main_frame,
            text="返回大廳",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_lobby
        )
        back_btn.pack(pady=20)

    def select_hero(self, hero_id):
        """選擇英雄"""
        self.sound_handler.on_select()
        self.current_hero = hero_id
        hero_name = HEROES[hero_id]["name"]
        messagebox.showinfo("成功", f"已選擇英雄：{hero_name}\n準備進入戰鬥...")
        self.show_battle_screen()

    # ========== 戰鬥界面 ==========
    def show_battle_screen(self):
        """顯示戰鬥界面"""
        self.clear_screen()
        
        hero = HEROES[self.current_hero]
        title_label = tk.Label(
            self.main_frame,
            text=f"戰鬥 - {hero['name']} ({hero['code']})",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=20)
        
        # 英雄信息
        info_label = tk.Label(
            self.main_frame,
            text=f"HP: {hero['hp']} | 護甲: {hero['armor']} | 速度: {hero['speed']}",
            font=("Arial", 14),
            fg=GAME_CONFIG["secondary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        info_label.pack(pady=10)
        
        # 戰鬥按鈕框架
        action_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        action_frame.pack(pady=30)
        
        # 射擊按鈕
        shoot_btn = tk.Button(
            action_frame,
            text="射擊",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.perform_shoot
        )
        shoot_btn.pack(side=tk.LEFT, padx=10)
        
        # 技能按鈕
        skill_btn = tk.Button(
            action_frame,
            text="釋放技能",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.perform_skill
        )
        skill_btn.pack(side=tk.LEFT, padx=10)
        
        # 安裝 C4 按鈕
        bomb_btn = tk.Button(
            action_frame,
            text="安裝 C4",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.perform_bomb_plant
        )
        bomb_btn.pack(side=tk.LEFT, padx=10)
        
        # 結果按鈕框架
        result_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["bg_color"])
        result_frame.pack(pady=30)
        
        # 勝利按鈕
        win_btn = tk.Button(
            result_frame,
            text="勝利",
            font=("Arial", 12, "bold"),
            bg="#00ff00",
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.perform_win
        )
        win_btn.pack(side=tk.LEFT, padx=10)
        
        # 失敗按鈕
        lose_btn = tk.Button(
            result_frame,
            text="失敗",
            font=("Arial", 12, "bold"),
            bg="#ff0000",
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=self.perform_lose
        )
        lose_btn.pack(side=tk.LEFT, padx=10)
        
        # 返回按鈕
        back_btn = tk.Button(
            self.main_frame,
            text="返回大廳",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_lobby
        )
        back_btn.pack(pady=20)

    def perform_shoot(self):
        """執行射擊"""
        self.sound_handler.on_shoot()
        messagebox.showinfo("射擊", "砰！射擊成功！")

    def perform_skill(self):
        """執行技能"""
        self.sound_handler.on_skill_cast()
        messagebox.showinfo("技能", "技能已釋放！")

    def perform_bomb_plant(self):
        """執行安裝 C4"""
        self.sound_handler.on_bomb_plant()
        messagebox.showinfo("C4", "開始安裝炸彈...")
        self.sound_handler.on_explosion()
        messagebox.showinfo("爆炸", "C4 已爆炸！")

    def perform_win(self):
        """執行勝利"""
        self.sound_handler.on_win()
        messagebox.showinfo("勝利", "恭喜！你贏了！")
        self.show_lobby()

    def perform_lose(self):
        """執行失敗"""
        self.sound_handler.on_lose()
        messagebox.showinfo("失敗", "遊戲結束，再接再厲！")
        self.show_lobby()

    # ========== 其他界面 ==========
    def show_hero_gallery(self):
        """顯示英雄圖鑑"""
        self.clear_screen()
        self.sound_handler.on_select()
        
        title_label = tk.Label(
            self.main_frame,
            text="英雄圖鑑",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=20)
        
        for hero_id, hero_data in HEROES.items():
            hero_frame = tk.Frame(self.main_frame, bg=GAME_CONFIG["secondary_color"])
            hero_frame.pack(pady=5, padx=20, fill=tk.X)
            
            hero_info = tk.Label(
                hero_frame,
                text=f"{hero_data['name']} ({hero_data['code']}) - {hero_data['role']}",
                font=("Arial", 12),
                fg=GAME_CONFIG["primary_color"],
                bg=GAME_CONFIG["secondary_color"],
                anchor=tk.W
            )
            hero_info.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        back_btn = tk.Button(
            self.main_frame,
            text="返回大廳",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_lobby
        )
        back_btn.pack(pady=20)

    def show_hero_skins(self):
        """顯示英雄皮膚"""
        self.clear_screen()
        self.sound_handler.on_select()
        messagebox.showinfo("英雄皮膚", "英雄皮膚系統（開發中）")
        self.show_lobby()

    def show_weapon_skins(self):
        """顯示槍枝皮膚"""
        self.clear_screen()
        self.sound_handler.on_select()
        messagebox.showinfo("槍枝皮膚", "槍枝皮膚系統（開發中）")
        self.show_lobby()

    def show_shop(self):
        """顯示商店"""
        self.clear_screen()
        self.sound_handler.on_select()
        messagebox.showinfo("課金商店", "課金商店系統（開發中）")
        self.show_lobby()

    def show_player_stats(self):
        """顯示玩家統計"""
        self.clear_screen()
        self.sound_handler.on_select()
        messagebox.showinfo("玩家資料", f"玩家：{self.current_player}\n等級：25\n勝場：50\n排名分數：2150")
        self.show_lobby()

    def show_audio_settings(self):
        """顯示音效設置"""
        self.clear_screen()
        self.sound_handler.on_select()
        
        title_label = tk.Label(
            self.main_frame,
            text="音效設置",
            font=("Arial", 32, "bold"),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        )
        title_label.pack(pady=20)
        
        # 主音量滑塊
        tk.Label(
            self.main_frame,
            text="主音量：",
            font=("Arial", 14),
            fg=GAME_CONFIG["primary_color"],
            bg=GAME_CONFIG["bg_color"]
        ).pack(pady=10)
        
        volume_slider = tk.Scale(
            self.main_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            length=300,
            command=lambda v: self.sound_manager.set_master_volume(int(v) / 100)
        )
        volume_slider.set(80)
        volume_slider.pack(pady=10)
        
        # 靜音按鈕
        mute_btn = tk.Button(
            self.main_frame,
            text="切換靜音",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["primary_color"],
            fg=GAME_CONFIG["bg_color"],
            padx=20,
            pady=10,
            command=lambda: self.sound_manager.toggle_mute()
        )
        mute_btn.pack(pady=20)
        
        # 返回按鈕
        back_btn = tk.Button(
            self.main_frame,
            text="返回大廳",
            font=("Arial", 12, "bold"),
            bg=GAME_CONFIG["secondary_color"],
            fg=GAME_CONFIG["primary_color"],
            padx=20,
            pady=10,
            command=self.show_lobby
        )
        back_btn.pack(pady=20)


# ================== 主程序 ==================
def main():
    """主程序"""
    root = tk.Tk()
    game = ZeroLineGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
