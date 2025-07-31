import math

def get_rounded_rect_points(x0, y0, w, h, r):
    """Tính toán các điểm để vẽ một hình chữ nhật bo góc."""
    points = []
    # Các cạnh thẳng
    points.append(([x0 + r, x0 + w - r], [y0, y0]))
    points.append(([x0 + r, x0 + w - r], [y0 + h, y0 + h]))
    points.append(([x0, x0], [y0 + r, y0 + h - r]))
    points.append(([x0 + w, x0 + w], [y0 + r, y0 + h - r]))

    # Các góc bo
    theta = list(range(0, 91, 5))
    corner_centers = [
        (x0 + w - r, y0 + h - r, 0),    # Top-right
        (x0 + r,     y0 + h - r, 90),   # Top-left
        (x0 + r,     y0 + r,     180),  # Bottom-left
        (x0 + w - r, y0 + r,     270)   # Bottom-right
    ]

    for cx, cy, start_angle in corner_centers:
        arc_xs = [cx + r * math.cos(math.radians(start_angle + a)) for a in theta]
        arc_ys = [cy + r * math.sin(math.radians(start_angle + a)) for a in theta]
        points.append((arc_xs, arc_ys))
        
    return points