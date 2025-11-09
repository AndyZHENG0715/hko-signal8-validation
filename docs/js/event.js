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
    renderChart();
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
    verdictBox.classList.remove('forecast', 'consistent');
    if (eventData.timing_analysis.assessment === 'forecast_driven') {
        verdictBox.classList.add('forecast');
        verdictIcon.textContent = '⚠️';
    } else if (eventData.timing_analysis.assessment === 'consistent') {
        verdictBox.classList.add('consistent');
        verdictIcon.textContent = '✓';
    } else {
        verdictIcon.textContent = '✅';
    }
    
    verdictTitle.textContent = getVerdictTitle(eventData.timing_analysis.assessment);
    verdictText.textContent = eventData.timing_analysis.verdict;
    
    // Render summary stats
    renderSummaryStats();
    
    // Update figure paths
    document.getElementById('timeline-figure').src = `../${eventData.figures.timeline}`;
    document.getElementById('heatmap-figure').src = `../${eventData.figures.heatmap}`;
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
            label: 'Forecast Lead Time',
            value: eventData.timing_analysis.start_delta_min
                ? `+${eventData.timing_analysis.start_delta_min} min`
                : 'N/A',
            na: !eventData.timing_analysis.start_delta_min
        },
        {
            label: 'Coverage',
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
function renderChart() {
    if (!eventData) return;
    
    const ctx = document.getElementById('timeline-chart').getContext('2d');
    
    // Prepare data
    const labels = [];
    const stationCounts = [];
    
    // For demonstration, create sample data points
    // In production, this would come from time_summary.csv data
    const startTime = eventData.official_signal8.issued 
        ? new Date(eventData.official_signal8.start)
        : new Date(eventData.date_range);
    
    // Generate hourly data points for 24 hours
    for (let i = 0; i < 24; i++) {
        const time = new Date(startTime.getTime() + i * 3600000);
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        
        // Simulate station counts (would be real data in production)
        if (eventData.algorithm_detection.detected) {
            // Peak around middle
            stationCounts.push(Math.max(0, Math.min(8, 4 + Math.sin(i / 3) * 3)));
        } else {
            stationCounts.push(Math.max(0, 2 + Math.random() * 2));
        }
    }
    
    // Define shaded regions
    const officialStart = eventData.official_signal8.issued ? 3 : null;
    const officialEnd = eventData.official_signal8.issued ? 18 : null;
    const algoStart = eventData.algorithm_detection.detected ? 8 : null;
    const algoEnd = eventData.algorithm_detection.detected ? 16 : null;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stations ≥63 km/h',
                data: stationCounts,
                borderColor: 'rgb(0, 78, 137)',
                backgroundColor: 'rgba(0, 78, 137, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                annotation: {
                    annotations: [
                        // T8 threshold line
                        {
                            type: 'line',
                            yMin: 4,
                            yMax: 4,
                            borderColor: 'rgb(220, 53, 69)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                content: 'T8 Threshold (≥4 stations)',
                                enabled: true,
                                position: 'end'
                            }
                        }
                    ]
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 8,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Number of Stations ≥63 km/h'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
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

function getVerdictTitle(assessment) {
    const titles = {
        'appropriate': 'VERDICT: ✅ APPROPRIATE ISSUANCE',
        'forecast_driven': 'VERDICT: ⚠️ FORECAST-BASED EARLY WARNING',
        'consistent': 'VERDICT: ✓ CONSISTENT (NO SIGNAL 8)'
    };
    return titles[assessment] || assessment.toUpperCase();
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
        return `${hours}h ${mins}m (${minutes} min)`;
    }
    return `${minutes} min`;
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
