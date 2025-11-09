// Data page JavaScript
let summaryData = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadSummary();
    renderEventDownloads();
});

async function loadSummary() {
    try {
        const response = await fetch('data/events/summary.json');
        summaryData = await response.json();
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

function renderEventDownloads() {
    if (!summaryData) return;
    
    const container = document.getElementById('event-downloads');
    
    container.innerHTML = summaryData.events.map(event => `
        <a href="data/events/${event.id}.json" class="download-item">
            <span class="download-name">📊 ${event.name} ${event.year} (${event.name_zh})</span>
            <span class="download-meta">${event.date_range}</span>
        </a>
    `).join('');
}