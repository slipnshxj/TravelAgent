import anyio


def test_workflow_import_inside_running_event_loop() -> None:
    async def import_workflow():
        from graph.workflow import graph

        return graph is not None

    assert anyio.run(import_workflow) is True
