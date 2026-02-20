import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from example_interfaces.action import Fibonacci  # Remplace par ton type d'action


class MonNoeudAction(Node):

    def __init__(self):
        super().__init__('mon_noeud_action')

        self._action_server = ActionServer(
            self,
            Fibonacci,               # Type d'action
            'fibonacci',             # Nom de l'action
            self.execute_callback    # Callback d'exécution
        )

        self.get_logger().info("Serveur d'action démarré !")

    async def execute_callback(self, goal_handle):
        self.get_logger().info(f"Nouveau goal reçu : {goal_handle.request}")

        feedback_msg = Fibonacci.Feedback()
        result = Fibonacci.Result()

        # --- Logique principale ici ---
        sequence = [0, 1]
        for i in range(1, goal_handle.request.order):
            sequence.append(sequence[-1] + sequence[-2])

            # Envoyer du feedback au client
            feedback_msg.partial_sequence = sequence
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"Feedback : {sequence}")

            # Vérifier si le goal a été annulé
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("Goal annulé.")
                return result

        # Marquer le goal comme réussi
        goal_handle.succeed()
        result.sequence = sequence
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MonNoeudAction()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

# Quelques points importants :

# **Structure d'une action ROS2** — une action comporte trois parties : le *goal* (ce qu'on demande), le *feedback* (progression en cours d'exécution), et le *result* (résultat final).

# **Le fichier `.action`** — si tu crées ton propre type d'action, il faut définir un fichier `MonAction.action` dans un package avec les trois sections séparées par `---` :
# ```
# # Goal
# int32 order
# ---
# # Result
# int32[] sequence
# ---
# # Feedback
# int32[] partial_sequence