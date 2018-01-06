"""
Implementation of a labeled property graph.

"""
# ===================================
# TODO: Number of relationships a node has
# TODO: Number of nodes that have a given relationship
# TODO: Number of nodes with a relationship
# TODO: Number of nodes with a label
# TODO: Traversals:
# - Depth first
# - Breadth-first
# - Dijkstra's
# - A*
# TODO: Need __repr__ for the lpg class itself

# ===================================


class Node:
    """Node object that will have a relationship to other nodes."""

    def __init__(self, name):
        """Initialized nodes contain properties and methods to view them."""
        self.name = name
        self.properties = {}
        self.labels = []

    def __getitem__(self, key):
        """Get node properties."""
        return self.properties[key]

    def add_property(self, property_, value):
        """Method to add a property to a node."""
        if property_ in self.properties:
            raise KeyError("Property already exists, use change_property()"
                           "to alter property value")
        self.properties[property_] = value

    def change_property(self, property_, value):
        """Method to alter a value on a property."""
        if property_ not in self.properties:
            raise AttributeError("Property does not exist, use add_property()"
                                 "to add a property")
        self.properties[property_] = value

    def remove_property(self, property_):
        """Method to remove a property from a node."""
        if property_ not in self.properties:
            raise AttributeError("Node does not contain that property")
        del self.properties[property_]

    def add_label(self, label):
        """Adds a label to the node."""
        if label in self.labels:
            raise ValueError('Label already set on node.')
        self.labels.append(label)

    def remove_label(self, label):
        """Removes a label from a node."""
        self.labels.remove(label)

    def __repr__(self):
        """Show the properties of the node."""
        props = "Name: {}\nProperties:".format(self.name)
        for key, value in self.properties.items():
            props += '\r{}: {}'.format(key, value)
        return props


class Relationship:
    """Relationship object that will be able to have properties as well."""

    def __init__(self, name):
        """Initialize relationships as to contain properites like nodes."""
        self.name = name
        self.properties = {}
        self.labels = []

    def add_property(self, property_, value):
        """Method to add a property to a node."""
        if property_ in self.properties:
            raise KeyError("Property already exists, use change_property()"
                           "to alter property value")
        self.properties[property_] = value

    def change_property(self, property_, value):
        """Method to alter a value on a property."""
        if property_ not in self.properties:
            raise AttributeError("Property does not exist, use add_property()"
                                 "to add a property")
        self.properties[property_] = value

    def remove_property(self, property_):
        """Method to remove a property from a node."""
        if property_ not in self.properties:
            raise AttributeError("Node does not contain that property")
        del self.properties[property_]

    def add_label(self, label):
        """Adds a label to the node."""
        if label in self.labels:
            raise ValueError('Label already set on node.')
        self.labels.append(label)

    def remove_label(self, label):
        """Removes a label from a node."""
        self.labels.remove(label)

    def __repr__(self):
        """Show the properties of the node."""
        props = "Name: {}\nProperties:"
        for key, value in self.properties.items():
            props += '\r{}: {}'.format(key, value)
        return props


