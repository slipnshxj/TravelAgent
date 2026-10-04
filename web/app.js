const state = {
  userId: localStorage.getItem('agent.userId') || 'memory_test_user',
  conversationId: null,
  memories: [],
  tools: [],
  map: null,
  markers: [],
  isChatPending: false,
  isToolPending: false,
  isPlacePending: false,
  memoryRequestId: 0,
  isAmapLoading: false,
};

const elements = {
  status: document.querySelector('#status'),
  userSelect: document.querySelector('#userSelect'),
  customUser: document.querySelector('#customUser'),
  applyUser: document.querySelector('#applyUser'),
  includeArchived: document.querySelector('#includeArchived'),
  memoryList: document.querySelector('#memoryList'),
  messages: document.querySelector('#messages'),
  chatForm: document.querySelector('#chatForm'),
  messageInput: document.querySelector('#messageInput'),
  newConversation: document.querySelector('#newConversation'),
  map: document.querySelector('#map'),
  mapFallback: document.querySelector('#mapFallback'),
  placeForm: document.querySelector('#placeForm'),
  placeInput: document.querySelector('#placeInput'),
  placeResults: document.querySelector('#placeResults'),
  toolSelect: document.querySelector('#toolSelect'),
  toolSchema: document.querySelector('#toolSchema'),
  toolArgs: document.querySelector('#toolArgs'),
  runTool: document.querySelector('#runTool'),
  toolResult: document.querySelector('#toolResult'),
  chatSubmit: document.querySelector('#chatForm button[type="submit"]'),
  placeSubmit: document.querySelector('#placeForm button[type="submit"]'),
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    throw new Error(
      typeof detail === 'string'
        ? detail
        : detail ? JSON.stringify(detail) : `HTTP ${response.status}`,
    );
  }
  return response.json();
}

function setStatus(message) {
  elements.status.textContent = message;
}

function addMessage(content, role = 'assistant') {
  const div = document.createElement('div');
  div.className = `bubble ${role}`;
  div.textContent = content;
  elements.messages.appendChild(div);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function addPendingMessage(label = '正在思考...') {
  const bubble = document.createElement('div');
  bubble.className = 'bubble assistant loading';
  bubble.setAttribute('aria-busy', 'true');
  bubble.setAttribute('data-pending', 'true');

  const spinner = document.createElement('span');
  spinner.className = 'spinner';
  spinner.setAttribute('aria-hidden', 'true');

  const text = document.createElement('span');
  text.className = 'loading-text';
  text.textContent = label;

  bubble.append(spinner, text);
  elements.messages.appendChild(bubble);
  elements.messages.scrollTop = elements.messages.scrollHeight;
  return bubble;
}

function completePendingMessage(pendingBubble, content, role = 'assistant') {
  if (!pendingBubble.isConnected) return;

  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;
  pendingBubble.replaceWith(bubble);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

async function loadConfig() {
  const config = await request('/api/config');
  if (!localStorage.getItem('agent.userId')) {
    state.userId = config.defaultUserId;
  }
}

async function loadUsers() {
  const data = await request('/api/users');
  const fragment = document.createDocumentFragment();
  const users = [...new Set([state.userId, ...data.users])];
  users.forEach((user) => {
    const option = document.createElement('option');
    option.value = user;
    option.textContent = user;
    fragment.appendChild(option);
  });
  elements.userSelect.replaceChildren(fragment);
  elements.userSelect.value = state.userId;
}

function persistUser() {
  localStorage.setItem('agent.userId', state.userId);
  setStatus(`当前用户：${state.userId}`);
}

function normalizeUserId(value) {
  const userId = String(value || '').trim();
  if (!userId || userId.length > 100 || /\s/.test(userId)) return null;
  return userId;
}

async function changeUser(userId, { refreshUsers = false } = {}) {
  const normalizedUserId = normalizeUserId(userId);
  if (!normalizedUserId) {
    setStatus('用户 ID 不能为空、包含空格或超过 100 字符');
    return;
  }

  state.userId = normalizedUserId;
  persistUser();
  await Promise.all([
    refreshUsers ? loadUsers() : Promise.resolve(),
    loadMemories(),
  ]);
}

async function loadMemories() {
  const requestId = ++state.memoryRequestId;
  const params = new URLSearchParams({
    user_id: state.userId,
    include_archived: elements.includeArchived.checked ? 'true' : 'false',
  });
  const data = await request(`/api/memories?${params}`);
  if (requestId !== state.memoryRequestId) return;
  state.memories = data.memories;
  renderMemories();
}

function renderMemories() {
  const fragment = document.createDocumentFragment();
  if (!state.memories.length) {
    const empty = document.createElement('div');
    empty.className = 'memory';
    empty.textContent = '暂无记忆';
    elements.memoryList.replaceChildren(empty);
    return;
  }
  state.memories.forEach((memory) => {
    const item = document.createElement('div');
    item.className = `memory${memory.is_active ? '' : ' archived'}`;
    const title = document.createElement('strong');
    title.textContent = `[${memory.category}] ${memory.content}`;
    const meta = document.createElement('div');
    meta.className = 'memory-meta';
    const importance = document.createElement('span');
    importance.textContent = `优先级 ${memory.importance}`;
    const status = document.createElement('span');
    status.textContent = memory.is_active ? '活跃' : '已归档';
    meta.append(importance, status);
    const actions = document.createElement('div');
    actions.className = 'memory-actions';
    const archive = document.createElement('button');
    archive.textContent = memory.is_active ? '归档' : '恢复';
    archive.onclick = async (event) => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await request(`/api/memories/${memory.id}/archive?user_id=${encodeURIComponent(state.userId)}`, {
          method: 'PATCH',
          body: JSON.stringify({ archived: memory.is_active }),
        });
        await loadMemories();
      } catch (error) {
        setStatus(`记忆操作失败：${error.message}`);
      } finally {
        button.disabled = false;
      }
    };
    const remove = document.createElement('button');
    remove.className = 'danger';
    remove.textContent = '删除';
    remove.onclick = async (event) => {
      if (!confirm('确认删除这条记忆？')) return;
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await request(`/api/memories/${memory.id}?user_id=${encodeURIComponent(state.userId)}`, { method: 'DELETE' });
        await loadMemories();
      } catch (error) {
        setStatus(`记忆删除失败：${error.message}`);
      } finally {
        button.disabled = false;
      }
    };
    actions.append(archive, remove);
    item.append(title, meta, actions);
    fragment.appendChild(item);
  });
  elements.memoryList.replaceChildren(fragment);
}

