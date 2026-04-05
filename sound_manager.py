"""
《代號：零線》完整音效管理系統
支援 12 款專業遊戲音效
"""

import os
import subprocess
import threading
import time
from typing import Dict, Optional


class SoundEffect:
    """音效類"""
    def __init__(self, name: str, file_path: str, volume: float = 1.0, loop: bool = False):
        self.name = name
        self.file_path = file_path
        self.volume = volume
        self.loop = loop
        self.is_playing = False
        self.process = None

    def play(self):
        """播放音效"""
        if not os.path.exists(self.file_path):
            print(f"⚠️ 警告：音效文件不存在 - {self.file_path}")
            return

        # 在新線程中播放，避免阻塞 UI
        thread = threading.Thread(target=self._play_async, daemon=True)
        thread.start()

    def _play_async(self):
        """異步播放音效"""
        try:
            self.is_playing = True
            
            # 嘗試使用 ffplay 播放
            cmd = [
                'ffplay',
                '-nodisp',
                '-autoexit',
                '-volume', str(int(self.volume * 100)),
                self.file_path
            ]
            
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process.wait()
            
        except FileNotFoundError:
            # 如果 ffplay 不可用，嘗試其他方法
            try:
                import wave
                import pyaudio
                self._play_with_pyaudio()
            except ImportError:
                print(f"⚠️ 無法播放音效：{self.name}（缺少音效播放庫）")
        finally:
            self.is_playing = False

    def _play_with_pyaudio(self):
        """使用 PyAudio 播放"""
        try:
            import wave
            import pyaudio
            
            with wave.open(self.file_path, 'rb') as wav_file:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=p.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True
                )
                
                data = wav_file.readframes(1024)
                while data:
                    stream.write(data)
                    data = wav_file.readframes(1024)
                
                stream.stop_stream()
                stream.close()
                p.terminate()
        except Exception as e:
            print(f"⚠️ PyAudio 播放失敗：{e}")

    def stop(self):
        """停止播放"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                pass
        self.is_playing = False


class SoundManager:
    """音效管理器"""
    def __init__(self, sound_dir: str = "/home/ubuntu"):
        self.sound_dir = sound_dir
        self.sounds: Dict[str, SoundEffect] = {}
        self.master_volume = 1.0
        self.is_muted = False
        self._load_sounds()

    def _load_sounds(self):
        """加載所有音效"""
        # UI & Menu 音效
        self.add_sound("login", "login.wav", volume=0.8)
        self.add_sound("select", "select.wav", volume=0.6)

        # Combat 音效
        self.add_sound("battle", "battle.wav", volume=0.9)
        self.add_sound("shoot", "shoot.wav", volume=0.7)
        self.add_sound("skill", "skill.wav", volume=0.8)

        # Objective 音效
        self.add_sound("bomb_plant", "bomb_plant.wav", volume=0.8)
        self.add_sound("defuse", "defuse.wav", volume=0.8)
        self.add_sound("explode", "explode.wav", volume=0.95)

        # Outcome 音效
        self.add_sound("win", "win.wav", volume=0.9)
        self.add_sound("lose", "lose.wav", volume=0.8)

        # 原有的啟動音效
        self.add_sound("startup", "tech_startup_intro.wav", volume=0.8)
        self.add_sound("click", "ui_click_1.wav", volume=0.5)

    def add_sound(self, name: str, filename: str, volume: float = 1.0, loop: bool = False):
        """添加音效"""
        file_path = os.path.join(self.sound_dir, filename)
        sound = SoundEffect(name, file_path, volume=volume * self.master_volume, loop=loop)
        self.sounds[name] = sound

    def play(self, sound_name: str):
        """播放音效"""
        if self.is_muted:
            return

        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"⚠️ 警告：音效不存在 - {sound_name}")

    def stop(self, sound_name: str):
        """停止播放"""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def stop_all(self):
        """停止所有音效"""
        for sound in self.sounds.values():
            sound.stop()

    def set_master_volume(self, volume: float):
        """設置主音量（0-1）"""
        self.master_volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.volume = sound.volume * self.master_volume

    def set_sound_volume(self, sound_name: str, volume: float):
        """設置單個音效音量"""
        if sound_name in self.sounds:
            self.sounds[sound_name].volume = max(0, min(1, volume))

    def mute(self):
        """靜音"""
        self.is_muted = True
        self.stop_all()

    def unmute(self):
        """取消靜音"""
        self.is_muted = False

    def toggle_mute(self):
        """切換靜音"""
        if self.is_muted:
            self.unmute()
        else:
            self.mute()

    def get_sound_info(self):
        """獲取所有音效信息"""
        info = {}
        for name, sound in self.sounds.items():
            info[name] = {
                "file": sound.file_path,
                "volume": sound.volume,
                "is_playing": sound.is_playing,
                "exists": os.path.exists(sound.file_path)
            }
        return info


class SoundEventHandler:
    """音效事件處理器"""
    def __init__(self, sound_manager: SoundManager):
        self.sound_manager = sound_manager

    # ========== UI & Menu Events ==========
    def on_login(self):
        """登入事件"""
        self.sound_manager.play("login")

    def on_select(self):
        """選擇事件"""
        self.sound_manager.play("select")

    def on_button_click(self):
        """按鈕點擊事件"""
        self.sound_manager.play("click")

    # ========== Combat Events ==========
    def on_battle_start(self):
        """戰鬥開始事件"""
        self.sound_manager.play("battle")

    def on_shoot(self):
        """射擊事件"""
        self.sound_manager.play("shoot")

    def on_skill_cast(self):
        """技能施放事件"""
        self.sound_manager.play("skill")

    # ========== Objective Events ==========
    def on_bomb_plant(self):
        """安裝炸彈事件"""
        self.sound_manager.play("bomb_plant")

    def on_defuse_start(self):
        """開始拆彈事件"""
        self.sound_manager.play("defuse")

    def on_explosion(self):
        """爆炸事件"""
        self.sound_manager.play("explode")

    # ========== Outcome Events ==========
    def on_win(self):
        """勝利事件"""
        self.sound_manager.play("win")

    def on_lose(self):
        """失敗事件"""
        self.sound_manager.play("lose")

    # ========== Startup Events ==========
    def on_game_startup(self):
        """遊戲啟動事件"""
        self.sound_manager.play("startup")


class SoundPresets:
    """音效預設"""
    
    @staticmethod
    def get_ui_sounds():
        """獲取 UI 音效"""
        return ["login", "select", "click"]

    @staticmethod
    def get_combat_sounds():
        """獲取戰鬥音效"""
        return ["battle", "shoot", "skill"]

    @staticmethod
    def get_objective_sounds():
        """獲取目標音效"""
        return ["bomb_plant", "defuse", "explode"]

    @staticmethod
    def get_outcome_sounds():
        """獲取結果音效"""
        return ["win", "lose"]

    @staticmethod
    def get_all_sounds():
        """獲取所有音效"""
        return (SoundPresets.get_ui_sounds() + 
                SoundPresets.get_combat_sounds() + 
                SoundPresets.get_objective_sounds() + 
                SoundPresets.get_outcome_sounds())


# 全局音效管理器實例
_global_sound_manager: Optional[SoundManager] = None


def get_sound_manager() -> SoundManager:
    """獲取全局音效管理器"""
    global _global_sound_manager
    if _global_sound_manager is None:
        _global_sound_manager = SoundManager()
    return _global_sound_manager


def play_sound(sound_name: str):
    """播放音效（全局函數）"""
    get_sound_manager().play(sound_name)


def stop_sound(sound_name: str):
    """停止音效（全局函數）"""
    get_sound_manager().stop(sound_name)


def stop_all_sounds():
    """停止所有音效（全局函數）"""
    get_sound_manager().stop_all()


def set_master_volume(volume: float):
    """設置主音量（全局函數）"""
    get_sound_manager().set_master_volume(volume)


def toggle_mute():
    """切換靜音（全局函數）"""
    get_sound_manager().toggle_mute()


if __name__ == "__main__":
    # 測試音效管理系統
    print("=== 音效管理系統測試 ===\n")
    
    manager = SoundManager()
    handler = SoundEventHandler(manager)
    
    print("可用音效：")
    for name in SoundPresets.get_all_sounds():
        print(f"  - {name}")
    
    print("\n音效文件狀態：")
    info = manager.get_sound_info()
    for name, details in info.items():
        status = "✅" if details["exists"] else "❌"
        print(f"  {status} {name}: {details['file']}")
    
    print("\n測試音效播放...")
    print("播放登入音效...")
    handler.on_login()
    time.sleep(2)
    
    print("播放選擇音效...")
    handler.on_select()
    time.sleep(1)
    
    print("播放戰鬥音效...")
    handler.on_battle_start()
    time.sleep(3)
    
    print("\n✅ 音效管理系統測試完成！")