class LabeledPropertyGraph:
    """Define a labeled property graph as dictionary composition."""

    def __init__(self):
        """Initialize the graph as a dictionary."""
        self._graph = {}
        self._nodes = {}
        self._relationships = {}

    def __getitem__(self, key):
        """Return _graphat key."""
        return self._nodes[key]

    #  Consider property decorator
    def nodes(self):
        """Return a list of nodes in the graph."""
        return [node for node in self._nodes.keys()]

    def unique_relationships(self):
        """Return list of unique relationships."""
        #  This will likely not return what I'm looking for.
        return [relationship for relationship in self._relationships.keys()]

    def add_node(self, name):
        """Add a node and pass the name to the node.name."""
        if name in self.nodes():
            raise KeyError('Node already exists in graph')
        node = Node(name)
        self._graph[name] = {}
        self._nodes[name] = node

    def add_relationship(self, name, node_a, node_b, both_ways=False):
        """Refactored add_relationship for EAFP."""
        if node_a == node_b:
            raise ValueError("Node should not have a relationship with itself.")
        nodes = self.nodes()
        if node_a not in nodes or node_b not in nodes:
            raise KeyError('A node is not present in this graph')

        def add(rel, a, b):
            """Local function to perform operation."""
            try:
                if self._relationships[rel][a].get(b):
                    raise ValueError('{} -> {} relationship'
                                     'already exists'.format(a, b))
                self._relationships[rel][a][b] = Relationship(rel)
            except KeyError as key_errors:
                key = key_errors.args[0]
                if key == rel:
                    self._relationships[rel] = {
                        a: {b: Relationship(rel)}}
                elif key == a:
                    self._relationships[rel][a] = {
                        b: Relationship(rel)}
            try:
                self._graph[a][b].append(rel)
            except KeyError:
                self._graph[a][b] = [rel]

        add(name, node_a, node_b)
        if both_ways:
            add(name, node_b, node_a)

    def remove_relationship(self, name, node_a, node_b):
        """Remove a relationship between two nodes."""
        del self._relationships[name][node_a][node_b]
        self._graph[node_a][node_b].remove(name)

    def remove_node(self, name):
        """Remove a node and all of its relationships."""
        for relationship in self._relationships:
            for node in self._relationships[relationship]:
                try:
                    del self._relationships[relationship][node][name]
                except KeyError:
                    continue
            try:
                del self._relationships[relationship][name]
            except KeyError:
                continue
        del self._graph[name]
        for node in self._graph:
            try:
                del self._graph[node][name]
            except KeyError:
                continue

    def get_relationships(self, node_a, node_b):
        """Return all relationships between two nodes."""
        return self._graph[node_a][node_b]

    def nodes_with_relationship(self, name):
        """Return all nodes with a given relationship."""
        return list(self._relationships[name].keys())

    def get_neighbors(self, node):
        """Return all nodes node has relationships with."""
        return list(self._graph[node].keys())

    def is_neighbor_to(self, node):
        """Return node that node is a neighbor to, but not vice versa."""
        return [vertex for vertex, rels in self._graph.items()
                if node in rels]

    def get_relationship_properties(self, name, node_a, node_b):
        """Return properties of a relationship between two nodes."""
        return self._relationships[name][node_a][node_b].properties

    def get_node_properties(self, name):
        """Return properties of a node."""
        return self._nodes[name].properties

    def has_neighbor(self, node_a, node_b):
        """Return boolean whether a node has a certain neighbor."""
        try:
            return node_b in self._graph[node_a]
        except KeyError:
            raise KeyError('{} not in graph'.format(node_a))

    def has_relationship(self, node_a, node_b, relationship, both_ways=False):
        """Return whether node_a has a given rel to node_b or vice_versa."""
        if both_ways:
            return relationship in self._graph[node_a][node_b] \
                and relationship in self._graph[node_b][node_a]
        return relationship in self._graph[node_a][node_b]

    def change_node_prop(self, node, property_, value):
        """Change the property of a node."""
        self._nodes[node].change_property(property_, value)

    def change_rel_prop(self, rel, node_a, node_b, prop, val):
        """Change the property of a relationship."""
        self._relationships[rel][node_a][node_b].change_property(prop, val)

    def remove_node_prop(self, node, property_):
        """Remove node property."""
        self._nodes[node].remove_property(property_)

    def remove_rel_prop(self, rel, node_a, node_b, prop):
        """Remove rel property."""
        self._relationships[rel][node_a][node_b].remove_property(prop)

    def add_node_props(self, node, **kwargs):
        """Add properties to a node with values."""
        for key, value in kwargs.items():
            self._nodes[node].add_property(key, value)

    def add_rel_props(self, rel, node_a, node_b, **kwargs):
        """Add relationship props with values."""
        for key, value in kwargs.items():
            self._relationships[rel][node_a][node_b].add_property(key, value)
