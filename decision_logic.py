from Model2 import Data
from direction import Direction

class DecisionLogic(object):

    ROUND_LIMIT = 2

    def __init__(self):
        self.data = Data()
        self.is_game_over = False
        self.round_count = 0

    def get_robot_direction(self):
        return self.data.getRobotAction()

    def human_agreed(self, robot_direction):
        self.data.receiveHumanRobotAction(robot_direction, robot_direction)

    def human_disagreed(self, robot_direction):
        human_direction = self.get_reverse_direction(robot_direction)
        self.data.receiveHumanRobotAction(human_direction, robot_direction)

    def get_reverse_direction(self, direction):
        if direction == Direction.NEGATIVE:
            return Direction.POSITIVE
        else:
            return Direction.NEGATIVE

    def update_is_game_over(self):
        theta = self.data.getCurrentTableTheta()
        if theta == self.data.goal1StateTheta:
            self.data.currState = self.data.goal1RestartStateIndx
        elif theta == self.data.goal2StateTheta:
            self.data.currState = self.data.goal2RestartStateIndx
        else:
            self.is_game_over = False
            return
        self.is_game_over = True
        self.round_count += 1
