#!/usr/bin/env python3
 
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf_transformations
from tf2_ros import TransformBroadcaster, TransformListener, Buffer
 
class rsTFComputationNode(Node):
    def __init__(self):
        super().__init__('rs_tf_computation_node')
 
        # Création du broadcaster pour publier la nouvelle transformation
        self.tf_broadcaster = TransformBroadcaster(self)
 
        # Buffer et listener pour recevoir les transformations
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
 
        # Timer pour exécuter périodiquement le calcul
        self.timer = self.create_timer(0.1, self.timer_callback)  # Exécution toutes les 0.1 secondes
 
        # Transformation connue entre cam_link et color_cam_link
        self.cam_to_color_tf = TransformStamped()
        self.cam_to_color_tf.header.frame_id = 'link_6'
        self.cam_to_color_tf.child_frame_id = 'camera_color_optical_frame'
        # Remplir avec les données connues de la transformation fixe

        #Calib manuelle avec model 3D:
        #tx, ty, tz, qx, qy, qz, qw: [0.0374, -0.0625, -0.0603, 0.0153, -0.0466, 0.9926, -0.1110] as euler: translation: 0.0374, -0.0625, -0.0603   rpy: -0.0961, -0.0201, -2.9179')

        #Calib avec nouveau Aruco 6 déc:
        #Current estimate: tx, ty, tz, qx, qy, qz, qw: [-0.0870, 0.0313, -0.0289, -0.4813, 0.4630, 0.5972, 0.4441] as euler: translation: -0.0870, 0.0313, -0.0289   rpy: 0.8611, 1.4045, 2.6041')

        self.cam_to_color_tf.transform.translation.x = -0.0870  # À ajuster
        self.cam_to_color_tf.transform.translation.y = 0.0313  # À ajuster
        self.cam_to_color_tf.transform.translation.z = -0.0289  # À ajuster
        self.cam_to_color_tf.transform.rotation.x = -0.4813
        self.cam_to_color_tf.transform.rotation.y = 0.4630
        self.cam_to_color_tf.transform.rotation.z = 0.5972
        self.cam_to_color_tf.transform.rotation.w = 0.4441
 
    def timer_callback(self):
        try:
            # Récupération de la transformation de calibration (camera_link -> camera_color_optical_frame)
            calibration_tf = self.tf_buffer.lookup_transform('camera_link', 'camera_color_optical_frame', rclpy.time.Time())
        except Exception as e:
            self.get_logger().warn(f'Could not get calibration transform: {e}')
            return
 
        # Calcul de la transformation entre camera_link et camera_color_optical_frame
        link6_to_camera_link_tf = self.compute_link6_to_camera_link(calibration_tf, self.cam_to_color_tf)
 
        # Publication de la transformation calculée
        self.tf_broadcaster.sendTransform(link6_to_camera_link_tf)
 
    def compute_link6_to_camera_link(self, calibration_tf, cam_to_color_tf):
        """
        Calcule la transformation entre link_6 et camera_link.
 
        Paramètres:
        - calibration_tf: TransformStamped représentant la transformation de camera_link vers camera_color_optical_frame.
        - cam_to_color_tf: TransformStamped représentant la transformation de link_6 vers camera_color_optical_frame .
 
        Retourne:
        - TransformStamped représentant la transformation de link_6 vers camera_link.
        """
 
        # Conversion de calibration_tf en matrice
        trans_calib = calibration_tf.transform.translation
        rot_calib = calibration_tf.transform.rotation
        T_camera_color_optical_frame_camera_link = tf_transformations.concatenate_matrices(
            tf_transformations.translation_matrix([trans_calib.x, trans_calib.y, trans_calib.z]),
            tf_transformations.quaternion_matrix([rot_calib.x, rot_calib.y, rot_calib.z, rot_calib.w])
        )
 
        # Inversion pour obtenir T_camera_link_camera_color_optical_frame
        T_camera_link_camera_color_optical_frame = tf_transformations.inverse_matrix(T_camera_color_optical_frame_camera_link)
 
        # Conversion de cam_to_color_tf en matrice
        trans_cam = cam_to_color_tf.transform.translation
        rot_cam = cam_to_color_tf.transform.rotation
        T_camera_color_optical_frame_link_6 = tf_transformations.concatenate_matrices(
            tf_transformations.translation_matrix([trans_cam.x, trans_cam.y, trans_cam.z]),
            tf_transformations.quaternion_matrix([rot_cam.x, rot_cam.y, rot_cam.z, rot_cam.w])
        )
 
        # Inversion pour obtenir T_link6_camera_color_optical_frame
        T_link6_camera_color_optical_frame = tf_transformations.inverse_matrix(T_camera_color_optical_frame_link_6)
 
        # Calcul de T_link6_camera_link
        T_link6_camera_link =  T_link6_camera_color_optical_frame @  T_camera_link_camera_color_optical_frame
 
        # Extraction de la translation et rotation
        translation = tf_transformations.translation_from_matrix(T_link6_camera_link)
        rotation = tf_transformations.quaternion_from_matrix(T_link6_camera_link)
 
        # Création du TransformStamped résultat
        result_tf = TransformStamped()
        result_tf.header.stamp = self.get_clock().now().to_msg()
        result_tf.header.frame_id = 'link_6'
        result_tf.child_frame_id = 'camera_link'
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
 
    node = rsTFComputationNode()
    rclpy.spin(node)
 
    node.destroy_node()
    rclpy.shutdown()
 
if __name__ == '__main__':
    main()