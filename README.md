

# 🐢 Turtlesim Catch the Turtle

A dynamic and interactive ROS 2 (Robot Operating System 2) application where a master turtle autonomously hunts down and "catches" target turtles spawning at random locations in the `turtlesim` simulator. 

This project serves as an educational and practical implementation of core ROS 2 concepts, demonstrating how multiple nodes collaborate seamlessly using Publishers, Subscribers, Services, Clients, and Custom ROS 2 Interfaces.

---

## 🎬 Demo
https://github.com/user-attachments/assets/e7bd1c3b-dd37-4cae-a284-6378a4fe84f3

---

## 🚀 Description

In this application, target turtles are spawned at random positions with random orientations within the 2D `turtlesim` window. A master turtle (`turtle1`) is controlled by a closed-loop proportional controller that calculates the distance and heading error to the nearest target turtle. Once the master turtle gets within a close proximity (less than 0.5 meters) of a target turtle:
1. It requests the **Spawner Node** to remove the target from its active tracking array via a custom service.
2. It requests the **Turtlesim Simulator** to visually kill (remove) the turtle from the screen.
3. The master turtle then immediately begins tracking the next spawned target turtle.

This project solves the problem of understanding ROS 2 node communications by providing a clear, interactive, and modular architecture.

---

## 🛠️ Tech Stack

*   **Framework:** [ROS 2 (Robot Operating System 2)](https://docs.ros.org/) (Humble Hawksbill / Iron Irwini / Jazzy Jalisco)
*   **Languages:** 
    *   **Python:** Used for node logic, controllers, and launch configurations.
    *   **C++ / CMake:** Used for building and compiling the custom ROS 2 messages and services.
*   **Simulation Engine:** `turtlesim`
*   **Build Tool:** `colcon`

---

## 📦 Installation

To set up and run this project locally, ensure you have ROS 2 installed on your system. Follow these step-by-step commands:

### 1. Clone or Navigate to the Workspace
Clone this repository into your ROS 2 workspace's `src` directory (e.g., `~/ros2_ws/src`), or navigate to the project root:
```bash
# Example if placing in a ROS 2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/vishaladem101/turtlesim_catch_the_turtle.git turtlesim_catch_the_turtle
cd ~/ros2_ws
```

### 2. Install Dependencies
Make sure you have `turtlesim` and the build dependencies installed:
```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-turtlesim -y
```

### 3. Build the Workspace
Build the custom interfaces and nodes using `colcon`:
```bash
# In the root of your workspace (e.g., ~/ros2_ws)
colcon build --packages-select turtle_interfaces turtle_spawner turtle_controller turtle_bringup
```
*Alternatively, build all packages in the workspace:*
```bash
colcon build
```

### 4. Source the Workspace
Source the installation setup files so ROS 2 can find the packages:
```bash
source install/setup.bash
```

---

## 🎮 Usage

You can launch the complete application with a single command using the provided launch file. This starts the `turtlesim` simulation node, the spawning manager, and the proportional controller:

```bash
ros2 launch turtle_bringup turtle_game.launch.py
```

### How it Works Under the Hood
1. **`turtle_bringup`**: Launches `turtlesim_node`, `turtle_spawner`, and `turtle_controller`.
2. **`turtle_interfaces`**: Compiles custom interface types:
    *   `Turtle.msg`: Contains `float64 x`, `float64 y`, `float64 theta`, and `string name`.
    *   `TurtleArray.msg`: Represents a list of currently active target turtles.
    *   `CatchTurtle.srv`: Service definition used to catch/remove a turtle by name.
3. **`turtle_spawner`**: Periodically spawns a new target turtle every second at a random coordinate, publishes the updated list to `/turtle_array`, and hosts the `/catch_turtle` service.
4. **`turtle_controller`**: Subscribes to the master turtle's pose and `/turtle_array`, calculates proportional velocity commands, publishes them to `/turtle1/cmd_vel`, and calls the catch and kill services once the target is reached.

---

## 📄 License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software for personal, educational, or commercial purposes. See the [LICENSE](LICENSE) file (if available) or standard MIT terms for details.
