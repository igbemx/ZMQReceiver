from zmq_receiver import ZMQReceiver
import time

main_json_identifiers = [
    b'positionerDefinition',
    b'positionerDefinitionJson',
    b'positionerStatus',
    b'detectorDefinition',
    b'focalStatus',
    b'detectorValues'
]

receiver = ZMQReceiver(
    main_json_identifiers=main_json_identifiers,
    url="tcp://b-softimax-sophie-cc-0:55561",
    debug=False
)
receiver.start_receiver()

while True:
    print(receiver.parsed_data)
    time.sleep(1)

# Later, when you want to stop:
receiver.stop_receiver()  # Stop receiving messages