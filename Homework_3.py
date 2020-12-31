from GraphStat.NetworkBuilder import node, graph, stat
from GraphStat.Visualization import plotgraph, plotnodes


def main():
    """
    主函数，完成了对于包内函数的调用
    """
    #Nodels = node.init_node('Vertices.txt')
    #node.print_node(Nodels[100])
    #Graph = graph.init_graph(Nodels, 'Edges.txt')
    #graph.save_graph(Graph)
    NewGraph = graph.load_graph('pickle_graph.pkl')
    #stat.cal_average_dgree(NewGraph)
    #stat.get_attr_distribution(NewGraph)
    #stat.cal_dgree_distribution(NewGraph)
    #plotgraph.plotdgree_distribution(NewGraph)
    attrs = ['type', 'inform']
    for attr in attrs:
        plotnodes.plot_nodes_attr(NewGraph, attr)
    plotnodes.plot_whole_graph(NewGraph, size=3000)
    return 0


if __name__ == '__main__':
    main()