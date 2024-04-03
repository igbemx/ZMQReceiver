import zmq
import json
from PyQt5.QtCore import QThread

class ZMQReceiver(QThread):
    def __init__(self, main_json_identifiers, url, debug=False, parent=None):
        super().__init__(parent)
        self.main_json_identifiers = main_json_identifiers
        self.url = url
        self.running = False
        self.debug = debug

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.url)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.parsed_data = {}
        self.current_identifier = None
        self.current_json_data = []

    def parse_binary_message(self, binary_msg):
        if binary_msg in self.main_json_identifiers:
            return True, binary_msg  # This message is an identifier
        else:
            try:
                return False, json.loads(binary_msg.decode('utf-8'))
            except json.JSONDecodeError:
                return False, binary_msg  # Return the message as-is if not JSON

    def run(self):
        try:
            while self.running:
                try:
                    binary_message = self.socket.recv()
                    if self.debug:
                        print("New message! Binary message is: ", binary_message)

                    is_identifier, data = self.parse_binary_message(binary_message)

                    if is_identifier:
                        # Handle identifier message
                        if self.current_identifier is not None:
                            self.parsed_data[self.current_identifier.decode('utf-8')] = self.current_json_data
                        self.current_identifier = data
                        self.current_json_data = []
                    else:
                        # Handle value message
                        if self.current_identifier is not None:
                            self.current_json_data.append(data)
                        else:
                            if self.debug:
                                print("WARNING: Value message received without an identifier. Ignoring.")

                    if self.debug:
                        print("Final Parsed Data: ")
                        for key, value in self.parsed_data.items():
                            print(f"{key}: {value}")

                except Exception as e:
                    if self.debug:
                        print(f"Error occurred: {e}")
                    # TO-DO Implement automatic recovery logic here (e.g., reconnect)
                    # One can use try-except blocks or external methods to initiate reconnection

        except KeyboardInterrupt:
            print("Interrupted by the user, stopping...")
        finally:
            # Ensure last values are stored
            if self.current_identifier is not None:
                self.parsed_data[self.current_identifier.decode('utf-8')] = self.current_json_data
            self.socket.close()
            self.context.term()

            if self.debug:
                print(f"Final Parsed Data: {self.parsed_data}")

    def start_receiver(self):
        self.running = True
        self.start()

    def stop_receiver(self):
        self.running = False
        self.wait()

    def set_debug(self, debug_enabled):
        self.debug = debug_enabled

# Example usage:
# This part can be included in the main script where the module is used
# receiver = ZMQReceiver(
#     main_json_identifiers=[b'positionerDefinition', ...],
#     url="tcp://b-softimax-sophie-cc-0:55561",
#     debug=True
# )
# receiver.start_receiver()
