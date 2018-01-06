"""Test labeled property graph comprehensively."""

from faker import Faker
import pytest
import random


@pytest.fixture
def lpg():
    """Fixture of labeled property graph(lpg) for testing."""
    from ..src.lpg_refactor import LabeledPropertyGraph
    lpg = LabeledPropertyGraph()
    return lpg


@pytest.fixture
def loaded_lpg():
    """Fixture of a loaded lpg."""
    from ..src.lpg_refactor import LabeledPropertyGraph
    lpg = LabeledPropertyGraph()
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)
    lpg.add_relationship('Charlie', 'Unicorn', 'cousins')

    return lpg


@pytest.fixture
def big_lpg():
    """Lpg that's big and nasty."""
    from ..src.lpg_refactor import LabeledPropertyGraph
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
    assert lpg.nodes == []


def test_empty_lpg_relationships(lpg):
    """Ensure it returns none if no relationships."""
    assert lpg.nodes == []


def test_adding_node(lpg):
    """Ensure we can successfully add nodes to lpg."""
    lpg.add_node('Kurt')
    assert lpg.nodes == ['Kurt']


def test_adding_lots_of_nodes(lpg):
    """Ensure we can put a lot of nodes in the graph."""
    names = [Faker().name() for _ in range(20)]
    names.append(3451)
    names.append(3.21)
    names.append(None)
    for name in names:
        lpg.add_node(name)
    for name in names:
        assert name in lpg.nodes


def test_adding_lots_of_nodes_2(lpg):
    """Ensure we can put a lot of nodes in the graph."""
    names = list(set([Faker().name() for _ in range(20)]))
    names.append(3451)
    names.append(3.21)
    names.append(None)
    for name in names:
        lpg.add_node(name)
    for name in lpg.nodes:
        assert name in names


def test_adding_node_error(lpg):
    """Ensure error raised if node already exists."""
    lpg.add_node('Kurt')
    with pytest.raises(KeyError):
        lpg.add_node('Kurt')


def test_removing_node_from_empty(lpg):
    """Ensure we get error when removing from empty lpg."""
    with pytest.raises(KeyError):
        del lpg['Kurt']


def test_removing_nodes_with_many_connections(loaded_lpg):
    """Ensure relationships to deleted node are cleared."""
    loaded_lpg.add_node('Isolated')
    loaded_lpg.add_node('Wendy')
    for node in ['Charlie', 'Unicorn', 'Pegasus']:
        loaded_lpg.add_relationship('Wendy', node, 'friends')
    for rel, node in zip(['boss', 'parent', 'administrator'],
                         ['Charlie', 'Unicorn', 'Pegasus']):
        loaded_lpg.add_relationship(node, 'Wendy', rel)
    del loaded_lpg['Wendy']
    for rel in loaded_lpg._relationships:
        assert 'Wendy' not in loaded_lpg._relationships[rel]


def test_get_neighbors(loaded_lpg):
    """Test get_neighbors method."""
    loaded_lpg.add_node('Wendy')
    loaded_lpg.add_node('Teddy')
    for node in loaded_lpg.nodes:
        if node != 'Wendy':
            loaded_lpg.add_relationship('Wendy', node, 'buddy')
    all_nodes = set(loaded_lpg.nodes)
    all_nodes.remove('Wendy')
    assert set(loaded_lpg.neighbors('Wendy')) == all_nodes


def test_adjacency(loaded_lpg):
    """Test returns correct neighbors."""
    loaded_lpg.add_node('Wendy')
    loaded_lpg.add_node('Teddy')
    for node in loaded_lpg.nodes:
        if node != 'Wendy':
            loaded_lpg.add_relationship(node, 'Wendy', 'buddy')
    assert all([loaded_lpg.adjacent('Teddy', 'Wendy'),
               loaded_lpg.adjacent('Charlie', 'Wendy'),
               loaded_lpg.adjacent('Unicorn', 'Wendy'),
               loaded_lpg.adjacent('Pegasus', 'Wendy')])


def test_add_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie']['kidneys'] = 1
    assert loaded_lpg._nodes['Charlie']._properties == {'kidneys': 1}


def test_get_node_properties(loaded_lpg):
    """Verify getitem is working correctly."""
    loaded_lpg['Charlie']['kidneys'] = 1
    loaded_lpg['Pegasus']['horns'] = 1
    assert all([loaded_lpg['Pegasus']['horns'] == 1,
                loaded_lpg['Charlie']['kidneys'] == 1])


def test_get_node_properties_method(loaded_lpg):
    """Verify properties method is working correctly."""
    loaded_lpg['Charlie']['kidneys'] = 1
    loaded_lpg['Charlie']['horns'] = 1
    assert loaded_lpg['Charlie'].properties == ['kidneys', 'horns']


