# Tool Box - ROS2 Humble Camera Calibration & ArUco Marker Tracking

Ce dépôt contient des outils pour la calibration de caméras et le suivi de marqueurs ArUco avec ROS2 Humble.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Packages inclus](#packages-inclus)
- [Compatibilité](#compatibilité)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Compilation](#compilation)
- [Dépannage](#dépannage)
- [Contribuer](#contribuer)

## 🎯 Vue d'ensemble

Ce projet fournit deux packages ROS2 principaux :

1. **ros2_markertracker** : Détection et suivi de marqueurs ArUco avec publication de transformations TF
2. **camera_calibration** : Calibration main-œil (hand-eye) pour caméras Azure Kinect et Intel RealSense

## 📦 Packages inclus

### ros2_markertracker

Package de détection de marqueurs ArUco qui :
- Détecte des marqueurs ArUco dans les images de caméra
- Calcule la pose 6DOF des marqueurs détectés
- Publie les transformations TF et les messages de pose
- Supporte différents dictionnaires ArUco
- Utilise les informations intrinsèques de la caméra depuis les topics camera_info

**Documentation détaillée** : [ros2_markertracker/README.md](ros2_markertracker/ros2_markertracker/README.md)

### camera_calibration

Package de calibration pour caméras montées sur robot (eye-on-hand) ou sur base fixe (eye-on-base) :
- Calibration Azure Kinect (eye-on-base avec correction de distorsion fish-eye)
- Calibration Intel RealSense D405 (eye-on-hand)
- Intégration avec le robot Doosan
- Utilise le package ros2_handeye_calibration

**Documentation détaillée** : [camera_calibration/README.md](camera_calibration/README.md)

### ros2_markertracker_interfaces

Package d'interfaces contenant les messages personnalisés :
- `FiducialMarker.msg` : Représente un marqueur fiduciel unique
- `FiducialMarkerArray.msg` : Tableau de marqueurs fiduciels

## ✅ Compatibilité

- **ROS2 Distribution** : Humble Hawksbill
- **OS** : Ubuntu 22.04 LTS (recommandé)
- **Python** : 3.10+
- **CMake** : 3.5+

## 📋 Prérequis

### Dépendances système

```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-opencv \
    python3-numpy \
    python3-transforms3d \
    ros-humble-cv-bridge \
    ros-humble-vision-opencv \
    ros-humble-tf-transformations
```

### Packages ROS2 requis

Les packages suivants doivent être installés dans votre workspace ROS2 :

#### Pour camera_calibration :
- [Azure Kinect ROS Driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver) (si utilisation d'Azure Kinect)
- [RealSense ROS](https://github.com/IntelRealSense/realsense-ros) (si utilisation de RealSense)
- [Doosan Robot](https://github.com/doosan-robotics/doosan-robot2) (si utilisation du robot Doosan)
- [ROS2 Hand-Eye Calibration](https://github.com/giuschio/ros2_handeye_calibration) **OBLIGATOIRE**

```bash
# Installation du package hand-eye calibration
cd ~/ros2_ws/src
git clone https://github.com/giuschio/ros2_handeye_calibration.git
cd ~/ros2_ws
colcon build --packages-select ros2_handeye_calibration
```

## 🔧 Installation

### 1. Cloner le dépôt

```bash
cd ~/ros2_ws/src
git clone https://github.com/Lab-CORO/tool_box.git
```

### 2. Installer les dépendances Python

```bash
cd ~/ros2_ws/src/tool_box
pip3 install -r requirements.txt
```

Si le fichier `requirements.txt` n'existe pas, installez manuellement :

```bash
pip3 install opencv-python opencv-contrib-python numpy transforms3d
```

## 🏗️ Compilation

### Compiler tous les packages

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash

# Compiler dans l'ordre correct (interfaces en premier)
colcon build --packages-select ros2_markertracker_interfaces
colcon build --packages-select ros2_markertracker
colcon build --packages-select camera_calibration

# Ou compiler tous les packages en une seule commande
colcon build --packages-select ros2_markertracker_interfaces ros2_markertracker camera_calibration
```

### Sourcer l'environnement

```bash
source ~/ros2_ws/install/setup.bash
```

**Important** : Ajoutez cette ligne à votre `~/.bashrc` pour sourcer automatiquement :

```bash
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

## 🚀 Utilisation rapide

### Lancer le détecteur de marqueurs ArUco

```bash
ros2 launch ros2_markertracker markertracker_raspicam_1280x720.launch.py
```

### Lancer la calibration Azure Kinect (eye-on-base)

```bash
ros2 launch camera_calibration kinect_eye_on_base_calibration.launch.py
```

### Lancer la calibration RealSense (eye-on-hand)

```bash
ros2 launch camera_calibration rs_eye_on_hand_calibrate.launch.py
```

Pour plus de détails sur l'utilisation, consultez les README des packages individuels.

## 🐛 Dépannage

### Erreur : "No module named 'cv2'"

```bash
pip3 install opencv-python opencv-contrib-python
```

### Erreur : "Package 'ros2_markertracker_interfaces' not found"

Assurez-vous de compiler d'abord le package d'interfaces :

```bash
colcon build --packages-select ros2_markertracker_interfaces
source install/setup.bash
```

### Erreur : "wait_for_message" ImportError

Le package `ros2_markertracker` inclut sa propre implémentation de `wait_for_message` compatible avec ROS2 Humble. Assurez-vous que le package est correctement compilé.

### Problèmes de compilation du package camera_calibration

Si vous rencontrez des erreurs de type "module not found", vérifiez que la structure du package est correcte :

```bash
ls camera_calibration/camera_calibration/
# Devrait afficher : __init__.py, kinect_tf_computation_node.py, pose_array_to_tf.py, rs_tf_computation_node.py
```

### Image Kinect déformée (fish-eye)

L'Azure Kinect utilise un objectif fish-eye qui nécessite une rectification. Utilisez l'une des méthodes suivantes :

**Méthode 1** : Utiliser le node image_proc

```bash
ros2 run image_proc rectify_node --ros-args \
    -r __node:=rectify_rgb \
    -r image:=rgb/image_raw \
    -r image_rect:=rgb/image_rect_raw \
    -r camera_info:=/rgb/camera_info
```

**Méthode 2** : Le launch file `kinect_eye_on_base_calibration.launch.py` inclut déjà la rectification.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

- **camera_calibration** : Apache-2.0
- **ros2_markertracker** : MIT
- **ros2_markertracker_interfaces** : TODO (à définir)

## 👥 Mainteneurs

- **camera_calibration** : will (will@todo.todo)
- **ros2_markertracker** : Alberto Naranjo (155007+Veilkrand@users.noreply.github.com)

## 📚 Ressources supplémentaires

- [ROS2 Humble Documentation](https://docs.ros.org/en/humble/)
- [OpenCV ArUco Documentation](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Hand-Eye Calibration Theory](https://en.wikipedia.org/wiki/Hand_eye_calibration_problem)
