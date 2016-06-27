# Instructions

```
mkdir kinect-control-workspace
cd kinect-control-workspace
wstool init src
catkin init
cd src
wstool merge ~/kinect_control.rosinstall
wstool up
cd ..
catkin build
copy momdp_data folder to kinect-control-workspace/devel/share
rosmasterherb
. devel/setup.bash
roslaunch humanpy humtrackkinect2_herb.launch seg_sim:=False
```
