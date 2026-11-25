from pico2d import load_image, load_font, get_canvas_width, get_canvas_height


class Blackboard:
    """좀비의 행동 노드가 공유하는 목적지와 화면 표시."""

    def __init__(self):
        self.target_location = (1000, 1000)
        self.image = load_image('blackboard.png')
        self.font = load_font('ENCR10B.TTF', 20)

    def update(self):
        pass

    def draw(self):
        left = get_canvas_width() - 380
        top = get_canvas_height() - 20
        self.image.draw(left + 180, top - 85, 360, 170)
        color = (255, 255, 255)
        tx, ty = self.target_location
        self.font.draw(left + 25, top - 40, 'BLACKBOARD', color)
        self.font.draw(left + 25, top - 85, f'Target X: {tx:.0f}', color)
        self.font.draw(left + 25, top - 120, f'Target Y: {ty:.0f}', color)
