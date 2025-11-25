// Multi-event comparison script
let summaryData = null;
const eventsCache = {};
// Store sparkline Chart instances so we can destroy them before re-rendering
let sparkCharts = [];

document.addEventListener('DOMContentLoaded', async () => {
  try {
    await loadSummary();
    buildSelector();
    bindControls();
  } catch (e) {
    console.error('Failed to init comparison page', e);
  }
});

async function loadSummary() {
  const res = await fetch('data/events/summary.json');
  summaryData = await res.json();
}

function buildSelector() {
  const ul = document.getElementById('event-selector');
  ul.innerHTML = '';
  summaryData.events.forEach(ev => {
    const li = document.createElement('li');
    li.innerHTML = `<label><input type="checkbox" class="event-checkbox" value="${ev.id}"> ${ev.name} ${ev.year}</label>`;
    ul.appendChild(li);
  });
}

function bindControls() {
  document.getElementById('select-all').addEventListener('click', () => {
    document.querySelectorAll('.event-checkbox').forEach(cb => cb.checked = true);
    updateComparison();
  });
  document.getElementById('clear-selection').addEventListener('click', () => {
    document.querySelectorAll('.event-checkbox').forEach(cb => cb.checked = false);
    updateComparison();
  });
  document.getElementById('apply-selection').addEventListener('click', () => updateComparison());
  // Auto select first 3 for initial view
  document.querySelectorAll('.event-checkbox').forEach((cb,i) => { if (i < 3) cb.checked = true; });
  updateComparison();
}

async function updateComparison() {
  const checked = [...document.querySelectorAll('.event-checkbox:checked')].map(cb => cb.value);
  const tbody = document.getElementById('compare-tbody');
  const emptyNote = document.getElementById('empty-note');
  tbody.innerHTML = '';
  if (!checked.length) {
    emptyNote.style.display = 'block';
    document.getElementById('sparkline-grid').innerHTML = '';
    return;
  }
  emptyNote.style.display = 'none';

  // Limit to 10 selections
  if (checked.length > 10) checked.length = 10;

  for (const id of checked) {
    const ev = await loadEvent(id);
    tbody.appendChild(buildRow(ev));
  }
  renderSparklines(checked);
}

async function loadEvent(id) {
  if (!eventsCache[id]) {
    const res = await fetch(`data/events/${id}.json`);
    eventsCache[id] = await res.json();
  }
  return eventsCache[id];
}

function buildRow(ev) {
  const tr = document.createElement('tr');
  const tier = ev.verification_tier || 'unverified';
  const sustained = ev.algorithm_detection.duration_min || 0;
  const official = ev.official_signal8.duration_min || 0;
  const coverage = ev.timing_analysis.coverage_percent || 0;
  const lead = ev.timing_analysis.start_delta_min;
  tr.innerHTML = `
    <td>${ev.name} ${ev.year}</td>
    <td class="tier-${tier}">${tier.replace('_',' ')}</td>
    <td>${official}</td>
    <td>${sustained}</td>
    <td>${coverage}%</td>
    <td>${lead ? '+'+lead+' min' : 'N/A'}</td>`;
  return tr;
}

async function renderSparklines(ids) {
  const grid = document.getElementById('sparkline-grid');
  // Destroy previous charts to prevent cumulative resize observers causing growing height
  if (sparkCharts.length) {
    sparkCharts.forEach(ch => { try { ch.destroy(); } catch(e) { console.warn('Chart destroy failed', e); } });
    sparkCharts = [];
  }
  grid.innerHTML = '';
  for (const id of ids) {
    const ev = await loadEvent(id);
    // Fetch time_summary.csv
    const csvPath = `${ev.validation_report}time_summary.csv`;
    const isInDocsFolder = window.location.pathname.includes('/docs/');
    const basePath = isInDocsFolder ? '../' : './';
    const res = await fetch(basePath + csvPath);
    if (!res.ok) continue;
    const text = await res.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',');
    const dtIdx = headers.indexOf('datetime');
    const cntIdx = headers.indexOf('count_ge_T8');
    const persIdx = headers.indexOf('persistent_T8');
    if (dtIdx === -1 || cntIdx === -1) continue;
    const counts = [];
    const persistent = [];
    for (let i=1;i<lines.length;i++) {
      const row = lines[i].split(',');
      const c = parseInt(row[cntIdx],10);
      counts.push(c);
      if (persIdx !== -1 && row[persIdx] === 'True') persistent.push(i-1);
    }
    const card = document.createElement('div');
    card.className = 'sparkline-card';
    card.innerHTML = `<h3>${ev.name} ${ev.year}</h3><canvas id="spark-${id}" height="80"></canvas>`;
    grid.appendChild(card);
    drawSparkline(`spark-${id}`, counts, persistent, ev);
  }
}

function drawSparkline(canvasId, counts, persistent, ev) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  // Build persistent boxes
  const boxes = [];
  if (persistent.length) {
    let s = persistent[0], e = persistent[0];
    for (let i=1;i<persistent.length;i++) {
      if (persistent[i] === e+1) e = persistent[i]; else { boxes.push({type:'box',xMin:s,xMax:e,backgroundColor:'rgba(0,78,137,0.25)',borderWidth:0}); s=persistent[i]; e=persistent[i]; }
    }
    boxes.push({type:'box',xMin:s,xMax:e,backgroundColor:'rgba(0,78,137,0.25)',borderWidth:0});
  }
  // Pattern annotation if pattern_validated
  const patternAnn = [];
  if (ev.verification_tier === 'pattern_validated') {
    // Simple highlight of any lull (<4) between two meet segments
    const countsArr = counts;
    let fmEnd = -1; let lullStart=-1; let lullEnd=-1; let secondStart=-1; let secondEnd=-1; let stage=0; // 0 searching first meet
    for (let i=0;i<countsArr.length;i++) {
      const c = countsArr[i];
      if (stage===0) { if (c>=4){ fmEnd=i; stage=1;} }
      else if (stage===1) { if (c<4){ lullStart=i; lullEnd=i; stage=2;} }
      else if (stage===2) { if (c<4){ lullEnd=i; } else { if (lullEnd - lullStart +1 >=2){ secondStart=i; secondEnd=i; stage=3; } else { stage= c>=4?1:0; } } }
      else if (stage===3) { if (c>=4){ secondEnd=i; } else break; }
    }
    if (secondStart !== -1) {
      patternAnn.push({type:'box',xMin:lullStart,xMax:lullEnd,backgroundColor:'rgba(120,120,120,0.15)',borderWidth:0});
      patternAnn.push({type:'line',xMin:lullStart,xMax:lullStart,borderColor:'rgba(120,120,120,0.6)',borderDash:[4,3],label:{content:'Lull',enabled:true,position:'start',color:'#555',font:{size:8}}});
    }
  }
  const chart = new Chart(ctx, {
    type:'line',
    data:{ labels: counts.map((_,i)=>i), datasets:[{ data: counts, borderColor:'#004e89', backgroundColor:'rgba(0,78,137,0.08)', borderWidth:1, tension:0.2, pointRadius:0 }]},
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, annotation:{ annotations:[ ...boxes, ...patternAnn, {type:'line', yMin:4, yMax:4, borderColor:'#dc3545', borderWidth:1, borderDash:[4,3]} ] } },
      scales:{ y:{display:false, suggestedMax:8}, x:{display:false} }
    }
  });
  sparkCharts.push(chart);
}
