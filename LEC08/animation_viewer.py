"""Drill #8: 서로 다른 크기의 로봇 프레임을 중앙에서 순환 재생합니다."""
from pathlib import Path
from dataclasses import dataclass
from os import environ
from math import isfinite
from time import perf_counter, sleep


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SCALE = 5
GROUND_Y = CANVAS_HEIGHT / 2 - 84 * SCALE / 2
REPEAT_COUNT = 5
TRANSITION_PAUSE = 1.0


@dataclass(frozen=True)
class Frame:
    """좌상단 기준 자르기 영역과 몸통/발 위치를 맞추는 기준점입니다."""
    left: int
    top: int
    width: int
    height: int
    anchor_x: float
    anchor_y: float

    def __post_init__(self):
        if min(self.left, self.top) < 0 or min(self.width, self.height) <= 0:
            raise ValueError('프레임 좌표는 음수가 아니고 크기는 양수여야 합니다.')
        if not 0 <= self.anchor_x <= self.width or self.anchor_y < 0:
            raise ValueError('프레임 기준점이 올바르지 않습니다.')


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = 0.12

    def __post_init__(self):
        if not self.frames or not isfinite(self.frame_seconds) or self.frame_seconds <= 0:
            raise ValueError('애니메이션에는 프레임과 양수인 재생 간격이 필요합니다.')


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


def validate_sheet(width, height, animations=ANIMATIONS):
    for animation in animations:
        for frame in animation.frames:
            if frame.left + frame.width > width or frame.top + frame.height > height:
                raise ValueError(f'{animation.name}: 프레임이 이미지 경계를 벗어납니다.')


def draw_frame(character, frame):
    # 시트의 위쪽 기준 top을 Pico2D의 아래쪽 기준 bottom으로 변환합니다.
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
    """5회 재생 → 마지막 프레임에서 1초 정지 → 다음 동작을 반복합니다."""
    def __init__(self, animations=ANIMATIONS):
        self.animations = tuple(animations)
        if not self.animations:
            raise ValueError('재생할 애니메이션이 없습니다.')
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
        if not isfinite(dt) or dt < 0:
            raise ValueError('경과 시간은 유한한 0 이상의 값이어야 합니다.')
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


def load_status_font(p2d):
    windows_fonts = Path(environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    candidates = (
        (windows_fonts / 'malgun.ttf', True),
        (Path('/System/Library/Fonts/AppleSDGothicNeo.ttc'), True),
        (Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'), True),
        (windows_fonts / 'arial.ttf', False),
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), False),
    )
    for path, korean in candidates:
        if path.is_file():
            try:
                return p2d.load_font(str(path), 20), korean
            except OSError:
                continue
    return None, False


def status_lines(player, korean=True):
    animation = player.animation
    loop = min(player.completed_loops + 1, REPEAT_COUNT)
    if player.paused:
        state = '일시정지'
    elif player.waiting:
        state = f'1초 정지 · 다음 동작까지 {TRANSITION_PAUSE - player.elapsed:.1f}초'
    else:
        state = '재생 중'
    if korean:
        return (
            f'애니메이션 뷰어  |  {animation.name}',
            f'반복 {loop} / {REPEAT_COUNT}   ·   프레임 {player.frame_index + 1} / {len(animation.frames)}   ·   {state}',
            'Space 일시정지 / 재개   ·   R 다시 재생   ·   → 다음 동작',
            '1 걷기   2 달리기   3 점프   4 공격   ·   ESC 종료',
        )
    names = ('Walk', 'Run', 'Jump', 'Attack')
    state = ('Paused' if player.paused else
             f'Wait {TRANSITION_PAUSE - player.elapsed:.1f}s' if player.waiting else 'Playing')
    return (
        f'Animation Viewer  |  {names[player.animation_index]}',
        f'Loop {loop}/{REPEAT_COUNT}  |  Frame {player.frame_index + 1}/{len(animation.frames)}  |  {state}',
        'Space: pause/resume   R: restart   Right: next',
        '1: Walk   2: Run   3: Jump   4: Attack   ESC: quit',
    )


def draw_background(p2d, player):
    p2d.clear_canvas()
    p2d.draw_rectangle(0, 0, 799, 599, 238, 243, 249, filled=True)
    p2d.draw_rectangle(0, 524, 799, 599, 255, 255, 255, filled=True)
    p2d.draw_rectangle(0, 0, 799, 64, 255, 255, 255, filled=True)
    p2d.draw_rectangle(0, 524, 5, 599, 24, 146, 173, filled=True)
    p2d.draw_rectangle(80, GROUND_Y - 3, 720, GROUND_Y - 2, 197, 209, 223, filled=True)
    for i in range(REPEAT_COUNT):
        color = (24, 146, 173) if i < player.completed_loops else (220, 229, 238)
        p2d.draw_rectangle(634 + i * 29, 564, 656 + i * 29, 573, *color, filled=True)


def draw_status(p2d, font, player, korean=True):
    lines = status_lines(player, korean)
    p2d.SDL_SetWindowTitle(p2d.pico2d.window, f'{lines[0]} | {lines[1]}'.encode('utf-8'))
    if font is not None:
        for y, line in zip((568, 538, 42, 16), lines):
            font.draw(28, y, line, (30, 40, 55))


def main():
    try:
        import pico2d as p2d
    except ModuleNotFoundError as error:
        if error.name != 'pico2d':
            raise
        raise SystemExit('Pico2D가 필요합니다. python -m pip install -r LEC08/requirements.txt') from error

    image_path = Path(__file__).resolve().with_name('Robot_sprite_sheet.png')
    if not image_path.is_file():
        raise SystemExit(f'스프라이트 이미지를 찾을 수 없습니다: {image_path}')

    p2d.SDL_SetHint(p2d.SDL_HINT_RENDER_SCALE_QUALITY, b'0')
    p2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    character = None
    font = None
    try:
        character = p2d.load_image(str(image_path))
        validate_sheet(character.w, character.h)
        font, korean = load_status_font(p2d)
        player = AnimationPlayer()
        previous_time = perf_counter()
        while handle_events(p2d, player):
            current_time = perf_counter()
            player.update(current_time - previous_time)
            previous_time = current_time
            draw_background(p2d, player)
            draw_frame(character, player.frame)
            draw_status(p2d, font, player, korean)
            p2d.update_canvas()
            sleep(1 / 120)
    except KeyboardInterrupt:
        pass
    finally:
        if font is not None:
            p2d.TTF_CloseFont(font.font)
        if character is not None:
            del character
        p2d.close_canvas()


if __name__ == '__main__':
    main()
