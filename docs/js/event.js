// Event detail page JavaScript
let eventData = null;
let stationsData = null;
const T8_THRESHOLD = 63;

// Load event data on page load
document.addEventListener('DOMContentLoaded', async function() {
    const urlParams = new URLSearchParams(window.location.search);
    const eventId = urlParams.get('id');
    
    if (!eventId) {
        window.location.href = 'index.html';
        return;
    }
    
    await loadEventData(eventId);
    await loadStationsMetadata();
    renderEventDetail();
    await renderChart();
    renderStationCards();
});

// Load event data
async function loadEventData(eventId) {
    try {
        const response = await fetch(`data/events/${eventId}.json`);
        eventData = await response.json();
        console.log('Event data loaded:', eventData);
    } catch (error) {
        console.error('Error loading event data:', error);
        alert('Failed to load event data');
        window.location.href = 'index.html';
    }
}

// Load stations metadata
async function loadStationsMetadata() {
    try {
        const response = await fetch('data/stations.json');
        stationsData = await response.json();
    } catch (error) {
        console.error('Error loading stations data:', error);
    }
}

// Render event detail
function renderEventDetail() {
    if (!eventData) return;
    
    // Update header
    const icon = getEventIcon(eventData.severity);
    document.getElementById('event-icon').textContent = icon;
    document.getElementById('event-title').textContent = 
        `${eventData.name} ${eventData.year} (${eventData.name_zh})`;
    document.getElementById('event-date').textContent = eventData.date_range;
    
    // Update verdict box
    const verdictBox = document.getElementById('verdict-box');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictText = document.getElementById('verdict-text');
    
    // Set verdict class
        // New verification tier logic
        const tier = eventData.verification_tier || eventData.timing_analysis.assessment;
        verdictBox.classList.remove('forecast', 'consistent', 'pattern');
        if (tier === 'verified') {
            verdictIcon.textContent = '✅';
        } else if (tier === 'pattern_validated') {
            verdictBox.classList.add('pattern');
            verdictIcon.textContent = '⚠️';
        } else if (tier === 'unverified') {
            verdictBox.classList.add('forecast');
            verdictIcon.textContent = '❓';
        } else if (tier === 'no_signal') {
            verdictBox.classList.add('consistent');
            verdictIcon.textContent = '✓';
        }

        verdictTitle.textContent = getVerdictTitle(tier);
        verdictText.textContent = eventData.timing_analysis.verdict;
    
    // Apply background color to summary panel based on verdict
    const summaryPanel = document.querySelector('.summary-panel');
    summaryPanel.classList.remove('verdict-appropriate', 'verdict-forecast');
    if (eventData.timing_analysis.assessment === 'appropriate') {
        summaryPanel.classList.add('verdict-appropriate');
    } else if (eventData.timing_analysis.assessment === 'forecast_driven') {
        summaryPanel.classList.add('verdict-forecast');
    }
    
    // Render summary stats
    renderSummaryStats();
    
    // Render T10 transparency if available
    if (eventData.t10_transparency) {
        renderT10Transparency();
    }
    
    // Update figure paths
    const isInDocsFolder = window.location.pathname.includes('/docs/');
    const basePath = isInDocsFolder ? '../' : './';
    const timelineFigure = document.getElementById('timeline-figure');
    const heatmapFigure = document.getElementById('heatmap-figure');
    
    timelineFigure.src = `${basePath}${eventData.figures.timeline}`;
    timelineFigure.style.display = ''; // Reset display style to show image
    
    heatmapFigure.src = `${basePath}${eventData.figures.heatmap}`;
    heatmapFigure.style.display = ''; // Reset display style to show image
}

