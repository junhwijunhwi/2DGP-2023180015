from pathlib import Path
from dataclasses import dataclass
from os import environ
from time import perf_counter, sleep


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SCALE = 5
GROUND_Y = CANVAS_HEIGHT / 2 - 84 * SCALE / 2
REPEAT_COUNT = 5
TRANSITION_PAUSE = 1.0


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int
    anchor_x: float
    anchor_y: float


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = 0.12


ANIMATIONS = (
    Animation('걷기', (
        Frame(10, 10, 62, 84, 31, 84),
        Frame(84, 10, 70, 84, 35, 84),
        Frame(166, 10, 72, 84, 36, 84),
        Frame(250, 10, 70, 84, 35, 84),
        Frame(332, 10, 62, 84, 31, 84),
        Frame(406, 10, 54, 84, 27, 84),
        Frame(472, 10, 52, 84, 26, 84),
        Frame(536, 10, 54, 84, 27, 84),
    )),
    Animation('달리기', (
        Frame(10, 116, 62, 84, 31, 84),
        Frame(84, 116, 78, 84, 39, 84),
        Frame(174, 116, 78, 84, 39, 84),
        Frame(264, 116, 62, 84, 31, 84),
        Frame(338, 116, 55, 84, 27.5, 84),
        Frame(405, 116, 55, 84, 27.5, 84),
    ), 0.08),
    Animation('점프', (
        Frame(10, 222, 62, 84, 31, 84),
        Frame(84, 222, 66, 80, 33, 84),
        Frame(162, 220, 70, 70, 35, 86),
        Frame(244, 220, 70, 62, 35, 86),
        Frame(326, 220, 66, 70, 33, 86),
        Frame(404, 222, 62, 80, 31, 84),
    )),
    Animation('공격', (
        Frame(10, 328, 67, 84, 31, 84),
        Frame(89, 328, 77, 84, 32, 84),
        Frame(178, 328, 92, 84, 31, 84),
        Frame(282, 328, 95, 84, 31, 84),
        Frame(387, 328, 86, 84, 32, 84),
        Frame(485, 328, 75, 84, 32, 84),
        Frame(572, 328, 68, 84, 31, 84),
    ), 0.10),
)


def draw_frame(character, frame):
    character.clip_draw(
        frame.left,
        character.h - frame.top - frame.height,
        frame.width,
        frame.height,
        CANVAS_WIDTH / 2 + (frame.width / 2 - frame.anchor_x) * SCALE,
        GROUND_Y + (frame.anchor_y - frame.height / 2) * SCALE,
        frame.width * SCALE,
        frame.height * SCALE,
    )


class AnimationPlayer:
    def __init__(self, animations=ANIMATIONS):
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_loops = 0
        self.waiting = False
        self.paused = False

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if self.paused:
            return
        self.elapsed += dt
        while True:
            duration = TRANSITION_PAUSE if self.waiting else self.animation.frame_seconds
            if self.elapsed + 1e-9 < duration:
                break
            self.elapsed = max(0.0, self.elapsed - duration)
            if self.waiting:
                self.animation_index = (self.animation_index + 1) % len(self.animations)
                self.frame_index = 0
                self.completed_loops = 0
                self.waiting = False
            elif self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.completed_loops += 1
                if self.completed_loops == REPEAT_COUNT:
                    self.waiting = True
                else:
                    self.frame_index = 0


    def select(self, index):
        self.animation_index = index % len(self.animations)
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_loops = 0
        self.waiting = False
        self.paused = False


def handle_events(p2d, player):
    for event in p2d.get_events():
        if event.type == p2d.SDL_QUIT:
            return False
        if event.type == p2d.SDL_KEYDOWN:
            if event.key == p2d.SDLK_ESCAPE:
                return False
            if event.key == p2d.SDLK_SPACE:
                player.paused = not player.paused
            elif event.key == p2d.SDLK_r:
                player.select(player.animation_index)
            elif event.key == p2d.SDLK_RIGHT:
                player.select(player.animation_index + 1)
            elif p2d.SDLK_1 <= event.key <= p2d.SDLK_4:
                player.select(event.key - p2d.SDLK_1)
    return True


def draw_status(font, player):
    animation = player.animation
    loop = min(player.completed_loops + 1, REPEAT_COUNT)
    if player.paused:
        state = '일시정지'
    elif player.waiting:
        state = f'1초 정지 · 다음 동작까지 {TRANSITION_PAUSE - player.elapsed:.1f}초'
    else:
        state = '재생 중'
    font.draw(28, 568, f'애니메이션 뷰어  |  {animation.name}', (30, 40, 55))
    font.draw(28, 538, f'반복 {loop} / {REPEAT_COUNT}   ·   프레임 {player.frame_index + 1} / {len(animation.frames)}   ·   {state}', (30, 40, 55))
    font.draw(28, 42, 'Space 일시정지 / 재개   ·   R 다시 재생   ·   → 다음 동작', (30, 40, 55))
    font.draw(28, 16, '1 걷기   2 달리기   3 점프   4 공격   ·   ESC 종료', (30, 40, 55))


def main():
    import pico2d as p2d

    p2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        character = p2d.load_image(str(Path(__file__).with_name('Robot_sprite_sheet.png')))
        font_path = Path(environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'malgun.ttf'
        font = p2d.load_font(str(font_path), 20)
        player = AnimationPlayer()
        previous_time = perf_counter()
        while handle_events(p2d, player):
            current_time = perf_counter()
            player.update(current_time - previous_time)
            previous_time = current_time
            p2d.clear_canvas()
            draw_frame(character, player.frame)
            draw_status(font, player)
            p2d.update_canvas()
            sleep(1 / 120)
    except KeyboardInterrupt:
        pass
    finally:
        p2d.close_canvas()


if __name__ == '__main__':
    main()
