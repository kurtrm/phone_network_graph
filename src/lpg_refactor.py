"""
Refactor of lpg to implement some more advanced class attributes
for simplicity. Particularly:
    Nodes:
        - __getitem__ to return properties
        - Format the repr and str methods.

    Relationships:
        - __getitem__ to return properties
        - I thought briefly about throwing nodes and relationships in the same dict,
          but I'm going to keep these separate for now.

    LPG:
        - Relationship keys will now be a tuple. So lpg['Kurt', 'Melissa'] will return
        the dictionary of relationships between the two nodes.
        - Modify __getitem__ to return either nodes or relationships
        - Implement __iter__
        - Define a property method for size, as well as a setter
        - Make it so that nodes can be added from iterables
        - Make it so relationships can be added from iterables
"""
#  TODO: Just realized I forgot that the tuple keys will have to return a list
#  of relationships. This is a major issue affecting this refactor.


class Node:
    """Node object that will have a relationship to other nodes."""

    def __init__(self, name):
        """Initialized nodes contain properties and methods to view them."""
        self.name = name
        self._properties = {}
        self.labels = []

    def __getitem__(self, key):
        """Get node properties."""
        return self._properties[key]

    def __setitem__(self, key, item):
        """Change or add node properties."""
        self._properties[key] = item

    def __delitem__(self, key):
        """Remove a property from the node."""
        try:
            del self._properties[key]
        except KeyError:
            raise KeyError("Node '{}' does not have property {}".format(self.name, key))

    def add_label(self, label):
        """Adds a label to the node."""
        if label in self.labels:
            raise ValueError('Label already set on node.')
        self.labels.append(label)

    def remove_label(self, label):
        """Removes a label from a node."""
        self.labels.remove(label)

    @property
    def properties(self):
        """Return the keys in self._properties."""
        return list(self._properties.keys())

    def __str__(self):  # pragma: no cover
        """Show the properties of the node."""
        props = """
-----------
Name: {}
-----------
Properties (key: value)
""".format(self.name)
        for key, value in self._properties.items():
            props += '\r{}: {}'.format(key, value)
        props += '\r\n\r\n-----------\rLabels: '
        props += ', '.join(self.labels)
        props += '\r\n\r\n'
        return props

    def __repr__(self):  # pragma: no cover
        """Return the same thing as repr."""
        return "<[{}] class Node {} Labels {} Properties>".format(self.name,
                                                                  len(self.labels),
                                                                  len(self.properties))


class Relationship:
    """Relationship object that will be able to have properties as well."""

    def __init__(self, name):
        """Initialize relationships as to contain properites like nodes."""
        self.name = name
        self._properties = {}
        self.labels = []

    def __getitem__(self, key):
        """Get node properties."""
        return self._properties[key]

    def __setitem__(self, key, item):
        """Change or add node properties."""
        self._properties[key] = item

    def __delitem__(self, key):
        """Remove a property from the node."""
        del self._properties[key]

    def add_label(self, label):
        """Adds a label to the node."""
        if label in self.labels:
            raise ValueError('Label already set on relationship.')
        self.labels.append(label)

    def remove_label(self, label):
        """Removes a label from a node."""
        self.labels.remove(label)

    @property
    def properties(self):
        """Return the keys in self._properties."""
        return list(self._properties.keys())

    def __str__(self):  # pragma: no cover
        """Show the properties of the node."""
        props = """
-----------
Name: {}
-----------
Properties (key: value)
""".format(self.name)
        for key, value in self._properties.items():
            props += '\r{}: {}'.format(key, value)
        props += '\r\n\r\n-----------\rLabels: '
        props += ', '.join(self.labels)
        props += '\r\n\r\n'
        return props

    def __repr__(self):  # pragma: no cover
        """Return the same thing as repr."""
        return "<[{}] Relationship {} Labels {} Properties>".format(self.name,
                                                                    len(self.labels),
                                                                    len(self.properties))