// Render summary stats
function renderSummaryStats() {
    const container = document.getElementById('summary-stats');
    
    const stats = [
        {
            label: 'Official Signal 8',
            value: eventData.official_signal8.issued 
                ? `${formatDuration(eventData.official_signal8.duration_min)}`
                : 'Not Issued',
            na: !eventData.official_signal8.issued
        },
        {
            label: 'Algorithm Detection',
            value: eventData.algorithm_detection.detected
                ? `${formatDuration(eventData.algorithm_detection.duration_min)}`
                : 'None Detected',
            na: !eventData.algorithm_detection.detected
        },
        {
            label: 'HKO Early Warning Time <span class="info-icon" title="Time HKO issued signal before algorithm detected persistent gale. N/A means algorithm did not detect persistent gale (forecast-driven signal).">ℹ️</span>',
            value: eventData.timing_analysis.start_delta_min
                ? `+${eventData.timing_analysis.start_delta_min} min`
                : 'N/A',
            na: !eventData.timing_analysis.start_delta_min
        },
        {
            label: 'Wind Coverage <span class="info-icon" title="% of signal period with sustained gale conditions (≥30 min)">ℹ️</span>',
            value: `${eventData.timing_analysis.coverage_percent}%`,
            na: eventData.timing_analysis.coverage_percent === 0
        },
        {
            label: 'Peak Stations ≥T8',
            value: eventData.algorithm_detection.peak_stations || 0,
            na: !eventData.algorithm_detection.detected
        },
        {
            label: 'Max Mean Wind',
            value: eventData.algorithm_detection.mean_wind_peak
                ? `${Math.round(eventData.algorithm_detection.mean_wind_peak)} km/h`
                : 'N/A',
            na: !eventData.algorithm_detection.detected
        }
    ];
    
    container.innerHTML = stats.map(stat => `
        <div class="summary-stat">
            <div class="summary-stat-label">${stat.label}</div>
            <div class="summary-stat-value ${stat.na ? 'na' : ''}">${stat.value}</div>
        </div>
    `).join('');
}

