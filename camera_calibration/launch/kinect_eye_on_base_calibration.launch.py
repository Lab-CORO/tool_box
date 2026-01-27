from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os

def generate_launch_description():
    # Déclaration des arguments
    namespace_prefix_arg = DeclareLaunchArgument("namespace_prefix", default_value="kinect_calib")
    marker_id_arg = DeclareLaunchArgument("marker_id", default_value="1")
    marker_size_arg = DeclareLaunchArgument("marker_size", default_value="0.096")
    eye_on_hand_arg = DeclareLaunchArgument("eye_on_hand", default_value="false")
    marker_frame_arg = DeclareLaunchArgument("marker_frame", default_value="aruco_marker")
    ref_frame_arg = DeclareLaunchArgument("ref_frame", default_value="base_link")
    corner_refinement_arg = DeclareLaunchArgument("corner_refinement", default_value="LINES")
    camera_frame_arg = DeclareLaunchArgument("camera_frame", default_value="rgb_camera_link")
    camera_image_topic_arg = DeclareLaunchArgument("camera_image_topic", default_value="/rgb/image_rect_raw")
    camera_info_topic_arg = DeclareLaunchArgument("camera_info_topic", default_value="/rgb/camera_info")

    
    # Include the Azure Kinect driver launch file
    azure_kinect_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("azure_kinect_ros_driver"), "launch", "driver.launch.py")
        )
    )
    
    # Rectify node (Kinect 2D image)
    rectify_node = Node(
        package="image_proc",
        executable="rectify_node",
        name="rectify_rgb",
        remappings=[
            ("image", "rgb/image_raw"),
            ("image_rect", "rgb/image_rect_raw"),
            ("camera_info", "/rgb/camera_info")
        ]
    )

    # Chemin des fichiers de lancement pour d'autres packages
    dsr_bringup2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("dsr_bringup2"), "launch", "dsr_bringup2_rviz.launch.py")
        ),
        launch_arguments={
            "mode": "real",
            "host": "192.168.50.100",
            "port": "12345",
            "model": "m1013"
        }.items()
    )

    #Nouveau nœud pour la détection des marqueurs fiduciaires
    markertracker_node = Node(
        package='ros2_markertracker',
        executable='markertracker_node',
        # output="screen",
        namespace="/ros2_markertracker",
        parameters=[{
            "input_image_topic": "/rgb/image_raw",
            "publish_topic_image_result": True,
            "camera_info_topic": '/rgb/camera_info',
            "marker_length": 9.6,
            "aruco_dictionary_id": "DICT_4X4_250",
            "camera_frame_id": "rgb_camera_link",
            "marker_frame_id": "marker",
            "ignore_marker_ids_array": 17
        }]
    )

    handeye_calibration_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('hand_eye_calibration'), 'calibration.launch.py'
            )
        ),
        launch_arguments={
            'calibration_type': 'eye-on-base',
            'namespace_prefix': LaunchConfiguration('namespace_prefix'),
            'freehand_robot_movement': 'true',
            'robot_base_frame': 'base_link',
            'robot_effector_frame': 'link_6',
            'tracking_base_frame': 'rgb_camera_link',
            'tracking_marker_frame': 'marker'
        }.items()
    )

    return LaunchDescription([
        namespace_prefix_arg,
        marker_id_arg,
        marker_size_arg,
        eye_on_hand_arg,
        marker_frame_arg,
        ref_frame_arg,
        corner_refinement_arg,
        camera_frame_arg,
        camera_image_topic_arg,
        camera_info_topic_arg,
        dsr_bringup2_launch,
        azure_kinect_driver_launch,
        rectify_node,
        markertracker_node,
        handeye_calibration_launch
    ])
