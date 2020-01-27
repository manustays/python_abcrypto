# ABCrypto - A Blockchain and Cryptocurrency implementation in Python

A custom Blockchain implementation in Python 3. Meant for understanding the basics of the Blockchain technology.


## Features:
- [x] Blockchain (chain of data)
- [x] Crypographic Wallets
- [x] Block Mining (Proof-Of-Work)
- [x] Block Hashing (asymmetric cryptography)
- [x] Verify transactions, blocks and blockchain
- [x] Network of Nodes
- [x] P2P Transactions
- [x] Share data between nodes and resolve conflicts
- [x] Command Line Interface
- [x] Web Interface in Vue and Vuetify
- [ ] TODO: Efficient block verification using a Merkle Tree of transaction hashes
- [ ] TODO: Dynamic mining difficulty
- [ ] TODO: Enhanced P2P networking using sockets
- [ ] TODO: Automatic network discovery
- [ ] TODO: Better consensus algorithm (like, <abbr title="Practical Byzantine Fault Tolerance">pBFT</abbr>)



## Installation:
1. Install **[Python 3](https://www.python.org/downloads)**
2. Install **pip**:
   - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer.
   - Open a command prompt window and navigate to the folder containing *get-pip.py*.
   - Run `python get-pip.py`
1. Install the **dependencies**:
   - Run `pip install -r requirements.txt`
     - The dependnecies should ideally be installed in a new virtualenv for this project.
     - The requirements.txt file was generated using `pip freeze > requirements.txt` to get all installed packages and dependencies in the project virtualenv.


## Run Blockchain:
- Start a Blockchain node as a **web service** with `python ./node.py`
   - The web server runs by default on port 4000. Use `python ./node.py --port=<PortNumber>` to use another port.
   - Open the web-app with the URL: http://127.0.0.1:4000
- Start a Blockchain node as a **<abbr title="Command Line Interface">CLI</abbr>** (for local testing) with `python ./node_cli.py`
