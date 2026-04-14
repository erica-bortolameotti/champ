import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare

from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    
    aliengo_z1_description = FindPackageShare('aliengo_z1_description')
    default_rviz_config_path = PathJoinSubstitution([aliengo_z1_description, 'config', 'config.rviz'])

    # Show joint state publisher GUI for joints = pubblica" la posizione 3D di ogni pezzo del robot (le trasformate TF). 
    # Senza questo, RViz non saprebbe dove si trova la zampa rispetto al corpo
    gui_arg = DeclareLaunchArgument(name='gui', default_value='true', choices=['true', 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    
    # RVIZ CONFIG FILE PATH
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                    description='Absolute path to rviz config file')
    
    rviz_launch_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Open RViz'
    )

    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='True',
        description='Flag to enable use_sim_time'
    )
    

    # URDF MODEL PATH
    model_arg = DeclareLaunchArgument(
        'model', default_value='robot.xacro',
        description='Name of the xacro description to load'
    )

    # Define the path to your URDF or Xacro file
    xacro_file_path = PathJoinSubstitution([
        aliengo_z1_description,
        "xacro",
        LaunchConfiguration('model')
    ])

    
    # LAUNCH RVIZ2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([aliengo_z1_description, 'rviz', LaunchConfiguration('rvizconfig')])],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': Command(['xacro', ' ', xacro_file_path, ' ', 'DEBUG:=false']),
             'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ]
    )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(rviz_launch_arg)
    launchDescriptionObject.add_action(sim_time_arg)
    launchDescriptionObject.add_action(gui_arg)
    launchDescriptionObject.add_action(rviz_arg)
    launchDescriptionObject.add_action(model_arg)
    launchDescriptionObject.add_action(rviz_node)
    launchDescriptionObject.add_action(robot_state_publisher_node)
    launchDescriptionObject.add_action(joint_state_publisher_gui_node)
    

    return launchDescriptionObject