import zmq
import json
from pprint import pprint
from datetime import datetime
from PyQt5.QtCore import QThread

class ZMQReceiver(QThread):
    def __init__(self, main_json_identifiers, url_receiv, url_request, timeout=500, debug=False, parent=None):
        super().__init__(parent)
        self.main_json_identifiers = main_json_identifiers
        self.url_receiv = url_receiv
        self.url_request = url_request
        self.running = False
        self.init_response = None
        self.init_response_dict = {}
        self.timeout = timeout
        self.debug = debug

        self.pix_ctrl_status =  None
        self.positioner_def = None
        self.detector_def = None
        self.oscilloscope_def = None
        self.zone_plate_def = None
        self.remote_file_system_nfo = None

        # Subscribing to the zmq stream from Pixelator
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.url_receiv)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        ## Set up ZMQ request socket
        self.REQsocket = self.context.socket(zmq.REQ)
        self.REQsocket.connect(self.url_request)
        self.REQsocket.setsockopt(zmq.LINGER, 0)

        self.parsed_data = {}
        self.parsed_data_dict = {}
        self.current_identifier = None
        self.current_json_data = []

        self.get_init_pixelator()

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

                    self.parsed_data_dict = self._convert_to_dict([self.parsed_data])[0]
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

    def clear_parsed_data(self):
        self.parsed_data = {}

    def zmq_request(self, command):
        """
        This function sends a command through the specified ZMQ request port
        and returns the response from the ZMQ server
        """

        def isListOfStrings(data):
            if type(data) != list:
                return False

            for d in data:
                if type(d) != str: ## Python 3 str = unicode
                    return False
            return True

        # check data
        if not isListOfStrings(command):
            raise Exception("ERROR >> zmq_request needs a list of strings (use json.dumps if you have a dictionary)")

        # something to send?
        if len(command) == 0:  # nothing to send
            print("WARNING >> zmq_request called without data")
            return ''

        try:
            # send all but last part
            for i in range(len(command)-1):
                self.REQsocket.send_string(command[i], flags=zmq.SNDMORE)
            # send last part
            self.REQsocket.send_string(command[-1])
        except zmq.error.ZMQError:
                self.zmqREQconnect()

        response = None
        if (self.REQsocket.poll(self.timeout) & zmq.POLLIN) != 0:
            response = [json.loads(x.decode()) for x in self.REQsocket.recv_multipart(zmq.NOBLOCK)]
            self.REQ_response = True
            self.time_last_message = datetime.now()
            if not (type(response) is list and response[0] == {'status':'ok'}): #responds with error message
                print(f"ZMQ ERROR >> {response[0]['message']}")
        else: #when no response at all
            self.REQ_response = False
        return response

    def get_init_pixelator(self):
        '''Request initial data from the Pixelator server.'''
        self.init_response = self.zmq_request(['initialize'])
        self.init_response_dict = self._convert_to_dict(self.init_response)

        self.pix_ctrl_status =  self.init_response_dict[0]
        self.positioner_def = self.init_response_dict[1]
        self.detector_def = self.init_response_dict[2]
        self.oscilloscope_def = self.init_response_dict[3]
        self.zone_plate_def = self.init_response_dict[4]
        self.remote_file_system_nfo = self.init_response_dict[5]

        pprint(self.zone_plate_def)

    def _convert_to_dict(self, lst):
        result = {}
        for i, item in enumerate(lst):
            if isinstance(item, list):
                result[i] = self._convert_to_dict(item)
            elif isinstance(item, dict):
                result[i] = {k: self._convert_to_dict(v) if isinstance(v, list) else v for k, v in item.items()}
            else:
                result[i] = item
        return result

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
