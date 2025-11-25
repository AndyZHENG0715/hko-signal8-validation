// Main JavaScript for homepage
let eventsData = null;
let summaryData = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        await loadData();
        renderTimeline();
        updateMetrics();
        updateKeyFindings();
        hideLoading();
    } catch (error) {
        console.error('Error initializing page:', error);
        showError('Failed to load typhoon data. Please refresh the page.');
        hideLoading();
    }
});

// Show/hide loading overlay
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('hidden');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        setTimeout(() => overlay.classList.add('hidden'), 300);
    }
}

function showError(message) {
    // Create error message if doesn't exist
    let errorEl = document.getElementById('error-message');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.id = 'error-message';
        errorEl.className = 'error-message';
        document.body.insertBefore(errorEl, document.body.firstChild);
    }
    errorEl.textContent = message;
    errorEl.classList.add('show');
}

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
    if (!summaryData || !eventsData) return;
    
    const stats = summaryData.statistics;
    
    // Safely update metrics with null checks
    const totalTyphoons = document.getElementById('total-typhoons');
    if (totalTyphoons) totalTyphoons.textContent = stats.total_events;
    
    const avgLeadTime = document.getElementById('avg-lead-time');
    if (avgLeadTime && stats.avg_lead_time_min) {
        avgLeadTime.innerHTML = 
            `${stats.avg_lead_time_min} <span class="metric-unit">min</span>`;
    }
    
    const stationCount = document.getElementById('station-count');
    if (stationCount) stationCount.textContent = stats.reference_stations;
    
    // Calculate peak coverage from Talim event
    const talimData = eventsData['talim'];
    const coveragePercent = document.getElementById('coverage-percent');
    if (coveragePercent && talimData) {
        const coverage = talimData.timing_analysis.coverage_percent;
        coveragePercent.innerHTML = `${coverage}<span class="metric-unit">%</span>`;
    }
    
    // Last updated
    const lastUpdated = document.getElementById('last-updated');
    if (lastUpdated) {
        const updatedDate = new Date(summaryData.generated_at);
        lastUpdated.textContent = 
            `Last updated: ${updatedDate.toISOString().split('T')[0]}`;
    }
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
    const tier = event.verification_tier || event.timing_analysis.assessment;
    card.className = `typhoon-event card severity-${event.severity.replace(' ', '-')} tier-${tier}`;
    card.onclick = () => {
        window.location.href = `event.html?id=${event.id}`;
    };
    
    // Determine icon from verification tier (tier overrides raw severity icon)
    let icon = '🌪️';
    if (tier === 'verified') icon = '🟢';
    else if (tier === 'pattern_validated') icon = '⚠️';
    else if (tier === 'unverified') icon = '❓';
    else if (tier === 'no_signal') icon = '➖';
    let verdictClass = 'verdict-consistent';
    if (tier === 'verified') {
        verdictClass = 'verdict-appropriate';
    } else if (tier === 'pattern_validated') {
        verdictClass = 'verdict-pattern';
    } else if (tier === 'unverified') {
        verdictClass = 'verdict-forecast';
    } else if (tier === 'no_signal') {
        verdictClass = 'verdict-consistent';
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
                ${getVerificationBadge(tier)}
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
                <div class="event-stat-label">Observed Sustained T8 Period</div>
                <div class="event-stat-value ${!event.algorithm_detection.detected ? 'na' : ''}">
                    ${event.algorithm_detection.detected ? `${event.algorithm_detection.duration_min} min` : 'None'}
                </div>
            </div>
            <div class="event-stat">
                <div class="event-stat-label">Early Warning Time</div>
                <div class="event-stat-value ${!event.timing_analysis.start_delta_min ? 'na' : ''}">
                    ${event.timing_analysis.start_delta_min ? `+${event.timing_analysis.start_delta_min} min` : 'N/A'}
                </div>
            </div>
            <div class="event-stat">
                <div class="event-stat-label">Sustained Wind Coverage</div>
                <div class="event-stat-value ${event.timing_analysis.coverage_percent === 0 ? 'na' : ''}">
                    ${event.timing_analysis.coverage_percent > 0 ? `${event.timing_analysis.coverage_percent}%` : '0%'}
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Get verdict badge text
function getVerificationBadge(tier) {
    const badges = {
        'verified': '✅ Verified',
        'pattern_validated': '⚠️ Pattern‑Validated',
        'unverified': '❓ Unverified',
        'no_signal': '✓ No Signal'
    };
    // Legacy fallbacks
    if (!badges[tier]) {
        if (tier === 'appropriate') return '✅ Appropriate';
        if (tier === 'forecast_driven') return '❓ Unverified';
        if (tier === 'consistent') return '✓ No Signal';
    }
    return badges[tier] || tier;
}

// Utility: Scroll to timeline
function scrollToTimeline() {
    document.getElementById('timeline').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

// Update Key Findings section
function updateKeyFindings() {
    if (!summaryData || !eventsData) return;
    
    // New tier counts
    const tierCounts = summaryData.statistics.tier_counts || {
        verified: 0,
        pattern_validated: 0,
        unverified: 0,
        no_signal: 0
    };
    
    const appropriateEl = document.getElementById('appropriate-count');
    if (appropriateEl) appropriateEl.textContent = tierCounts.verified;
    const forecastEl = document.getElementById('forecast-count');
    if (forecastEl) forecastEl.textContent = tierCounts.unverified;
    const patternEl = document.getElementById('pattern-count');
    if (patternEl) patternEl.textContent = tierCounts.pattern_validated;
    
    // Calculate coverage statistics
    const coverages = summaryData.events
        .map(e => eventsData[e.id].timing_analysis.coverage_percent)
        .filter(c => c !== null && c !== undefined);
    
    const avgCoverage = coverages.length ? coverages.reduce((sum, c) => sum + c, 0) / coverages.length : 0;
    
    const avgCoverageEl = document.getElementById('avg-coverage');
    if (avgCoverageEl) avgCoverageEl.textContent = `${avgCoverage.toFixed(1)}%`;
    
    // Find highest and lowest coverage
    let highestEvent = null;
    let lowestEvents = [];
    let maxCoverage = -1;
    let minCoverage = 101;
    
    summaryData.events.forEach(event => {
        const coverage = eventsData[event.id].timing_analysis.coverage_percent;
        if (coverage > maxCoverage) {
            maxCoverage = coverage;
            highestEvent = event;
        }
        if (coverage < minCoverage) {
            minCoverage = coverage;
            lowestEvents = [event];
        } else if (coverage === minCoverage) {
            lowestEvents.push(event);
        }
    });
    
    const highestEl = document.getElementById('highest-coverage');
    if (highestEl && highestEvent) {
        highestEl.textContent = `${highestEvent.name} (${maxCoverage}%)`;
    }
    
    const lowestEl = document.getElementById('lowest-coverage');
    if (lowestEl && lowestEvents.length > 0) {
        const names = lowestEvents.map(e => e.name).join(', ');
        lowestEl.textContent = `${names} (${minCoverage}%)`;
    }
}

// Expose globally
window.scrollToTimeline = scrollToTimeline;
