"""Test labeled property graph comprehensively."""

from faker import Faker
import pytest
import random


@pytest.fixture
def lpg():
    """Fixture of labeled property graph(lpg) for testing."""
    from ..src.labeled_property_graph import LabeledPropertyGraph
    lpg = LabeledPropertyGraph()
    return lpg


@pytest.fixture
def loaded_lpg():
    """Fixture of a loaded lpg."""
    from ..src.labeled_property_graph import LabeledPropertyGraph
    lpg = LabeledPropertyGraph()
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)
    lpg.add_relationship('cousins', 'Charlie', 'Unicorn')

    return lpg


@pytest.fixture
def big_lpg():
    """Lpg that's big and nasty."""
    from ..src.labeled_property_graph import LabeledPropertyGraph
    lpg = LabeledPropertyGraph()
    faker = Faker()
    phone_nums = list(set([faker.phone_number() for _ in range(100)]))
    relations = list(set([faker.word() for _ in range(100)]))
    for number in phone_nums:
        lpg.add_node(number)
    for _ in range(250):
        name_a = random.choice(phone_nums)
        name_b = random.choice(phone_nums)
        relationship = random.choice(relations)
        both_ways = bool(random.getrandbits(1))
        try:
            lpg.add_relationship(relationship, name_a, name_b, both_ways)
        except ValueError:
            continue

    return lpg

# ==================== Nodes ======================


def test_empty_lpg_nodes(lpg):
    """Ensure it returns none if no nodes in lpg."""
    assert lpg.nodes() == []


def test_empty_lpg_relationships(lpg):
    """Ensure it returns none if no relationships."""
    assert lpg.nodes() == []


def test_adding_node(lpg):
    """Ensure we can successfully add nodes to lpg."""
    lpg.add_node('Kurt')
    assert lpg.nodes() == ['Kurt']


def test_adding_lots_of_nodes(lpg):
    """Ensure we can put a lot of nodes in the graph."""
    names = [Faker().name() for _ in range(20)]
    names.append(3451)
    names.append(3.21)
    names.append(None)
    for name in names:
        lpg.add_node(name)
    for name in names:
        assert name in lpg.nodes()


def test_adding_lots_of_nodes_2(lpg):
    """Ensure we can put a lot of nodes in the graph."""
    names = list(set([Faker().name() for _ in range(20)]))
    names.append(3451)
    names.append(3.21)
    names.append(None)
    for name in names:
        lpg.add_node(name)
    for name in lpg.nodes():
        assert name in names


def test_adding_node_error(lpg):
    """Ensure error raised if node already exists."""
    lpg.add_node('Kurt')
    with pytest.raises(KeyError):
        lpg.add_node('Kurt')


def test_removing_node_from_empty(lpg):
    """Ensure we get error when removing from empty lpg."""
    with pytest.raises(KeyError):
        lpg.remove_node('Kurt')


def test_removing_nodes_with_many_connections(loaded_lpg):
    """Ensure relationships to deleted node are cleared."""
    loaded_lpg.add_node('Isolated')
    loaded_lpg.add_node('Wendy')
    for node in ['Charlie', 'Unicorn', 'Pegasus']:
        loaded_lpg.add_relationship('friends', 'Wendy', node)
    for rel, node in zip(['boss', 'parent', 'administrator'],
                         ['Charlie', 'Unicorn', 'Pegasus']):
        loaded_lpg.add_relationship(rel, node, 'Wendy')
    loaded_lpg.remove_node('Wendy')
    for rel in loaded_lpg._relationships:
        assert 'Wendy' not in loaded_lpg._relationships[rel]


def test_get_neighbors(loaded_lpg):
    """Test get_neighbors method."""
    loaded_lpg.add_node('Wendy')
    loaded_lpg.add_node('Teddy')
    for node in loaded_lpg.nodes():
        if node != 'Wendy':
            loaded_lpg.add_relationship('buddy', 'Wendy', node)
    assert loaded_lpg.get_neighbors('Wendy') == list(loaded_lpg._graph['Wendy']
                                                     .keys())


def test_is_neighbors_to(loaded_lpg):
    """Test returns correct neighbors."""
    loaded_lpg.add_node('Wendy')
    loaded_lpg.add_node('Teddy')
    for node in loaded_lpg.nodes():
        if node != 'Wendy':
            loaded_lpg.add_relationship('buddy', node, 'Wendy')
    assert sorted(loaded_lpg.is_neighbor_to('Wendy')) == sorted(['Teddy',
                                                                 'Pegasus',
                                                                'Charlie',
                                                                 'Unicorn'])


def test_add_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    assert loaded_lpg._nodes['Charlie'].properties['kidneys'] == 1


def test_change_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    assert loaded_lpg._nodes['Charlie'].properties['kidneys'] == 1
    loaded_lpg.change_node_prop('Charlie', 'kidneys', 0)
    assert loaded_lpg._nodes['Charlie'].properties['kidneys'] == 0


