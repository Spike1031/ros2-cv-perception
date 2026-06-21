from setuptools import find_packages, setup

package_name = 'cv_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='spike',
    maintainer_email='spike@todo.todo',
    description='ROS2 computer vision perception package',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hello_node = cv_perception.hello_node:main',
            'image_publisher_node = cv_perception.image_publisher_node:main',
            'yolo_detector_node = cv_perception.yolo_detector_node:main',
            'traffic_perception_node = cv_perception.traffic_perception_node:main',
        ],
    },
)
