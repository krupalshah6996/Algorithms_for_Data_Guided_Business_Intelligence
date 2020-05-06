import sys
import time
import networkx as nx
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions
from graphframes import *
from copy import deepcopy

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)
#Connected_components = []
#ID = []
def articulations(g, usegraphframe=False):
	# Get the starting count of connected components
	# YOUR CODE HERE
	Start_Count = g.connectedComponents().select('component').distinct().count()
	print("Start Count: ",Start_Count)
	
	# Default version sparkifies the connected components process 
	# and serializes node iteration.
	vertices = g.vertices.map(lambda k: k.id).collect()
	# print(vertices)
	if usegraphframe:
		# Get vertex list for serial iteration
		# YOUR CODE HERE
		output = []
		for i,vertex in enumerate(vertices):
			temp_vertex = g.vertices.filter("id!='{}'".format(vertex))
			temp_edge = g.edges.filter("src!='{}'".format(vertex)).filter("dst!='{}'".format(vertex))
			temp_graph = GraphFrame(temp_vertex, temp_edge)
			temp_components = temp_graph.connectedComponents().select('component').distinct().count()
			output.append(vertex, 1 if temp_components > Start_Count else 0)
		return sqlContext.createDataFrame(sc.parallelize(output), ['id', 'articulation'])
		# For each vertex, generate a new graphframe missing that vertex
		# and calculate connected component count. Then append count to
		# the output
		# YOUR CODE HERE

	#graph_x = nx.Graph()
	#graph_x.add_nodes_from(vertices)
	#graph_x.add_edges_from(g.edges.map(lambda x:(x.src,x.dst)).collect())	
	# Non-default version sparkifies node iteration and uses networkx 
	# for connected components count.
	
#	def comp(n):
	#	temp= deepcopy(graph_x)
        #	temp.remove_node(n)
        #	return nx.number_connected_components(temp)
	else:
		
		graph_x = nx.Graph()
		graph_x.add_nodes_from(g.vertices.map(lambda x:x.id).collect())
		graph_x.add_edges_from(g.edges.map(lambda x:(x.src,x.dst)).collect())
		#temp_dict = {}
		def comp(n):
			#temp_dict = {}
                	temp = deepcopy(graph_x)
                	temp.remove_node(n)
		#			ID.append(n) 
		#	Connected_components.append(nx.number_connected_components(temp))
			#print("ID:" + str(n) + "Connected Components: "+str(nx.number_connected_components(g)))
                	return nx.number_connected_components(temp)
		return sqlContext.createDataFrame(g.vertices.map(lambda x:(x.id, 1 if comp(x.id) > Start_Count else 0)), ['id','articulation'])
        # YOUR CODE HERE
		

filename = sys.argv[1]
lines = sc.textFile(filename)

pairs = lines.map(lambda s: s.split(","))
e = sqlContext.createDataFrame(pairs,['src','dst'])
e = e.unionAll(e.selectExpr('src as dst','dst as src')).distinct() # Ensure undirectedness 	

# Extract all endpoints from input file and make a single column frame.
v = e.selectExpr('src as id').unionAll(e.selectExpr('dst as id')).distinct()	

# Create graphframe from the vertices and edges.
g = GraphFrame(v,e)

#Runtime approximately 5 minutes
print("---------------------------")
print("Processing graph using Spark iteration over nodes and serial (networkx) connectedness calculations")
init = time.time()
df = articulations(g, False)
print("Execution time: %s seconds" % (time.time() - init))
print("Articulation points:")
df.filter('articulation = 1').show(truncate=False)
print("---------------------------")

df.filter('articulation = 1').toPandas().to_csv('articulation_out.csv')
#print(temp_dict)
#print(max(Connected_components))
#print(ID[Connected_components.index(max(Connected_components))])
#Runtime for below is more than 2 hours
#print("Processing graph using serial iteration over nodes and GraphFrame connectedness calculations")
#init = time.time()
#df = articulations(g, True)
#print("Execution time: %s seconds" % (time.time() - init))
#print("Articulation points:")
#df.filter('articulation = 1').show(truncate=False)