async function startConversation() {
  const data = await request('/api/conversations', { method: 'POST' });
  state.conversationId = data.conversationId;
  elements.messages.replaceChildren();
  addMessage('新对话已开启。', 'assistant');
}

async function loadTools() {
  const data = await request('/api/tools');
  state.tools = data.tools;
  const fragment = document.createDocumentFragment();
  state.tools.forEach((tool) => {
    const option = document.createElement('option');
    option.value = tool.name;
    option.textContent = tool.name;
    fragment.appendChild(option);
  });
  elements.toolSelect.replaceChildren(fragment);
  renderToolSchema();
}

function renderToolSchema() {
  const tool = state.tools.find((item) => item.name === elements.toolSelect.value);
  elements.toolSchema.textContent = tool ? JSON.stringify(tool.inputSchema, null, 2) : '{}';
}

function loadAmap(config) {
  if (!config.configured) return;
  if (state.isAmapLoading) return;

  state.isAmapLoading = true;
  elements.mapFallback.style.display = 'none';
  if (config.securityJsCode) {
    window._AMapSecurityConfig = { securityJsCode: config.securityJsCode };
  }

  const script = document.createElement('script');
  script.src = `https://webapi.amap.com/maps?v=${config.version}&key=${encodeURIComponent(config.jsKey)}`;
  script.onload = () => {
    try {
      state.map = new AMap.Map(elements.map, {
        center: config.center,
        zoom: config.zoom,
      });
    } catch (error) {
      elements.mapFallback.textContent = `高德地图加载失败：${error.message}`;
      elements.mapFallback.style.display = 'grid';
    } finally {
      state.isAmapLoading = false;
    }
  };
  script.onerror = () => {
    state.isAmapLoading = false;
    elements.mapFallback.textContent = '高德地图脚本加载失败，请检查网络和 AMAP_JS_KEY。';
    elements.mapFallback.style.display = 'grid';
  };
  document.head.appendChild(script);
}

function clearPlaceMarkers() {
  if (state.map && state.markers.length) {
    state.map.remove(state.markers);
  }
  state.markers = [];
}

