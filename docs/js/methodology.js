// Methodology page JavaScript
let stationsData = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadStationsData();
    renderStations();
});

async function loadStationsData() {
    try {
        const response = await fetch('data/stations.json');
        stationsData = await response.json();
        console.log('Stations data loaded:', stationsData);
    } catch (error) {
        console.error('Error loading stations data:', error);
    }
}

function renderStations() {
    if (!stationsData) return;
    
    const container = document.getElementById('stations-grid');
    
    container.innerHTML = stationsData.stations.map(station => `
        <div class="station-info-card">
            <h3>${station.name}</h3>
            <div class="station-name-zh">${station.name_zh}</div>
            <p>${station.description}</p>
            <div class="station-meta">
                <div>📍 Elevation: ${station.elevation_m}m</div>
                <div>🌐 ${station.latitude.toFixed(4)}°N, ${station.longitude.toFixed(4)}°E</div>
            </div>
        </div>
    `).join('');
}