def test_rm_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    assert loaded_lpg._nodes['Charlie'].properties['kidneys'] == 1
    loaded_lpg.remove_node_prop('Charlie', 'kidneys')
    assert not loaded_lpg._nodes['Charlie'].properties.get('kidneys')


def test_error_when_adding_duplicates(loaded_lpg):
    """Test that we raise the appropriate error."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    with pytest.raises(KeyError):
        loaded_lpg.add_node_props('Charlie', kidneys=1)


def test_change_node_prop_DNE(loaded_lpg):
    """Test that we get error if we try to change a property that DNE."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    with pytest.raises(AttributeError):
        loaded_lpg.change_node_prop('Charlie', 'horn', 1)


def test_remove_node_DNE_prop(loaded_lpg):
    """Test that we raise an error if removing DNE prop."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    with pytest.raises(AttributeError):
        loaded_lpg.remove_node_prop('Charlie', 'kids')


def test_node_repr(loaded_lpg):
    """Test that we get the expected string when 'calling' the class."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    assert repr(loaded_lpg._nodes['Charlie']) == "Name: Charlie\nProperties:\rkidneys: 1"


def test_get_node_props(loaded_lpg):
    """Test getting node properties."""
    loaded_lpg.add_node_props('Charlie', kidneys=1)
    assert loaded_lpg.get_node_properties('Charlie') == {'kidneys': 1}


def test_has_neighbor_true(loaded_lpg):
    """Test has_neighbor method."""
    assert loaded_lpg.has_neighbor('Charlie', 'Unicorn')


def test_has_neighbor_false(loaded_lpg):
    """Test has neighbor method false."""
    assert not loaded_lpg.has_neighbor('Charlie', 'Pegasus')

def test_has_neighbor_exception(loaded_lpg):
    """Test exception is raised if node not there."""
    with pytest.raises(KeyError):
        loaded_lpg.has_neighbor('Cheeky', 'Charlie')

# ================== Relationsihps ================


def test_adding_rel_to_empty_lpg(lpg):
    """Ensure we can't add relationships between nonexistent nodes."""
    with pytest.raises(KeyError):
        lpg.add_relationship('durka', 'Will', 'Bill')


def test_adding_rel_one_node_dne(lpg):
    """Ensure we can add relationships between existent and non-existent."""
    lpg.add_node('Kurt')
    with pytest.raises(KeyError):
        lpg.add_relationship('durka', 'Kurt', 'Bill')


def test_adding_rel_other_dne(lpg):
    """Ensure second parameter works as well."""
    lpg.add_node('Billy')
    with pytest.raises(KeyError):
        lpg.add_relationship('durka', 'Kurt', 'Billy')


def test_adding_rel_success(lpg):
    """Ensure successful of adding a relationship."""
    lpg.add_node('Kurt')
    lpg.add_node('Meliss')
    lpg.add_relationship('rel', 'Kurt', 'Meliss')
    assert lpg.unique_relationships() == ['rel']


def test_adding_rel_success_view(lpg):
    """Ensure we can see the relationship as a key in the dict."""
    lpg.add_node('Kurt')
    lpg.add_node('Meliss')
    lpg.add_relationship('rel', 'Kurt', 'Meliss')
    assert (lpg._graph['Kurt'],
            lpg._relationships['rel']['Kurt']['Meliss'].name) == \
        ({'Meliss': ['rel']}, 'rel')


def test_adding_rel_with_other_rels(lpg):
    """Ensure we can add to a list of rels in _graph."""
    lpg.add_node('Kurt')
    lpg.add_node('Meliss')
    lpg.add_node('Mom')
    lpg.add_relationship('rel', 'Kurt', 'Meliss')
    lpg.add_relationship('rel', 'Kurt', 'Mom')
    graph_key = lpg._graph['Kurt']
    rel_node = lpg._relationships['rel']['Kurt']['Meliss']
    assert (graph_key,
            rel_node.name) == ({'Meliss': ['rel'], 'Mom': ['rel']}, 'rel')


def test_adding_existent_rel(lpg):
    """Ensure we get the proper key erro."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn')
    with pytest.raises(ValueError):
        lpg.add_relationship('buddies', 'Charlie', 'Unicorn')


def test_adding_existent_rel_both_ways(lpg):
    """Ensure we get the proper key erro."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn')
    with pytest.raises(ValueError):
        lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)


def test_adding_both_ways_success_graph(lpg):
    """Ensure successful both ways relationship add."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)
    assert lpg._graph['Charlie']['Unicorn'] == lpg._graph['Unicorn']['Charlie']


def test_adding_both_ways_success_rels(lpg):
    """Ensure successful both ways relationship add."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)
    assert lpg._relationships['buddies']['Charlie']['Unicorn'].name == \
        lpg._relationships['buddies']['Unicorn']['Charlie'].name


