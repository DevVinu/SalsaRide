class SignalVisualizer {
  updateState(signalState) {
    if (!signalState) return;

    const nsLamp = signalState.north_south_lamp;
    const ewLamp = signalState.east_west_lamp;
    const remaining = signalState.remaining_seconds;
    const phase = signalState.current_phase;

    // Phase badge
    const badge = document.getElementById('phase-badge');
    if (badge) {
      badge.textContent = phase;
      if (phase.includes('GREEN')) {
        badge.className = 'badge badge-green';
      } else if (phase.includes('YELLOW')) {
        badge.className = 'badge badge-amber';
      } else {
        badge.className = 'badge badge-red';
      }
    }

    // NS Lamps
    this.setLamp('ns-red', nsLamp === 'RED');
    this.setLamp('ns-yellow', nsLamp === 'YELLOW');
    this.setLamp('ns-green', nsLamp === 'GREEN');

    // EW Lamps
    this.setLamp('ew-red', ewLamp === 'RED');
    this.setLamp('ew-yellow', ewLamp === 'YELLOW');
    this.setLamp('ew-green', ewLamp === 'GREEN');

    // Countdowns
    const nsCount = document.getElementById('ns-countdown');
    const ewCount = document.getElementById('ew-countdown');

    if (nsLamp === 'GREEN' || nsLamp === 'YELLOW') {
      if (nsCount) nsCount.textContent = `${remaining}s`;
      if (ewCount) ewCount.textContent = '--';
    } else {
      if (nsCount) nsCount.textContent = '--';
      if (ewCount) ewCount.textContent = `${remaining}s`;
    }

    // Priority & Allocation text
    const priorityText = document.getElementById('priority-corridor-text');
    if (priorityText) {
      priorityText.textContent = signalState.priority_corridor || 'NORTH';
    }

    const durationText = document.getElementById('signal-duration-text');
    if (durationText) {
      durationText.textContent = `Phase Allocation: ${signalState.phase_duration_seconds}s`;
    }
  }

  setLamp(elementId, isActive) {
    const el = document.getElementById(elementId);
    if (el) {
      if (isActive) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    }
  }
}

const signalVisualizer = new SignalVisualizer();

