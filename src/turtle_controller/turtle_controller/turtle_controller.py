import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_interfaces.msg import Turtle, TurtleArray
from turtle_interfaces.srv import CatchTurtle
from turtlesim.srv import Kill
import math

class TurtleController(Node):
    def __init__(self):
        super().__init__("turtle_controller")
        self.turtles = []
        self.master_turtle_pose = Pose()
        self.turtle_catch_pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)

        self.create_subscription(Pose, "/turtle1/pose", self.callback_master_turtle, 10)
        self.turtle_subscriber = self.create_subscription(TurtleArray, "/turtle_array", self.callback_spawned_turtle, 10)

        self.kill_client = self.create_client(Kill, "/kill")
        self.remove_turtle_client = self.create_client(CatchTurtle, "/catch_turtle")

        self.declare_parameter("linear_gain", 2.5)
        self.declare_parameter("angular_gain", 8.0)

        self.create_timer(0.1, self.controller)
        self.get_logger().info("Turtle Controller Started")

    def callback_master_turtle(self, master_pose: Pose):
        self.master_turtle_pose = master_pose

    def callback_spawned_turtle(self, alive_turtles: TurtleArray):
        self.turtles = alive_turtles.turtle_array

    def controller(self):
        while not self.kill_client.wait_for_service(1.0):
            self.get_logger().warn("Kill Service is not Active")
        
        if self.turtles:
            x1 = self.master_turtle_pose.x
            y1 = self.master_turtle_pose.y

            # Find the nearest turtle in the list
            nearest_turtle = None
            min_distance = float('inf')

            for turtle in self.turtles:
                dist = math.sqrt((turtle.x - x1)**2 + (turtle.y - y1)**2)
                if dist < min_distance:
                    min_distance = dist
                    nearest_turtle = turtle

            if nearest_turtle is not None:
                x2 = nearest_turtle.x
                y2 = nearest_turtle.y

                opp = (y2 - y1)
                adj = (x2 - x1)
                target_angle = math.atan2(opp, adj)
                
                angle_error = target_angle - self.master_turtle_pose.theta

                if angle_error > math.pi:
                    angle_error = angle_error - (2 * math.pi)
                elif angle_error < -math.pi:
                    angle_error = angle_error + (2 * math.pi)
                
                linear_gain = self.get_parameter("linear_gain").value
                angular_gain = self.get_parameter("angular_gain").value

                send_goal = Twist()
                send_goal.linear.x = linear_gain * min_distance
                send_goal.angular.z = angular_gain * angle_error

                if min_distance < 0.5:
                    send_goal.linear.x = 0.0
                    send_goal.angular.z = 0.0
                    turtle_remove_req = CatchTurtle.Request()
                    turtle_remove_req.name = nearest_turtle.name
                    future_remove = self.remove_turtle_client.call_async(turtle_remove_req)
                    # Pass the specific turtle's name to the callback to avoid race conditions
                    future_remove.add_done_callback(
                        lambda future, name=nearest_turtle.name: self.callback_remove(future, name)
                    )
                    
                self.turtle_catch_pub.publish(send_goal)

    def callback_remove(self, future, name):
        response = future.result()
        if response.success:
            turtle_kill_req = Kill.Request()
            turtle_kill_req.name = name
            future_kill = self.kill_client.call_async(turtle_kill_req)
            future_kill.add_done_callback(
                lambda future, n=name: self.callback_kill(future, n)
            )
            self.get_logger().info(f"Turtle '{name}' got Removed")

    def callback_kill(self, future, name):
        response = future.result()
        self.get_logger().info(f"Turtle '{name}' got Killed")
def main():
    rclpy.init()
    turlte_controller = TurtleController()
    rclpy.spin(turlte_controller)
    rclpy.shutdown()
