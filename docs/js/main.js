// Main JavaScript for homepage
let eventsData = null;
let summaryData = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', async function() {
    await loadData();
    renderTimeline();
    updateMetrics();
});

// Load JSON data
async function loadData() {
    try {
        const summaryResponse = await fetch('data/events/summary.json');
        summaryData = await summaryResponse.json();
        
        // Load individual event details
        eventsData = {};
        for (const event of summaryData.events) {
            const response = await fetch(`data/events/${event.id}.json`);
            eventsData[event.id] = await response.json();
        }
        
        console.log('Data loaded successfully:', summaryData);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update key metrics
function updateMetrics() {
    if (!summaryData) return;
    
    const stats = summaryData.statistics;
    
    document.getElementById('total-typhoons').textContent = stats.total_events;
    
    if (stats.avg_lead_time_min) {
        document.getElementById('avg-lead-time').innerHTML = 
            `${stats.avg_lead_time_min} <span class="metric-unit">min</span>`;
    }
    
    document.getElementById('station-count').textContent = stats.reference_stations;
    
    // Last updated
    const updatedDate = new Date(summaryData.generated_at);
    document.getElementById('last-updated').textContent = 
        `Last updated: ${updatedDate.toISOString().split('T')[0]}`;
}

// Render typhoon timeline
function renderTimeline() {
    if (!summaryData || !eventsData) return;
    
    const container = document.getElementById('typhoon-events');
    container.innerHTML = '';
    
    summaryData.events.forEach(event => {
        const eventData = eventsData[event.id];
        const card = createEventCard(eventData);
        container.appendChild(card);
    });
}

// Create event card
function createEventCard(event) {
    const card = document.createElement('div');
    card.className = `typhoon-event severity-${event.severity.replace(' ', '-')}`;
    card.onclick = () => {
        window.location.href = `event.html?id=${event.id}`;
    };
    
    // Determine icon based on severity
    let icon = '🌪️';
    if (event.severity === 'T10') {
        icon = '🔴';
    } else if (event.severity === 'T8') {
        icon = '🟡';
    } else {
        icon = '🟢';
    }
    
    // Determine verdict class
    let verdictClass = 'verdict-consistent';
    if (event.timing_analysis.assessment === 'appropriate') {
        verdictClass = 'verdict-appropriate';
    } else if (event.timing_analysis.assessment === 'forecast_driven') {
        verdictClass = 'verdict-forecast';
    }
    
    card.innerHTML = `
        <div class="event-header">
            <div class="event-name">
                <div class="event-icon">${icon}</div>
                <div class="event-title">
                    <h3>${event.name} ${event.year} <span style="font-size: 20px; color: #999;">${event.name_zh}</span></h3>
                    <div class="event-date">${event.date_range}</div>
                </div>
            </div>
            <div class="event-verdict ${verdictClass}">
                ${getVerdictBadge(event.timing_analysis.assessment)}
            </div>
        </div>
        
        <div class="event-stats">
            <div class="event-stat">
                <div class="event-stat-label">Official Signal 8 Duration</div>
                <div class="event-stat-value ${!event.official_signal8.issued ? 'na' : ''}">
                    ${event.official_signal8.issued ? `${event.official_signal8.duration_min} min` : 'Not Issued'}
                </div>
            </div>
            <div class="event-stat">
                <div class="event-stat-label">Algorithm Detection</div>
                <div class="event-stat-value ${!event.algorithm_detection.detected ? 'na' : ''}">
                    ${event.algorithm_detection.detected ? `${event.algorithm_detection.duration_min} min` : 'None'}
                </div>
            </div>
            <div class="event-stat">
                <div class="event-stat-label">Forecast Lead Time</div>
                <div class="event-stat-value ${!event.timing_analysis.start_delta_min ? 'na' : ''}">
                    ${event.timing_analysis.start_delta_min ? `+${event.timing_analysis.start_delta_min} min` : 'N/A'}
                </div>
            </div>
            <div class="event-stat">
                <div class="event-stat-label">Coverage</div>
                <div class="event-stat-value ${event.timing_analysis.coverage_percent === 0 ? 'na' : ''}">
                    ${event.timing_analysis.coverage_percent > 0 ? `${event.timing_analysis.coverage_percent}%` : '0%'}
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Get verdict badge text
function getVerdictBadge(assessment) {
    // Updated label to explicitly indicate Signal 8 issuance context for forecast-driven cases
    const badges = {
        'appropriate': '✅ Appropriate',
        'forecast_driven': '⚠️ Signal 8 Issued (Forecast-Driven)',
        'consistent': '✓ Consistent'
    };
    return badges[assessment] || assessment;
}

// Utility: Scroll to timeline
function scrollToTimeline() {
    document.getElementById('timeline').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

// Expose globally
window.scrollToTimeline = scrollToTimeline;