def test_conditionals_in_add_rels(lpg):
    """Ensure we successfully add rels b/w nodes."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)
    lpg.add_relationship('buddies', 'Charlie', 'Pegasus')
    assert lpg._graph['Charlie']['Pegasus'][0] == \
        lpg._relationships['buddies']['Charlie']['Pegasus'].name


def test_adding_another_rel_between_nodes(lpg):
    """Ensure we except attribute error."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('buddies', 'Charlie', 'Unicorn', both_ways=True)
    lpg.add_relationship('cousins', 'Charlie', 'Unicorn')
    assert lpg._graph['Charlie']['Unicorn'][1] == \
        lpg._relationships['cousins']['Charlie']['Unicorn'].name


def test_removing_rel(loaded_lpg):
    """Ensure relationships can be removed."""
    loaded_lpg.remove_relationship('cousins', 'Charlie', 'Unicorn')
    assert loaded_lpg._graph['Charlie']['Unicorn'] == ['buddies']


# def test_removing_rel_single(loaded_lpg):
#     """Ensure relationships can be removed."""
#     loaded_lpg.remove_relationship('cousins', 'Charlie', 'Unicorn')
#     loaded_lpg.remove_relationship('buddies', 'Charlie', 'Unicorn')
#     with pytest.raises(KeyError):
#         loaded_lpg._graph['Charlie']['Unicorn'] == []


def test_add_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    assert loaded_lpg._relationships['buddies']['Charlie']['Unicorn'].properties['since'] == 1985


def test_change_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    assert loaded_lpg._relationships['buddies']['Charlie']['Unicorn'].properties['since'] == 1985
    loaded_lpg.change_rel_prop('buddies', 'Charlie', 'Unicorn', 'since', 1990)
    assert loaded_lpg._relationships['buddies']['Charlie']['Unicorn'].properties['since'] == 1990


def test_rm_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    assert loaded_lpg._relationships['buddies']['Charlie']['Unicorn'].properties['since'] == 1985
    loaded_lpg.remove_rel_prop('buddies', 'Charlie', 'Unicorn', 'since')
    assert not loaded_lpg._relationships['buddies']['Charlie']['Unicorn'].properties.get('since')


def test_error_when_adding_rel_prop_duplicates(loaded_lpg):
    """Test that we raise the appropriate error."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    with pytest.raises(KeyError):
        loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)


def test_change_rel_prop_DNE(loaded_lpg):
    """Test that we get error if we try to change a property that DNE."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    with pytest.raises(AttributeError):
        loaded_lpg.change_rel_prop('buddies', 'Charlie', 'Unicorn', 'butt', 1)


def test_remove_rel_DNE_prop(loaded_lpg):
    """Test that we raise an error if removing DNE prop."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    with pytest.raises(AttributeError):
        loaded_lpg.remove_rel_prop('buddies', 'Charlie', 'Unicorn', 'butt')


#def test_rel_repr(loaded_lpg):
#    """Test that we get the expected string when 'calling' the class."""
#    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
#    assert repr(loaded_lpg._relationships['buddies']['Charlie']['Unicorn']) == "Name: buddies\nProperties:\rsince: 1985"


def test_adding_self_ref_rel(loaded_lpg):
    """Test that we get an error when trying to add a rel b/w node and self."""
    with pytest.raises(ValueError):
        loaded_lpg.add_relationship('buddies', 'Charlie', 'Charlie')


def test_get_rel_props(loaded_lpg):
    """Test that we get the appropriate properties back."""
    loaded_lpg.add_rel_props('buddies', 'Charlie', 'Unicorn', since=1985)
    assert loaded_lpg.get_relationship_properties('buddies', 'Charlie', 'Unicorn') == \
           {'since': 1985}

# ====================== RETRIEVAL =============================


def test_get_relationships(loaded_lpg):
    """Ensure returns correct relationships."""
    loaded_lpg.add_relationship('guys', 'Charlie', 'Pegasus')
    assert loaded_lpg.get_relationships('Charlie',
                                        'Pegasus') == \
        loaded_lpg._graph['Charlie']['Pegasus']


def test_nodes_with_relationships(loaded_lpg):
    """Ensure returns correction relationships."""
    assert loaded_lpg.nodes_with_relationship('buddies') == \
        list(loaded_lpg._relationships['buddies'].keys())


def test_nodes_with_relationships_2(loaded_lpg):
    """Ensure returns keys of _graph."""
    loaded_lpg.add_node('Willy')
    loaded_lpg.add_node('Billy')
    loaded_lpg.add_node('Gilly')
    loaded_lpg.add_node('Lilly')
    for node in loaded_lpg._graph:
        if node == 'Billy':
            continue
        loaded_lpg.add_relationship('acquaintances', 'Billy', node)
    assert loaded_lpg.nodes_with_relationship('acquaintances') == \
        list(loaded_lpg._relationships['acquaintances'].keys())


def test_has_relationship_true(loaded_lpg):
    """Ensure returns given relationship."""
    assert loaded_lpg.has_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)


def test_has_relationship_false(loaded_lpg):
    """ensure returns false."""
    assert not loaded_lpg.has_relationship('Charlie', 'Unicorn', 'siblings')
