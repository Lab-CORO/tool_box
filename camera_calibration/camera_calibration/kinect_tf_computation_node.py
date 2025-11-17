#!/usr/bin/env python3
 
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf_transformations
from tf2_ros import TransformBroadcaster, TransformListener, Buffer
 
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
        self.cam_to_color_tf = TransformStamped()
        self.cam_to_color_tf.header.frame_id = 'base_link'
        self.cam_to_color_tf.child_frame_id = 'rgb_camera_link'
        # Remplir avec les données connues de la transformation fixe

        #Calib manuelle avec model 3D:
        #tx, ty, tz, qx, qy, qz, qw: [0.0374, -0.0625, -0.0603, 0.0153, -0.0466, 0.9926, -0.1110] as euler: translation: 0.0374, -0.0625, -0.0603   rpy: -0.0961, -0.0201, -2.9179')

        # self.cam_to_color_tf.transform.translation.x = 0.0374  # À ajuster
        # self.cam_to_color_tf.transform.translation.y = -0.0625  # À ajuster
        # self.cam_to_color_tf.transform.translation.z = -0.0603  # À ajuster
        # self.cam_to_color_tf.transform.rotation.x = 0.0153
        # self.cam_to_color_tf.transform.rotation.y = -0.0466
        # self.cam_to_color_tf.transform.rotation.z = 0.9926
        # self.cam_to_color_tf.transform.rotation.w = -0.1110


        #Calib avec nouveau Aruco 6 déc:
        #'Current estimate: tx, ty, tz, qx, qy, qz, qw: [0.2725, 0.0811, 0.9726, 0.4272, 0.0920, 0.8986, 0.0397] as euler: translation: 0.2725, 0.0811, 0.9726   rpy: 0.3119, -0.8640, 2.9086')

        self.cam_to_color_tf.transform.translation.x = 0.2725  # À ajuster
        self.cam_to_color_tf.transform.translation.y = 0.0811  # À ajuster
        self.cam_to_color_tf.transform.translation.z = 0.9726  # À ajuster
        self.cam_to_color_tf.transform.rotation.x = 0.4272
        self.cam_to_color_tf.transform.rotation.y = 0.0920
        self.cam_to_color_tf.transform.rotation.z = 0.8986
        self.cam_to_color_tf.transform.rotation.w = 0.0397

 
    def timer_callback(self):
        try:
            # Récupération de la transformation de calibration (camera_base -> rgb_camera_link)
            calibration_tf = self.tf_buffer.lookup_transform('camera_base', 'rgb_camera_link', rclpy.time.Time())
        except Exception as e:
            self.get_logger().warn(f'Could not get calibration transform: {e}')
            return
 
        # Calcul de la transformation entre camera_link et camera_color_optical_frame
        base_link_to_camera_base_tf = self.compute_base_link_to_camera_base(calibration_tf, self.cam_to_color_tf)
 
        # Publication de la transformation calculée
        self.tf_broadcaster.sendTransform(base_link_to_camera_base_tf)
 
    def compute_base_link_to_camera_base(self, calibration_tf, cam_to_color_tf):
        """
        Calcule la transformation entre base_link et camera_base.
 
        Paramètres:
        - calibration_tf: TransformStamped représentant la transformation de camera_base vers rgb_camera_link.
        - cam_to_color_tf: TransformStamped représentant la transformation de base_link vers rgb_camera_link .
 
        Retourne:
        - TransformStamped représentant la transformation de base_link vers camera_base.
        """
 
        # Conversion de calibration_tf en matrice
        trans_calib = calibration_tf.transform.translation
        rot_calib = calibration_tf.transform.rotation
        T_rgb_camera_link_camera_base = tf_transformations.concatenate_matrices(
            tf_transformations.translation_matrix([trans_calib.x, trans_calib.y, trans_calib.z]),
            tf_transformations.quaternion_matrix([rot_calib.x, rot_calib.y, rot_calib.z, rot_calib.w])
        )
 
        # Inversion pour obtenir T_camera_base_rgb_camera_link
        T_camera_base_rgb_camera_link = tf_transformations.inverse_matrix(T_rgb_camera_link_camera_base)
 
        # Conversion de cam_to_color_tf en matrice
        trans_cam = cam_to_color_tf.transform.translation
        rot_cam = cam_to_color_tf.transform.rotation
        T_rgb_camera_link_base_link = tf_transformations.concatenate_matrices(
            tf_transformations.translation_matrix([trans_cam.x, trans_cam.y, trans_cam.z]),
            tf_transformations.quaternion_matrix([rot_cam.x, rot_cam.y, rot_cam.z, rot_cam.w])
        )
 
        # Inversion pour obtenir T_base_link_rgb_camera_link
        T_base_link_rgb_camera_link = tf_transformations.inverse_matrix(T_rgb_camera_link_base_link)
 
        # Calcul de T_base_link_camera_base
        T_base_link_camera_base =  T_base_link_rgb_camera_link @  T_camera_base_rgb_camera_link
 
        # Extraction de la translation et rotation
        translation = tf_transformations.translation_from_matrix(T_base_link_camera_base)
        rotation = tf_transformations.quaternion_from_matrix(T_base_link_camera_base)
 
        # Création du TransformStamped résultat
        result_tf = TransformStamped()
        result_tf.header.stamp = self.get_clock().now().to_msg()
        result_tf.header.frame_id = 'base_link'
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