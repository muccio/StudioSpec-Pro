// StudioSpec Pro - Client Application Logic

let allDevices = [];
let currentFilter = 'all';
let calcSampleRate = 48000;
let calcBufferSize = 128;

document.addEventListener('DOMContentLoaded', () => {
  fetchDiagnostics();
  fetchDrives();
  updateLatencyCalc();
});

async function fetchDiagnostics() {
  try {
    const res = await fetch('/api/report');
    const data = await res.json();
    renderReport(data);
  } catch (err) {
    console.error('Error fetching diagnostics:', err);
  }
}

async function refreshDiagnostics() {
  const hostPill = document.getElementById('hostPill');
  hostPill.classList.add('loading');
  try {
    const res = await fetch('/api/refresh');
    const data = await res.json();
    renderReport(data);
  } catch (err) {
    console.error('Error refreshing diagnostics:', err);
  } finally {
    hostPill.classList.remove('loading');
  }
}

async function fetchDrives() {
  try {
    const res = await fetch('/api/drives');
    const data = await res.json();
    const select = document.getElementById('driveSelect');
    select.innerHTML = '';
    (data.drives || []).forEach(d => {
      const opt = document.createElement('option');
      opt.value = d.mount_point;
      opt.textContent = `${d.name} (${d.free_gb} GB liberi su ${d.total_gb} GB)`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Error fetching drives:', err);
  }
}

function renderReport(data) {
  // Metadata
  document.getElementById('hostname').textContent = data.hostname || 'Local Workstation';
  document.getElementById('platformText').textContent = data.platform || 'macOS';

  // 1. Score & Gauge
  const score = data.score || {};
  const total = score.total_score || 0;
  document.getElementById('totalScoreNum').textContent = total;
  document.getElementById('tierBadge').textContent = score.tier_badge || 'VALUTATO';
  document.getElementById('tierTitle').textContent = score.tier || 'Studio Workstation';
  document.getElementById('tierDesc').textContent = score.tier_description || '';

  // Animate Gauge
  const circle = document.getElementById('scoreCircle');
  const circumference = 2 * Math.PI * 70; // ~440
  const offset = circumference - (total / 100) * circumference;
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${offset}`;

  // Breakdown Bars
  const audioPct = ((score.audio_io_score || 0) / 30) * 100;
  const cpuPct = ((score.cpu_dsp_score || 0) / 30) * 100;
  const ramPct = ((score.ram_sample_score || 0) / 25) * 100;
  const storagePct = ((score.storage_dfd_score || 0) / 15) * 100;

  document.getElementById('audioIoScore').textContent = `${score.audio_io_score} / 30`;
  document.getElementById('cpuDspScore').textContent = `${score.cpu_dsp_score} / 30`;
  document.getElementById('ramSampleScore').textContent = `${score.ram_sample_score} / 25`;
  document.getElementById('storageDfdScore').textContent = `${score.storage_dfd_score} / 15`;

  document.getElementById('fillAudio').style.width = `${audioPct}%`;
  document.getElementById('fillCpu').style.width = `${cpuPct}%`;
  document.getElementById('fillRam').style.width = `${ramPct}%`;
  document.getElementById('fillStorage').style.width = `${storagePct}%`;

  // 2. Hardware Specs
  const cpu = data.cpu || {};
  document.getElementById('cpuModel').textContent = cpu.model || '--';
  document.getElementById('cpuTopology').textContent = `${cpu.physical_cores} Cores (${cpu.performance_cores} P-Cores, ${cpu.efficiency_cores} E-Cores, ${cpu.logical_threads} Threads)`;
  document.getElementById('cpuSimd').textContent = (cpu.simd_features || []).slice(0, 2).join(', ') || 'SIMD Standard';

  const ram = data.ram || {};
  document.getElementById('ramTotal').textContent = `${ram.total_gb} GB RAM`;
  document.getElementById('ramSwap').textContent = `${ram.memory_type} (Swap: ${ram.swap_used_mb} MB - ${ram.swap_pressure})`;

  const storage = data.storage || {};
  document.getElementById('storageName').textContent = `${storage.primary_drive_name} (${storage.medium_type})`;
  document.getElementById('storageSpace').textContent = `${storage.free_gb} GB liberi su ${storage.total_gb} GB (${storage.free_percentage}%) • DFD: ${storage.dfd_streaming_readiness}`;

  const osInfo = data.os_info || {};
  document.getElementById('audioSubsystem').textContent = osInfo.audio_subsystem || '--';
  document.getElementById('audioDaemon').textContent = `${osInfo.audio_daemon_status} • ${osInfo.power_plan}`;
  document.getElementById('pluginFormats').textContent = (osInfo.plugin_formats_supported || []).join(', ') || '--';

  // 3. Audio Devices Table
  allDevices = data.audio_devices || [];
  document.getElementById('devCount').textContent = allDevices.length;
  renderDevicesTable();

  // 4. Disk Benchmark & Kontakt DFD
  if (data.disk_benchmark) {
    renderBenchmarkResults(data.disk_benchmark);
  }

  // 5. DAW Readiness
  const dawContainer = document.getElementById('dawList');
  dawContainer.innerHTML = '';
  (score.daw_readiness || []).forEach(d => {
    const item = document.createElement('div');
    item.className = 'daw-item';
    item.innerHTML = `
      <div class="daw-header">
        <span class="daw-title">${d.use_case}</span>
        <span class="daw-rating">${d.rating} (${d.score_pct}%)</span>
      </div>
      <p class="daw-desc">${d.comment}</p>
    `;
    dawContainer.appendChild(item);
  });

  // 6. Strengths & Recommendations
  const strContainer = document.getElementById('strengthsList');
  strContainer.innerHTML = '';
  (score.strengths || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    strContainer.appendChild(li);
  });

  const recContainer = document.getElementById('recommendationsList');
  recContainer.innerHTML = '';
  (score.recommendations || []).forEach(r => {
    const li = document.createElement('li');
    li.textContent = r;
    recContainer.appendChild(li);
  });
}

function renderBenchmarkResults(b) {
  document.getElementById('benchRndRead').textContent = `${b.rnd_read_speed_mbs} MB/s`;
  document.getElementById('benchIops').textContent = `${b.rnd_iops.toLocaleString()} IOPS`;
  document.getElementById('benchSeqRead').textContent = `${b.seq_read_speed_mbs} MB/s`;
  document.getElementById('benchSeqWrite').textContent = `${b.write_speed_mbs} MB/s`;

  document.getElementById('kontaktHeavy').textContent = `~${b.patches_heavy_48k}`;
  document.getElementById('kontaktStandard').textContent = `~${b.patches_standard_48k}`;
  document.getElementById('kontaktVoices').textContent = `${b.max_voices_48k.toLocaleString()} voci`;

  document.getElementById('clickRiskBadge').textContent = b.click_risk;
  document.getElementById('kontaktBufferVal').textContent = b.recommended_kontakt_dfd_buffer;
}

async function triggerDiskBenchmark() {
  const mount = document.getElementById('driveSelect').value || '/';
  const loading = document.getElementById('benchLoading');
  const results = document.getElementById('benchResults');
  const btn = document.getElementById('btnRunBench');

  loading.style.display = 'block';
  results.style.opacity = '0.4';
  btn.disabled = true;

  try {
    const res = await fetch('/api/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mount_point: mount, size_mb: 64 })
    });
    const benchData = await res.json();
    renderBenchmarkResults(benchData);
  } catch (err) {
    alert('Errore durante l\'esecuzione del benchmark: ' + err);
  } finally {
    loading.style.display = 'none';
    results.style.opacity = '1';
    btn.disabled = false;
  }
}

function renderDevicesTable() {
  const tbody = document.getElementById('devicesTableBody');
  const search = (document.getElementById('devSearch').value || '').toLowerCase();
  tbody.innerHTML = '';

  const filtered = allDevices.filter(d => {
    // Type filter
    if (currentFilter === 'input' && d.device_type !== 'Input' && d.device_type !== 'Duplex') return false;
    if (currentFilter === 'output' && d.device_type !== 'Output' && d.device_type !== 'Duplex') return false;
    if (currentFilter === 'duplex' && d.device_type !== 'Duplex') return false;
    if (currentFilter === 'pro' && !d.studio_grade.includes('Pro') && !d.studio_grade.includes('Tier 1')) return false;

    // Search filter
    if (search) {
      const match = d.name.toLowerCase().includes(search) ||
                    d.manufacturer.toLowerCase().includes(search) ||
                    d.driver_name.toLowerCase().includes(search) ||
                    d.transport.toLowerCase().includes(search);
      if (!match) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center" style="padding: 24px; color: var(--text-dim)">Nessun dispositivo audio trovato per i filtri selezionati.</td></tr>';
    return;
  }

  filtered.forEach(d => {
    const tr = document.createElement('tr');
    
    // Max sample rate
    const maxSr = Math.max(...(d.supported_sample_rates || [48000]).map(x => typeof x === 'number' ? x : 48000));
    const srStr = `${Math.round(maxSr / 1000)} kHz`;

    // Default badge
    let defaultTag = '';
    if (d.is_default_output && d.is_default_input) {
      defaultTag = '<span class="badge-default">★ PREDEF I/O</span>';
    } else if (d.is_default_output) {
      defaultTag = '<span class="badge-default">★ PREDEF OUT</span>';
    } else if (d.is_default_input) {
      defaultTag = '<span class="badge-default">★ PREDEF IN</span>';
    }

    tr.innerHTML = `
      <td><strong>${d.name}</strong> ${defaultTag}</td>
      <td>${d.manufacturer}</td>
      <td><span class="badge-driver" title="${d.driver_bundle_id || ''}">${d.driver_name}</span> <small style="display:block; color:var(--text-dim)">${d.driver_version || ''}</small></td>
      <td>${d.transport}</td>
      <td><span class="badge-ch">${d.input_channels} In / ${d.output_channels} Out</span></td>
      <td>${srStr}</td>
      <td><strong>${d.round_trip_latency_ms.toFixed(1)} ms</strong></td>
      <td><small style="color:var(--accent-cyan); font-weight:600">${d.studio_grade}</small></td>
    `;
    tbody.appendChild(tr);
  });
}

function setDevFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  renderDevicesTable();
}

function filterDeviceTable() {
  renderDevicesTable();
}

// Latency Calculator Interactive Handlers
function setCalcSampleRate(sr) {
  calcSampleRate = sr;
  document.querySelectorAll('.radio-chips')[0].querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  event.target.classList.add('active');
  updateLatencyCalc();
}

function setCalcBuffer(buf) {
  calcBufferSize = buf;
  document.querySelectorAll('.radio-chips')[1].querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  event.target.classList.add('active');
  updateLatencyCalc();
}

function updateLatencyCalc() {
  // Calculation with typical hardware/converter latency + safety offset (~96 samples total)
  const hwLatency = 64;
  const safetyOffset = 48;
  const halfExtra = (hwLatency + safetyOffset) / 2;

  const inMs = ((calcBufferSize + halfExtra) / calcSampleRate) * 1000;
  const outMs = ((calcBufferSize + halfExtra) / calcSampleRate) * 1000;
  const rtlMs = inMs + outMs;

  document.getElementById('calcRtlMs').textContent = `${rtlMs.toFixed(2)} ms`;
  document.getElementById('calcInMs').textContent = `${inMs.toFixed(2)} ms`;
  document.getElementById('calcOutMs').textContent = `${outMs.toFixed(2)} ms`;

  const suitEl = document.getElementById('calcSuitability');
  if (rtlMs < 3.5) {
    suitEl.textContent = '🚀 Latenza impercettibile: Perfetto per monitoraggio in-ear di voci & amp simulator per chitarra';
    suitEl.style.color = 'var(--accent-cyan)';
    suitEl.style.background = 'rgba(0, 242, 254, 0.15)';
  } else if (rtlMs < 6.5) {
    suitEl.textContent = '✅ Ottimale: Ideale per esecuzione di tastiere MIDI & strumenti virtuali in tempo reale';
    suitEl.style.color = 'var(--accent-green)';
    suitEl.style.background = 'rgba(16, 185, 129, 0.15)';
  } else if (rtlMs < 12.0) {
    suitEl.textContent = '⚠️ Standard / Medio: Accettabile per overdubbing; possibile lieve effetto pettine in cuffia su voce';
    suitEl.style.color = 'var(--accent-amber)';
    suitEl.style.background = 'rgba(245, 158, 11, 0.15)';
  } else {
    suitEl.textContent = '🛑 Buffer alto: Ideale per mixing e mastering con molti plugin DSP, sconsigliato per tracking live';
    suitEl.style.color = 'var(--accent-red)';
    suitEl.style.background = 'rgba(239, 68, 68, 0.15)';
  }
}
