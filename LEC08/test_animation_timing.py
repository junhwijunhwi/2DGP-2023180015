"""GUI 없이 과제의 반복 횟수와 시간 조건을 검사합니다."""
import unittest

from animation_viewer import ANIMATIONS, AnimationPlayer


class AnimationTimingTests(unittest.TestCase):
    def test_frame_changes_only_after_its_duration(self):
        player = AnimationPlayer()
        player.update(0.119)
        self.assertEqual(player.frame_index, 0)
        player.update(0.001)
        self.assertEqual(player.frame_index, 1)

    def test_each_animation_displays_five_complete_loops(self):
        for index, animation in enumerate(ANIMATIONS):
            with self.subTest(animation=animation.name):
                player = AnimationPlayer()
                player.select(index)
                for loop in range(5):
                    for frame in range(len(animation.frames)):
                        self.assertFalse(player.waiting)
                        self.assertEqual(player.completed_loops, loop)
                        self.assertEqual(player.frame_index, frame)
                        player.update(animation.frame_seconds)
                self.assertTrue(player.waiting)
                self.assertEqual(player.completed_loops, 5)
                self.assertEqual(player.frame_index, len(animation.frames) - 1)

    def test_last_frame_stays_for_one_second(self):
        player = AnimationPlayer()
        player.update(4.8)
        self.assertTrue(player.waiting)
        self.assertEqual(player.frame_index, 7)
        player.update(0.999)
        self.assertEqual(player.animation_index, 0)
        self.assertEqual(player.frame_index, 7)
        player.update(0.001)
        self.assertEqual(player.animation_index, 1)
        self.assertEqual(player.frame_index, 0)
        self.assertEqual(player.completed_loops, 0)

    def test_all_four_animations_repeat_after_18_point_3_seconds(self):
        player = AnimationPlayer()
        # 걷기 4.8 + 달리기 2.4 + 점프 3.6 + 공격 3.5 + 정지 4초
        player.update(18.3)
        self.assertEqual(player.animation_index, 0)
        self.assertEqual(player.frame_index, 0)
        self.assertEqual(player.completed_loops, 0)
        self.assertFalse(player.waiting)
        self.assertAlmostEqual(player.elapsed, 0)
        player.update(18.3 + 0.24)
        self.assertEqual(player.animation_index, 0)
        self.assertEqual(player.frame_index, 2)

    def test_delayed_updates_preserve_the_same_playback_position(self):
        once, split = AnimationPlayer(), AnimationPlayer()
        once.update(39.257)
        for _ in range(39257):
            split.update(0.001)
        for attribute in ('animation_index', 'frame_index', 'completed_loops', 'waiting'):
            self.assertEqual(getattr(once, attribute), getattr(split, attribute))
        self.assertAlmostEqual(once.elapsed, split.elapsed, places=7)

    def test_manual_pause_freezes_frame_time(self):
        player = AnimationPlayer()
        player.update(0.05)
        player.paused = True
        player.update(100)
        self.assertEqual(player.frame_index, 0)
        self.assertAlmostEqual(player.elapsed, 0.05)
        player.paused = False
        player.update(0.07)
        self.assertEqual(player.frame_index, 1)

    def test_manual_pause_freezes_transition_wait(self):
        player = AnimationPlayer()
        player.update(5.05)
        self.assertTrue(player.waiting)
        player.paused = True
        player.update(100)
        self.assertAlmostEqual(player.elapsed, 0.25)
        player.paused = False
        player.update(0.75)
        self.assertEqual(player.animation_index, 1)

    def test_selecting_an_animation_restarts_its_five_loops(self):
        player = AnimationPlayer()
        player.update(5.0)
        player.paused = True
        player.select(3)
        self.assertEqual(player.animation_index, 3)
        self.assertEqual(player.frame_index, 0)
        self.assertEqual(player.completed_loops, 0)
        self.assertEqual(player.elapsed, 0)
        self.assertFalse(player.waiting)
        self.assertFalse(player.paused)
        player.select(4)
        self.assertEqual(player.animation_index, 0)

    def test_invalid_elapsed_time_is_rejected(self):
        for value in (-1, float('inf'), float('nan')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                AnimationPlayer().update(value)


if __name__ == '__main__':
    unittest.main()
