# Camera Calibration Package for ROS2 Humble

Package de calibration main-œil (hand-eye calibration) pour caméras Azure Kinect et Intel RealSense avec le robot Doosan.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Concepts théoriques](#concepts-théoriques)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Workflows de calibration](#workflows-de-calibration)
- [Résolution de problèmes](#résolution-de-problèmes)
- [Conseils pour améliorer la précision](#conseils-pour-améliorer-la-précision)

## 🎯 Vue d'ensemble

Ce package fournit des outils pour calibrer la transformation entre :
- **Eye-on-base** : Caméra fixée sur une base statique (ex: Azure Kinect)
- **Eye-on-hand** : Caméra montée sur l'effecteur du robot (ex: RealSense D405)

La calibration permet au robot de connaître précisément la position de la caméra par rapport à sa base ou à son effecteur, essentiel pour les tâches de vision par ordinateur et manipulation robotique.

## ✨ Fonctionnalités

- ✅ Calibration eye-on-base pour Azure Kinect
- ✅ Calibration eye-on-hand pour Intel RealSense D405
- ✅ Correction automatique de distorsion fish-eye pour Azure Kinect
- ✅ Intégration avec le robot Doosan
- ✅ Utilisation de marqueurs ArUco pour la détection
- ✅ Interface de calibration interactive
- ✅ Support du mode collaboratif du robot Doosan
- ✅ Visualisation temps réel dans RViz
- ✅ Compatible ROS2 Humble

## 📋 Prérequis

### Packages ROS2 requis

Avant d'utiliser ce package, vous devez installer les packages suivants :

#### 1. Azure Kinect ROS Driver (pour calibration Kinect)

```bash
cd ~/ros2_ws/src
git clone https://github.com/microsoft/Azure_Kinect_ROS_Driver.git
cd ~/ros2_ws
colcon build --packages-select azure_kinect_ros_driver
```

#### 2. RealSense ROS (pour calibration RealSense)

```bash
sudo apt install ros-humble-realsense2-camera ros-humble-realsense2-description
```

Ou depuis les sources :

```bash
cd ~/ros2_ws/src
git clone https://github.com/IntelRealSense/realsense-ros.git -b ros2-development
cd ~/ros2_ws
colcon build --packages-select realsense2_camera realsense2_description
```

#### 3. Doosan Robot ROS2 (pour intégration robot)

```bash
cd ~/ros2_ws/src
git clone https://github.com/doosan-robotics/doosan-robot2.git
cd ~/ros2_ws
colcon build --packages-select dsr_bringup2 dsr_description2 dsr_msgs2
```

#### 4. ROS2 Hand-Eye Calibration (OBLIGATOIRE)

```bash
cd ~/ros2_ws/src
git clone https://github.com/giuschio/ros2_handeye_calibration.git
cd ~/ros2_ws
colcon build --packages-select hand_eye_calibration
```

#### 5. Image Proc (pour rectification d'image)

```bash
sudo apt install ros-humble-image-proc
```

#### 6. ROS2 MarkerTracker (inclus dans ce dépôt)

Ce package est déjà inclus dans le dépôt `tool_box`. Ne clonez PAS le dépôt original.

### Dépendances système

```bash
sudo apt install -y \
    python3-transforms3d \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    ros-humble-rqt
```

## 🔧 Installation

### 1. Cloner le dépôt (si pas déjà fait)

```bash
cd ~/ros2_ws/src
git clone https://github.com/Lab-CORO/tool_box.git
```

### 2. Installer les dépendances

Installez tous les packages prérequis listés dans la section [Prérequis](#prérequis).

### 3. Compiler le package

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash

# Compiler dans l'ordre
colcon build --packages-select ros2_markertracker_interfaces
colcon build --packages-select ros2_markertracker
colcon build --packages-select camera_calibration

source install/setup.bash
```

## 📚 Concepts théoriques

### Calibration Hand-Eye

La calibration main-œil résout l'équation mathématique **AX = XB** où :
- **A** : Transformation entre deux poses du robot
- **B** : Transformation entre deux observations du marqueur
- **X** : Transformation inconnue à calculer (caméra ↔ robot)

#### Eye-on-Base
La caméra est fixe dans l'environnement. On calcule la transformation entre la base du robot et la caméra.

```
base_link → camera_link
```

#### Eye-on-Hand
La caméra est montée sur l'effecteur du robot. On calcule la transformation entre l'effecteur et la caméra.

```
end_effector → camera_link
```

### Workflow général

1. Placer un marqueur ArUco visible par la caméra
2. Déplacer le robot dans différentes poses
3. Pour chaque pose, capturer la transformation robot et la pose du marqueur
4. L'algorithme calcule la transformation optimale caméra-robot
5. Sauvegarder la transformation pour utilisation future

## ⚙️ Configuration

### Marqueurs ArUco

Imprimez des marqueurs ArUco du dictionnaire **DICT_4X4_250**. Vous pouvez les générer sur :
- [ArUco Marker Generator](https://chev.me/arucogen/)

**Paramètres importants** :
- Taille : Environ 10 cm × 10 cm (ajuster selon la distance caméra-marqueur)
- Mesurez précisément la taille du marqueur (bord noir à bord noir)
- Impression : Utilisez du papier de qualité, évitez les déformations
- Fixation : Montez sur une surface plane et rigide

### Configuration du robot Doosan

Pour utiliser le robot en mode manuel durant la calibration :

```bash
# Lancer RQT
rqt
```

Dans RQT :
1. Plugins → Services → Service caller
2. Sélectionner `/dsr01/system/set_robot_mode`
3. Définir la valeur à `0` (mode manuel)
4. Appeler le service

Cela permet de déplacer manuellement le robot pendant la calibration.

## 🚀 Utilisation

### Calibration Azure Kinect (Eye-on-Base)

Le fichier launch démarre tous les composants nécessaires :
- Driver Azure Kinect
- Node de rectification d'image (correction fish-eye)
- Détecteur de marqueurs ArUco
- Robot Doosan
- Interface de calibration

#### 1. Lancer la calibration

```bash
ros2 launch camera_calibration kinect_eye_on_base_calibration.launch.py
```

#### 2. Configurer le robot en mode manuel

```bash
rqt
# Puis suivez les instructions dans "Configuration du robot Doosan"
```

#### 3. Positionner le marqueur ArUco

Placez le marqueur ArUco bien visible devant la caméra Azure Kinect, sur une surface plane.

#### 4. Capturer les poses

Déplacez le robot dans différentes positions. Pour chaque position, attendez que la détection du marqueur soit stable dans RViz, puis capturez :

```bash
ros2 service call /hand_eye_calibration/capture_point std_srvs/srv/Trigger {}
```

**Recommandation** : Capturez au moins **15-20 poses** pour une bonne précision.

#### 5. Résultat

Quand suffisamment de poses sont capturées, le terminal affichera la transformation calculée :

```
Current estimate: tx, ty, tz, qx, qy, qz, qw: [0.2725, 0.0811, 0.9726, 0.4272, 0.0920, 0.8986, 0.0397]
as euler: translation: 0.2725, 0.0811, 0.9726   rpy: 0.3119, -0.8640, 2.9086
```

Copiez ces valeurs pour configurer votre broadcaster TF statique.

### Calibration RealSense D405 (Eye-on-Hand)

#### 1. Lancer la calibration

```bash
ros2 launch camera_calibration rs_eye_on_hand_calibrate.launch.py
```

#### 2. Positionner le marqueur ArUco

Placez le marqueur ArUco sur une surface fixe. La caméra RealSense (montée sur le robot) doit pouvoir le voir.

#### 3. Configurer le robot en mode manuel

```bash
rqt
# Puis suivez les instructions dans "Configuration du robot Doosan"
```

#### 4. Capturer les poses

Déplacez le robot (et donc la caméra) dans différentes positions en gardant le marqueur visible. Pour chaque position :

```bash
ros2 service call /hand_eye_calibration/capture_point std_srvs/srv/Trigger {}
```

**Recommandation** : Capturez au moins **15-20 poses**.

#### 5. Résultat

La transformation entre l'effecteur du robot et la caméra sera affichée dans le terminal.

## 🛠️ Workflows de calibration

### Workflow détaillé Eye-on-Base (Azure Kinect)

```bash
# Terminal 1 : Lancer la calibration complète
ros2 launch camera_calibration kinect_eye_on_base_calibration.launch.py

# Terminal 2 : Configurer le robot en mode manuel
rqt
# Plugins → Services → Service caller → /dsr01/system/set_robot_mode → value: 0

# Terminal 3 : Visualiser dans RViz (optionnel mais recommandé)
rviz2

# Terminal 4 : Capturer les poses (répéter 15-20 fois)
ros2 service call /hand_eye_calibration/capture_point std_srvs/srv/Trigger {}
```

### Workflow détaillé Eye-on-Hand (RealSense)

```bash
# Terminal 1 : Lancer la calibration
ros2 launch camera_calibration rs_eye_on_hand_calibrate.launch.py

# Terminal 2 : Mode manuel robot
rqt

# Terminal 3 : Capturer (répéter 15-20 fois)
ros2 service call /hand_eye_calibration/capture_point std_srvs/srv/Trigger {}
```

### Utilisation de la transformation après calibration

Une fois la calibration terminée, utilisez les valeurs obtenues dans un broadcaster TF statique :

```xml
<node pkg="tf2_ros" exec="static_transform_publisher"
      args="tx ty tz qx qy qz qw parent_frame child_frame" />
```

Exemple pour Azure Kinect :

```bash
ros2 run tf2_ros static_transform_publisher \
    0.2725 0.0811 0.9726 0.4272 0.0920 0.8986 0.0397 \
    base_link rgb_camera_link
```

## 🐛 Résolution de problèmes

### Problème : Image Kinect déformée (fish-eye)

**Solution** : L'Azure Kinect utilise un objectif fish-eye. Le launch file inclut automatiquement un nœud de rectification. Si vous lancez les composants séparément, ajoutez :

```bash
ros2 run image_proc rectify_node --ros-args \
    -r __node:=rectify_rgb \
    -r image:=rgb/image_raw \
    -r image_rect:=rgb/image_rect_raw \
    -r camera_info:=/rgb/camera_info
```

### Problème : Marqueur ArUco non détecté

**Solutions** :
1. Vérifiez l'éclairage (évitez reflets et ombres)
2. Assurez-vous que le dictionnaire ArUco correspond (DICT_4X4_250)
3. Vérifiez que `marker_length` dans le launch file correspond à la vraie taille (en cm)
4. Rapprochez le marqueur de la caméra

### Problème : TF entre marker et caméra instable

**Solutions** :
1. Améliorez l'éclairage
2. Augmentez la taille du marqueur
3. Utilisez un marqueur avec meilleure qualité d'impression
4. Fixez le marqueur sur une surface parfaitement plane
5. Attendez quelques secondes avant de capturer pour stabilisation

### Problème : Calibration imprécise

**Solutions** :
1. Capturez plus de poses (25-30 au lieu de 15)
2. Maximisez les rotations entre poses
3. Couvrez tout l'espace de travail
4. Vérifiez la précision de la taille du marqueur
5. Recalibrez les paramètres intrinsèques de la caméra si nécessaire

### Problème : "Package 'hand_eye_calibration' not found"

**Solution** : Installez le package hand-eye calibration :

```bash
cd ~/ros2_ws/src
git clone https://github.com/giuschio/ros2_handeye_calibration.git
cd ~/ros2_ws
colcon build --packages-select hand_eye_calibration
source install/setup.bash
```

### Problème : Erreur de compilation "module camera_calibration not found"

**Solution** : La structure du package a été corrigée. Assurez-vous que vous avez la dernière version :

```bash
cd ~/ros2_ws/src/tool_box
git pull
cd ~/ros2_ws
colcon build --packages-select camera_calibration
```

### Problème : Robot Doosan ne répond pas

**Solutions** :
1. Vérifiez l'adresse IP du robot dans le launch file (défaut: `192.168.137.100`)
2. Assurez-vous que le robot est connecté au réseau
3. Vérifiez que le bon modèle est spécifié (`m1013`, etc.)
4. Redémarrez le contrôleur du robot

## 💡 Conseils pour améliorer la précision

### Placement des poses

1. **Maximisez les rotations** : Variez l'orientation du robot entre chaque pose
2. **Minimisez les translations** : Gardez le robot relativement proche
3. **Distance au marqueur** : Maintenez une distance constante et raisonnable (30-60 cm)
4. **Poses redondantes** : Capturez plus de poses que le minimum (20-30 recommandé)

### Qualité du marqueur

1. Imprimez sur du papier épais ou carton
2. Montez sur une surface rigide (plaque métallique, bois)
3. Assurez-vous que le marqueur est parfaitement plat
4. Mesurez précisément la taille (avec pied à coulisse si possible)
5. Évitez les reflets (surface mate)

### Conditions environnementales

1. Éclairage uniforme et suffisant
2. Évitez la lumière directe du soleil
3. Pas de reflets sur le marqueur
4. Surface de travail stable (pas de vibrations)

### Calibration de la caméra

Si la précision n'est toujours pas satisfaisante, recalibrez les paramètres intrinsèques de votre caméra :

```bash
ros2 run camera_calibration cameracalibrator \
    --size 8x6 \
    --square 0.025 \
    image:=/camera/image_raw \
    camera:=/camera
```

Utilisez un damier (chessboard) pour la calibration intrinsèque.

### Vérification de la calibration

Pour vérifier la qualité de votre calibration :

1. **Test visuel dans RViz** :
   - Placez un objet à une position connue
   - Vérifiez que sa position TF correspond à la réalité

2. **Test avec pick-and-place** :
   - Détectez un objet avec la caméra
   - Demandez au robot de le saisir
   - La précision doit être < 5mm pour une bonne calibration

3. **Reproductibilité** :
   - Refaites la calibration plusieurs fois
   - Les valeurs doivent être similaires (variation < 1cm)

## 📄 Structure des fichiers

```
camera_calibration/
├── camera_calibration/           # Modules Python
│   ├── __init__.py
│   ├── kinect_tf_computation_node.py   # Node de calcul TF Kinect
│   ├── pose_array_to_tf.py            # Convertisseur PoseArray → TF
│   └── rs_tf_computation_node.py      # Node de calcul TF RealSense
├── config/                       # Fichiers de configuration
│   └── *.yaml
├── launch/                       # Fichiers launch
│   ├── kinect_eye_on_base_calibration.launch.py
│   └── rs_eye_on_hand_calibrate.launch.py
├── test/                         # Tests unitaires
├── package.xml                   # Métadonnées du package
├── setup.py                      # Configuration Python
├── setup.cfg                     # Configuration Python
└── README.md                     # Ce fichier
```

## 📚 Ressources

- [ROS2 Hand-Eye Calibration](https://github.com/giuschio/ros2_handeye_calibration) - Package de calibration utilisé
- [Hand-Eye Calibration Theory](https://en.wikipedia.org/wiki/Hand_eye_calibration_problem) - Théorie
- [Azure Kinect ROS Driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver) - Driver Kinect
- [RealSense ROS](https://github.com/IntelRealSense/realsense-ros) - Driver RealSense
- [Doosan Robotics ROS2](https://github.com/doosan-robotics/doosan-robot2) - Driver Doosan

## 📝 Licence

Apache-2.0

## 👥 Mainteneur

- will (will@todo.todo)
- Lab-CORO

## 🤝 Contribution

Pour contribuer, consultez le [README principal](../README.md#contribuer).
