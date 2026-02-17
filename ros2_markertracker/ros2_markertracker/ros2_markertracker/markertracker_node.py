#!/usr/bin/env python
"""
http://wiki.ros.org/cv_bridge/Tutorials/ConvertingBetweenROSImagesAndOpenCVImagesPython

Subscribe to a ROS raw image topic, transform to OpenCV image. And process the image.

"""
import threading

import cv2
from cv_bridge import CvBridge, CvBridgeError
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, PoseWithCovarianceStamped, PoseArray, Pose, PoseStamped  #, Point32
from sensor_msgs.msg import Image, CameraInfo

# from tf.transformations import quaternion_from_euler, euler_from_quaternion, euler_from_matrix
# from ros2_markertracker.transformations import quaternion_from_euler
from scipy.spatial.transform import Rotation as R

# from tf import TransformBroadcaster
import tf_transformations
from tf2_ros import TransformBroadcaster, TransformListener, Buffer
from geometry_msgs.msg import TransformStamped

import math
import numpy as np

from ros2_markertracker_interfaces.msg import FiducialMarker, FiducialMarkerArray
from ros2_markertracker.ArucoWrapper import ArucoWrapper
from rclpy.wait_for_message import wait_for_message


# ---
# Ros2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
# from std_msgs.msg import String




def main(args=None):

    rclpy.init(args=args)

    markertracker_node = ProcessFramePubSub()

    # Spin in a separate thread
    thread = threading.Thread(target=rclpy.spin, args=(markertracker_node,), daemon=True)
    thread.start()
    # Processing rate can be adjusted to only process the last image frame received
    r = markertracker_node.create_rate(30)  #30 Hz # 10 Hz
    try:
        while rclpy.ok():
            # markertracker_node.get_logger().info('New loop')
            if markertracker_node.new_msg_available:
                markertracker_node.new_msg_available = False
                markertracker_node.process_frame(markertracker_node.latest_msg)
            r.sleep()
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    markertracker_node.destroy_node()
    rclpy.shutdown()
    thread.join()



# -----
class ReusableIdGenerator:

    def __init__(self, number):
        self.index = 1
        self.number = number

    def get_id(self):
        self.index += 1

        if self.index == self.number: self.index = 1

        return int(self.index)

