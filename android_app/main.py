"""
DeepSeek 余额悬浮球 - Android
============================
手机桌面悬浮显示余额，拖拽移动，双击设置
"""

from kivy.config import Config
Config.set("graphics", "width", "240")
Config.set("graphics", "height", "90")
Config.set("graphics", "borderless", "1")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "fullscreen", "0")

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

DEEPSEEK_URL = "https://api.deepseek.com/user/balance"


class FloatingWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore("ds_config.json")
        self.api_key = ""
        self.balance = 0.0
        self.available = False

        if self.store.exists("config"):
            self.api_key = self.store.get("config").get("api_key", "")

        # 悬浮球位置
        self.touch_start = None
        self.win_start = None

        # 背景
        with self.canvas.before:
            Color(0.086, 0.129, 0.243, 0.92)
            self.bg = RoundedRectangle(
                size=(dp(240), dp(90)),
                pos=(0, 0),
                radius=[(dp(20), dp(20))]*4
            )

        # 余额数字
        self.balance_label = Label(
            text=self._display_text(),
            font_size=dp(32),
            bold=True,
            color=(0, 0.83, 0.67, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(None, None),
            size=(dp(240), dp(40)),
        )
        self.add_widget(self.balance_label)

        # 底部文字
        self.info_label = Label(
            text=self._info_text(),
            font_size=dp(10),
            color=(0.53, 0.53, 0.67, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.18},
            size_hint=(None, None),
            size=(dp(240), dp(16)),
        )
        self.add_widget(self.info_label)

        # 事件
        Window.bind(on_touch_down=self._on_down)
        Window.bind(on_touch_move=self._on_move)
        Window.bind(on_touch_up=self._on_up)

        # 自动查询
        if self.api_key:
            Clock.schedule_once(lambda dt: self.fetch(), 0.5)
        Clock.schedule_interval(lambda dt: self.fetch(), 60)

    def _display_text(self):
        if not self.api_key:
            return "⚙️"
        return f"¥{self.balance:.2f}" if self.balance else "--.--"

    def _info_text(self):
        if not self.api_key:
            return "双击设置 API Key"
        return "● 正常" if self.available else "● 异常"

    def fetch(self):
        if not self.api_key:
            return
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        UrlRequest(DEEPSEEK_URL, req_headers=headers,
                   on_success=self._ok, on_failure=self._fail, on_error=self._fail, timeout=10)

    def _ok(self, req, res):
        try:
            info = (res.get("balance_infos") or [{}])[0]
            self.balance = float(info.get("total_balance", res.get("balance", 0)))
            self.available = res.get("is_available", False)
            self.balance_label.text = self._display_text()
            self.balance_label.color = (0, 0.83, 0.67, 1) if self.available else (1, 0.28, 0.34, 1)
            self.info_label.text = self._info_text()
        except:
            pass

    def _fail(self, req, err):
        self.info_label.text = "连接失败"

    def _on_down(self, win, touch):
        if touch.is_double_tap:
            self._show_settings()
            return
        self.touch_start = (touch.x, touch.y)
        self.win_start = (Window.left if hasattr(Window, 'left') else 0,
                          Window.top if hasattr(Window, 'top') else 0)

    def _on_move(self, win, touch):
        if self.touch_start and self.win_start:
            dx = touch.x - self.touch_start[0]
            dy = touch.y - self.touch_start[1]
            try:
                from kivy.core.window import Window as W
                W.left = int(self.win_start[0] + dx)
                W.top = int(self.win_start[1] + dy)
            except:
                pass
        return True

    def _on_up(self, win, touch):
        self.touch_start = None

    def _show_settings(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        content.add_widget(Label(text="DeepSeek API Key", font_size=dp(14), size_hint_y=0.3))
        ti = TextInput(text=self.api_key, hint_text="sk-xxx", multiline=False,
                       size_hint_y=0.4, background_color=(0.2, 0.2, 0.4, 1),
                       foreground_color=(1, 1, 1, 1), cursor_color=(0, 0.83, 0.67, 1))
        content.add_widget(ti)

        def save(btn):
            key = ti.text.strip()
            if key:
                self.api_key = key
                self.store.put("config", api_key=key)
                popup.dismiss()
                self.balance_label.text = "⋯"
                Clock.schedule_once(lambda dt: self.fetch(), 0.3)
                Clock.schedule_interval(lambda dt: self.fetch(), 60)

        btn = Button(text="💾 保存", size_hint_y=0.4,
                     background_color=(0, 0.83, 0.67, 1), color=(0, 0, 0, 1))
        btn.bind(on_press=save)
        content.add_widget(btn)

        popup = Popup(title="⚙️ 设置", content=content,
                      size_hint=(0.75, 0.45), background="#16213e",
                      title_color=(1, 1, 1, 1), separator_color="#2a2a55")
        popup.open()


class DSBalanceApp(App):
    def build(self):
        self.title = "DS 余额"
        return FloatingWidget()

    def on_start(self):
        # Android 悬浮窗权限
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.SYSTEM_ALERT_WINDOW,
                ])
                from android import mActivity
                window = mActivity.getWindow()
                params = window.getAttributes()
                params.type = 2003  # TYPE_SYSTEM_OVERLAY
                params.flags |= 0x100  # FLAG_NOT_FOCUSABLE
                window.setAttributes(params)
            except:
                pass

    def on_pause(self):
        return True


if __name__ == "__main__":
    DSBalanceApp().run()
