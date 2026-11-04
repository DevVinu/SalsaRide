const API_BASE = window.location.origin.includes('3000')
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';

const WS_BASE = window.location.origin.includes('3000')
  ? 'ws://localhost:8000/ws'
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

class SmartFlowAPI {
  async getJunctions() {
    try {
      const res = await fetch(`${API_BASE}/junctions`);
      return await res.json();
    } catch (e) {
      console.error('Failed to fetch junctions:', e);
      return [];
    }
  }

  async getTrafficStatus(junctionId) {
    try {
      const res = await fetch(`${API_BASE}/traffic/${junctionId}`);
      return await res.json();
    } catch (e) {
      console.error('Failed to fetch traffic status:', e);
      return null;
    }
  }

  async getSignalState(junctionId) {
    try {
      const res = await fetch(`${API_BASE}/signals/${junctionId}`);
      return await res.json();
    } catch (e) {
      console.error('Failed to fetch signal state:', e);
      return null;
    }
  }

  async getParticipants(junctionId) {
    try {
      const res = await fetch(`${API_BASE}/traffic/${junctionId}/participants`);
      return await res.json();
    } catch (e) {
      return { participants: [] };
    }
  }

  async applyPreset(junctionId, preset) {
    try {
      const res = await fetch(`${API_BASE}/simulation/${junctionId}/preset?preset=${preset}`, {
        method: 'POST',
      });
      return await res.json();
    } catch (e) {
      console.error('Failed to apply preset:', e);
    }
  }

  async injectVehicle(junctionId, corridor, isEmergency = false, fraction = 0.5) {
    try {
      const res = await fetch(`${API_BASE}/simulation/${junctionId}/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corridor,
          distance_fraction: fraction,
          speed_kmh: isEmergency ? 45.0 : 25.0,
          is_emergency: isEmergency,
        }),
      });
      return await res.json();
    } catch (e) {
      console.error('Failed to inject vehicle:', e);
    }
  }

  async stepPhase(junctionId) {
    try {
      const res = await fetch(`${API_BASE}/signals/${junctionId}/step`, {
        method: 'POST',
      });
      return await res.json();
    } catch (e) {
      console.error('Failed to step phase:', e);
    }
  }

  async clearSimulation(junctionId) {
    try {
      const res = await fetch(`${API_BASE}/simulation/${junctionId}/clear`, {
        method: 'DELETE',
      });
      return await res.json();
    } catch (e) {
      console.error('Failed to clear simulation:', e);
    }
  }

  connectWebSocket(junctionId, onMessage, onStatusChange) {
    const url = `${WS_BASE}/junctions/${junctionId}`;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('Connected to SmartFlow WebSocket:', url);
      if (onStatusChange) onStatusChange(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) onMessage(data);
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed. Reconnecting in 3s...');
      if (onStatusChange) onStatusChange(false);
      setTimeout(() => this.connectWebSocket(junctionId, onMessage, onStatusChange), 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      ws.close();
    };

    return ws;
  }
}

const api = new SmartFlowAPI();