class ProcessFramePubSub(Node):
    """
     Subscribe to a image topic, call a process callback and publish results
    """

    def __init__(self):

        super().__init__('markertracker_node')

        # Publisher topics
        _result_image_topic = '/image_result'
        _result_poses_topic = '/poses'
        _result_markers_viz_topic = '/visualization_markers'
        _result_marker_topic = '/fiducial_markers'

        # Declare and read parameters
        self.declare_parameter("input_image_topic", "/rgb/image_raw")
        _input_image_topic = self.get_parameter("input_image_topic").get_parameter_value().string_value

        self.declare_parameter("marker_length", 10.0)
        self.marker_length = self.get_parameter("marker_length").get_parameter_value().double_value
        self.get_logger().info(f"Marker length set to: {self.marker_length}")

        self.declare_parameter("publish_topic_image_result", False)

        self.declare_parameter("camera_frame_id", "camera")
        self._camera_frame_id = self.get_parameter("camera_frame_id").get_parameter_value().string_value


        self.declare_parameter("aruco_dictionary_id", "DICT_4X4_50")
        _aruco_dictionary_id = self.get_parameter("aruco_dictionary_id").get_parameter_value().string_value

        self.declare_parameter("path_to_camera_file", "calibration/camerav2_1280x720.yaml")
        _path_to_camera_file = self.get_parameter("path_to_camera_file").get_parameter_value().string_value

        # get camera info from topic
        self.declare_parameter("camera_info_topic", "/camera_info")
        camera_info_topic = self.get_parameter("camera_info_topic").get_parameter_value().string_value
        
        # wait for camera info with retry logic (timeout 30 seconds)
        self.get_logger().info(f'Waiting for camera info on {camera_info_topic}...')
        max_retries = 6
        retry_delay = 5  # seconds
        camera_info = None
        
        for attempt in range(max_retries):
            try:
                result = wait_for_message(CameraInfo, self, camera_info_topic, time_to_wait=5.0)
                
                if isinstance(result, tuple):
                    success, camera_info = result
                else:
                    camera_info = result
                    success = camera_info is not None
                
                if success and camera_info is not None:
                    self.get_logger().info(f'Camera info received on attempt {attempt + 1}')
                    break
            except Exception as e:
                self.get_logger().warn(f'Attempt {attempt + 1}/{max_retries}: Camera info not ready - {str(e)}')
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
        
        if camera_info is None:
            self.get_logger().error('Failed to get camera info after multiple attempts')
            return

            
        # get the intrinsic matrix and distortion coefficients from the camera info
        _camera_matrix = np.reshape(np.array(camera_info.k), (3, 3))
        _dist_coeffs = np.array(camera_info.d)

        # TODO: Setup all remain params for Aruco

        self.publish_topic_image_result = True

        assert(len(_camera_matrix) and len(_dist_coeffs))
        self.get_logger().debug(f'Camera Matrix: {_camera_matrix}')
        self.get_logger().debug(f'Dist Coeff: {_dist_coeffs}')



        # Setup OpenCV
        self.bridge = CvBridge()
        self.detector = ArucoWrapper(self.marker_length,
                                     _camera_matrix, _dist_coeffs,
                                     aruco_dictionary_name=_aruco_dictionary_id)

        ## --
        ## Subscribers

        # Image raw topic
        # Use a permissive QoS profile that auto-negotiates with most camera drivers
        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,  # Changed to RELIABLE - Kinect may use this
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10  # Increased buffer to avoid missing frames
        )

        self.image_sub = self.create_subscription(Image,
                                                  _input_image_topic,
                                                  self._image_callback,
                                                  qos_profile=image_qos)

        # self.image_sub = rospy.Subscriber(_input_image_topic, Image, self._callback, queue_size=1)
        self.get_logger().info(f'Subscribed to {_input_image_topic} with RELIABLE QoS')


        self.latest_msg = None  # keep latest received message
        self.new_msg_available = False

        ## ---
        ## Publishers

        # TF broadcaster
        self.tf_br = TransformBroadcaster(self)

        # Image Publisher
        if self.publish_topic_image_result:
            self.image_pub = self.create_publisher(Image, _result_image_topic, 1)

        # Marker viz marker publisher
        self.marker_viz_pub = self.create_publisher(MarkerArray, _result_markers_viz_topic, 100)

        # Marker viz pose publisher
        self.poses_pub = self.create_publisher(PoseArray, _result_poses_topic, 100)

        # FiducialMarkerArray publisher
        self.fiducial_markers_pub = self.create_publisher(FiducialMarkerArray, _result_marker_topic, 100)

        self.id_gen = ReusableIdGenerator(500)



    def _publish_cv_image(self, image):
        if image is None: return
        try:
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(image, "bgr8"))
        except CvBridgeError as e:
            print(e)

    def _image_callback(self, data):
        self.latest_msg = data
        self.new_msg_available = True

    def process_frame(self, image):

        if image is None:
            return

        ## Preprocess
        try:
            cv_image = self.bridge.imgmsg_to_cv2(image, "bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
            raise e

        ## Pose and corners used
        cv_image_result, poses = self.detector.get_poses_from_image(cv_image,
                                                                    draw_image=self.publish_topic_image_result)

        # process poses to messages
        if poses is not None and len(poses) > 0:
            self._create_and_publish_markers_msgs_from_pose_results(poses, image.header.stamp, self._camera_frame_id)


        # Publish CV debug image
        if self.publish_topic_image_result:
            if cv_image_result is not None:
                self._publish_cv_image(cv_image_result)


    def create_viz_marker_object(self, pose):

        marker = Marker()
        marker.id = self.id_gen.get_id()

        # marker.ns = self.node_name
        marker.header.frame_id = self._camera_frame_id
        marker.type = marker.CUBE
        marker.action = marker.ADD
        marker.lifetime = rclpy.duration.Duration(seconds=1).to_msg()

        # Size of the viz marker
        marker.scale.x = 0.025
        marker.scale.y = 1.0
        marker.scale.z = 1.0

        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 0.10

        marker.pose.position = pose.position
        marker.pose.orientation = pose.orientation

        return marker

    def _create_and_publish_markers_msgs_from_pose_results(self, poses, image_timestamp, camera_frame_id):

        marker_array = MarkerArray()  # For Rviz visualization

        pose_array = PoseArray()  # For Rviz visualization with current time stamp
        pose_array.header.stamp = image_timestamp
        pose_array.header.frame_id = camera_frame_id

        gate_marker_array = FiducialMarkerArray()  # For output results
        gate_marker_array.header.stamp = self.get_clock().now().to_msg()
        gate_marker_array.camera_frame_stamp = image_timestamp

        _index = -1
        for e in poses:
            _index += 1


            gate_pose = Pose()

            gate_pose.position.x = e['tvec'][0]/100   # Z_optique → X_rgb (avant)
            gate_pose.position.y = e['tvec'][1]/100  # -X_optique → Y_rgb (gauche = -droite)
            gate_pose.position.z = e['tvec'][2]/100   # Y_optique → Z_rgb (bas)
            
            r = R.from_euler('xyz', e['rvec'], degrees=False)
            _quaternion_optical = r.as_quat()

            gate_pose.orientation.x = _quaternion_optical[0]
            gate_pose.orientation.y = _quaternion_optical[1]
            gate_pose.orientation.z = _quaternion_optical[2]
            gate_pose.orientation.w = _quaternion_optical[3]
            gate_viz_marker = self.create_viz_marker_object(gate_pose)

            gate_marker = self.create_gate_marker_object(gate_pose, tuple(e['corners']), camera_frame_id, image_timestamp, e['marker_id'])


            
            result_tf = TransformStamped()
            result_tf.header.stamp = self.get_clock().now().to_msg()
            result_tf.header.frame_id = self._camera_frame_id
            result_tf.child_frame_id = 'marker'
            result_tf.transform.translation.x = gate_pose.position.x
            result_tf.transform.translation.y = gate_pose.position.y
            result_tf.transform.translation.z = gate_pose.position.z
            result_tf.transform.rotation.x = gate_pose.orientation.x
            result_tf.transform.rotation.y = gate_pose.orientation.y
            result_tf.transform.rotation.z = gate_pose.orientation.z
            result_tf.transform.rotation.w = gate_pose.orientation.w
            self.tf_br.sendTransform(result_tf)


            marker_array.markers.append(gate_viz_marker)
            pose_array.poses.append(gate_pose)
            gate_marker_array.marker.append(gate_marker)


        # DEBUG


        '''
        _q = (marker_array.markers[0].pose.orientation.x,
              marker_array.markers[0].pose.orientation.y,
              marker_array.markers[0].pose.orientation.z,
              marker_array.markers[0].pose.orientation.w)

        _euler = euler_from_quaternion(_q)
        #_R = e['rot_m']
        #_euler = euler_from_matrix(_R, 'rzyx')


        _r = 180 * _euler[0] / math.pi
        _p = 180 * _euler[1] / math.pi
        _y = 180 * _euler[2] / math.pi
        rospy.loginfo("R:{:.0f} P:{:.0f} Y:{:.0f}".format(_r, _p, _y))
        '''

        # Publish Topics
        self.poses_pub.publish(pose_array)
        self.marker_viz_pub.publish(marker_array)
        self.fiducial_markers_pub.publish(gate_marker_array)

    def create_gate_marker_object(self, pose, corners, frame_id, image_timestamp, marker_id):

        marker = FiducialMarker()
        marker.id = int(marker_id)
        marker.pose_cov_stamped.header.frame_id = frame_id
        marker.pose_cov_stamped.header.stamp = image_timestamp
        marker.pose_cov_stamped.pose.pose = pose

        # TODO: simple covariances... Get from latest ego pose/odometry
        _covariance = [1e-6, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 1e-6, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 1e-6, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 1e-3, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 1e-3, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 1e-3]

        marker.pose_cov_stamped.pose.covariance = _covariance

        return marker




if __name__ == '__main__':
    main()
