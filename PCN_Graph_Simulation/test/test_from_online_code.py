import NetworkX as nx

# https://www.geeksforgeeks.org/betweenness-centrality-centrality-measure/

def betweenness_centrality(G, k=None, normalized=True, weight=None,
						endpoints=False, seed=None):
	r"""

    Compute the shortest-path betweenness centrality for nodes.

	Betweenness centrality of a node $v$ is the sum of the
	fraction of all-pairs shortest paths that pass through $v$

	.. math::

	c_B(v) =\sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}

	where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
	shortest $(s, t)$-paths, and $\sigma(s, t|v)$ is the number of
	those paths passing through some node $v$ other than $s, t$.
	If $s = t$, $\sigma(s, t) = 1$, and if $v \in {s, t}$,
	$\sigma(s, t|v) = 0$ [2]_.

	Parameters
	----------
	G : graph
	A NetworkX graph.

	k : int, optional (default=None)
	If k is not None use k node samples to estimate betweenness.
	The value of k <= n where n is the number of nodes in the graph.
	Higher values give better approximation.

	normalized : bool, optional
	If True the betweenness values are normalized by `2/((n-1)(n-2))`
	for graphs, and `1/((n-1)(n-2))` for directed graphs where `n`
	is the number of nodes in G.

	weight : None or string, optional (default=None)
	If None, all edge weights are considered equal.
	Otherwise holds the name of the edge attribute used as weight.

	endpoints : bool, optional
	If True include the endpoints in the shortest path counts.

	Returns
	-------
	nodes : dictionary
	Dictionary of nodes with betweenness centrality as the value.


	Notes
	-----
	The algorithm is from Ulrik Brandes [1]_.
	See [4]_ for the original first published version and [2]_ for details on
	algorithms for variations and related metrics.

	For approximate betweenness calculations set k=#samples to use
	k nodes ("pivots") to estimate the betweenness values. For an estimate
	of the number of pivots needed see [3]_.

	For weighted graphs the edge weights must be greater than zero.
	Zero edge weights can produce an infinite number of equal length
	paths between pairs of nodes.


	"""
	betweenness = dict.fromkeys(G, 0.0) # b[v]=0 for v in G
	if k is None:
		nodes = G
	else:
		random.seed(seed)
		nodes = random.sample(G.nodes(), k)
	for s in nodes:

		# single source shortest paths
		if weight is None: # use BFS
			S, P, sigma = _single_source_shortest_path_basic(G, s)
		else: # use Dijkstra's algorithm
			S, P, sigma = _single_source_dijkstra_path_basic(G, s, weight)

		# accumulation
		if endpoints:
			betweenness = _accumulate_endpoints(betweenness, S, P, sigma, s)
		else:
			betweenness = _accumulate_basic(betweenness, S, P, sigma, s)

	# rescaling
	betweenness = _rescale(betweenness, len(G), normalized=normalized,
						directed=G.is_directed(), k=k)
	return betweenness

G= nx.erdos_reyni_graph(50,0.5)
b=nx.betweenness_centrality(G)
print b
