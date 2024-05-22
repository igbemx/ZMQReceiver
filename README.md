# ZMQReceiver

This repository contains the source code for the ZMQReceiver application. ZMQReceiver is a Python application designed to communicate with a Pixelator STXM controller using the ZeroMQ library. It receives messages (commands and data) from the controller, parses them, and can send requests back.

## Features

- ZeroMQ communication: Establishes connections to a ZeroMQ publisher (receiving messages) and a requester (sending commands).
- Message parsing: Decodes binary messages and parses JSON-formatted data.
- Data organization: Stores parsed data in a dictionary structure based on message identifiers.
- Initial data retrieval: Requests and stores initial configuration data from the Pixelator controller upon startup.
- Error handling: Includes basic error handling during message receiving and parsing.

## Requirements

- Python 3.x
- ZeroMQ library (pyzmq)
- PyQt5 (for the QThread class, might be removable if not used in your main application)

## Getting Started

1. Clone this repository.
2. Install the required libraries using `pip install <library_name>`.
3. (Optional) Modify the `main_json_identifiers` list in the example usage section to include the message identifiers you are interested in.
4. (Optional) Set the `debug` argument to `True` in the ZMQReceiver constructor for additional logging information.
5. Integrate the ZMQReceiver class into your main script, following the example usage provided.

## Usage

The provided example showcases how to:

- Create a ZMQReceiver instance
- Start receiving messages
- Access the parsed data dictionary

