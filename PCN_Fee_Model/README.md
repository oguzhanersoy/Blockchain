# Lightning Network - Multi-hop Payment Fee Simulator

In this project, I wrote a greedy algorithm aiming to maximize the fee gained by an intermediary node in LN.


## Useful References

### How to Setup a LND Local cluster
See: https://dev.lightning.community/tutorial/01-lncli/index.html

### Retrevieving the network topology
lncli describegraph > /tmp/graph.json

### How to obtain snapshot of the network topology

https://bitcoin.stackexchange.com/questions/88328/where-can-i-download-a-snapshot-of-the-lightning-network-topology?noredirect=1&lq=1

Use: wget https://rompert.com/networkgraphv2 | jq '.' | less
