# Blind Sailing

Blind Sailing is a web game made over the course of 24 hours at Durhack 2024. 

This game is based on the game battleships but extended by the ability to move each of your ships every turn and also having both players on the same board with a fog-of-war mechanic. 

## Requirements

- Python3
- Python libraries: flask, numpy

## Usage

Run the python file to start the web server:
```bash
python3 src/server/app.py
```

This starts a Flask web server on `localhost:5000`. You can then go to this address on your web browser to play the game. 
Firewall rules or port forwarding will need to be enabled for you to be able to access this from other machines.