def test_change_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie']['kidneys'] = 2
    loaded_lpg['Pegasus']['horns'] = 1
    assert all([loaded_lpg['Pegasus']['horns'] == 1,
                loaded_lpg['Charlie']['kidneys'] == 2])
    loaded_lpg['Charlie']['kidneys'] = 1
    loaded_lpg['Pegasus']['horns'] = 0
    assert all([loaded_lpg['Pegasus']['horns'] == 0,
                loaded_lpg['Charlie']['kidneys'] == 1])


def test_rm_node_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie']['kidneys'] = 1
    assert loaded_lpg._nodes['Charlie']['kidneys'] == 1
    del loaded_lpg['Charlie']['kidneys']
    assert not loaded_lpg._nodes['Charlie']._properties.get('kidneys')


def test_remove_node_DNE_prop(loaded_lpg):
    """Test that we raise an error if removing DNE prop."""
    loaded_lpg['Charlie']['kidneys'] = 1
    with pytest.raises(KeyError):
        del loaded_lpg['Charlie']['kids']


def test_add_label_node(loaded_lpg):
    """Test that we successfully add labels to a node."""
    loaded_lpg['Charlie'].add_label('fantastic')
    assert loaded_lpg['Charlie'].labels == ['fantastic']


def test_add_label_node_error(loaded_lpg):
    """Test that we successfully add labels to a node."""
    loaded_lpg['Charlie'].add_label('fantastic')
    with pytest.raises(ValueError):
        loaded_lpg['Charlie'].add_label('fantastic')


def test_remove_label_node(loaded_lpg):
    """Test that labels are removed appropriately."""
    loaded_lpg['Charlie'].add_label('fantastic')
    loaded_lpg['Charlie'].remove_label('fantastic')
    assert loaded_lpg['Charlie'].labels == []


# # ================== Relationsihps ================


def test_adding_rel_to_empty_lpg(lpg):
    """Ensure we can't add relationships between nonexistent nodes."""
    with pytest.raises(KeyError):
        lpg.add_relationship('Will', 'Bill', 'durka')


def test_adding_rel_one_node_dne(lpg):
    """Ensure we can add relationships between existent and non-existent."""
    lpg.add_node('Kurt')
    with pytest.raises(KeyError):
        lpg.add_relationship('Kurt', 'Bill', 'durka')


def test_adding_rel_other_dne(lpg):
    """Ensure second parameter works as well."""
    lpg.add_node('Billy')
    with pytest.raises(KeyError):
        lpg.add_relationship('Kurt', 'Billy', 'durka')


def test_adding_rel_success(lpg):
    """Ensure successful of adding a relationship."""
    lpg.add_node('Kurt')
    lpg.add_node('Meliss')
    lpg.add_relationship('Kurt', 'Meliss', 'rel')
    assert lpg.unique_relationships() == {'rel'}


def test_adding_rel_success_view(lpg):
    """Ensure we can see the relationship."""
    lpg.add_node('Kurt')
    lpg.add_node('Meliss')
    lpg.add_relationship('Kurt', 'Meliss', 'rel')
    assert (list(lpg.get_relationships('Kurt', 'Meliss')),
            lpg['Kurt', 'Meliss']['rel'].name) == \
        (['rel'], 'rel')


def test_adding_existent_rel(lpg):
    """Ensure we get the proper key erro."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies')
    with pytest.raises(ValueError):
        lpg.add_relationship('Charlie', 'Unicorn', 'buddies')


def test_adding_existent_rel_both_ways(lpg):
    """Ensure we get the proper key erro."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies')
    with pytest.raises(ValueError):
        lpg.add_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)


def test_adding_both_ways_success_graph(lpg):
    """Ensure successful both ways relationship add."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)
    assert (lpg['Charlie', 'Unicorn']['buddies'].name,
            lpg['Unicorn', 'Charlie']['buddies'].name) == ('buddies', 'buddies')


def test_conditionals_in_add_rels(lpg):
    """Ensure we successfully add rels b/w nodes."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)
    lpg.add_relationship('Charlie', 'Pegasus', 'buddies')
    assert (lpg.get_relationships('Charlie', 'Unicorn'),
            lpg.get_relationships('Charlie', 'Pegasus'),
            lpg.get_relationships('Unicorn', 'Charlie')) == \
        (['buddies'], ['buddies'], ['buddies'])


def test_adding_another_rel_between_nodes(lpg):
    """Ensure we except attribute error."""
    lpg.add_node('Charlie')
    lpg.add_node('Unicorn')
    lpg.add_node('Pegasus')
    lpg.add_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)
    lpg.add_relationship('Charlie', 'Unicorn', 'cousins')
    assert sorted(list(lpg['Charlie', 'Unicorn'].keys())) == \
        sorted(['buddies', 'cousins'])


