"""소닉 스프라이트 시트의 동작을 순서대로 재생한다."""

import pico2d


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


def main():
    """애니메이션 뷰어의 실행 진입점."""
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pico2d.clear_canvas()
        pico2d.update_canvas()
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