class LabeledPropertyGraph:
    """Define a labeled property graph as dictionary composition."""

    def __init__(self):
        """
        Initialize the graph as a dictionary (well, several).
        Right now, _graph maps the nodes and relationships. It does not
        contain node objects.

        _nodes contains the actual node objects.

        _relationships contains the actual relationship objects.
        """
        self._nodes = {}
        self._relationships = {}

    def __getitem__(self, key):
        """
        Return either node or relationship, depending on what type of
        object is passed into the subscripts. For relationships, this returns
        a list of relationships. The user can then grab a particular
        relationship by passing the name of the desired link into another
        set of subscripts.
        """
        if isinstance(key, tuple):
            return self._relationships[key]
        return self._nodes[key]

    # def __setitem__(self, key, item):
    #     """Modify or create new nodes or relationships.
    #        Warning: passing a tuple into the subscript will
    #        create new relationship, not node."""
    #     if isinstance(key, tuple):
    #         if not isinstance(item, Relationship):
    #             raise ValueError("Graph relationships must "
    #                              "be of type Relationship")
    #         self._relationships[key][item] = Relationship(item)
    #     else:
    #         if not isinstance(item, Node):
    #             raise ValueError("Graph nodes must "
    #                              "be of type Node")
    #         self._nodes[key] = item

    def __delitem__(self, key):
        """Delete node or relationship from graph."""
        try:
            if isinstance(key, tuple):
                del self._relationships[key]
            else:
                del self._nodes[key]
                for keys in list(self._relationships.keys()):
                    if key in keys:
                        del self._relationships[keys]
        except KeyError as error:
            err = "Relationship" if isinstance(error.args[0], tuple) else "Node"
            raise KeyError("{} {} not in graph".format(err, error.args[0]))

    @property
    def nodes(self):
        """Return a list of nodes in the graph."""
        return [node for node in self._nodes.keys()]

    @property
    def relationships(self):
        """Return list of unique relationships."""
        edges = []
        for edge in self._relationships.values():
            for key in edge.keys():
                if key not in edges:
                    edges.append(key)
        return edges

    def unique_relationships(self):
        """Return a list of unique relationship names."""
        return set([key for link in self._relationships.values() for key in link.keys()])

    def add_node(self, name):
        """Add a node and pass the name to the node.name."""
        if name in self.nodes:
            raise KeyError('Node already exists in graph')
        node = Node(name)
        self._nodes[name] = node

    def add_relationship(self, node_a, node_b, name, both_ways=False):
        """Refactored add_relationship for EAFP."""
        if node_a == node_b:
            raise ValueError("Node should not have a relationship with itself.")
        nodes = self.nodes
        if node_a not in nodes or node_b not in nodes:
            raise KeyError('A node is not present in this graph')

        def add(a, b, rel):
            """Local function to perform operation."""
            try:
                if self._relationships[a, b].get((rel)):
                    raise ValueError('{} -> {} relationship'
                                     'already exists'.format(a, b))
                else:
                    self._relationships[a, b][rel] = Relationship(rel)
            except KeyError:
                self._relationships[a, b] = {rel: Relationship(rel)}
        add(node_a, node_b, name)
        if both_ways:
            add(node_b, node_a, name)

    def get_relationships(self, node_a, node_b):
        """Return all relationships between two nodes."""
        return list(self._relationships[node_a, node_b].keys())

    def nodes_with_relationship(self, name):
        """Return a list of nodes with a given relationship."""
        nodes = set()
        for key, value in self._relationships.items():
            if name in value:
                nodes.add(key[0])
                nodes.add(key[1])
        return list(nodes)

    def neighbors(self, node):
        """Return all nodes node has relationship with."""
        return [key[1] for key in self._relationships.keys() if node == key[0]]

    def adjacent(self, node_a, node_b):
        """Return whether a node has a certain neighbor."""
        return (node_a, node_b) in self._relationships.keys()

    def has_relationship(self, node_a, node_b, relationship, both_ways=False):
        """Returns boolean if nodes have a particular relationship."""
        if both_ways:
            return relationship in self._relationships[node_a, node_b] \
                and relationship in self._relationships[node_b, node_a]
        else:
            return relationship in self._relationships[node_a,  node_b]