def test_removing_rel(loaded_lpg):
    """Ensure relationships can be removed."""
    del loaded_lpg['Charlie', 'Unicorn']['cousins']
    assert list(loaded_lpg['Charlie', 'Unicorn'].keys()) == ['buddies']


def test_removing_all_rels_between_nodes(loaded_lpg):
    """Ensure all relationships are removed."""
    del loaded_lpg['Charlie', 'Unicorn']
    assert loaded_lpg._relationships.get(('Charlie', 'Unicorn')) is None


def test_getting_all_rels_in_graph(loaded_lpg):
    """Ensure we get a list of all rels."""
    assert loaded_lpg.relationships == ['buddies', 'cousins']


def test_removing_rel_single(loaded_lpg):
    """Ensure relationships can be removed."""
    del loaded_lpg['Charlie', 'Unicorn']['cousins']
    del loaded_lpg['Charlie', 'Unicorn']['buddies']
    with pytest.raises(KeyError):
        del loaded_lpg['Charlie', 'Unicorn']['raisins']


def test_add_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] = 1985
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].properties == ['since']


def test_change_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] = 1985
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].properties == ['since']
    loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] = 1986
    assert loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] == 1986


def test_rm_rel_properties(loaded_lpg):
    """Test that we can add node properties."""
    loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] = 1985
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].properties == ['since']
    del loaded_lpg['Charlie', 'Unicorn']['buddies']['since']
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].properties == []


def test_adding_self_ref_rel(loaded_lpg):
    """Test that we get an error when trying to add a rel b/w node and self."""
    with pytest.raises(ValueError):
        loaded_lpg.add_relationship('Charlie', 'Charlie', 'buddies')


def test_get_rel_props(loaded_lpg):
    """Test that we get the appropriate properties back."""
    loaded_lpg['Charlie', 'Unicorn']['buddies']['since'] = 1985
    assert loaded_lpg['Charlie', 'Unicorn']['buddies']._properties == \
        {'since': 1985}


def test_add_label_relationship(loaded_lpg):
    """Test that we successfully add labels to a node."""
    loaded_lpg['Charlie', 'Unicorn']['buddies'].add_label('fantastic')
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].labels == ['fantastic']


def test_add_label_relationship_error(loaded_lpg):
    """Test that we successfully add labels to a node."""
    loaded_lpg['Charlie', 'Unicorn']['buddies'].add_label('fantastic')
    with pytest.raises(ValueError):
        loaded_lpg['Charlie', 'Unicorn']['buddies'].add_label('fantastic')


def test_remove_label_relationship(loaded_lpg):
    """Test that labels are removed appropriately."""
    loaded_lpg['Charlie', 'Unicorn']['buddies'].add_label('fantastic')
    loaded_lpg['Charlie', 'Unicorn']['buddies'].remove_label('fantastic')
    assert loaded_lpg['Charlie', 'Unicorn']['buddies'].labels == []


# # ====================== RETRIEVAL =============================


def test_get_relationships(loaded_lpg):
    """Ensure returns correct relationships."""
    loaded_lpg.add_relationship('Charlie', 'Pegasus', 'guys')
    assert loaded_lpg.get_relationships('Charlie',
                                        'Pegasus') == \
        ['guys']


def test_nodes_with_relationships(loaded_lpg):
    """Ensure returns correction relationships."""
    assert all(['Unicorn' in loaded_lpg.nodes_with_relationship('buddies'),
                'Charlie' in loaded_lpg.nodes_with_relationship('buddies')])


def test_nodes_with_relationships_2(loaded_lpg):
    """Ensure returns keys of _graph."""
    loaded_lpg.add_node('Willy')
    loaded_lpg.add_node('Billy')
    loaded_lpg.add_node('Gilly')
    loaded_lpg.add_node('Lilly')
    for node in loaded_lpg.nodes:
        if node == 'Billy':
            continue
        loaded_lpg.add_relationship('Billy', node, 'acquaintances')
    assert sorted(loaded_lpg.nodes_with_relationship('acquaintances')) == \
        sorted(loaded_lpg.nodes)


def test_has_relationship_true(loaded_lpg):
    """Ensure returns given relationship."""
    assert loaded_lpg.has_relationship('Charlie', 'Unicorn', 'buddies', both_ways=True)


def test_has_relationship_false(loaded_lpg):
    """ensure returns false."""
    assert not loaded_lpg.has_relationship('Charlie', 'Unicorn', 'siblings')
