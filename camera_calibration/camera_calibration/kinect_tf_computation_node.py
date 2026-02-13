#!/usr/bin/env python3
 
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf_transformations
from tf2_ros import TransformBroadcaster, TransformListener, Buffer
import ros2_numpy
import numpy as np
from numpy.linalg import inv
class kinectTFComputationNode(Node):
    def __init__(self):
        super().__init__('kinect_tf_computation_node')
 
        # Création du broadcaster pour publier la nouvelle transformation
        self.tf_broadcaster = TransformBroadcaster(self)
 
        # Buffer et listener pour recevoir les transformations
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
 
        # Timer pour exécuter périodiquement le calcul
        self.timer = self.create_timer(0.1, self.timer_callback)  # Exécution toutes les 0.1 secondes
 
        # Transformation connue entre cam_link et color_cam_link
        self.base_link_to_rgb = TransformStamped()
        self.base_link_to_rgb.header.frame_id = 'base_link'
        self.base_link_to_rgb.child_frame_id = 'rgb_camera_link'
        # Remplir avec les données connues de la transformation fixe

        #Calib manuelle avec model 3D:
        #tx, ty, tz, qx, qy, qz, qw: [0.0374, -0.0625, -0.0603, 0.0153, -0.0466, 0.9926, -0.1110] as euler: translation: 0.0374, -0.0625, -0.0603   rpy: -0.0961, -0.0201, -2.9179')

        self.base_link_to_rgb.transform.translation.x = -0.247400 # À ajuster
        self.base_link_to_rgb.transform.translation.y = -0.470300  # À ajuster
        self.base_link_to_rgb.transform.translation.z = 1.082100 # À ajuster
        self.base_link_to_rgb.transform.rotation.x = 0.191300
        self.base_link_to_rgb.transform.rotation.y = 0.272700
        self.base_link_to_rgb.transform.rotation.z = 0.849500
        self.base_link_to_rgb.transform.rotation.w = -0.409100

        # # std_srvs.srv.Trigger_Response(success=True, message='Current estimate: tx, ty, tz, qx, qy, qz, qw: [0.1946, -0.3640, 0.9618, 0.4544, 0.0085, 0.8659, -0.2091] as euler: translation: 0.1946, -0.3640, 0.9618   rpy: -0.2903, -0.9116, -2.5247')

 
    def timer_callback(self):
        try:
            # Récupération de la transformation de calibration (camera_base <- rgb_camera_link)
            rgb_to_cam = self.tf_buffer.lookup_transform('camera_base', 'rgb_camera_link', rclpy.time.Time())
        except Exception as e:
            self.get_logger().warn(f'Could not get calibration transform: {e}')
            return
 
        # Calcul de la transformation entre camera_link et camera_color_optical_frame
        base_link_to_camera_base_tf = self.compute_base_link_to_camera_base(rgb_to_cam, self.base_link_to_rgb)
 
        # Publication de la transformation calculée
        self.tf_broadcaster.sendTransform(base_link_to_camera_base_tf)
 
    def compute_base_link_to_camera_base(self, rgb_to_cam, base_link_to_rgb):
        """
        Calcule la transformation entre base_link et camera_base.
 
        Paramètres:
        - rgb_to_cam: TransformStamped représentant la transformation de camera_base vers rgb_camera_link.
        - base_link_to_rgb: TransformStamped représentant la transformation de base_link vers rgb_camera_link .
 
        Retourne:
        - TransformStamped représentant la transformation de base_link vers camera_base.
        """
 
        # Conversion de rgb_to_cam en matrice
        trans_calib = rgb_to_cam.transform.translation
        rot_calib = rgb_to_cam.transform.rotation
        T_rgb_camera_link_to_camera_base = ros2_numpy.numpify(rgb_to_cam.transform ) 
 
        # Conversion de base_link_to_rgb en matrice
        trans_cam = base_link_to_rgb.transform.translation
        rot_cam = base_link_to_rgb.transform.rotation
        T_base_link_to_rgb = ros2_numpy.numpify(base_link_to_rgb.transform) 
 
        # Calcul de T_base_link_camera_base 
        T_base_link_camera_base = np.dot((T_base_link_to_rgb), inv(T_rgb_camera_link_to_camera_base))#  @   

        # Extraction de la translation et rotation
        translation = tf_transformations.translation_from_matrix(T_base_link_camera_base)
        rotation = tf_transformations.quaternion_from_matrix(T_base_link_camera_base)
 
        # Création du TransformStamped résultat
        result_tf = TransformStamped()
        result_tf.header.stamp = self.get_clock().now().to_msg()
        result_tf.header.frame_id = 'world'
        result_tf.child_frame_id = 'camera_base'
        result_tf.transform.translation.x = translation[0]
        result_tf.transform.translation.y = translation[1]
        result_tf.transform.translation.z = translation[2]
        result_tf.transform.rotation.x = rotation[0]
        result_tf.transform.rotation.y = rotation[1]
        result_tf.transform.rotation.z = rotation[2]
        result_tf.transform.rotation.w = rotation[3]
 
        return result_tf
 
def main(args=None):
    rclpy.init(args=args)
 
    node = kinectTFComputationNode()
    rclpy.spin(node)
 
    node.destroy_node()
    rclpy.shutdown()
 
if __name__ == '__main__':
    main()