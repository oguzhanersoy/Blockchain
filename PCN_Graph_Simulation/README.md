# LN Simulator
This section inludes the code related with our analysis on LN.

## How to Setup a LND Local cluster
See: https://dev.lightning.community/tutorial/01-lncli/index.html

## Retrevieving the network topology
lncli describegraph > /tmp/graph.json

## How to obtain snapshot of the network topology

https://bitcoin.stackexchange.com/questions/88328/where-can-i-download-a-snapshot-of-the-lightning-network-topology?noredirect=1&lq=1

Use: wget https://rompert.com/networkgraphv2 | jq '.' | less

## Useful Links

- Elias Rohrer and Julian Malliaris and Florian Tschorsch (2019). Discharged Payment Channels: Quantifying the Lightning Network's Resilience to Topology-Based Attacks. S&B '19: Proceedings of IEEE Security & Privacy on the Blockchain.
  - https://gitlab.tu-berlin.de/rohrer/discharged-pc-data
