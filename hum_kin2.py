PACKAGE = 'humanpy'
import re
import time as pythontime
import random
import numpy
from DecisionLogic import DecisionLogic
KIN_FRAME = '/head/skel_depth_frame'
SAMPLING_PERIOD = 0.8
STEPSIZE_THRESHOLD = 0.4
Z_DISTANCE = 2.5
Z_DISTANCE_DELTA = 0.3
BASE_TURN_ANGLE = numpy.pi / 9
DECISION_TIME = 3
# DOES_AGREE_SEQUENCE = [False, False]

def enum(**enums):
    return type('Enum', (), enums)
Direction = enum(POSITIVE=1, NEGATIVE=0, STAY=2)


class Orhuman(object):

    def __init__(self, user_id, env):
        self.id = user_id
        self.enabled = True
        self.env = env
        self.robot = env.GetRobot('herb')
        self.frame_name = "/skel/" + self.id + "/SpineMid"
        self.world_name = KIN_FRAME
        self.last_update_time = pythontime.time()
        #self.does_agree_sequence_index = 0

    def update(self, tf, logic):
        if not logic.is_game_over:
            time_since_last_update = pythontime.time() - self.last_update_time
            if time_since_last_update > SAMPLING_PERIOD:
                self.last_update_time = pythontime.time()
                if tf.frameExists(self.frame_name) and tf.frameExists(self.world_name):
                    print "id = %s, z = %.2f" % (self.id, self.get_z_distance(tf))
                    direction = self.get_human_direction(tf)
                    if direction == Direction.STAY:
                        return True

                    does_agree = logic.does_agree_to_move(direction)
                    if not does_agree:
                        direction = self.resolve_disagreement(tf, logic)
                    if direction == Direction.POSITIVE:
                        self.robot.base.Rotate(BASE_TURN_ANGLE)
                        #print "ROTATE RIGHT!"
                    elif direction == Direction.NEGATIVE:
                        self.robot.base.Rotate(-BASE_TURN_ANGLE)
                        #print "ROTATE LEFT!"

                    logic.update_is_game_over()
        else:
            self.robot.Say("We did it")
            if logic.round_count < DecisionLogic.ROUND_LIMIT:
                raw_input("Press to start the second round")
                logic.is_game_over = False
        return True

    def get_xyz(self, tf):
        success = False
        while not success:
            try:
                time = tf.getLatestCommonTime(self.frame_name, self.world_name)
                pos = tf.lookupTransform(
                    self.world_name, self.frame_name, time)[0]
                return pos
            except:
                print "caught exception in get_xyz"

    def get_z_distance(self, tf):
        xyz = self.get_xyz(tf)
        return xyz[2]

    def resolve_disagreement(self, tf, logic):
        robot_agrees = False
        while not robot_agrees:
            #print "I DISAGREE"
            self.robot.Say("I disagree")
            pythontime.sleep(DECISION_TIME)
            direction = self.get_human_direction(tf)
            if direction == Direction.STAY:
                break
            else:
                robot_agrees = logic.does_agree_to_move(direction)
        return direction

    def get_human_direction(self, tf):
        xyz = self.get_xyz(tf)
        x_position = xyz[0]
        print "x = %.2f" % x_position
        if abs(x_position) > STEPSIZE_THRESHOLD:
            if x_position > 0:
                return Direction.POSITIVE
            else:
                return Direction.NEGATIVE
        return Direction.STAY

    # def does_robot_agree_to_move(self, direction):
    #     if self.does_agree_sequence_index < len(DOES_AGREE_SEQUENCE):
    #         self.does_agree_sequence_index += 1
    #         return DOES_AGREE_SEQUENCE[self.does_agree_sequence_index - 1]
    #     return True


def humanInList(human, ids):
    for id_num in ids:
        if human.id == 'user_' + id_num:
            return True
    return False


def addRemoveHumans(transform, humans, env):
    matcher = re.compile('.*user_(\\d+).*')
    all_tfs = transform.getFrameStrings()
    all_human_ids = []
    for frame_name in all_tfs:
        match = matcher.match(frame_name)
        if match is not None:
            all_human_ids.append(match.groups()[0])

    # removing
    for i in xrange(len(humans)):
        old_human = humans[i]
        if not humanInList(old_human, all_human_ids):
            humans.pop(i)
            print "{} wasn't detected".format(old_human.id)
        elif abs(old_human.get_z_distance(transform) - Z_DISTANCE) > Z_DISTANCE_DELTA:
            humans.pop(i)
            print "{} has invalid z = {}".format(old_human.id, old_human.get_z_distance(transform))

    # adding
    for id_num in all_human_ids:
        found = False
        for human in humans:
            if human.id == 'user_' + id_num:
                found = True
                break
        if not found:
            new_human = Orhuman('user_' + id_num, env)
            if abs(new_human.get_z_distance(transform) - Z_DISTANCE) < Z_DISTANCE_DELTA:
                humans.append(new_human)
                print "added {}".format(new_human.id)

    if len(humans) > 1:
        print "{} legal humans now".format(len(humans))
        print "{}, {}".format(humans[0].id, humans[1].id)