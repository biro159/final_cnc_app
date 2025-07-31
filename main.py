import os
from functools import partial
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.label import MDLabel

from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Giả sử các file này đã có trong thư mục dự án
from gcode_logic import generate_gcode_logic
from plot_logic import get_rounded_rect_points
from circle_logic import get_spiral_points

class GcodeKivyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
        self.current_shape = "rectangle"
        self.inputs = {}

    def build(self):
        self.title = "Tạo Gcode CNC (Phiên bản Hoàn thiện)"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        self.main_layout = BoxLayout(padding=dp(10), spacing=dp(20))
        
        self.controls_layout = BoxLayout(
            orientation='vertical', spacing=dp(10), padding=dp(10), size_hint_y=None
        )
        self.controls_layout.bind(minimum_height=self.controls_layout.setter('height'))
        self.scroll_view = MDScrollView()
        self.scroll_view.add_widget(self.controls_layout)

        shape_selector_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # SỬA LỖI CUỐI CÙNG: Thêm 'x' vào lambda cho các nút này
        self.rect_button = MDRaisedButton(
            text="Chữ nhật",
            on_release=lambda x: self.select_shape("rectangle"),
        )
        self.circle_button = MDRaisedButton(
            text="Hốc tròn",
            on_release=lambda x: self.select_shape("circle"),
        )
        
        shape_selector_layout.add_widget(self.rect_button)
        shape_selector_layout.add_widget(self.circle_button)
        self.controls_layout.add_widget(shape_selector_layout)
        self.controls_layout.add_widget(MDLabel(height=dp(10), size_hint_y=None))

        self.input_container = BoxLayout(size_hint_y=None)
        self.input_container.bind(minimum_height=self.input_container.setter('height'))
        self.controls_layout.add_widget(self.input_container)
        
        self.rect_input_grid = self.create_rect_input_grid()
        self.circle_input_grid = self.create_circle_input_grid()
        
        self.input_container.add_widget(self.rect_input_grid)

        self.offset_button = MDRaisedButton(text="Offset: Center", size_hint_y=None, height=dp(40))
        self.offset_button.bind(on_release=self.open_offset_menu)
        self.current_offset = "center"
        
        # Giữ nguyên lambda không có tham số cho menu Offset
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Offset: Center", "height": dp(56), "on_release": lambda: self.set_offset("center")},
            {"viewclass": "OneLineListItem", "text": "Offset: Inside", "height": dp(56), "on_release": lambda: self.set_offset("inside")},
            {"viewclass": "OneLineListItem", "text": "Offset: Outside", "height": dp(56), "on_release": lambda: self.set_offset("outside")},
        ]
        self.offset_menu = MDDropdownMenu(caller=self.offset_button, items=menu_items, width_mult=4)
        self.controls_layout.add_widget(self.offset_button)

        action_buttons_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        button_preview = MDRaisedButton(text="Xem Trước", on_press=self.update_plot, md_bg_color=self.theme_cls.primary_color)
        button_export = MDRaisedButton(text="Xuất G-code", on_press=self.export_gcode)
        action_buttons_layout.add_widget(button_preview)
        action_buttons_layout.add_widget(button_export)
        self.controls_layout.add_widget(action_buttons_layout)

        self.plot_placeholder = BoxLayout()
        
        self.main_layout.add_widget(self.scroll_view)
        self.main_layout.add_widget(self.plot_placeholder)
        
        return self.main_layout
    
    def select_shape(self, shape, instance=None):
        self.current_shape = shape
        self.input_container.clear_widgets()
        
        is_rect = shape == "rectangle"
        self.input_container.add_widget(self.rect_input_grid if is_rect else self.circle_input_grid)
        self.rect_button.md_bg_color = self.theme_cls.primary_color if is_rect else self.theme_cls.disabled_hint_text_color
        self.circle_button.md_bg_color = self.theme_cls.primary_color if not is_rect else self.theme_cls.disabled_hint_text_color
        
        self.offset_button.disabled = not is_rect
        
        self.update_plot(None)

    def create_rect_input_grid(self):
        grid = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        params_config = {
            "width": ("Chiều rộng tổng (mm)", "100"), "height": ("Chiều cao tổng (mm)", "100"),
            "depth": ("Độ sâu Z (âm)", "-3"), "z_step": ("Lát cắt Z mỗi lớp:", "1"),
            "feed": ("Tốc độ G1", "800"), "z_safe": ("Z an toàn", "5"), 
            "tool_dia": ("Đường kính dao", "6"), "corner_radius": ("Bo góc R (mm)", "10"), 
            "num_layers": ("Số lớp (Nested)", "5"), "layer_step": ("Khoảng cách lớp", "10"), 
            "array_x": ("Số lượng theo X", "1"), "array_y": ("Số lượng theo Y", "1"), 
            "array_spacing_x": ("Khoảng cách X", "130"), "array_spacing_y": ("Khoảng cách Y", "130")
        }
        for key, (hint_text, default_text) in params_config.items():
            text_input = MDTextField(hint_text=hint_text, text=default_text)
            self.inputs[key] = text_input
            grid.add_widget(text_input)
        return grid

    def create_circle_input_grid(self):
        grid = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        params_config = {
            "center_x": ("Tâm X", "50"), "center_y": ("Tâm Y", "50"),
            "radius": ("Bán kính", "40"), "stepover": ("Stepover %", "40"),
            "depth": ("Độ sâu Z (âm)", "-3"), "z_step": ("Lát cắt Z mỗi lớp:", "1"),
            "feed": ("Tốc độ G1", "800"), "z_safe": ("Z an toàn", "5"), 
            "tool_dia": ("Đường kính dao", "6"),
        }
        for key, (hint_text, default_text) in params_config.items():
            text_input = MDTextField(hint_text=hint_text, text=default_text)
            self.inputs[key] = text_input
            grid.add_widget(text_input)
        return grid
    
    def on_start(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.plot_widget = FigureCanvasKivyAgg(self.fig)
        self.plot_placeholder.add_widget(self.plot_widget)
        
        self.select_shape("rectangle")
        Clock.schedule_once(lambda dt: self.on_window_resize(Window, Window.width, Window.height))

    def on_window_resize(self, window, width, height):
        threshold = dp(700)
        if width < threshold:
            self.main_layout.orientation = "vertical"
            self.scroll_view.size_hint = (1, 0.6)
            self.plot_placeholder.size_hint = (1, 0.4)
        else:
            self.main_layout.orientation = "horizontal"
            self.scroll_view.size_hint = (0.45, 1)
            self.plot_placeholder.size_hint = (0.55, 1)
        Clock.schedule_once(lambda dt: self.update_plot(None), 0.1)

    def open_offset_menu(self, button):
        self.offset_menu.open()

    # Giữ nguyên hàm set_offset không có 'instance'
    def set_offset(self, offset_type):
        self.current_offset = offset_type
        self.offset_button.text = f"Offset: {offset_type.capitalize()}"
        self.offset_menu.dismiss()
        self.update_plot(None)

    def get_params_from_ui(self):
        params = {}
        try:
            for key, widget in self.inputs.items():
                params[key] = widget.text
            
            params['offset_mode'] = self.current_offset
            params['current_shape'] = self.current_shape
            return params
        except Exception as e:
            return None

    def update_plot(self, instance):
        if not hasattr(self, 'ax'): return
        
        self.ax.clear()
        params_str = self.get_params_from_ui()
        
        try:
            params = {key: float(value) for key, value in params_str.items() if isinstance(value, str) and value.replace('.', '', 1).replace('-', '', 1).isdigit()}
        except (ValueError, TypeError):
            self.ax.grid(True, linestyle='--', alpha=0.6); self.plot_widget.draw(); return
        
        if self.current_shape == "rectangle":
            tool_dia = params.get('tool_dia', 6)
            offset_val = {"inside": tool_dia / 2, "outside": -tool_dia / 2, "center": 0}.get(self.current_offset, 0)
            
            for ix in range(int(params.get('array_x', 1))):
                for iy in range(int(params.get('array_y', 1))):
                    ox, oy = ix * params.get('array_spacing_x', 0), iy * params.get('array_spacing_y', 0)
                    for i in range(int(params.get('num_layers', 1))):
                        w = params.get('width', 100) - i * params.get('layer_step', 10) * 2
                        h = params.get('height', 100) - i * params.get('layer_step', 10) * 2
                        if w <= 0 or h <= 0: continue
                        x0, y0, r = ox + i * params.get('layer_step', 10), oy + i * params.get('layer_step', 10), params.get('corner_radius', 10)
                        
                        for xs, ys in get_rounded_rect_points(x0, y0, w, h, r): self.ax.plot(xs, ys, color='white', linewidth=1)
                        w_offset, h_offset, r_offset = w - 2 * offset_val, h - 2 * offset_val, r - offset_val
                        if r_offset < 0: r_offset = 0
                        for xs, ys in get_rounded_rect_points(x0 + offset_val, y0 + offset_val, w_offset, h_offset, r_offset): self.ax.plot(xs, ys, color=self.theme_cls.primary_light, linewidth=1.5)

        elif self.current_shape == "circle":
            center_x, center_y, radius = params.get('center_x', 50), params.get('center_y', 50), params.get('radius', 40)
            tool_dia, stepover = params.get('tool_dia', 6), params.get('stepover', 40)
            
            spiral_points = get_spiral_points(center_x, center_y, radius, tool_dia, stepover)
            if spiral_points:
                x_coords, y_coords = zip(*spiral_points)
                self.ax.plot(x_coords, y_coords, color=self.theme_cls.primary_light)

            self.ax.set_xlim(center_x - radius - 10, center_x + radius + 10)
            self.ax.set_ylim(center_y - radius - 10, center_y + radius + 10)

        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        try:
            self.fig.tight_layout(pad=0.5)
        except Exception:
            pass
        self.plot_widget.draw()

    def export_gcode(self, instance):
        params = self.get_params_from_ui()
        if not params:
            self.show_alert_dialog("Lỗi", "Vui lòng kiểm tra lại các thông số.")
            return

        self.generated_gcode = generate_gcode_logic(params)
        
        if "Lỗi" in self.generated_gcode:
            self.show_alert_dialog("Lỗi tạo G-code", self.generated_gcode)
        else:
            if not hasattr(self, 'save_dialog'):
                self.save_dialog_content = MDTextField(hint_text="Nhập tên file (ví dụ: part1)")
                self.save_dialog = MDDialog(
                    title="Lưu File G-code", type="custom", content_cls=self.save_dialog_content,
                    buttons=[
                        MDFlatButton(text="HỦY", on_release=lambda x: self.save_dialog.dismiss()),
                        MDRaisedButton(text="LƯU", on_release=self.save_file_action),
                    ],
                )
            self.save_dialog.open()
    
    def save_file_action(self, instance):
        filename = self.save_dialog_content.text.strip()
        if not filename: filename = "output"
        full_path = f"{filename}.nc"
        with open(full_path, 'w') as f:
            f.write(self.generated_gcode)
        self.save_dialog.dismiss()
        self.show_alert_dialog("Thành Công", f"Đã lưu file thành công tại:\n{os.path.abspath(full_path)}")

    def show_alert_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())])
        dialog.open()

if __name__ == '__main__':
    GcodeKivyApp().run()