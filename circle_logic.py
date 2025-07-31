import math

def get_spiral_points(center_x, center_y, radius, tool_dia, stepover_percent):
    """
    Tính toán các điểm cho đường chạy dao xoắn ốc để phay hốc tròn.
    """
    points = []
    stepover = tool_dia * (stepover_percent / 100.0)
    if stepover <= 0:
        stepover = tool_dia * 0.4

    # Bán kính hiệu dụng (tính cả bán kính dao)
    effective_radius = radius - (tool_dia / 2)
    if effective_radius <= 0:
        return points # Không thể tạo đường chạy dao

    # Tính toán các tham số cho đường xoắn ốc Archimedean: r = a * theta
    a = stepover / (2 * math.pi)
    
    # Bắt đầu từ tâm
    theta = 0
    points.append((center_x, center_y))

    while a * theta < effective_radius:
        x = center_x + (a * theta) * math.cos(theta)
        y = center_y + (a * theta) * math.sin(theta)
        points.append((x, y))
        theta += math.radians(10) # Tăng góc, 10 độ mỗi bước cho đường cong mượt

    # Thêm điểm cuối cùng trên đường tròn
    x_final = center_x + effective_radius * math.cos(theta)
    y_final = center_y + effective_radius * math.sin(theta)
    points.append((x_final, y_final))

    return points

def generate_circle_pocket_gcode(params, z_level):
    """
    Tạo G-code cho một lớp Z của hốc tròn.
    """
    center_x = params.get('center_x', 50)
    center_y = params.get('center_y', 50)
    radius = params.get('radius', 40)
    tool_dia = params.get('tool_dia', 6)
    stepover = params.get('stepover', 40)
    feed = params.get('feed', 800)

    gcode_lines = []
    spiral_points = get_spiral_points(center_x, center_y, radius, tool_dia, stepover)

    if not spiral_points:
        return gcode_lines

    # Di chuyển đến điểm bắt đầu (tâm)
    start_point = spiral_points[0]
    gcode_lines.append(f"G0 X{start_point[0]:.3f} Y{start_point[1]:.3f}")
    # Đi xuống độ sâu Z
    gcode_lines.append(f"G1 Z{z_level:.3f} F{feed / 2}")
    
    # Chạy dao theo các điểm xoắn ốc
    for point in spiral_points[1:]:
        gcode_lines.append(f"G1 X{point[0]:.3f} Y{point[1]:.3f} F{feed}")

    # Cắt một vòng tròn hoàn chỉnh ở cuối để làm mịn biên
    # G2 là lệnh cắt cung tròn theo chiều kim đồng hồ
    gcode_lines.append(f"G2 X{start_point[0] + (radius - tool_dia / 2):.3f} Y{start_point[1]:.3f} I{radius - tool_dia / 2:.3f} J0")
    
    return gcode_lines