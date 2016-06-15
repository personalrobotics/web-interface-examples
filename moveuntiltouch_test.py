#!/usr/bin/env python
import herbpy
import numpy

RIGHT_DOFS = [5.58752674, -0.81569425, -0.25011433,  2.25228782,
              -3.34832888, 1.46559139,  0.84342324]
LEFT_DOFS = [0.6373099, -0.79577868,  0.3423032,  2.31692865,  0.28152565,
             -1.53230128,  2.19221046]

env, robot = herbpy.initialize(sim=False)

while True:
    inp = raw_input(
        "Options: default_right, default_left, open, unstiff_right, unstiff_left, stiff_right, stiff_left, q ")
    if inp == "default_right":
        robot.right_arm.SetStiffness(1)
        robot.right_arm.PlanToConfiguration(RIGHT_DOFS, execute=True)
    elif inp == "default_left":
        robot.left_arm.SetStiffness(1)
        robot.left_arm.PlanToConfiguration(LEFT_DOFS, execute=True)
    elif inp == "open":
        robot.right_hand.OpenHand()
        robot.left_hand.OpenHand()
    elif inp == "unstiff_right":
        robot.right_arm.SetStiffness(0)
    elif inp == "unstiff_left":
        robot.left_arm.SetStiffness(0)
    elif inp == "stiff_right":
        robot.right_arm.SetStiffness(1)
    elif inp == "stiff_left":
        robot.left_arm.SetStiffness(1)
    elif inp == 'q':
        break

robot.right_arm.SetStiffness(1)
robot.left_arm.SetStiffness(1) 

raw_input('take the table. press enter to close hands')
robot.right_hand.CloseHand()
robot.left_hand.CloseHand()

while True:
    inp = raw_input('press enter to tare sensors. otherwise type q ')
    if inp == 'q':
        break
    robot.left_hand.TareForceTorqueSensor()
    print "left tare returned"
    robot.right_hand.TareForceTorqueSensor()
    print "right tare returned"

FORCE = 20
DISTANCE = 0.1
push_done = False
arm = robot.left_arm
while True:
    inp = raw_input('Options: push, pull, open, switch, q ')
    try:
        if inp == 'q':
            break
        elif inp == "switch":
            if arm == robot.left_arm:
                arm = robot.right_arm
            else:
                arm = robot.left_arm
        elif inp == 'push':
            transform = robot.GetTransform()
            xyz = transform[0:3, 0]
            start_pose = arm.GetEndEffectorTransform()
            felt_force = arm.MoveUntilTouch(
                direction=xyz, distance=DISTANCE, max_distance=DISTANCE, max_force=FORCE)
            print "felt_force = ", felt_force
            push_done = True
        elif inp == 'pull' and push_done:
            end_pose = arm.GetEndEffectorTransform()
            start_end_delta = numpy.linalg.norm(end_pose[:3, 3] - start_pose[:3, 3])
            arm.PlanToEndEffectorOffset(
                direction=-xyz, distance=start_end_delta)
            push_done = False
        elif inp == "open":
            robot.right_hand.OpenHand()
            robot.left_hand.OpenHand()
    except Exception as e:
        print "exception occured: ", e.strerror
