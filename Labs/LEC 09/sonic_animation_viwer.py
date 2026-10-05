"""소닉 스프라이트 시트의 동작을 순서대로 재생한다."""

from pathlib import Path
from dataclasses import dataclass
import pico2d
from time import sleep


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
        running = True
        while running:
            running = handle_events()
            pico2d.clear_canvas()
            pico2d.update_canvas()
            sleep(1 / 120)
    finally:
        if "sprite" in locals():
            del sprite
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
