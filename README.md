# SupplyBlockChain
Supply Chain From Blockchain

Transactions We Want To Make

Create Agent

Create Record

Transfer Record

Update Record

# python_blockchain_app

A simple tutorial for developing a blockchain application from scratch in Python.



## Instructions to run


Install the dependencies,

```sh
$ cd python_blockchain_app
$ pip install -r requirements.txt
```

Start a blockchain node server,

```sh
# Windows users can follow this: https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery
$ set FLASK_APP=nodeServer.py
$ flask run --port 8000 &
```

One instance of our blockchain node is now up and running at port 8000.


Run the application on a different terminal session,

```sh
$ python run_app.py
```

The application should be up and running at [http://localhost:5000](http://localhost:5000).


To play around by spinning off multiple custom nodes, use the `register_with/` endpoint to register a new node. 

Here's a sample scenario that you might wanna try,

```sh
# already running
$ flask run --port 8000 &
# spinning up new nodes
$ flask run --port 8001 &
$ flask run --port 8002 &
```

You can use the following cURL requests to register the nodes at port `8001` and `8002` with the already running `8000`.

```sh
curl -X POST \
  http://127.0.0.1:8001/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

```sh
curl -X POST \
  http://127.0.0.1:8002/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

This will make the node at port 8000 aware of the nodes at port 8001 and 8002, and make the newer nodes sync the chain with the node 8000, so that they are able to actively participate in the mining process post registration.

To update the node with which the frontend application syncs (default is localhost port 8000), change `CONNECTED_NODE_ADDRESS` field in the [views.py](/app/views.py) file.

Once you do all this, you can run the application, create transactions (post messages via the web inteface), and once you mine the transactions, all the nodes in the network will update the chain. The chain of the nodes can also be inspected by inovking `/chain` endpoint using cURL.

```sh
$ curl -X GET http://localhost:8001/chain
$ curl -X GET http://localhost:8002/chain
```
