# ROS2 MarkerTracker

Package ROS2 pour la détection et le suivi de marqueurs ArUco avec publication de transformations TF et de poses 6DOF.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Topics ROS2](#topics-ros2)
- [Paramètres](#paramètres)
- [Exemples](#exemples)
- [Dépannage](#dépannage)

## 🎯 Vue d'ensemble

`ros2_markertracker` est un package ROS2 Humble qui détecte les marqueurs ArUco dans les flux vidéo en temps réel et calcule leur pose 6DOF (position et orientation) par rapport au repère de la caméra. Le package utilise OpenCV pour la détection et publie les résultats sous forme de transformations TF2 et de messages ROS2.

## ✨ Fonctionnalités

- ✅ Détection de marqueurs ArUco en temps réel
- ✅ Calcul de pose 6DOF (position + orientation quaternion)
- ✅ Publication des transformations TF2
- ✅ Support de multiples dictionnaires ArUco (4x4, 5x5, 6x6, 7x7, etc.)
- ✅ Utilisation des paramètres intrinsèques de caméra depuis camera_info topic
- ✅ Visualisation dans RViz (marqueurs et poses)
- ✅ Publication de messages personnalisés (FiducialMarker, FiducialMarkerArray)
- ✅ Traitement optimisé avec contrôle de fréquence
- ✅ Compatible ROS2 Humble

## 🏗️ Architecture

### Packages

Le projet contient deux packages :

1. **ros2_markertracker** : Package principal de détection
2. **ros2_markertracker_interfaces** : Définitions de messages personnalisés

### Messages personnalisés

#### FiducialMarker.msg
```
uint16 id                                          # ID du marqueur ArUco
geometry_msgs/PoseWithCovarianceStamped pose_cov_stamped  # Pose avec covariance
uint16[] corners                                   # Coins du marqueur (pixels)
```

#### FiducialMarkerArray.msg
```
std_msgs/Header header                    # Timestamp et frame_id
builtin_interfaces/Time camera_frame_stamp  # Timestamp de l'image source
FiducialMarker[] marker                   # Tableau de marqueurs détectés
```

### Nœud principal : markertracker_node

Le nœud principal subscribe à un topic d'image et publie :
- Transformations TF2 des marqueurs détectés
- Poses des marqueurs (PoseArray)
- Marqueurs pour visualisation RViz
- Messages FiducialMarkerArray personnalisés

## 📦 Installation

### Prérequis

```bash
sudo apt install -y \
    python3-opencv \
    python3-numpy \
    ros-humble-cv-bridge \
    ros-humble-vision-opencv \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs
```

### Compilation

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash

# Compiler d'abord les interfaces
colcon build --packages-select ros2_markertracker_interfaces
source install/setup.bash

# Puis le package principal
colcon build --packages-select ros2_markertracker
source install/setup.bash
```

## ⚙️ Configuration

### Paramètres de caméra

Le package utilise maintenant les informations intrinsèques de la caméra depuis le topic `camera_info` au lieu d'un fichier YAML. Cela rend le package plus flexible et compatible avec différentes caméras.

Si votre caméra ne publie pas de topic `camera_info`, vous devrez configurer votre driver de caméra pour le faire.

### Dictionnaires ArUco supportés

Le package supporte les dictionnaires ArUco suivants :
- `DICT_4X4_50`, `DICT_4X4_100`, `DICT_4X4_250`, `DICT_4X4_1000`
- `DICT_5X5_50`, `DICT_5X5_100`, `DICT_5X5_250`, `DICT_5X5_1000`
- `DICT_6X6_50`, `DICT_6X6_100`, `DICT_6X6_250`, `DICT_6X6_1000`
- `DICT_7X7_50`, `DICT_7X7_100`, `DICT_7X7_250`, `DICT_7X7_1000`
- `DICT_ARUCO_ORIGINAL`

## 🚀 Utilisation

### Lancement basique

```bash
ros2 run ros2_markertracker markertracker_node --ros-args \
    -p input_image_topic:=/camera/image_raw \
    -p camera_info_topic:=/camera/camera_info \
    -p marker_length:=10.0 \
    -p camera_frame_id:=camera_optical_frame \
    -p aruco_dictionary_id:=DICT_4X4_50
```

### Lancement avec fichier launch

```bash
ros2 launch ros2_markertracker markertracker_raspicam_1280x720.launch.py
```

### Visualisation dans RViz

```bash
rviz2
```

Ajoutez les affichages suivants :
- **TF** : Pour voir les transformations des marqueurs
- **MarkerArray** : Topic `/visualization_markers`
- **PoseArray** : Topic `/poses`
- **Image** : Topic `/image_result` (si publish_topic_image_result=True)

## 📡 Topics ROS2

### Topics souscrits

| Topic | Type | Description |
|-------|------|-------------|
| `/camera/image_raw` | `sensor_msgs/Image` | Image brute de la caméra (configurable) |
| `/camera/camera_info` | `sensor_msgs/CameraInfo` | Paramètres intrinsèques de la caméra |

### Topics publiés

| Topic | Type | Description |
|-------|------|-------------|
| `/image_result` | `sensor_msgs/Image` | Image avec marqueurs détectés dessinés |
| `/poses` | `geometry_msgs/PoseArray` | Poses de tous les marqueurs détectés |
| `/visualization_markers` | `visualization_msgs/MarkerArray` | Marqueurs pour RViz |
| `/fiducial_markers` | `ros2_markertracker_interfaces/FiducialMarkerArray` | Messages personnalisés avec détails des marqueurs |

### Transformations TF2

Le nœud publie une transformation TF2 pour chaque marqueur détecté :
- **parent_frame** : `camera_frame_id` (paramètre)
- **child_frame** : `marker` (nom fixe, peut être étendu pour multi-marqueurs)

## 🔧 Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `input_image_topic` | string | `/camera/image_raw` | Topic d'entrée de l'image |
| `camera_info_topic` | string | `/camera_info` | Topic des infos intrinsèques caméra |
| `marker_length` | double | `10.0` | Taille du marqueur ArUco en cm |
| `camera_frame_id` | string | `camera` | ID du repère de la caméra |
| `aruco_dictionary_id` | string | `DICT_4X4_50` | Dictionnaire ArUco à utiliser |
| `publish_topic_image_result` | bool | `False` | Publier l'image avec marqueurs dessinés |

### Exemple de configuration dans launch file

```python
Node(
    package='ros2_markertracker',
    executable='markertracker_node',
    output="screen",
    parameters=[{
        "input_image_topic": "/camera/color/image_raw",
        "camera_info_topic": "/camera/color/camera_info",
        "marker_length": 9.6,  # en cm
        "aruco_dictionary_id": "DICT_4X4_250",
        "camera_frame_id": "camera_color_optical_frame",
        "publish_topic_image_result": True
    }]
)
```

## 📝 Exemples

### Exemple 1 : Détection simple avec RealSense D405

```bash
# Terminal 1 : Lancer la caméra RealSense
ros2 launch realsense2_camera rs_launch.py

# Terminal 2 : Lancer le détecteur de marqueurs
ros2 run ros2_markertracker markertracker_node --ros-args \
    -p input_image_topic:=/camera/color/image_raw \
    -p camera_info_topic:=/camera/color/camera_info \
    -p marker_length:=9.6 \
    -p camera_frame_id:=camera_color_optical_frame \
    -p aruco_dictionary_id:=DICT_4X4_250

# Terminal 3 : Visualiser dans RViz
rviz2
```

### Exemple 2 : Détection avec Azure Kinect

```bash
# Terminal 1 : Lancer Azure Kinect
ros2 launch azure_kinect_ros_driver driver.launch.py

# Terminal 2 : Lancer le détecteur
ros2 run ros2_markertracker markertracker_node --ros-args \
    -p input_image_topic:=/rgb/image_raw \
    -p camera_info_topic:=/rgb/camera_info \
    -p marker_length:=10.0 \
    -p camera_frame_id:=rgb_camera_link \
    -p aruco_dictionary_id:=DICT_4X4_50
```

### Exemple 3 : Écouter les transformations TF

```bash
# Afficher la transformation du marqueur
ros2 run tf2_ros tf2_echo camera_color_optical_frame marker
```

### Exemple 4 : Sauvegarder les poses détectées

```bash
# Enregistrer les poses dans un fichier bag
ros2 bag record /poses /fiducial_markers
```

## 🐛 Dépannage

### Problème : Aucun marqueur détecté

**Solutions** :
1. Vérifiez que le dictionnaire ArUco correspond à vos marqueurs imprimés
2. Assurez-vous que `marker_length` est correct (en cm)
3. Vérifiez l'éclairage (évitez les reflets et ombres fortes)
4. Vérifiez que le topic camera_info est publié : `ros2 topic echo /camera/camera_info`
5. Assurez-vous que les marqueurs sont suffisamment grands dans l'image

### Problème : Poses incorrectes ou instables

**Solutions** :
1. Calibrez correctement votre caméra (paramètres intrinsèques)
2. Vérifiez que `marker_length` est exact (mesurez avec précision)
3. Assurez-vous que le repère `camera_frame_id` est correct
4. Augmentez la qualité d'impression des marqueurs

### Problème : "No camera info" erreur

**Solutions** :
1. Vérifiez que votre driver de caméra publie sur `/camera_info`
2. Ajustez le paramètre `camera_info_topic` si nécessaire
3. Augmentez le timeout dans `wait_for_message` si votre caméra est lente à démarrer

### Problème : Performances faibles

**Solutions** :
1. Réduisez la résolution de l'image d'entrée
2. Définissez `publish_topic_image_result` à `False`
3. Ajustez la fréquence de traitement dans le code (paramètre `rate`)

### Problème : ImportError pour cv_bridge

```bash
sudo apt install ros-humble-cv-bridge ros-humble-vision-opencv
```

### Problème : Module 'transformations' not found

Le package inclut son propre module `transformations.py` pour la compatibilité ROS2 Humble. Assurez-vous que le package est correctement compilé.

## 📚 Ressources

- [Documentation OpenCV ArUco](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Génération de marqueurs ArUco](https://chev.me/arucogen/)
- [ROS2 TF2 Tutorials](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html)

## 🔗 Projets connexes

- [ROS2 Hand-Eye Calibration](https://github.com/giuschio/ros2_handeye_calibration)
- [camera_calibration package](../camera_calibration/README.md)

## 📄 Licence

MIT License - Alberto Naranjo

## 👥 Contributeurs

- Alberto Naranjo ([@Veilkrand](https://github.com/Veilkrand)) - Auteur original
- Lab-CORO - Modifications et adaptations pour ROS2 Humble
