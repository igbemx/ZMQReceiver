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
    url_receiv="tcp://b-softimax-sophie-cc-0:55561",
    url_request="tcp://b-softimax-sophie-cc-0:55562",
    debug=False
)
receiver.start_receiver()
time.sleep(2)

while True:
    for key, value in receiver.parsed_data.items():
        print(key)
    
    for num, value in enumerate(receiver.parsed_data['positionerStatus'][0]):
        print(f'positioner {num} value is: {value}')
    #print(receiver.parsed_data)
    time.sleep(2)

# Later, when you want to stop:
receiver.stop_receiver()  # Stop receiving messages