from launch_ros.actions import Node
from launch import LaunchDescription

def generate_launch_description():

    turtlesim_package = Node(
        package="turtlesim",
        executable="turtlesim_node"
    )

    turtle_controller = Node(
        package="turtle_controller",
        executable="turtle_controller"
    )

    turtle_spawner = Node(
        package="turtle_spawner",
        executable="turtle_spawner"
    )

    return LaunchDescription([
        turtlesim_package,
        turtle_spawner,
        turtle_controller
    ])