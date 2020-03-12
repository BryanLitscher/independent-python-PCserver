# Independent Study - Python web server controlling numato relay board

This project uses a web browser to contol and display the status of a numato relay board.  The browser communicates with the server using socket.io.  The server communicates with the relay board via serial communications.

This project is configured for a Windows PC

It uses socket.io so that there is real time bidirectional communications between the browser and the server.  As soon as there is a change to the GPIO input, the server emits the results to the client and displayed in the browser screen.  The browser does not need to continually poll the server to see if there is a change.

The server uses serial communications to communicate with the numato relay board.

http://localhost:8080/

Socket.io
https://python-socketio.readthedocs.io/en/latest/ 
https://tutorialedge.net/python/python-socket-io-tutorial/
https://github.com/miguelgrinberg/python-socketio/blob/master/examples/server/aiohttp/app.py

Numato
https://numato.com/product-category/automation/relay-modules/usb-relay
https://github.com/numato/samplecode/tree/master/RelayAndGPIOModules/USBRelayAndGPIOModules/python/usbrelay1_2_4_8

