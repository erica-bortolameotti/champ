import os
import launch_ros

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # CONFIGURAZIONE PERCORSI 
    pkg_name = 'aliengo_z1_description'
    pkg_share = FindPackageShare(pkg_name).find(pkg_name)
    
    gz_pkg_share = FindPackageShare(package="robot_gazebo").find("robot_gazebo")
    
    aliengo_share = os.path.join(get_package_prefix('aliengo_description'), 'share')
    z1_share = os.path.join(get_package_prefix('z1_description'), 'share')

    # 2. Uniscili in un'unica azione SetEnvironmentVariable
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            aliengo_share,    # Percorso Aliengo
            os.pathsep,       # :
            z1_share,         # Percorso Z1
            os.pathsep,       # :
            os.environ.get('GAZEBO_MODEL_PATH', '') 
        ]
    )

    # CONFIGURAZIONE VARIABILI 
    robot_name = LaunchConfiguration("robot_name")
    use_sim_time = LaunchConfiguration("use_sim_time")
    headless = LaunchConfiguration("headless")
    gazebo_world = LaunchConfiguration("world")
    
    world_init_x = LaunchConfiguration("world_init_x")
    world_init_y = LaunchConfiguration("world_init_y")
    world_init_z = LaunchConfiguration("world_init_z")
    paused = LaunchConfiguration("paused")
    gui = LaunchConfiguration("gui")
    

    # DICHIARAZIONE ARGOMENTI
    declare_robot_name = DeclareLaunchArgument("robot_name", default_value="aliengoZ1")
    declare_use_sim_time = DeclareLaunchArgument("use_sim_time", default_value="True")
    declare_headless = DeclareLaunchArgument("headless", default_value="False")        
    declare_gui = DeclareLaunchArgument("gui", default_value="True")
    declare_paused = DeclareLaunchArgument("paused", default_value="True")

    #dichiarazione world da caricare
    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(gz_pkg_share, 'worlds', 'cubo.world'),
        description='Percorso file mondo per Gazebo Classic'
    )

    declare_world_init_x = DeclareLaunchArgument("world_init_x", default_value="0.0")
    declare_world_init_y = DeclareLaunchArgument("world_init_y", default_value="0.0")
    declare_world_init_z = DeclareLaunchArgument("world_init_z", default_value="0.6") #questo valore su z me lo fa stare appeso

    #declare_world_init_heading = DeclareLaunchArgument(
    #    "world_init_heading", default_value="0.6"
    #)

    # PERCORSO FILE XACRO
    default_model_path = os.path.join(pkg_share, 'xacro','robot.xacro')

    declare_description_path = DeclareLaunchArgument(
        name="description_path", 
        default_value=default_model_path
    )

    #aggiunta 
    ros_control_file = LaunchConfiguration("ros_control_file")

    #disabilita la ricerca in modelli di gazebo
    disable_fuel = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')
  
    #se ci sono variabili con la virgola le porta in punto
    set_env_lc = SetEnvironmentVariable('LC_NUMERIC', 'en_US.UTF-8')

    # ROBOT STATE PUBLISHER
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": Command(["xacro ", LaunchConfiguration("description_path")]),
            "use_sim_time": True
        }]
    )

    robot_description = {"robot_description": Command(["xacro ", LaunchConfiguration("description_path")])}

    gazebo_world = LaunchConfiguration('world')

    config_pkg_share = launch_ros.substitutions.FindPackageShare(
        package="champ_config"
    ).find("champ_config")
    
    links_config = os.path.join(config_pkg_share, "config/links/links.yaml")
    gait_config = os.path.join(config_pkg_share, "config/gait/gait.yaml")

    gazebo_config = os.path.join(launch_ros.substitutions.FindPackageShare(
    package="robot_gazebo"
    ).find("robot_gazebo"), "config/gazebo.yaml")
   
    launch_dir = os.path.join(gz_pkg_share, "launch")
    


    # GAZEBO SERVER
    start_gazebo_server_cmd = ExecuteProcess(
        cmd=[
            "gzserver",
            "-u", # <--- AGGIUNGI QUESTO PER IL PAUSE
            "-s", 
            "libgazebo_ros_init.so",
            "-s", 
            "libgazebo_ros_factory.so",
            gazebo_world,
            "--verbose", # Ci serve per vedere l'errore reale
            "--ros-args"
        ],
        output="screen",
    )

    # GAZEBO CLIENT
    start_gazebo_client_cmd = ExecuteProcess(
        condition=IfCondition(PythonExpression([" not ", headless])),
        cmd=["gzclient"],
        output="screen",
    )

    # SPAWN
    start_gazebo_spawner_cmd = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        output="screen",
        arguments=[
            "-entity",
            robot_name,
            "-topic",
            "/robot_description",
            "-robot_namespace",
            "",
            "-x",
            world_init_x,
            "-y",
            world_init_y,
            "-z",
            world_init_z,
            "-R",
            "0",
            "-P",
            "0",
            "-Y",
            "0",
        #    world_init_heading,
        ],
    )

    #CONTROLLI
    # robot_controllers = os.path.join(
    #    get_package_share_directory('aliengo_z1_description'),
    #    'config',
    #    'robot_control.yaml'
    #)
    
    
    declare_ros_control_file = DeclareLaunchArgument(
        "ros_control_file",
        default_value=os.path.join(pkg_share, "config/ros_control.yaml"),
    )

    #declare_ros_control_file = DeclareLaunchArgument(
    #    "ros_control_file",
    #    default_value=os.path.join(aliengo_share, "config/ros_control.yaml"),
    #)
    
    contact_sensor = Node(
        package="robot_gazebo",
        executable="contact_sensor",
        output="screen",
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")},links_config],
        # prefix=['xterm -e gdb -ex run --args'],
    )

    load_joint_state_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_states_controller'],
        output='screen',
    )

    load_joint_trajectory_position_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_group_position_controller'],
        output='screen'
    )
    load_joint_trajectory_effort_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_group_effort_controller'],
        output='screen'
    )

    return LaunchDescription(
        [
            set_gazebo_model_path,
            set_env_lc,
            disable_fuel,
            declare_robot_name,
            declare_use_sim_time,
            declare_gui,
            declare_paused,
            declare_headless,

            declare_ros_control_file,
            
            declare_world_cmd,
            declare_description_path,
            declare_world_init_x,
            declare_world_init_y,
            declare_world_init_z,
            #declare_world_init_heading,
            robot_state_publisher_node,
            start_gazebo_server_cmd,
            start_gazebo_client_cmd,
            start_gazebo_spawner_cmd,
            load_joint_state_controller,
            load_joint_trajectory_effort_controller,
            contact_sensor
        ]
    )
