"""PNG의 실제 불투명 픽셀과 렌더링 좌표를 대조합니다."""
from pathlib import Path
import struct
import unittest
import zlib

from animation_viewer import (
    ANIMATIONS, CANVAS_HEIGHT, CANVAS_WIDTH, SCALE,
    Animation, Frame, draw_frame, validate_sheet,
)


def read_opaque_pixels(path):
    """제공된 8비트 RGBA PNG를 표준 라이브러리로 읽습니다."""
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    chunks, offset = [], 8
    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        chunks.append((data[offset + 4:offset + 8], data[offset + 8:offset + 8 + length]))
        offset += length + 12
    header = next(value for name, value in chunks if name == b'IHDR')
    width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', header)
    assert (depth, color, compression, filtering, interlace) == (8, 6, 0, 0, 0)
    raw = zlib.decompress(b''.join(value for name, value in chunks if name == b'IDAT'))
    stride, offset = width * 4, 0
    previous, opaque = bytearray(stride), set()
    for y in range(height):
        kind = raw[offset]
        row = bytearray(raw[offset + 1:offset + 1 + stride])
        offset += stride + 1
        for i in range(stride):
            left = row[i - 4] if i >= 4 else 0
            above = previous[i]
            diagonal = previous[i - 4] if i >= 4 else 0
            if kind == 0:
                predictor = 0
            elif kind == 1:
                predictor = left
            elif kind == 2:
                predictor = above
            elif kind == 3:
                predictor = (left + above) // 2
            elif kind == 4:
                estimate = left + above - diagonal
                predictor = min((left, above, diagonal), key=lambda value: abs(estimate - value))
            else:
                raise ValueError(f'알 수 없는 PNG 필터: {kind}')
            row[i] = (row[i] + predictor) & 255
        opaque.update((x, y) for x in range(width) if row[x * 4 + 3])
        previous = row
    return width, height, opaque


class SpriteFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.width, cls.height, cls.opaque = read_opaque_pixels(
            Path(__file__).with_name('Robot_sprite_sheet.png'))

    def test_animation_lengths_and_varying_frame_sizes(self):
        self.assertEqual([len(animation.frames) for animation in ANIMATIONS], [8, 6, 6, 7])
        sizes = {(frame.width, frame.height) for animation in ANIMATIONS for frame in animation.frames}
        self.assertGreater(len(sizes), 4)

    def test_every_visible_pixel_is_in_exactly_one_tight_frame(self):
        covered = set()
        for animation in ANIMATIONS:
            for index, frame in enumerate(animation.frames):
                with self.subTest(animation=animation.name, frame=index):
                    pixels = {(x, y) for x, y in self.opaque
                              if frame.left <= x < frame.left + frame.width
                              and frame.top <= y < frame.top + frame.height}
                    self.assertTrue(pixels)
                    self.assertFalse(covered.intersection(pixels))
                    self.assertEqual(min(x for x, _ in pixels), frame.left)
                    self.assertEqual(max(x for x, _ in pixels), frame.left + frame.width - 1)
                    self.assertEqual(min(y for _, y in pixels), frame.top)
                    self.assertEqual(max(y for _, y in pixels), frame.top + frame.height - 1)
                    # 둘 이상의 캐릭터가 한 프레임에 들어가면 사이의 빈 열이 검출됩니다.
                    self.assertEqual({x for x, _ in pixels}, set(range(frame.left, frame.left + frame.width)))
                    covered.update(pixels)
        self.assertEqual(covered, self.opaque)

    def test_drawn_frames_fit_on_screen_and_fill_half_its_height(self):
        class ImageProbe:
            def clip_draw(self, *args):
                self.arguments = args

        image = ImageProbe()
        image.h = self.height
        for animation in ANIMATIONS:
            for frame in animation.frames:
                with self.subTest(animation=animation.name, frame=frame):
                    draw_frame(image, frame)
                    left, bottom, width, height, x, y, drawn_width, drawn_height = image.arguments
                    self.assertEqual((left, self.height - bottom - height), (frame.left, frame.top))
                    self.assertGreaterEqual(bottom, 0)
                    self.assertLessEqual(left + width, self.width)
                    self.assertEqual(drawn_width / width, SCALE)
                    self.assertEqual(drawn_height / height, SCALE)
                    self.assertGreaterEqual(drawn_height, CANVAS_HEIGHT / 2)
                    self.assertGreaterEqual(x - drawn_width / 2, 0)
                    self.assertLessEqual(x + drawn_width / 2, CANVAS_WIDTH)
                    self.assertGreaterEqual(y - drawn_height / 2, 64)
                    self.assertLessEqual(y + drawn_height / 2, 524)

    def test_sheet_size_is_checked_before_drawing(self):
        validate_sheet(self.width, self.height)
        with self.assertRaises(ValueError):
            validate_sheet(100, 100)

    def test_empty_frames_and_invalid_durations_are_rejected(self):
        with self.assertRaises(ValueError):
            Frame(0, 0, 0, 84, 0, 84)
        with self.assertRaises(ValueError):
            Animation('빈 동작', ())
        for duration in (0, -1, float('inf'), float('nan')):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                Animation('잘못된 간격', ANIMATIONS[0].frames, duration)


if __name__ == '__main__':
    unittest.main()
