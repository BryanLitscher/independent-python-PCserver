
# base example https://tutorialedge.net/python/python-socket-io-tutorial/
# example to emit data to client https://github.com/miguelgrinberg/python-socketio/blob/master/examples/server/aiohttp/app.py
import re
import json
import serial
import time
from aiohttp import web
import socketio
import datetime
import threading

portName = "COM4";
serPort = serial.Serial(portName, 19200, timeout=1)
GPIOStatusDict = ""
GPIOinputs = [0, 1, 2, 3]
Relays = [0,1]







def GetboardStatus():
	boardStatus= {}
	relayStatus=getRelayStatus(Relays)
	gpioStatus=getGPIOStatus(GPIOinputs)
	boardStatus["relays"] = relayStatus
	boardStatus["gpios"] = gpioStatus
	return boardStatus




def setRelays( relayDictionary ) :
  #print( relayDictionary, flush=True )
  for n in Relays:
    #print(relayDictionary["relay{}".format(n)], flush=True)
    if relayDictionary["relay{}".format(n)]=="on":
      signal= "relay on {}\n\r".format(n)
    else:
      signal= "relay off {}\n\r".format(n)
    serPort.write( signal.encode() )
    response = serPort.read_until(b'>')


def getRelayStatus (Relays):
  relayStatus = {}
  for n in Relays:
    serPort.write(("relay read {}\n\r").format(n).encode())
    response = serPort.read_until(b'>')
    a= response.split(b"\n\r")
    if a[1] == b'on':
      relayStatus["relay{}".format(n)] = "on"
    else:
      relayStatus["relay{}".format(n)] = "off"
  return relayStatus
  
  
def getGPIOStatus ( inp ):
  gp = {}
  
  for x in inp:
    serPort.write(("gpio read " + str(x) + "\n\r").encode())	
    response = serPort.read_until(b'>')
    responsArray = response.split(b"\n\r")
    gp[ responsArray[0].strip().decode("utf-8").replace(" read ", "")  ] =  responsArray[1].strip().decode("utf-8") 
  return gp
  



# creates a new Async Socket IO Server
sio = socketio.AsyncServer()
# Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
# instance
sio.attach(app)

# we can define aiohttp endpoints just as we normally
# would with no change
async def index(request):
    with open('relaycontrol.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


# boardComparisonDict determines action from the server.
#  If the GPIO from the board is different, emit board status to the client.
#  If the Relay section is different, set the relay on the board.
boardComparisonDict = GetboardStatus()


async def background_task():
    #"""Example of how to send server generated events to clients."""
    while True:
        await sio.sleep(0.5)
        currentBoardState = GetboardStatus()
        #print(currentBoardState["gpios"],  flush=True )
        #print(boardComparisonDict["gpios"],  flush=True )
        #print("",  flush=True )
        if currentBoardState["gpios"] !=  boardComparisonDict["gpios"]:
            boardComparisonDict["gpios"] = currentBoardState["gpios"]
            a = currentBoardState["gpios"].copy()
            a["command"]="currentGPIOStatus"
            GPIOStatusJSON = json.dumps( a )
            await sio.emit('message', GPIOStatusJSON )
        if currentBoardState["relays"] !=  boardComparisonDict["relays"]:
            setRelays( boardComparisonDict["relays"] )


# If we wanted to create a new websocket endpoint,
# use this decorator, passing in the name of the
# event we wish to listen out for
@sio.on('message')
async def print_message(sid, message):
  global GPIOStatusJSON
  #print("Socket ID: " , sid)
  #print(message, flush=True)
  messageDict = json.loads(message)
  if messageDict["command"]=="setSwitch":
    boardComparisonDict["relays"]["relay1"] = messageDict["relay1"]
    boardComparisonDict["relays"]["relay0"] = messageDict["relay0"]

  if messageDict["command"]=="getSwitchStatus":
     ()
  if messageDict["command"]=="getBoardStatus":
    a = boardComparisonDict.copy()
    a["command"] = "currentBoardStatus"
    BoardStatusJSON = json.dumps( a )
    await sio.emit('message', BoardStatusJSON )
 

# We bind our aiohttp endpoint to our app
# router
app.router.add_get('/', index)

# We kick off our server
if __name__ == '__main__':
  sio.start_background_task(background_task)
  print("I am running" , flush=True)
  web.run_app(app)