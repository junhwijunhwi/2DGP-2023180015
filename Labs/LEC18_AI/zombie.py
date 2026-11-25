import random
import math

from pico2d import load_image, load_font, draw_rectangle, get_canvas_width, get_canvas_height

import game_framework
import game_world
import common
from behavior_tree import BehaviorTree, Action, Condition, Sequence, Selector

# 좀비 달리기 속력: km/h -> 픽셀/초
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)
CHASE_RADIUS = common.INTERACTION_RADIUS  # 소년을 발견하는 거리 (픽셀)

# 좀비 애니메이션 속도: 0.5초에 10프레임
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10

ANIMATION_NAMES = ['Walk', 'Idle']


class Zombie:
    images = None
    font = None
    marker_image = None

    def load_images(self):
        if Zombie.images is None:
            Zombie.images = {
                name: [load_image(f'./zombie/{name} ({i}).png') for i in range(1, 11)]
                for name in ANIMATION_NAMES
            }
            Zombie.font = load_font('ENCR10B.TTF', 40)
            Zombie.marker_image = load_image('hand_arrow.png')

    def __init__(self, blackboard, x=None, y=None):
        self.load_images()
        self.x = x if x is not None else random.randint(100, get_canvas_width() - 100)
        self.y = y if y is not None else random.randint(100, get_canvas_height() - 100)
        self.dir = 0.0  # 이동 방향 (라디안)
        self.speed = 0.0
        self.frame = random.randint(0, 9)
        self.state = 'Idle'
        self.ball_count = 0  # 주운 공의 개수

        self.blackboard = blackboard
        self.patrol_locations = [
            (43, 274), (1118, 274), (1050, 494), (575, 804),
            (235, 991), (575, 804), (1050, 494), (1118, 274),
        ]
        self.patrol_index = 0
        self.build_behavior_tree()

    def build_behavior_tree(self):
        flee = Sequence(
            '소년에게서 도망',
            Condition('소년이 근처에 있는가?', self.is_boy_nearby),
            Condition('좀비의 공이 더 적은가?', self.has_fewer_balls),
            Action('소년 반대 방향으로 이동', self.flee_from_boy),
            memory=False,
        )
        boy_nearby = Condition('소년이 근처에 있는가?', self.is_boy_nearby)
        move_to_boy = Action('소년한테가기', self.move_to_boy)
        chase = Sequence('소년추적', boy_nearby, move_to_boy, memory=False)

        set_target = Action('순찰 목적지 설정', self.set_patrol_target)
        move_to = Action('move to', self.move_to)
        next_target = Action('다음 순찰 지점', self.advance_patrol_target)
        patrol = Sequence('순찰', set_target, move_to, next_target)

        # 추적/도망 중에도 순찰 번호를 유지해 같은 지점부터 재개한다.
        root = Selector('도망 또는 추적 또는 순찰', flee, chase, patrol)
        self.bt = BehaviorTree(root)

    def has_fewer_balls(self):
        return common.boy is not None and self.ball_count < common.boy.ball_count

    def flee_from_boy(self):
        dx, dy = self.x - common.boy.x, self.y - common.boy.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            dx, dy, distance = 1.0, 0.0, 1.0
        # 목적지를 블랙보드에 기록하여 도망 중에도 화살표와 좌표를 표시한다.
        self.blackboard.target_location = (
            max(50, min(get_canvas_width() - 50, self.x + dx / distance * CHASE_RADIUS)),
            max(50, min(get_canvas_height() - 50, self.y + dy / distance * CHASE_RADIUS)),
        )
        self.move_to()
        return BehaviorTree.RUNNING

    def set_patrol_target(self):
        self.blackboard.target_location = self.patrol_locations[self.patrol_index]
        return BehaviorTree.SUCCESS

    def advance_patrol_target(self):
        # 목적지에 도착한 뒤에만 다음 지점으로 넘어간다.
        self.patrol_index = (self.patrol_index + 1) % len(self.patrol_locations)
        return BehaviorTree.SUCCESS

    def is_boy_nearby(self):
        boy = common.boy
        return boy is not None and math.hypot(boy.x - self.x, boy.y - self.y) <= CHASE_RADIUS

    def move_to_boy(self):
        # 움직이는 소년을 따라가도록 목적지를 매 프레임 갱신한다.
        self.blackboard.target_location = (common.boy.x, common.boy.y)
        return self.move_to()

    def set_target_location(self):
        self.blackboard.target_location = (
            random.randint(100, get_canvas_width() - 100),
            random.randint(100, get_canvas_height() - 100),
        )
        return BehaviorTree.SUCCESS

    def move_to(self):
        tx, ty = self.blackboard.target_location
        dx, dy = tx - self.x, ty - self.y
        distance = math.hypot(dx, dy)
        self.speed = RUN_SPEED_PPS
        step = self.speed * game_framework.frame_time

        if distance <= step:
            self.x, self.y = tx, ty
            self.speed = 0.0
            self.state = 'Idle'
            return BehaviorTree.SUCCESS

        self.dir = math.atan2(dy, dx)
        self.state = 'Walk'
        self.x += math.cos(self.dir) * step
        self.y += math.sin(self.dir) * step
        return BehaviorTree.RUNNING

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * dt) % FRAMES_PER_ACTION
        if self.bt.run() == BehaviorTree.FAIL:
            self.speed = 0.0
            self.state = 'Idle'

    def draw(self):
        image = Zombie.images[self.state][int(self.frame)]
        if math.cos(self.dir) < 0:  # 왼쪽을 향하고 있으면 좌우 반전
            image.composite_draw(0, 'h', self.x, self.y, 100, 100)
        else:
            image.draw(self.x, self.y, 100, 100)
        Zombie.font.draw(self.x - 10, self.y + 60, f'{self.ball_count}', (0, 0, 255))
        tx, ty = self.blackboard.target_location
        Zombie.marker_image.draw(tx + 25, ty - 25)  # 블랙보드의 목표 위치 표시
        draw_rectangle(*self.get_bb())

    # 바운딩 박스: (left, bottom, right, top)
    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1
