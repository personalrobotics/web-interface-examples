import time as pythontime
import numpy
import herbpy
from decision_logic import DecisionLogic
from direction import Direction

DECISION_TIME = 3
BASE_TURN_ANGLE = numpy.pi / 9
SAMPLING_PERIOD = 0.2
DISTANCE = 0.1
FORCE_DIFFERENCE = 0
RIGHT_DOFS = [5.58752674, -0.81569425, -0.25011433, 2.25228782,
              -3.34832888, 1.46559139, 0.84342324]
LEFT_DOFS = [0.6373099, -0.79577868, 0.3423032, 2.31692865, 0.28152565,
             -1.53230128, 2.19221046]


class TableTurn(object):

    def __init__(self, env, robot):
        self.env = env
        self.robot = robot
        self.right_arm = self.robot.right_arm
        self.left_arm = self.robot.left_arm
        self.right_hand = self.robot.right_hand
        self.left_hand = self.robot.left_hand
        self.base = self.robot.base
        self.logic = DecisionLogic()

    def start(self):
        raw_input('press enter to start the game!')
        while not self.logic.is_game_over:
            timer_start_time = pythontime.time()
            current_time = timer_start_time
            human_moved_before_times_up = False
            while current_time - timer_start_time < DECISION_TIME:
                human_direction = self.get_human_direction()
                if human_direction != Direction.STAY:
                    human_moved_before_times_up = True
                    break
                pythontime.sleep(SAMPLING_PERIOD)
                current_time = pythontime.time()

            robot_direction = self.logic.get_robot_direction()
            if human_moved_before_times_up:
                if human_direction == robot_direction:
                    self.logic.human_agreed(robot_direction)
                    self.rotate(robot_direction)
                else:
                    self.logic.human_disagreed(robot_direction)
                    self.push_arm(robot_direction)
                    self.return_arm(robot_direction)
            else:
                human_agreed = self.push_arm(robot_direction)
                if human_agreed:
                    self.logic.human_agreed(robot_direction)
                    self.rotate(robot_direction)
                else:
                    self.logic.human_disagreed(robot_direction)
                self.return_arm(robot_direction)
            self.logic.update_is_game_over()
        self.round_ended()

    def round_ended(self):
        self.setup()
        if self.logic.round_count < self.logic.ROUND_LIMIT:
            self.logic.is_game_over = False
            print 'round 2!'
            self.start()
        else:
            print 'the game is over'

    def setup(self):
        while True:
            inp = raw_input(
                "Options: default_right, default_left, open_right, open_left,",
                "unstiff_right, unstiff_left, stiff_right, stiff_left,",
                "rotate_positive, rotate_negative, tare_sensors, done")
            if inp == "default_right":
                self.right_arm.PlanToConfiguration(RIGHT_DOFS, execute=True)
            elif inp == "default_left":
                self.left_arm.PlanToConfiguration(LEFT_DOFS, execute=True)
            elif inp == "open_right":
                self.right_hand.OpenHand()
            elif inp == "open_left":
                self.left_hand.OpenHand()
            elif inp == "unstiff_right":
                self.right_arm.SetStiffness(0)
            elif inp == "unstiff_left":
                self.left_arm.SetStiffness(0)
            elif inp == "stiff_right":
                self.right_arm.SetStiffness(1)
            elif inp == "stiff_left":
                self.left_arm.SetStiffness(1)
            elif inp == "rotate_positive":
                self.base.Rotate(BASE_TURN_ANGLE)
            elif inp == "rotate_negative":
                self.base.Rotate(-BASE_TURN_ANGLE)
            elif inp == "tare_sensors":
                while True:
                    inp = raw_input('press enter to tare sensors. q if done')
                    if inp == 'q':
                        break
                    self.left_hand.TareForceTorqueSensor()
                    print "left tare returned"
                    self.right_hand.TareForceTorqueSensor()
                    print "right tare returned"
            elif inp == 'done':
                break

    def get_human_direction(self):
        left_vector = self.left_hand.getForceTorque()[0]
        left_force = numpy.linalg.norm(left_vector)
        right_vector = self.right_hand.getForceTorque()
        right_force = numpy.linalg.norm(right_vector)
        print "left: ", left_force
        print "right: ", right_force
        if abs(left_force - right_force) > FORCE_DIFFERENCE:
            if left_force > right_force:
                return Direction.NEGATIVE
            else:
                return Direction.POSITIVE

    def rotate(self, direction):
        if direction == Direction.POSITIVE:
            self.base.Rotate(BASE_TURN_ANGLE)
        else:
            self.base.Rotate(-BASE_TURN_ANGLE)

    def push_arm(self, direction):
        transform = self.robot.GetTransform()
        self.move_direction = transform[0:3, 0]
        arm = self.direction_to_arm(direction)
        self.start_pose = arm.GetEndEffectorTransform()
        felt_force = arm.MoveUntilTouch(
            direction=self.move_direction, distance=DISTANCE, max_distance=DISTANCE)
        return not felt_force  # human_agreed is true if it didnt feel force

    def return_arm(self, direction):
        arm = self.direction_to_arm(direction)
        end_pose = arm.GetEndEffectorTransform()
        start_end_delta = numpy.linalg.norm(
            end_pose[:3, 3] - self.start_pose[:3, 3])
        robot.right_arm.PlanToEndEffectorOffset(
            direction=-self.move_direction, distance=start_end_delta)

    def direction_to_arm(self, direction):
        if direction == Direction.POSITIVE:
            return self.left_arm
        else:
            return self.right_arm

if __name__ == "__main__":
    env, robot = herbpy.initialize(sim=False)
    game = TableTurn(env, robot)
    game.setup()
    game.start()
