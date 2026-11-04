let smartMap = null;
let currentJunction = null;
let activeWs = null;

document.addEventListener('DOMContentLoaded', async () => {
  smartMap = new SmartFlowMap('map-container');

  // Handle map click to inject vehicle
  window.onMapClicked = (lat, lon) => {
    if (!currentJunction) return;
    // Inject at clicked location
    fetch(`${API_BASE}/traffic/ping`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        speed_kmh: 22.0,
      }),
    }).then(() => refreshData());
  };

  // Force step button
  const stepBtn = document.getElementById('btn-force-step');
  if (stepBtn) {
    stepBtn.addEventListener('click', () => {
      if (currentJunction) {
        api.stepPhase(currentJunction.id).then(() => refreshData());
      }
    });
  }

  // Load junctions
  await initJunctions();
});

async function initJunctions() {
  const junctions = await api.getJunctions();
  const select = document.getElementById('junction-select');
  select.innerHTML = '';

  if (!junctions.length) {
    select.innerHTML = '<option value="">No junctions found</option>';
    return;
  }

  junctions.forEach((j) => {
    const opt = document.createElement('option');
    opt.value = j.id;
    opt.textContent = `${j.name} (${j.junction_code})`;
    select.appendChild(opt);
  });

  select.addEventListener('change', (e) => {
    const selected = junctions.find((j) => j.id === e.target.value);
    if (selected) selectJunction(selected);
  });

  selectJunction(junctions[0]);
}

function selectJunction(junction) {
  currentJunction = junction;

  // Update details card
  document.getElementById('junc-code-badge').textContent = junction.junction_code;
  document.getElementById('junc-name').textContent = junction.name;
  document.getElementById('junc-address').textContent = junction.address;
  document.getElementById('junc-coords').textContent = `${junction.latitude.toFixed(4)}, ${junction.longitude.toFixed(4)}`;
  document.getElementById('junc-radius').textContent = `${junction.detection_radius_meters}m`;
  document.getElementById('junc-inner').textContent = `${junction.inner_zone_meters}m`;

  // Update map view
  smartMap.setJunction(junction);

  // Reconnect WebSocket
  if (activeWs) activeWs.close();
  activeWs = api.connectWebSocket(
    junction.id,
    (msg) => handleWsMessage(msg),
    (isConnected) => {
      const statusEl = document.getElementById('ws-status');
      if (statusEl) {
        statusEl.className = isConnected ? 'badge badge-green' : 'badge badge-red';
        statusEl.textContent = isConnected ? '● Connected' : '○ Disconnected';
      }
    }
  );

  refreshData();
}

function handleWsMessage(data) {
  if (data.signal_state) {
    signalVisualizer.updateState(data.signal_state);
  }
  if (data.corridors) {
    updateCorridorCards(data.corridors);
  }
}

async function refreshData() {
  if (!currentJunction) return;

  const [traffic, signal, parts] = await Promise.all([
    api.getTrafficStatus(currentJunction.id),
    api.getSignalState(currentJunction.id),
    api.getParticipants(currentJunction.id),
  ]);

  if (signal) signalVisualizer.updateState(signal);
  if (traffic && traffic.corridors) updateCorridorCards(traffic.corridors);

  if (parts && parts.participants) {
    document.getElementById('active-count-display').textContent = `${parts.participants.length} vehicles tracked`;
  }
}

function updateCorridorCards(corridors) {
  const directions = ['NORTH', 'SOUTH', 'EAST', 'WEST'];

  directions.forEach((dir) => {
    const data = corridors[dir];
    if (!data) return;

    const countEl = document.getElementById(`count-${dir}`);
    const innerEl = document.getElementById(`inner-${dir}`);
    const waitEl = document.getElementById(`wait-${dir}`);
    const scoreEl = document.getElementById(`score-${dir}`);
    const badgeEl = document.getElementById(`badge-${dir}`);

    if (countEl) countEl.textContent = data.vehicle_count;
    if (innerEl) innerEl.textContent = data.inner_zone_count;
    if (waitEl) waitEl.textContent = `${data.average_wait_time_seconds}s`;
    if (scoreEl) scoreEl.textContent = data.priority_score ? data.priority_score.toFixed(1) : '0.0';

    if (badgeEl) {
      badgeEl.textContent = data.congestion_level;
      if (data.congestion_level === 'OVERCROWDED') {
        badgeEl.className = 'badge badge-red';
      } else if (data.congestion_level === 'MODERATE') {
        badgeEl.className = 'badge badge-amber';
      } else {
        badgeEl.className = 'badge badge-green';
      }
    }
  });
}

// Preset Handler
window.applyPreset = async (preset) => {
  if (!currentJunction) return;
  await api.applyPreset(currentJunction.id, preset);
  refreshData();
};

// Single Vehicle Inject
window.injectVehicle = async (isEmergency) => {
  if (!currentJunction) return;
  const corridor = document.getElementById('inject-corridor').value;
  await api.injectVehicle(currentJunction.id, corridor, isEmergency);
  refreshData();
};

// Clear Simulation
window.clearSimulation = async () => {
  if (!currentJunction) return;
  await api.clearSimulation(currentJunction.id);
  refreshData();
};

