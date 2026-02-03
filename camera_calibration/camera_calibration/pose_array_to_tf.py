import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import PoseArray, TransformStamped
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

class PoseArrayToTF(Node):

    def __init__(self):
        super().__init__('pose_array_to_tf')

        # Define parameter descriptors for better documentation
        subscription_pose_array_descriptor = ParameterDescriptor(
            type=ParameterType.PARAMETER_STRING,
            description='Topic name to subscribe to PoseArray messages')
        parent_frame_id_descriptor = ParameterDescriptor(
            type=ParameterType.PARAMETER_STRING,
            description='Parent frame ID for the TF transformation')
        publisher_frame_id_descriptor = ParameterDescriptor(
            type=ParameterType.PARAMETER_STRING,
            description='Child frame ID for the TF transformation')

        # Declare parameters with default values
        self.declare_parameter(
            'subscription_pose_array', 'aruco_poses', subscription_pose_array_descriptor)
        self.declare_parameter(
            'parent_frame_id', 'rgb_camera_link', parent_frame_id_descriptor)
        self.declare_parameter(
            'publisher_frame_id', 'aruco_marker', publisher_frame_id_descriptor)

        # Retrieve parameter values
        self.subscription_pose_array = self.get_parameter(
            'subscription_pose_array').get_parameter_value().string_value
        self.parent_frame_id = self.get_parameter(
            'parent_frame_id').get_parameter_value().string_value
        self.publisher_frame_id = self.get_parameter(
            'publisher_frame_id').get_parameter_value().string_value

        # Create publisher and subscriber using the parameters
        self.publisher = self.create_publisher(TFMessage, 'tf', 10)
        self.subscription = self.create_subscription(
            PoseArray,
            self.subscription_pose_array,
            self.conversion_callback,
            10)

    def conversion_callback(self, msg):
        if not msg.poses:
            return  # If the list of poses is empty, do nothing

        pose = msg.poses[0]  # Take the first (and only) pose
        tf_message = TFMessage()
        transform = TransformStamped()

        # Configure the TransformStamped using the parameters
        transform.header.stamp = msg.header.stamp
        transform.header.frame_id = self.parent_frame_id  # Parent frame from parameters
        transform.child_frame_id = self.publisher_frame_id  # Child frame from parameters

        # Set the translation
        transform.transform.translation.x = pose.position.x
        transform.transform.translation.y = pose.position.y
        transform.transform.translation.z = pose.position.z

        # Set the rotation
        transform.transform.rotation = pose.orientation

        tf_message.transforms.append(transform)

        self.publisher.publish(tf_message)

def main(args=None):
    rclpy.init(args=args)
    node = PoseArrayToTF()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
