# Camera calibration pakcage for Real Sense and Azure Kinect 

This repo explains the steps to calibrate the Azure Kinect and Real Sense cameras relatively to the base of the Doosan robot.

## Required packages
To proceed to the calibration of the cameras, you will need a few packages, three of which are assumed installed and operational : 

- [Azure Kinect camera](https://github.com/microsoft/Azure_Kinect_ROS_Driver)
- [Real Sense camera](https://github.com/IntelRealSense/realsense-ros)
- [Doosan robot](https://github.com/doosan-robotics/doosan-robot2)

The two additionnal packages used in this package are :

- [ros2_markertracker](https://github.com/Veilkrand/ros2_markertracker)
- [ROS2 Hand eye calibration](https://github.com/giuschio/ros2_handeye_calibration)

**IMPORTANT INFO** : The "ros2_markertracker" package has been modified and is already incorporated in the tool_box repo here. You should not git clone the repo,
as opposed to the ROS2_Hand_eye_calibration package, which you need to install separately.

## Steps to calibrate the cameras

This repo contains two launch files, one for each camera. Launching a launch file should start the corresponding camera as well as the aruco, the Doosan robot and the calibration nodes. It should also start the custom calibration node that converts the data published by the aruco marker to the expected /tf type that the calibration node is subscribed to.

### Unlock doosan arm to collaboratif control
**Please note** : For the calibration, it is recommended to use the robot in manual mode. To do this when it is connected to the computer, simply open the RQT interface :

```bash
rqt
```
Go to -> Plugins -> Services -> Service caller

Find, in the dropdown menu, the service called : "/dsr01/system/set_safety_mode" and set the value of safety_mode to 1 and the value of safety_event to 2
Find, in the dropdown menu, the service called : "/dsr01/system/set_robot_mode" and set the value to 0, 




### Calibration for a camera on the base (ex: Azure kinect)
Command to launch the calibration for the Azure Kinect : 

```bash
ros2 launch camera_calibration kinect_eye_on_base_calibration.launch.py
```
**Important note** : The kinect has a fish-eye lense. In the calibration file, there is already a function
in place that rectifies the image. There is also a ros2 node command that has the same effect. It needs to be run 
when you have started the azure kinect launch file alone:
<!-- ```bash
ros2 run image_proc rectify_node --ros-args -r __node:=rectify_rgb --remap image:=rgb/image_raw --remap image_rect:=rgb/image_rect_raw
--remap camera_info:=/rgb/camera_info
```
### Calibration for a camera on hand (ex: D405 RealSense)
Command to launch the calibration for the Real Sense : 
```bash 
ros2 launch camera_calibration rs_eye_on_hand_calibrate.launch.py
``` -->

### Take picture for calibration
In another terminal, you will need to make a service call to calibrate the camera with : 
```bash
ros2 service call /hand_eye_calibration/capture_point std_srvs/srv/Trigger {}
```
It is recommended to take a least 15 triggers for a better calibration accuracy. For more details on the calibration itself, refer to the [ROS2 Hand eye calibration](https://github.com/giuschio/ros2_handeye_calibration) package mentionned previously. 

When the calibration is completed, the terminal should output the transform generated between the robot and the camera, both in quaternion and Euler format.

Take the quaternion or euler values and put them into the corresponding tf2 node to broadcast the new transformation.

## Tips for accuracy
    Wait for the stability of the marker's tf in rviz
    Maximize rotation between poses.
    Minimize the distance from the target to the camera of the tracking system.
    Minimize the translation between poses.
    Use redundant poses.
    Calibrate the camera intrinsics if necessary / applicable.
    Calibrate the robot if necessary / applicable.


## 
