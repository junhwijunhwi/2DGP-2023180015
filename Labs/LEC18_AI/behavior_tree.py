class BehaviorTree:
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    RUNNING = 'RUNNING'

    def __init__(self, root):
        self.root = root

    def run(self):
        return self.root.run()


class Action:
    def __init__(self, name, function):
        self.name = name
        self.function = function

    def run(self):
        return self.function()

    def reset(self):
        pass


class Condition:
    def __init__(self, name, predicate):
        self.name = name
        self.predicate = predicate

    def run(self):
        return BehaviorTree.SUCCESS if self.predicate() else BehaviorTree.FAIL

    def reset(self):
        pass


class Sequence:
    """memory=False이면 매 프레임 첫 자식의 조건부터 다시 검사한다."""

    def __init__(self, name, *children, memory=True):
        self.name = name
        self.children = list(children)
        self.current_child = 0
        self.memory = memory

    def reset(self):
        self.current_child = 0
        for child in self.children:
            child.reset()

    def run(self):
        if not self.memory:
            self.current_child = 0
        while self.current_child < len(self.children):
            result = self.children[self.current_child].run()
            if result == BehaviorTree.RUNNING:
                return result
            if result == BehaviorTree.FAIL:
                self.current_child = 0
                return result
            self.current_child += 1

        self.current_child = 0
        return BehaviorTree.SUCCESS


class Selector:
    """매 프레임 왼쪽부터 검사하여 우선순위가 높은 행동을 실행한다."""

    def __init__(self, name, *children):
        self.name = name
        self.children = list(children)
        self.active_child = None

    def reset(self):
        self.active_child = None
        for child in self.children:
            child.reset()

    def run(self):
        for child in self.children:
            result = child.run()
            if result == BehaviorTree.FAIL:
                child.reset()
                continue

            if self.active_child is not None and self.active_child is not child:
                # 중단된 행동은 재개할 때 첫 노드부터 실행한다.
                self.active_child.reset()
            self.active_child = child if result == BehaviorTree.RUNNING else None
            if result == BehaviorTree.SUCCESS:
                child.reset()
            return result

        self.reset()
        return BehaviorTree.FAIL
