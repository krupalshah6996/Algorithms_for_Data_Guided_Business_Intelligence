import pandas as pd
import igraph
from sklearn.metrics.pairwise import cosine_similarity
import sys
from collections import defaultdict
from collections import Counter
from scipy import spatial
from copy import deepcopy

#Function to compute the modularity gain for each community after placing a vertex in a specific community
def modularity_gain(graph, communities, community_1, alpha, current_community, vertex):
    vertex_community = dict.fromkeys(range(graph.vcount()), 0)
    # print("Communities:", communities)
    # print(vertex_community)
    for com_num, community in enumerate(communities):

        for t_vert in community:
            # print(vert)
            # print(com_num)
            vertex_community[t_vert] = com_num
    # print(vertex_community)
    # print(communities.index(current_community))
    vertex_community_updated = deepcopy(vertex_community)
    vertex_community_updated[vertex] = communities.index(current_community)
    # print(vertex_community)
    # print(vertex_community_updated)
    # print(vertex)
    # print(current_community)
    # if Counter(list(vertex_community_updated.values())) == Counter(list(vertex_community.values())):
    #     print(True)
    Q_newman = graph.modularity(list(vertex_community_updated.values())) - graph.modularity(list(vertex_community.values()))
    total = 0.0
    for vert in current_community:
        total += similarity_matrix[vertex][vert]
    Q_attr = total/len(current_community)
    # print("Q_attr: ",Q_attr)
    # print("Q_newman: ",Q_newman)
    # print(alpha)
    # print((alpha * Q_newman) + ((1 - alpha)*Q_attr))
    return alpha * Q_newman + (1 - alpha) * Q_attr


#Function to calculate the phase 1 of the algorithm
def calcualte_phase_1(graph, alpha, communities):
    # vertices = [x for x in range(g.vcount())]
    # communities = igraph.clustering.VertexClustering(graph, vertices)
    # print(communities)
    for i in range(15):
        # print(communities)
        for vertex in range(graph.vcount()):

            remaining_communities = list()
            community_1 = list()
            community_2 = list()
            max_modularity_gain = -1
            for temp_community in communities:
                if vertex in temp_community:
                    community_1 = temp_community
                    break
            # print(community_1)
            
            for community in communities:
                # print("C: ",community)
                if Counter(community_1) != Counter(community):
                    remaining_communities.append(community)
                
            # print("Communities: ",communities)
            # print("Community_1: ",community_1)
            # print("REmaining: ",remaining_communities)
            # remaining_communities = remaining_communities.reverse()
            # print(remaining_communities)
            # print("Vertex_i",vertex)
            for community in remaining_communities:
                # print(community)
                Q_delta = modularity_gain(graph, communities, community_1, alpha, community, vertex)
                # print(Q_delta)
                if (Q_delta > max_modularity_gain) and (Q_delta > 0):
                    max_modularity_gain = Q_delta
                    community_2 = community
            # print(Q_delta)
            # print("Vertex_f",vertex)
            if max_modularity_gain > 0:
                # print(community_1)
                # print("Vertex: ",vertex)
                community_1.remove(vertex)
                community_2.append(vertex)
            if len(community_1) == 0:
                # print(communities)
                # print(community_1)
                communities.remove(community_1)
            # print(community_2)
            # print("Communities: ",communities)
    return communities


#Function to calculate the phase 2 of the algorithm        
def calcualte_phase_2(graph, alpha, communities):
    vertex_community = dict.fromkeys(range(graph.vcount()), 0)
    # print("Communities:", communities)
    # print(vertex_community)
    for com_num, community in enumerate(communities):

        for t_vert in community:
            # print(vert)
            # print(com_num)
            vertex_community[t_vert] = com_num
    # for i in vertex_community:
    #     print(i)
    # print(vertex_community)
    graph.contract_vertices(list(vertex_community.values()), combine_attrs = "mean")
    graph.simplify(combine_edges = sum)
    return graph


#Main function of the program to calculate the algorithm SAC given in the paper 
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Invalid Input. Please specify the alpha value")
    else:
        alpha = float(sys.argv[1])
        attributes = pd.read_csv('./data/fb_caltech_small_attrlist.csv')
        edges = open('./data/fb_caltech_small_edgelist.txt').readlines()
        for edge in range(len(edges)):
            temp = edges[edge].split(" ")
            edges[edge] = (int(temp[0]), int(temp[1]))
        graph = igraph.Graph()
        graph.add_vertices(len(attributes))
        for att in attributes.columns.tolist():
            graph.vs[att] = attributes[att]
        graph.add_edges(edges)
        global similarity_matrix
        similarity_matrix = cosine_similarity(attributes,attributes)
        # print(similarity_matrix)
        communities = list()
        for i in range(graph.vcount()):
            communities.append([int(i)])
        C_1 = calcualte_phase_1(graph,alpha, communities)
        vertex_community_C1 = dict.fromkeys(range(graph.vcount()), 0)
        # print("Community Count for Phase 1:",len(C_1))
        # print(C_1)
        # print("Communities:", communities)
        # print(vertex_community)
        for com_num, community in enumerate(C_1):
            for vert in community:
                # print(vert)
                # print(com_num)
                vertex_community_C1[vert] = com_num
        mod_C1 = graph.modularity(list(vertex_community_C1.values()))
        # print(mod_C1)
        graph = calcualte_phase_2(graph, alpha, C_1)
        # print(graph)
        communities_phase_2 = list()
        for i in range(graph.vcount()):
            communities_phase_2.append([int(i)])
        for i in range(graph.vcount()):
            for j in range(graph.vcount()):
                # print(graph.vs[i].attributes().values())
                # print(graph.vs[j].attributes().values())
                similarity_matrix[i][j] = 1 - spatial.distance.cosine(list(graph.vs[i].attributes().values()), list(graph.vs[j].attributes().values()))
        
        # print("Similarity Matrix: ",similarity_matrix)
        # print("-----------C2----------------")
        C_2 = calcualte_phase_1(graph,alpha, communities_phase_2)
        # print("Community Count for Phase 2:",len(C_2))
        vertex_community_C2 = dict.fromkeys(range(graph.vcount()), 0)
        for com_num, community in enumerate(C_2):
            for vert in community:
                vertex_community_C2[vert] = com_num
        mod_C2 = graph.modularity(list(vertex_community_C2.values()))
        # print(mod_C2)
        final_community = C_1 if mod_C1 > mod_C2 else C_2
        if alpha == 0:
            output = open("communities_0.txt", 'w+')
            for community in final_community:
                for i in range(len(community) - 1):
                    output.write(str(community[i])+",")
                output.write(str(community[-1]))
                output.write('\n')            
            output.close()
        elif alpha == 0.5:
            output = open("communities_5.txt", 'w+')
            for community in final_community:
                for i in range(len(community) - 1):
                    output.write(str(community[i])+",")
                output.write(str(community[-1]))
                output.write('\n')            
            output.close()
        else:
            output = open("communities_1.txt", 'w+')
            for community in final_community:
                for i in range(len(community) - 1):
                    output.write(str(community[i])+",")
                output.write(str(community[-1]))
                output.write('\n')            
            output.close()
    
    
