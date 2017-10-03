from aztk.clusterlib import Cluster
import azure.batch.models as batch_models

clusterlib = Cluster(None, None, None, None, None)

def create_mock_cluster(
        pool_id='test',
        vm_size='standard_f2',
        target_dedicated_nodes=3,
        current_dedcated_nodes=0,
        target_low_priority_nodes=2,
        current_low_priority_nodes=0,
        state=batch_models.PoolState.active,
        allocation_state=batch_models.AllocationState.resizing
) -> batch_models.CloudPool:
    pool = batch_models.CloudPool(
        id=pool_id,
        current_low_priority_nodes=current_low_priority_nodes,
        target_low_priority_nodes=target_low_priority_nodes,
        current_dedicated_nodes=current_dedcated_nodes,
        target_dedicated_nodes=target_dedicated_nodes,
        vm_size=vm_size,
        state=state,
        allocation_state=allocation_state
    )
    cluster = clusterlib.ClusterModel(pool)
    return cluster


def test_node_count_steady():
    cluster = create_mock_cluster(
        current_dedcated_nodes=3,
        current_low_priority_nodes=2,
        allocation_state=batch_models.AllocationState.steady
    )
    expected_value = '5'
    value = clusterlib.pretty_node_count(cluster)
    assert expected_value == value


def test_node_count_resizing():
    cluster = create_mock_cluster()
    expected_value = '0 -> 5'
    value = clusterlib.pretty_node_count(cluster)
    assert expected_value == value


def test_pretty_print_dedicated_nodes_steady():
    cluster = create_mock_cluster(
        current_dedcated_nodes=3,
        allocation_state=batch_models.AllocationState.steady
    )
    expected_value = '3'
    value = clusterlib.pretty_dedicated_node_count(cluster)
    assert expected_value == value


def test_pretty_print_dedicated_nodes_resizing():
    cluster = create_mock_cluster()
    expected_value = '0 -> 3'
    value = clusterlib.pretty_dedicated_node_count(cluster)
    assert expected_value == value


def test_pretty_print_low_priority_nodes_steady():
    cluster = create_mock_cluster(
        current_low_priority_nodes=2,
        allocation_state=batch_models.AllocationState.steady
    )
    expected_value = '2'
    value = clusterlib.pretty_low_pri_node_count(cluster)
    assert expected_value == value


def test_pretty_print_low_priority_nodes_resizing():
    cluster = create_mock_cluster()
    expected_value = '0 -> 2'
    value = clusterlib.pretty_low_pri_node_count(cluster)
    assert expected_value == value
