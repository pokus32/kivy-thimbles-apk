import random
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Quad, Ellipse, Rectangle
from kivy.clock import Clock

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text='НАПЁРСТКИ\nOFFLINE', font_size='36sp', halign='center', bold=True, color=(1, 0.8, 0, 1)))
        
        self.balance_label = Label(text='Ваш баланс: 0 руб.', font_size='22sp', color=(0.2, 0.9, 0.2, 1))
        layout.add_widget(self.balance_label)
        
        btn_play = Button(text='Играть (Одиночный)', font_size='22sp', size_hint=(1, 0.18))
        btn_play.bind(on_press=self.go_to_quick_game)
        layout.add_widget(btn_play)
        
        btn_settings = Button(text='Настройки', font_size='22sp', size_hint=(1, 0.18))
        layout.add_widget(btn_settings)
        
        btn_tournament = Button(text='Онлайн режим (Турнир)', font_size='22sp', size_hint=(1, 0.18), background_color=(0.2, 0.6, 1, 1))
        btn_tournament.bind(on_press=self.go_to_tournament)
        layout.add_widget(btn_tournament)
        
        layout.add_widget(Label(text='v 1.0', font_size='14sp', size_hint=(1, 0.05), halign='right'))
        self.add_widget(layout)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.balance_label.text = f'Ваш баланс: {app.wallet} руб.'

    def go_to_quick_game(self, instance):
        App.get_running_app().game_mode = "quick"
        self.manager.current = 'game'

    def go_to_tournament(self, instance):
        App.get_running_app().game_mode = "tournament"
        self.manager.current = 'game'

class GameCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.winning_cup = None
        self.chosen_cup = None
        self.game_state = "intro" 
        self.bind(size=self.draw_scene, pos=self.draw_scene)

    def draw_scene(self, *args):
        self.canvas.clear()
        with self.canvas:
            cx = self.center_x
            cy = self.top - 130
            Color(0.4, 0.7, 0.3, 1)
            Rectangle(pos=(cx - 60, cy - 60), size=(120, 80))
            Color(0.8, 0.3, 0.6, 1)
            Rectangle(pos=(cx - 55, cy + 20), size=(110, 50))
            Color(1, 1, 1, 1)
            Rectangle(pos=(cx - 35, cy + 35), size=(70, 20))
            Color(0, 0, 0, 1)
            Ellipse(pos=(cx - 20, cy + 42), size=(6, 6))
            Ellipse(pos=(cx + 10, cy + 42), size=(6, 6))

            cup_width = 110
            cup_height = 130
            positions = [self.width * 0.22, self.width * 0.5, self.width * 0.78]

            for i, x in enumerate(positions):
                if self.game_state == "reveal" and i == self.winning_cup:
                    Color(1, 0.1, 0.1, 1)  
                    Ellipse(pos=(x - 18, self.y + 40), size=(36, 36))

                if self.game_state == "reveal":
                    if i == self.winning_cup: Color(0.2, 0.8, 0.2, 1)  
                    elif i == self.chosen_cup: Color(0.8, 0.2, 0.2, 1)  
                    else: Color(0.6, 0.4, 0.3, 1)  
                else: Color(0.6, 0.4, 0.3, 1)  

                y_bottom = self.y + 30
                y_top = y_bottom + cup_height
                if self.game_state == "reveal" and i == self.winning_cup:
                    y_bottom += 60
                    y_top += 60

                Quad(points=[x - cup_width/2, y_bottom, x + cup_width/2, y_bottom, x + cup_width/3, y_top, x - cup_width/3, y_top])
                Color(0.4, 0.2, 0.1, 1)
                Rectangle(pos=(x - cup_width/2.2, y_bottom + 20), size=(cup_width * 0.85, 8))

    def on_touch_down(self, touch):
        if self.game_state != "playing": return super().on_touch_down(touch)
        positions = [self.width * 0.22, self.width * 0.5, self.width * 0.78]
        for i, x in enumerate(positions):
            if x - 60 < touch.x < x + 60 and self.y < touch.y < self.y + 180:
                self.parent.parent.check_cup(i)  
                return True
        return super().on_touch_down(touch)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.winning_cup = None
        self.stages = ["Четвертьфинал", "Полуфинал", "ФИНАЛ!"]
        self.current_stage_idx = 0
        
        root_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.mode_label = Label(text="", font_size='20sp', bold=True, size_hint=(1, 0.08), color=(1, 0.5, 0, 1))
        root_layout.add_widget(self.mode_label)
        
        self.status_label = Label(text='', font_size='16sp', size_hint=(1, 0.08), halign='center')
        root_layout.add_widget(self.status_label)
        
        self.game_canvas = GameCanvas(size_hint=(1, 0.69))
        root_layout.add_widget(self.game_canvas)
        
        bottom_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        self.btn_shuffle = Button(text='Перемешать', font_size='18sp', background_color=(0.2, 0.8, 0.2, 1))
        self.btn_shuffle.bind(on_press=self.start_shuffle)
        
        btn_back = Button(text='В меню', font_size='18sp', size_hint=(0.4, 1))
        btn_back.bind(on_press=self.go_to_menu)
        
        bottom_layout.add_widget(self.btn_shuffle)
        bottom_layout.add_widget(btn_back)
        root_layout.add_widget(bottom_layout)
        self.add_widget(root_layout)

    def on_enter(self, *args):
        app = App.get_running_app()
        self.btn_shuffle.disabled = False
        self.game_canvas.game_state = "intro"
        self.game_canvas.draw_scene()
        
        if app.game_mode == "tournament":
            self.current_stage_idx = 0
            self.mode_label.text = f"Онлайн турнир: {self.stages[self.current_stage_idx]}"
            self.status_label.text = 'Нажмите "Перемешать", чтобы начать раунд!'
        else:
            self.mode_label.text = "Одиночная тренировка"
            self.status_label.text = 'Нажмите "Перемешать", чтобы сыграть матч!'

    def start_shuffle(self, instance):
        self.status_label.text = 'Робот-ниндзя перемешивает...'
        self.game_canvas.game_state = "shuffling"
        self.game_canvas.draw_scene()
        Clock.schedule_once(self.finish_shuffle, 1.0)

    def finish_shuffle(self, dt):
        self.winning_cup = random.randint(0, 2)
        self.game_canvas.winning_cup = self.winning_cup
        self.game_canvas.game_state = "playing"
        self.game_canvas.draw_scene()
        self.status_label.text = 'Готово! Тапни по стаканчику!'

    def check_cup(self, chosen_idx):
        if self.winning_cup is None: return
        self.game_canvas.chosen_cup = chosen_idx
        self.game_canvas.game_state = "reveal"
        self.game_canvas.draw_scene()
        app = App.get_running_app()

        if chosen_idx == self.winning_cup:
            if app.game_mode == "tournament":
                if self.current_stage_idx == 0:
                    self.current_stage_idx = 1
                    self.mode_label.text = f"Онлайн турнир: {self.stages[self.current_stage_idx]}"
                    self.status_label.text = '🎉 Четвертьфинал пройден! +100 руб!'
                    app.add_money(100)
                elif self.current_stage_idx == 1:
                    self.current_stage_idx = 2
                    self.mode_label.text = f"Онлайн турнир: {self.stages[self.current_stage_idx]}"
                    self.status_label.text = '🎉 Полуфинал взят! +500 руб!'
                    app.add_money(500)
                elif self.current_stage_idx == 2:
                    self.status_label.text = '🏆 ЧЕМПИОН! Вы выиграли 1000 руб!'
                    app.add_money(1000)
                    self.btn_shuffle.disabled = True
            else:
                self.status_label.text = '🎉 Вы угадали! Робот-ниндзя побежден!'
        else:
            if app.game_mode == "tournament":
                self.status_label.text = '❌ Вы выбыли из турнира! Попробуйте снова.'
            else:
                self.status_label.text = '❌ Мимо! Попробуйте перемешать снова.'
            self.btn_shuffle.disabled = True
        self.winning_cup = None

    def go_to_menu(self, instance):
        self.manager.current = 'menu'

class ThimblesApp(App):
    def build(self):
        # Храним файл сохранения прямо на устройстве
        self.save_file = os.path.join(self.user_data_dir, 'wallet.txt')
        self.wallet = self.load_money()
        self.game_mode = "quick"
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

    def load_money(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                try: return int(f.read())
                except: return 0
        return 0

    def add_money(self, amount):
        self.wallet += amount
        with open(self.save_file, 'w') as f:
            f.write(str(self.wallet))

if __name__ == '__main__':
    ThimblesApp().run()
