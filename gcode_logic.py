import math
# Import hàm mới từ circle_logic
from circle_logic import generate_circle_pocket_gcode

def generate_gcode_logic(params):
    """
    Hàm điều phối: Gọi hàm tạo G-code tương ứng với hình dạng được chọn.
    """
    try:
        final_depth = float(params['depth'])
        z_step = abs(float(params['z_step']))
        z_safe = float(params['z_safe'])
        current_shape = params['current_shape']

        gcode_lines = []
        gcode_lines.append("G21 G90 G54")
        gcode_lines.append("T1 M6")
        gcode_lines.append("M3 S18000")
        gcode_lines.append(f"G0 Z{z_safe}")
        gcode_lines.append("G0 X0 Y0")

        if current_shape == 'rectangle':
            # Logic cho hình chữ nhật
            width = float(params['width']); height = float(params['height'])
            tool_dia = float(params['tool_dia']); r = float(params['corner_radius'])
            num_layers = int(params['num_layers']); layer_step = float(params['layer_step'])
            array_x = int(params['array_x']); array_y = int(params['array_y'])
            spacing_x = float(params['array_spacing_x']); spacing_y = float(params['array_spacing_y'])
            offset_type = params['offset_mode']

            tool_offset = {"inside": tool_dia / 2, "outside": -tool_dia / 2, "center": 0}.get(offset_type, 0)

            for ix in range(array_x):
                for iy in range(array_y):
                    ox, oy = ix * spacing_x, iy * spacing_y
                    for i in range(num_layers):
                        w, h = width - i * layer_step * 2, height - i * layer_step * 2
                        if w <= 0 or h <= 0: continue
                        
                        x0, y0 = ox + i * layer_step + tool_offset, oy + i * layer_step + tool_offset
                        w_offset, h_offset = w - 2 * tool_offset, h - 2 * tool_offset

                        current_depth = 0
                        while current_depth > final_depth:
                            current_depth -= z_step
                            if current_depth < final_depth: current_depth = final_depth
                            
                            sx, sy = x0 + r, y0
                            gcode_lines.append(f"G0 X{sx:.3f} Y{sy:.3f}")
                            gcode_lines.append(f"G1 Z{current_depth:.3f} F{params['feed'] / 2}")
                            gcode_lines.append(f"G1 X{x0 + w_offset - r:.3f} Y{y0:.3f} F{params['feed']}")
                            gcode_lines.append(f"G3 X{x0 + w_offset:.3f} Y{y0 + r:.3f} R{r:.3f}")
                            gcode_lines.append(f"G1 X{x0 + w_offset:.3f} Y{y0 + h_offset - r:.3f}")
                            gcode_lines.append(f"G3 X{x0 + w_offset - r:.3f} Y{y0 + h_offset:.3f} R{r:.3f}")
                            gcode_lines.append(f"G1 X{x0 + r:.3f} Y{y0 + h_offset:.3f}")
                            gcode_lines.append(f"G3 X{x0:.3f} Y{y0 + h_offset - r:.3f} R{r:.3f}")
                            gcode_lines.append(f"G1 X{x0:.3f} Y{y0 + r:.3f}")
                            gcode_lines.append(f"G3 X{sx:.3f} Y{sy:.3f} R{r:.3f}")
                        
                        gcode_lines.append(f"G0 Z{z_safe:.3f}")

        elif current_shape == 'circle':
            # Logic cho hốc tròn
            current_depth = 0
            while current_depth > final_depth:
                current_depth -= z_step
                if current_depth < final_depth: current_depth = final_depth
                
                # Gọi hàm tạo G-code cho hốc tròn cho mỗi lớp Z
                circle_gcode = generate_circle_pocket_gcode(params, current_depth)
                gcode_lines.extend(circle_gcode)

            gcode_lines.append(f"G0 Z{z_safe:.3f}")

        gcode_lines.append("M5")
        gcode_lines.append("M30")
        
        return "\n".join(gcode_lines)

    except (ValueError, KeyError) as e:
        return f"Lỗi Dữ Liệu Đầu Vào: {e}. Vui lòng kiểm tra lại các thông số."