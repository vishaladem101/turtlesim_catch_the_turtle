import rclpy
from rclpy.node import Node
from turtle_interfaces.msg import Turtle, TurtleArray
from turtle_interfaces.srv import CatchTurtle
from turtlesim.srv import Spawn

import random
import math

class TurtleSpawner(Node):
    def __init__(self):
        super().__init__("turtle_spawner")
        self.alive_turtles = TurtleArray()
        self.turtle_counter = 2
        self.spawn_client = self.create_client(Spawn,"/spawn")
        self.turtle_publisher =  self.create_publisher(TurtleArray,"/turtle_array",10)

        self.declare_parameter("spawn_period", 0.3)
        spawn_period = self.get_parameter("spawn_period").value

        self.create_service(CatchTurtle, "/catch_turtle", self.callback_catch_turtle)
        self.spawner_timer = self.create_timer(spawn_period, self.spawner)
        self.add_on_set_parameters_callback(self.callback_parameter_change)
        self.get_logger().info("Spawner has started")

    def callback_parameter_change(self, params):
        from rcl_interfaces.msg import SetParametersResult
        for param in params:
            if param.name == "spawn_period":
                new_period = param.value
                self.get_logger().info(f"Dynamically changing spawn period to: {new_period} seconds")
                # Destroy old timer and recreate it with the new period
                self.spawner_timer.destroy()
                self.spawner_timer = self.create_timer(new_period, self.spawner)
        return SetParametersResult(successful=True)

    def spawner(self):
        while(not self.spawn_client.wait_for_service(1.0)):
            self.get_logger().warn("Service is not Active")
        turtle = Turtle()
        x = turtle.x = round(random.uniform(1, 10), 2)
        y = turtle.y =round(random.uniform(1,10), 2)
        theta = turtle.theta = round(random.uniform(-math.pi, math.pi),2)
        name = turtle.name = f"turtle{self.turtle_counter}"
        self.alive_turtles.turtle_array.append(turtle)
        self.turtle_publisher.publish(self.alive_turtles)
        self.spawn_turtle(x, y, theta, name)
        self.turtle_counter += 1

    def spawn_turtle(self, x, y, theta, name):
        spawn = Spawn.Request()
        spawn.x = x
        spawn.y = y
        spawn.name = name
        spawn.theta = theta
        future = self.spawn_client.call_async(spawn)
        future.add_done_callback(self.callback_response)

    def callback_response(self, future):
        response = future.result()
        if(response.name != ""):
            self.get_logger().info(f"Turtle Spawned: {self.turtle_counter}")

    def callback_catch_turtle(self, request: CatchTurtle.Request, response: CatchTurtle.Response):
        for turtle in self.alive_turtles.turtle_array:
            if(turtle.name == request.name):
                self.alive_turtles.turtle_array.remove(turtle)
                response.success = True
                break
            else:
                response.success = False
        return response

def main():
    rclpy.init()
    turtle_spawner= TurtleSpawner()
    rclpy.spin(turtle_spawner)
    rclpy.shutdown()

    