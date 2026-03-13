import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'camera_calibration'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*launch.[pxy][yma]*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='will',
    maintainer_email='will@todo.todo',
    description='Package to house camera calibration utilities',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_array_to_tf = camera_calibration.pose_array_to_tf:main',
            'rs_tf_computation_node = camera_calibration.rs_tf_computation_node:main',
        ],
    },
)
