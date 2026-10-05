"""소닉 스프라이트 시트의 동작을 순서대로 재생한다."""

from pathlib import Path
import pico2d
from time import sleep


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


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
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        running = True
        while running:
            running = handle_events()
            pico2d.clear_canvas()
            pico2d.update_canvas()
            sleep(1 / 120)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
