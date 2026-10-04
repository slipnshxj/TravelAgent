from fastapi.testclient import TestClient

import api


client = TestClient(api.app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_is_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Agent Object 控制台" in response.text
    assert 'id="map"' in response.text


def test_frontend_has_pending_message_ui() -> None:
    response = client.get("/app.js")
    assert response.status_code == 200
    assert "addPendingMessage" in response.text
    assert "completePendingMessage" in response.text
    assert "spinner" in response.text


def test_frontend_assets_are_cache_busted() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "styles.css?v=20261003-2" in response.text
    assert "app.js?v=20261003-2" in response.text


def test_topbar_allows_full_status_text() -> None:
    response = client.get("/styles.css")
    assert response.status_code == 200
    assert "#newConversation" in response.text
    assert "white-space: nowrap" in response.text
    assert "#status" in response.text


def test_map_config(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_JS_KEY", "test-js-key")
    response = client.get("/api/map/config")
    assert response.status_code == 200
    body = response.json()
    assert body["configured"] is True
    assert body["jsKey"] == "test-js-key"


def test_memories_endpoint(monkeypatch) -> None:
    def fake_list_memories(**kwargs):
        return [(1, kwargs["user_id"], "preference", "喜欢北京", 5, "manual", True, None, None)]

    monkeypatch.setattr(api, "list_memories", fake_list_memories)
    response = client.get("/api/memories", params={"user_id": "user-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["memories"][0]["id"] == 1
    assert body["memories"][0]["is_active"] is True


def test_archive_requires_existing_memory(monkeypatch) -> None:
    monkeypatch.setattr(api, "archive_memory", lambda *args, **kwargs: False)
    response = client.patch(
        "/api/memories/999/archive",
        params={"user_id": "user-1"},
        json={"archived": True},
    )
    assert response.status_code == 404


def test_create_memory_returns_id(monkeypatch) -> None:
    monkeypatch.setattr(api, "save_memory", lambda **kwargs: 123)
    response = client.post(
        "/api/memories",
        json={
            "user_id": "user-1",
            "category": "preference",
            "content": "喜欢安静的城市",
            "importance": 5,
        },
    )
    assert response.status_code == 201
    assert response.json() == {"id": 123}


def test_delete_memory_success(monkeypatch) -> None:
    monkeypatch.setattr(api, "delete_memory", lambda *args, **kwargs: True)
    response = client.delete("/api/memories/1", params={"user_id": "user-1"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "deleted": True}


def test_tools_endpoint(monkeypatch) -> None:
    async def fake_list_tools():
        return [{"name": "weather", "description": "weather", "inputSchema": {"type": "object"}}]

    monkeypatch.setattr(api.tool_gateway, "list_tools", fake_list_tools)
    response = client.get("/api/tools")
    assert response.status_code == 200
    assert response.json()["tools"][0]["name"] == "weather"


def test_new_conversation() -> None:
    response = client.post("/api/conversations")
    assert response.status_code == 200
    assert response.json()["conversationId"]


def test_extract_map_keyword_find_place() -> None:
    assert api.extract_map_keyword("帮我找一下故宫") == "故宫"
    assert api.extract_map_keyword("故宫在哪里") == "故宫"
    assert api.extract_map_keyword("帮我查找颐和园的位置") == "颐和园"
    assert api.extract_map_keyword("今天天气怎么样") is None


def test_chat_returns_map_targets(monkeypatch) -> None:
    async def fake_run_travel_workflow(user_id, message):
        return {
            "researchResult": "research",
            "planResult": "plan",
            "finalResult": "final",
            "error": "",
        }

    async def fake_build_map_context(message):
        return {
            "keyword": "故宫",
            "targets": [{"name": "故宫", "address": "北京", "location": "116.397,39.918"}],
            "error": "",
        }

    monkeypatch.setattr(api, "run_travel_workflow", fake_run_travel_workflow)
    monkeypatch.setattr(api, "build_map_context", fake_build_map_context)
    response = client.post(
        "/api/chat",
        json={"user_id": "user-1", "message": "帮我找一下故宫"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mapKeyword"] == "故宫"
    assert body["mapTargets"][0]["name"] == "故宫"
