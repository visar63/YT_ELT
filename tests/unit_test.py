def test_api_key(api_key):
    assert api_key == "MOCK_KEY1234"

def test_channel_handle(channel_handle):
    assert channel_handle == "ArianaGrande"

def test_postgres_conn(mock_postgress_conn_vars):
    conn = mock_postgress_conn_vars
    assert conn.login == "mock_user"
    assert conn.password == "mock_password"
    assert conn.host == "mock_host"
    assert conn.port == 1234
    assert conn.schema == "mock_schema"


def test_dags_integrity(dag_bag):
    # lets split in 4 parts
    # 1. Check for import errors
    assert len(dag_bag.import_errors) == 0, f"DAG import errors: {dag_bag.import_errors}"
    print("==============")
    print(dag_bag.import_errors)

    # 2. Check for the number of DAGs loaded
    expected_dag_ids = ["youtube_video_stats", "update_db", "data_quality_checks"]
    loaded_dag_ids = list(dag_bag.dags.keys())
    print("=== Loaded DAG IDs ===")
    print(loaded_dag_ids)
    assert set(expected_dag_ids) == set(loaded_dag_ids), f"Expected DAGs: {expected_dag_ids}, but found: {loaded_dag_ids}"

    # 3. Check for the number of dags
    assert dag_bag.size() == 3
    print("==============")
    print(dag_bag.size())

    # 4. Check if dag has number of tasks we expect
    expected_task_count = {
        "youtube_video_stats": 4,
        "update_db": 2,
        "data_quality_checks": 2,
    }
    for dag_id in expected_dag_ids:
        assert dag_id in dag_bag.dags, f"DAG {dag_id} not found in the DagBag"
        dag = dag_bag.get_dag(dag_id)
        task_length = len(dag.tasks)
        assert task_length > 0, f"DAG {dag_id} has no tasks"
        print("=== Number of Tasks ===")
        print(f'DAG "{dag_id}" has {task_length} tasks')
        assert task_length == expected_task_count[dag_id], f"DAG {dag_id} has {task_length} tasks, expected {expected_task_count[dag_id]}"
