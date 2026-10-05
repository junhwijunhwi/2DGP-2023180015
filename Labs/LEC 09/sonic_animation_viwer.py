"""소닉 스프라이트 시트의 동작을 순서대로 재생한다."""

from pathlib import Path
from dataclasses import dataclass
import pico2d
from time import perf_counter, sleep


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# 원본 시트의 위쪽부터 아래쪽까지, 소닉 그림이 있는 열 개의 동작 행.
# 제목(0~32행)과 크레딧 및 다른 캐릭터(472~524행)는 제외한다.
ACTION_LAYOUT = (
    ("걷기", 11),
    ("달리기", 12),
    ("점프", 6),
    ("공중 회전", 9),
    ("공 모양", 6),
    ("이동", 6),
    ("스핀", 6),
    ("피격", 8),
    ("방향 전환", 8),
    ("마무리", 4),
)


@dataclass(frozen=True)
class Frame:
    """시트의 왼쪽 위를 원점으로 측정한 자르기 영역."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        if min(self.x, self.y) < 0 or min(self.width, self.height) <= 0:
            raise ValueError("프레임 좌표와 크기가 올바르지 않습니다.")


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = 0.10

    def __post_init__(self):
        if not self.frames or self.frame_seconds <= 0:
            raise ValueError("동작에는 프레임과 양수 재생 간격이 필요합니다.")


ANIMATIONS: tuple[Animation, ...] = (
    Animation("걷기", (
        Frame(1, 39, 29, 39), Frame(31, 40, 26, 38),
        Frame(58, 39, 29, 39), Frame(87, 40, 29, 38),
        Frame(118, 40, 30, 38), Frame(150, 40, 30, 38),
        Frame(182, 40, 29, 38), Frame(211, 39, 30, 38),
        Frame(241, 39, 28, 38), Frame(270, 45, 24, 32),
        Frame(302, 51, 29, 26),
    ), 0.12),
    Animation("달리기", (
        Frame(8, 80, 26, 37), Frame(37, 80, 27, 37),
        Frame(65, 80, 31, 38), Frame(97, 80, 37, 37),
        Frame(135, 80, 32, 35), Frame(170, 79, 32, 38),
        Frame(206, 79, 26, 38), Frame(238, 80, 24, 37),
        Frame(263, 80, 30, 37), Frame(295, 80, 36, 37),
        Frame(334, 80, 32, 36), Frame(370, 79, 29, 38),
    ), 0.08),
    Animation("점프", (
        Frame(1, 124, 33, 40), Frame(39, 124, 35, 39),
        Frame(89, 125, 35, 38), Frame(130, 121, 34, 42),
        Frame(181, 122, 34, 41), Frame(228, 122, 33, 40),
    )),
    Animation("공중 회전", (
        Frame(1, 169, 29, 30), Frame(35, 167, 29, 31),
        Frame(67, 169, 30, 29), Frame(98, 169, 31, 29),
        Frame(131, 168, 29, 30), Frame(162, 168, 29, 31),
        Frame(193, 170, 30, 29), Frame(230, 170, 31, 29),
        Frame(268, 170, 30, 30),
    ), 0.08),
    Animation("공 모양", (
        Frame(1, 206, 30, 27), Frame(36, 206, 29, 27),
        Frame(70, 206, 29, 27), Frame(105, 206, 29, 27),
        Frame(139, 206, 29, 27), Frame(174, 206, 29, 27),
    ), 0.08),
    Animation("이동", (
        Frame(1, 239, 29, 35), Frame(36, 239, 30, 35),
        Frame(74, 239, 31, 35), Frame(111, 238, 31, 36),
        Frame(149, 239, 30, 35), Frame(186, 238, 31, 36),
    ), 0.10),
    Animation("스핀", (
        Frame(1, 283, 29, 35), Frame(36, 283, 30, 35),
        Frame(72, 286, 39, 31), Frame(123, 285, 39, 32),
        Frame(172, 286, 39, 31), Frame(218, 285, 38, 32),
    ), 0.08),
    Animation("피격", (
        Frame(1, 326, 24, 45), Frame(31, 327, 29, 44),
        Frame(65, 327, 20, 44), Frame(90, 327, 25, 43),
        Frame(119, 327, 25, 43), Frame(149, 327, 20, 44),
        Frame(184, 341, 40, 28), Frame(232, 341, 39, 27),
    ), 0.12),
    Animation("방향 전환", (
        Frame(1, 379, 27, 38), Frame(31, 379, 31, 36),
        Frame(64, 379, 31, 36), Frame(99, 377, 33, 38),
        Frame(136, 379, 32, 36), Frame(176, 379, 33, 36),
        Frame(217, 379, 33, 36), Frame(254, 378, 33, 36),
    ), 0.10),
    Animation("마무리", (
        Frame(6, 429, 34, 40), Frame(49, 426, 34, 43),
        Frame(96, 427, 23, 39), Frame(125, 427, 23, 39),
    ), 0.12),
)


class AnimationPlayer:
    """동작의 현재 프레임과 경과 시간을 관리한다."""

    def __init__(self, animations=ANIMATIONS):
        if not animations:
            raise ValueError("재생할 동작이 없습니다.")
        self.animations = tuple(animations)
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_loops = 0

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if dt < 0:
            raise ValueError("경과 시간은 음수가 될 수 없습니다.")
        self.elapsed += dt
        while self.elapsed >= self.animation.frame_seconds:
            self.elapsed -= self.animation.frame_seconds
            if self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.completed_loops += 1
                self.frame_index = 0


def validate_sheet(width, height):
    """정의한 모든 동작의 프레임이 이미지 안에 있는지 확인한다."""
    if len(ANIMATIONS) != len(ACTION_LAYOUT):
        raise ValueError("동작 목록의 개수가 시트 조사 결과와 다릅니다.")
    for animation, (name, expected_count) in zip(ANIMATIONS, ACTION_LAYOUT):
        if animation.name != name or len(animation.frames) != expected_count:
            raise ValueError(f"{name}: 이름 또는 프레임 수가 맞지 않습니다.")
        for frame in animation.frames:
            if frame.x + frame.width > width or frame.y + frame.height > height:
                raise ValueError(f"{name}: 이미지 경계를 벗어난 프레임이 있습니다.")


def draw_frame(sprite, frame):
    """시트의 위쪽 기준 좌표를 Pico2D의 아래쪽 기준 좌표로 바꿔 그린다."""
    sprite.clip_draw(
        frame.x, sprite.h - frame.y - frame.height,
        frame.width, frame.height,
        CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2,
    )


def sprite_path():
    """실행 위치와 관계없이 원본 스프라이트를 찾는다."""
    return Path(__file__).resolve().parents[1] / "LEC08_Animation" / "sonic-sprite.png"


def handle_events():
    """창 닫기와 Esc 키를 처리한다."""
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            return False
        if event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE:
            return False
    return True


def main():
    """애니메이션 뷰어의 실행 진입점."""
    image_path = sprite_path()
    if not image_path.is_file():
        raise SystemExit(f"스프라이트 이미지를 찾을 수 없습니다: {image_path}")

    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        try:
            sprite = pico2d.load_image(str(image_path))
        except Exception as error:
            raise SystemExit(f"스프라이트 이미지를 불러오지 못했습니다: {image_path}") from error
        validate_sheet(sprite.w, sprite.h)
        player = AnimationPlayer()
        running = True
        previous_time = perf_counter()
        while running:
            now = perf_counter()
            dt = now - previous_time
            previous_time = now
            running = handle_events()
            player.update(dt)
            pico2d.clear_canvas()
            draw_frame(sprite, player.frame)
            pico2d.update_canvas()
            sleep(1 / 120)
    finally:
        if "sprite" in locals():
            del sprite
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