// Render chart
async function renderChart() {
    if (!eventData) return;

    try {
        // Determine path to CSV
        const isInDocsFolder = window.location.pathname.includes('/docs/');
        const basePath = isInDocsFolder ? '../' : './';
        const csvPath = `${basePath}${eventData.validation_report}time_summary.csv`;

        const response = await fetch(csvPath);
        if (!response.ok) throw new Error(`Failed to fetch ${csvPath}`);
        const csvText = await response.text();
        const lines = csvText.trim().split('\n');
        if (lines.length < 2) throw new Error('CSV appears empty');
        const headers = lines[0].split(',');

        const datetimeIdx = headers.indexOf('datetime');
        const countIdx = headers.indexOf('count_ge_T8');
        const persistentIdx = headers.indexOf('persistent_T8');
        if (datetimeIdx === -1 || countIdx === -1) throw new Error('Required columns missing');

        const labels = [];
        const stationCounts = [];
        const persistentPeriods = []; // indices where persistent_T8 True
        const intermittentPeriods = []; // indices with count>=4 but not persistent

        for (let i = 1; i < lines.length; i++) {
            const row = lines[i].split(',');
            if (row.length < headers.length) continue;
            const dt = new Date(row[datetimeIdx]);
            const count = parseInt(row[countIdx], 10);
            const isPersistent = persistentIdx !== -1 && row[persistentIdx] === 'True';

            // Format time: show hour:minute, display every 30 min for readability
            const minutes = dt.getMinutes();
            const shouldShowLabel = (minutes === 0 || minutes === 30);
            labels.push(shouldShowLabel ? dt.toLocaleTimeString('en-US', {
                hour: '2-digit', minute: '2-digit', hour12: false
            }) : '');
            stationCounts.push(count);

            if (isPersistent) {
                persistentPeriods.push(i - 1); // chart indices
            } else if (count >= 4) {
                intermittentPeriods.push(i - 1);
            }
        }

        // Build boxes for persistent periods
        const algoBoxes = [];
        if (persistentPeriods.length) {
            let start = persistentPeriods[0];
            let end = persistentPeriods[0];
            for (let i = 1; i < persistentPeriods.length; i++) {
                if (persistentPeriods[i] === end + 1) {
                    end = persistentPeriods[i];
                } else {
                    algoBoxes.push(makePersistentBox(start, end));
                    start = persistentPeriods[i];
                    end = persistentPeriods[i];
                }
            }
            algoBoxes.push(makePersistentBox(start, end));
        }

        function makePersistentBox(xMin, xMax) {
            return {
                type: 'box', xMin, xMax,
                backgroundColor: 'rgba(0,78,137,0.25)', borderColor: 'rgba(0,78,137,0.6)', borderWidth: 2,
                label: { content: 'Persistent T8 (≥30 min)', enabled: true, position: 'start', color: '#004e89', font: { weight: 'bold', size: 11 } }
            };
        }

        // Intermittent gale (non-persistent ≥4 station) boxes
        const intermittentBoxes = [];
        if (intermittentPeriods.length) {
            let s = intermittentPeriods[0];
            let e = intermittentPeriods[0];
            for (let i = 1; i < intermittentPeriods.length; i++) {
                if (intermittentPeriods[i] === e + 1) {
                    e = intermittentPeriods[i];
                } else {
                    intermittentBoxes.push(makeIntermittentBox(s, e));
                    s = intermittentPeriods[i];
                    e = intermittentPeriods[i];
                }
            }
            intermittentBoxes.push(makeIntermittentBox(s, e));
        }
        function makeIntermittentBox(xMin, xMax) {
            return { type: 'box', xMin, xMax, backgroundColor: 'rgba(173,216,230,0.15)', borderWidth: 0 };
        }

        // Pattern‑validated annotation (wind‑lull‑wind) if applicable
        const patternBoxes = [];
        if (eventData.verification_tier === 'pattern_validated') {
            // Simple state machine to find first meet (≥4), lull (≥2 <4), second meet (≥4)
            const counts = stationCounts;
            let stage = 0; // 0 searching first meet, 1 in first meet, 2 lull, 3 second meet
            let fmStart = null, fmEnd = null, lullStart = null, lullEnd = null, smStart = null, smEnd = null;
            for (let i = 0; i < counts.length; i++) {
                const c = counts[i];
                if (stage === 0) {
                    if (c >= 4) { fmStart = i; fmEnd = i; stage = 1; }
                } else if (stage === 1) {
                    if (c >= 4) { fmEnd = i; }
                    else { lullStart = i; lullEnd = i; stage = 2; }
                } else if (stage === 2) {
                    if (c < 4) { lullEnd = i; }
                    else {
                        if ((lullEnd - lullStart + 1) >= 2) { smStart = i; smEnd = i; stage = 3; }
                        else { // insufficient lull resets
                            stage = c >= 4 ? 1 : 0;
                            if (stage === 1) { fmStart = i; fmEnd = i; lullStart = lullEnd = null; }
                        }
                    }
                } else if (stage === 3) {
                    if (c >= 4) { smEnd = i; }
                    else { break; }
                }
            }
            if (smStart !== null) {
                patternBoxes.push({ type: 'box', xMin: fmStart, xMax: fmEnd, backgroundColor: 'rgba(0,200,83,0.15)', borderColor: 'rgba(0,200,83,0.5)', borderWidth: 1, label: { content: 'First Meet ≥4', enabled: true, position: 'start', color: '#008c3a', font: { size: 10, weight: 'bold' } } });
                patternBoxes.push({ type: 'box', xMin: lullStart, xMax: lullEnd, backgroundColor: 'rgba(120,120,120,0.12)', borderColor: 'rgba(120,120,120,0.4)', borderWidth: 1, borderDash: [4,3], label: { content: 'Lull (<4)', enabled: true, position: 'center', color: '#555', font: { size: 10 } } });
                patternBoxes.push({ type: 'box', xMin: smStart, xMax: smEnd, backgroundColor: 'rgba(255,193,7,0.18)', borderColor: 'rgba(255,193,7,0.6)', borderWidth: 1, label: { content: 'Second Meet ≥4', enabled: true, position: 'end', color: '#b38600', font: { size: 10, weight: 'bold' } } });
            }
        }

        // Official Signal 8 period box
        let officialBox = null;
        if (eventData.official_signal8.issued) {
            const officialStart = new Date(eventData.official_signal8.start);
            const officialEnd = new Date(eventData.official_signal8.end);
            let sIdx = null, eIdx = null;
            for (let i = 1; i < lines.length; i++) {
                const dt = new Date(lines[i].split(',')[datetimeIdx]);
                if (sIdx === null && dt >= officialStart) sIdx = i - 1;
                if (dt <= officialEnd) eIdx = i - 1;
            }
            if (sIdx !== null && eIdx !== null) {
                officialBox = { type: 'box', xMin: sIdx, xMax: eIdx, backgroundColor: 'rgba(255,107,53,0.18)', borderColor: 'rgba(255,107,53,0.5)', borderWidth: 1, label: { content: 'Official Signal 8', enabled: true, position: 'end' } };
            }
        }

        // Signal 10 period box (if present)
        let t10Box = null;
        if (eventData.t10_transparency) {
            const t10Start = new Date(eventData.t10_transparency.first_interval);
            const t10End = new Date(eventData.t10_transparency.last_interval);
            let sIdx = null, eIdx = null;
            for (let i = 1; i < lines.length; i++) {
                const dt = new Date(lines[i].split(',')[datetimeIdx]);
                if (sIdx === null && dt >= t10Start) sIdx = i - 1;
                if (dt <= t10End) eIdx = i - 1;
            }
            if (sIdx !== null && eIdx !== null) {
                t10Box = { type: 'box', xMin: sIdx, xMax: eIdx, backgroundColor: 'rgba(148,103,189,0.15)', borderColor: 'rgba(148,103,189,0.6)', borderDash: [3,3], borderWidth: 2, label: { content: 'Signal 10 Period', enabled: true, position: 'center', color: '#6b4c9a', font: { weight: 'bold' } } };
            }
        }

        // Key moment: first persistent
        const keyMoments = [];
        if (persistentPeriods.length) {
            keyMoments.push({ type: 'line', xMin: persistentPeriods[0], xMax: persistentPeriods[0], borderColor: 'rgba(0,78,137,0.7)', borderWidth: 2, borderDash: [3,3], label: { content: 'First Persistent (≥30 min)', enabled: true, position: 'top', color: '#004e89', backgroundColor: 'rgba(255,255,255,0.85)', font: { size: 10, weight: 'bold' } } });
        }

        const ctx = document.getElementById('timeline-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Stations ≥63 km/h',
                    data: stationCounts,
                    borderColor: 'rgb(0,78,137)',
                    backgroundColor: 'rgba(0,78,137,0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.15,
                    pointRadius: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: { mode: 'index', intersect: false },
                    annotation: {
                        annotations: [
                            ...intermittentBoxes,
                            // Threshold line
                            { type: 'line', yMin: 4, yMax: 4, borderColor: 'rgb(220,53,69)', borderWidth: 2, borderDash: [5,5], label: { content: 'T8 Threshold (≥4 stations)', enabled: true, position: 'end', color: '#dc3545', font: { weight: 'bold' } } },
                            ...(officialBox ? [officialBox] : []),
                            ...(t10Box ? [t10Box] : []),
                            ...patternBoxes,
                            ...algoBoxes,
                            ...keyMoments
                        ]
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 8,
                        ticks: {
                            stepSize: 1,
                            callback: v => Number.isInteger(v) ? v : ''
                        },
                        title: { display: true, text: 'Stations ≥63 km/h' }
                    },
                    x: {
                        ticks: { maxRotation: 45, minRotation: 45, autoSkip: true, maxTicksLimit: 24 },
                        title: { display: true, text: 'Time' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading or parsing CSV:', error);
        const ctx = document.getElementById('timeline-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: { labels: ['No Data'], datasets: [{ label: 'Stations ≥63 km/h', data: [0], borderColor: '#ccc', backgroundColor: 'rgba(200,200,200,0.15)' }] },
            options: { plugins: { title: { display: true, text: 'Timeline data unavailable', color: '#dc3545' }, legend: { display: false } }, scales: { y: { beginAtZero: true }, x: {} } }
        });
    }
}

// Render station cards
function renderStationCards() {
    if (!eventData || !eventData.station_summary) return;
    
    const container = document.getElementById('station-grid');
    
    // Sort stations by max wind speed (descending)
    const sortedStations = [...eventData.station_summary].sort(
        (a, b) => b.max_wind_kmh - a.max_wind_kmh
    );
    
    container.innerHTML = sortedStations.map(station => {
        // Find matching station metadata
        const metadata = stationsData?.stations.find(s => s.name === station.name);
        const nameZh = metadata?.name_zh || '';
        
        const exceedsT8 = station.max_wind_kmh >= T8_THRESHOLD;
        
        return `
            <div class="station-card">
                <h3>${station.name}</h3>
                <div class="station-name-zh">${nameZh}</div>
                
                <div class="station-stats">
                    <div class="station-stat-row">
                        <span class="station-stat-label">Mean Wind</span>
                        <span class="station-stat-value">${station.mean_wind_kmh} km/h</span>
                    </div>
                    <div class="station-stat-row">
                        <span class="station-stat-label">P90 Wind</span>
                        <span class="station-stat-value">${station.p90_wind_kmh} km/h</span>
                    </div>
                    <div class="station-stat-row">
                        <span class="station-stat-label">Max Wind</span>
                        <span class="station-stat-value ${exceedsT8 ? 'highlight' : ''}">${station.max_wind_kmh} km/h</span>
                    </div>
                    <div class="station-stat-row">
                        <span class="station-stat-label">Max Gust</span>
                        <span class="station-stat-value ${station.max_gust_kmh >= 100 ? 'highlight' : ''}">${station.max_gust_kmh} km/h</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Utility functions
function getEventIcon(severity) {
    if (severity === 'T10') return '🔴';
    if (severity === 'T8') return '🟡';
    return '🟢';
}

function getVerdictTitle(tier) {
    const titles = {
        'verified': 'VERIFICATION: ✅ VERIFIED BY OBSERVATION',
        'pattern_validated': 'VERIFICATION: ⚠️ PATTERN‑VALIDATED',
        'unverified': 'VERIFICATION: ❓ UNVERIFIED (OBSERVATION)',
        'no_signal': 'VERIFICATION: ✓ NO SIGNAL ISSUED'
    };
    if (!titles[tier]) {
        if (tier === 'appropriate') return 'VERIFICATION: ✅ VERIFIED';
        if (tier === 'forecast_driven') return 'VERIFICATION: ❓ UNVERIFIED';
        if (tier === 'consistent') return 'VERIFICATION: ✓ NO SIGNAL ISSUED';
    }
    return titles[tier] || String(tier).toUpperCase();
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
        return `${hours}h ${mins}m (${minutes} min)`;
    }
    return `${minutes} min`;
}

// Render T10 transparency metrics
function renderT10Transparency() {
    if (!eventData || !eventData.t10_transparency) return;
    
    const t10 = eventData.t10_transparency;
    const container = document.getElementById('summary-stats');
    
    // Create transparency section after existing stats
    const transparencySection = document.createElement('div');
    transparencySection.style.gridColumn = '1 / -1';
    transparencySection.style.marginTop = '1rem';
    transparencySection.style.paddingTop = '1rem';
    transparencySection.style.borderTop = '2px solid #e0e0e0';
    
    const galeCoveragePct = Math.round(t10.gale_coverage_intervals / t10.intervals * 100);
    const hurricaneCoveragePct = Math.round(t10.hurricane_coverage_intervals / t10.intervals * 100);
    
    transparencySection.innerHTML = `
        <h4 style="margin: 0 0 0.75rem 0; color: #004e89; font-size: 0.95rem;">Signal 10 Transparency Metrics</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem;">
            <div class="summary-stat">
                <div class="summary-stat-label">T10 Period</div>
                <div class="summary-stat-value">${formatDateRange(t10.first_interval, t10.last_interval)}</div>
            </div>
            <div class="summary-stat">
                <div class="summary-stat-label">Total Intervals</div>
                <div class="summary-stat-value">${t10.intervals}</div>
            </div>
            <div class="summary-stat">
                <div class="summary-stat-label">Gale Coverage (≥4/8 @ ≥63 km/h) <span class="info-icon" title="% of T10 period with sustained gale conditions">ℹ️</span></div>
                <div class="summary-stat-value ${t10.gale_coverage_intervals === 0 ? 'na' : ''}">${t10.gale_coverage_intervals} / ${t10.intervals} (${galeCoveragePct}%)</div>
            </div>
            <div class="summary-stat">
                <div class="summary-stat-label">Hurricane Coverage (≥4/8 @ ≥118 km/h) <span class="info-icon" title="% of T10 period with hurricane-force winds">ℹ️</span></div>
                <div class="summary-stat-value ${t10.hurricane_coverage_intervals === 0 ? 'na' : ''}">${t10.hurricane_coverage_intervals} / ${t10.intervals} (${hurricaneCoveragePct}%)</div>
            </div>
            <div class="summary-stat">
                <div class="summary-stat-label">Low Wind Intervals</div>
                <div class="summary-stat-value ${t10.low_wind_intervals === 0 ? 'na' : ''}">${t10.low_wind_intervals} / ${t10.intervals}</div>
            </div>
        </div>
        <p style="margin: 0.75rem 0 0 0; font-size: 0.85rem; color: #666; line-height: 1.5;">
            <strong>Note:</strong> Transparency metrics show observed wind coverage during the official Signal 10 period. 
            Gale coverage indicates intervals where ≥4 of 8 reference stations simultaneously recorded ≥63 km/h (gale force). 
            Hurricane coverage indicates intervals where ≥4 stations simultaneously recorded ≥118 km/h (hurricane force). 
            Low gale/hurricane coverage does not invalidate the signal; HKO uses forecast and expert judgment considering 
            spatial heterogeneity, eye passage, and terrain effects beyond the lowland reference network.
        </p>
    `;
    
    container.appendChild(transparencySection);
    
    // Add Wind Pattern Analysis section
    renderT10WindPattern();
}

// Render T10 Wind Pattern Analysis (before/during/after)
async function renderT10WindPattern() {
    if (!eventData || !eventData.t10_transparency) return;
    
    try {
        // Fetch time_summary.csv to analyze before/during/after patterns
        const isInDocsFolder = window.location.pathname.includes('/docs/');
        const basePath = isInDocsFolder ? '../' : './';
        const csvPath = `${basePath}${eventData.validation_report}time_summary.csv`;
        
        const response = await fetch(csvPath);
        const csvText = await response.text();
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        
        const datetimeIdx = headers.indexOf('datetime');
        const countT8Idx = headers.indexOf('count_ge_T8');
        const inT8Idx = headers.indexOf('in_T8_window');
        const inT10Idx = headers.indexOf('in_T10_window');
        
        const t10Start = new Date(eventData.t10_transparency.first_interval);
        const t10End = new Date(eventData.t10_transparency.last_interval);
        const t8Start = new Date(eventData.official_signal8.start);
        const t8End = new Date(eventData.official_signal8.end);
        
        let beforeGaleCount = 0;
        let duringGaleCount = 0;
        let afterGaleCount = 0;
        
        for (let i = 1; i < lines.length; i++) {
            const row = lines[i].split(',');
            if (row.length < headers.length) continue;
            
            const datetime = new Date(row[datetimeIdx]);
            const countT8 = parseInt(row[countT8Idx], 10);
            const meetsT8 = countT8 >= 4;
            
            if (datetime >= t8Start && datetime < t10Start) {
                // Before T10 (within T8 period before T10 started)
                if (meetsT8) beforeGaleCount++;
            } else if (datetime >= t10Start && datetime <= t10End) {
                // During T10
                if (meetsT8) duringGaleCount++;
            } else if (datetime > t10End && datetime <= t8End) {
                // After T10 (remaining T8 period after T10 ended)
                if (meetsT8) afterGaleCount++;
            }
        }
        
        const duringTotal = eventData.t10_transparency.intervals;
        
        // Calculate before/after totals
        const beforeTotal = Math.floor((t10Start - t8Start) / (10 * 60 * 1000));
        const afterTotal = Math.floor((t8End - t10End) / (10 * 60 * 1000));
        
        // Create wind pattern analysis section
        const container = document.getElementById('summary-stats');
        const patternSection = document.createElement('div');
        patternSection.style.gridColumn = '1 / -1';
        patternSection.style.marginTop = '1.5rem';
        
        patternSection.innerHTML = `
            <details style="background: #faf5ff; padding: 1rem; border-radius: 8px; border: 1px solid #e9d5ff;">
                <summary style="cursor: pointer; font-weight: 600; color: #6b4c9a; font-size: 0.95rem; margin-bottom: 0.75rem;">
                    📊 Understanding Wind Persistence During T10 (Click to expand)
                </summary>
                <div style="margin-top: 0.75rem;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                        <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #ddd;">
                            <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.25rem;">BEFORE T10 ESCALATION</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #004e89;">${beforeGaleCount}</div>
                            <div style="font-size: 0.7rem; color: #888;">of ${beforeTotal} intervals with gale coverage</div>
                        </div>
                        <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #ddd;">
                            <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.25rem;">DURING T10 PERIOD</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #6b4c9a;">${duringGaleCount}</div>
                            <div style="font-size: 0.7rem; color: #888;">of ${duringTotal} intervals with gale coverage</div>
                        </div>
                        <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #ddd;">
                            <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.25rem;">AFTER T10 CANCELLATION</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #004e89;">${afterGaleCount}</div>
                            <div style="font-size: 0.7rem; color: #888;">of ${afterTotal} intervals with gale coverage</div>
                        </div>
                    </div>
                    <p style="font-size: 0.85rem; color: #444; line-height: 1.6; margin: 0; padding: 0.75rem; background: #fffbeb; border-left: 3px solid #f59e0b; border-radius: 4px;">
                        <strong>Signal Justification:</strong> While the T10 period may have included calm intervals (e.g., due to storm structure or eye passage), 
                        the presence of sustained gale-force winds both before and after this period demonstrates that HKO's "wind condition is expected to persist" 
                        criterion was met. The signal issuance appropriately reflects the overall dangerous wind environment throughout the event.
                    </p>
                </div>
            </details>
        `;
        
        container.appendChild(patternSection);
        
    } catch (error) {
        console.error('Error rendering wind pattern analysis:', error);
    }
}

function formatDateRange(start, end) {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const startStr = startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    const endStr = endDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    return `${startStr} - ${endStr}`;
}

// Accordion toggle
function toggleAccordion(index) {
    const items = document.querySelectorAll('.accordion-item');
    const item = items[index];
    
    // Close all other items
    items.forEach((otherItem, i) => {
        if (i !== index) {
            otherItem.classList.remove('active');
        }
    });
    
    // Toggle current item
    item.classList.toggle('active');
}

// Expose globally
window.toggleAccordion = toggleAccordion;