function renderPlaceMarkers(pois) {
  if (!state.map || !window.AMap) return;

  clearPlaceMarkers();
  pois.forEach((poi) => {
    if (!poi.location) return;
    const [lng, lat] = poi.location.split(',').map(Number);
    if (!Number.isFinite(lng) || !Number.isFinite(lat)) return;

    const marker = new AMap.Marker({
      position: [lng, lat],
      title: poi.name,
    });
    state.map.add(marker);
    state.markers.push(marker);
  });

  if (state.markers.length) {
    state.map.setFitView(state.markers, false, [40, 40, 40, 40]);
  }
}

async function init() {
  try {
    await Promise.all([loadConfig(), request('/api/health')]);
    persistUser();
    const [usersResult, memoriesResult] = await Promise.allSettled([
      loadUsers(),
      loadMemories(),
    ]);
    await Promise.all([loadTools(), startConversation()]);
    const mapConfig = await request('/api/map/config');
    loadAmap(mapConfig);

    const warnings = [];
    if (usersResult.status === 'rejected') warnings.push('用户列表不可用');
    if (memoriesResult.status === 'rejected') warnings.push('记忆服务不可用');
    setStatus(
      `API 已连接 | 当前用户：${state.userId}`
      + (warnings.length ? ` | ${warnings.join('、')}` : ''),
    );
  } catch (error) {
    setStatus(`初始化失败：${error.message}`);
  }
}

elements.userSelect.addEventListener('change', () => {
  changeUser(elements.userSelect.value);
});

elements.applyUser.addEventListener('click', async () => {
  await changeUser(elements.customUser.value, { refreshUsers: true });
});

elements.includeArchived.addEventListener('change', loadMemories);
elements.newConversation.addEventListener('click', startConversation);

elements.chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (state.isChatPending) return;

  const message = elements.messageInput.value.trim();
  if (!message) return;

  state.isChatPending = true;
  elements.chatSubmit.disabled = true;
  elements.chatSubmit.textContent = '发送中';
  addMessage(message, 'user');
  elements.messageInput.value = '';
  const pendingBubble = addPendingMessage();

  try {
    const result = await request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        user_id: state.userId,
        message,
        conversation_id: state.conversationId,
      }),
    });
    state.conversationId = result.conversationId;
    completePendingMessage(
      pendingBubble,
      result.error || result.finalResult || result.planResult || result.researchResult,
    );
    if (result.mapTargets?.length) {
      renderPlaceMarkers(result.mapTargets);
      elements.placeInput.value = result.mapKeyword || '';
      elements.placeResults.textContent = result.mapTargets
        .map((poi) => `${poi.name} ${poi.address || ''}`)
        .join('\n');
    } else if (result.mapError) {
      elements.placeResults.textContent = result.mapError;
    }
    await loadMemories();
  } catch (error) {
    completePendingMessage(pendingBubble, error.message, 'error');
  }
  finally {
    state.isChatPending = false;
    elements.chatSubmit.disabled = false;
    elements.chatSubmit.textContent = '发送';
    elements.messageInput.focus();
  }
});

elements.toolSelect.addEventListener('change', renderToolSchema);

elements.runTool.addEventListener('click', async () => {
  if (state.isToolPending) return;

  state.isToolPending = true;
  elements.runTool.disabled = true;
  try {
    const args = JSON.parse(elements.toolArgs.value || '{}');
    const result = await request(`/api/tools/${encodeURIComponent(elements.toolSelect.value)}/invoke`, {
      method: 'POST',
      body: JSON.stringify({ arguments: args }),
    });
    elements.toolResult.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    elements.toolResult.textContent = error.message;
  } finally {
    state.isToolPending = false;
    elements.runTool.disabled = false;
  }
});

elements.placeForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (state.isPlacePending) return;

  const keywords = elements.placeInput.value.trim();
  if (!keywords) return;

  state.isPlacePending = true;
  elements.placeSubmit.disabled = true;
  try {
    const result = await request(`/api/map/places?keywords=${encodeURIComponent(keywords)}`);
    const pois = result.pois || [];
    elements.placeResults.textContent = pois
      .map((poi) => `${poi.name} ${poi.address || ''}`)
      .join('\n');
    renderPlaceMarkers(pois);
  } catch (error) {
    elements.placeResults.textContent = error.message;
  } finally {
    state.isPlacePending = false;
    elements.placeSubmit.disabled = false;
  }
});

init();
