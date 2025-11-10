# HKO Signal 8 Transparency Portal

**Data-driven validation of Hong Kong Observatory Signal No. 8 timing**

[![Live Site](https://img.shields.io/badge/Live-Site-blue)](https://AndyZHENG0715.github.io/GCAP3226/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-green)](https://github.com/AndyZHENG0715/GCAP3226)

## Overview

This project provides independent, transparent validation of Hong Kong Observatory's (HKO) tropical cyclone Signal No. 8 issuance timing. By comparing official signal periods with observation-based detection algorithms, we demonstrate the value of forecast-based early warning systems and validate that HKO follows published standards appropriately.

### Key Features

- 📊 **Interactive Timeline**: Explore 6 analyzed typhoon events from 2023-2025
- 📈 **Detailed Analysis**: View station-by-station wind data and timing comparisons
- 🔍 **Transparent Methodology**: Full explanation of algorithms and validation process
- 💾 **Open Data**: All raw data, analysis results, and source code publicly available
- 🌍 **Bilingual**: English and Traditional Chinese (中文) support

## Live Portal

Visit the portal at: **[https://AndyZHENG0715.github.io/GCAP3226/](https://AndyZHENG0715.github.io/GCAP3226/)**

## Project Structure

```
docs/
├── index.html              # Homepage with typhoon timeline
├── event.html              # Detailed event analysis page
├── methodology.html        # Methodology and FAQ
├── data.html              # Data downloads and API
├── about.html             # Project information
├── css/
│   ├── styles.css         # Main stylesheet
│   ├── event.css          # Event detail styles
│   ├── methodology.css    # Methodology page styles
│   ├── data.css           # Data page styles
│   └── about.css          # About page styles
├── js/
│   ├── main.js            # Homepage logic
│   ├── event.js           # Event detail page logic
│   ├── methodology.js     # Methodology page logic
│   ├── data.js            # Data page logic
│   └── language.js        # Bilingual support
├── data/
    ├── events/
    │   ├── summary.json   # All events summary
    │   ├── talim.json     # Talim 2023 data
    │   ├── yagi.json      # Yagi 2024 data
    │   ├── toraji.json    # Toraji 2024 data
    │   ├── tapah.json     # Tapah 2025 data
    │   ├── wipha.json     # Wipha 2025 data (Signal 10)
    │   └── ragasa.json    # Ragasa 2025 data (Signal 10)
    ├── stations.json      # Reference stations metadata
    └── sensitivity.json   # Persistence sensitivity analysis
```

## Data Sources

All wind data is sourced from **Hong Kong Observatory's public archives** of 10-minute mean wind speeds at reference stations:
- Chek Lap Kok (赤鱲角)
- Lau Fau Shan (流浮山)
- Ta Kwu Ling (打鼓嶺)
- Sha Tin (沙田)
- Sai Kung (西貢)
- Kai Tak (啟德)
- Tsing Yi (青衣)
- Cheung Chau (長洲)

## Methodology

### HKO Official Process (Forecast-Based)
1. Typhoon track and intensity forecast (12-24h ahead)
2. Wind speed prediction at reference stations
3. Expect ≥4 of 8 stations to reach gale-force winds (≥63 km/h)
4. Issue Signal 8 with lead time for public preparation
5. Monitor and update as conditions change

### Our Validation Algorithm (Observation-Only)
1. Observe actual 10-minute mean wind speeds
2. Count stations currently ≥63 km/h
3. Require ≥4 stations for ≥2 consecutive periods (persistence check)
4. Compare detection timing with official signal periods
5. Generate validation report

**Key Difference**: HKO uses **forecast** (what is expected), our algorithm validates using **observation** (what actually happened). Timing differences represent valuable early warning lead time.

## Key Findings

✅ **HKO Signal 8 issuances are appropriate** and consistent with published standards

⏱️ **Average lead time**: 330 minutes for Talim 2023 (forecast advantage)

🎯 **Coverage validation**: 64.9% overlap for peak event (Talim)

🏆 **Historic 2025**: First year since 1964 with two Signal 10 warnings (Wipha, Ragasa)

⚠️ **Some events show no detection**: Localized/offshore winds justify official signals despite not meeting lowland multi-station criteria

❌ **Algorithm limitations**: Fails for direct-hit typhoons with eye passage (Wipha, Ragasa)

## Building and Deployment

### Prerequisites
- Python 3.8+ (for data processing)
- Modern web browser (for viewing portal)

### Generate Data Files

```bash
# Install Python dependencies
pip install pandas

# Run data export script
python export_web_data.py
```

This generates JSON files in `docs/data/` from validation reports in `reports/`.

### Local Development

Simply open `docs/index.html` in a web browser, or use a local server:

```bash
# Python 3
cd docs
python -m http.server 8000

# Then visit http://localhost:8000
```

### GitHub Pages Deployment

1. Push the repository to GitHub
2. Go to Settings → Pages
3. Select branch `main` and folder `/docs`
4. Your portal will be live at `https://andyzheng0715.github.io/hko-signal8-validation/`

## Technology Stack

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **Vanilla JavaScript**: No frameworks, fast loading
- **Chart.js 4.x**: Interactive timeline visualizations
- **Google Fonts (Inter)**: Clean, readable typography

### Data Processing
- **Python 3**: Analysis and validation
- **pandas**: Data manipulation
- **JSON**: Structured data format for web consumption

### Design Philosophy
- **Mobile-first**: Optimized for Hong Kong's 60%+ mobile traffic
- **Progressive disclosure**: Simple view → technical details
- **Accessibility**: WCAG standards, bilingual support
- **Performance**: Static site, fast CDN delivery

## Data API

All data is available as JSON endpoints:

```javascript
// Get all events summary
fetch('https://andyzheng0715.github.io/hko-signal8-validation/data/events/summary.json')
  .then(response => response.json())
  .then(data => console.log(data));

// Get specific event details
fetch('https://andyzheng0715.github.io/hko-signal8-validation/data/events/talim.json')
  .then(response => response.json())
  .then(data => console.log(data));

// Get stations metadata
fetch('https://andyzheng0715.github.io/hko-signal8-validation/data/stations.json')
  .then(response => response.json())
  .then(data => console.log(data));
```

## License

This project is provided for educational and research purposes. Wind data is sourced from Hong Kong Observatory public archives.

**Suggested Citation**:
```
HKO Signal 8 Transparency Portal (2025). Validation of Tropical Cyclone Signal No. 8 Timing. 
https://andyzheng0715.github.io/hko-signal8-validation/
```

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This is an **independent citizen analysis** for transparency and education. It is **not official** and **not endorsed by or affiliated with** the Hong Kong Observatory. Our goal is validation and public understanding, not criticism.

## Contact

- **GitHub Issues**: [Report bugs or suggest features](https://github.com/yourusername/hko-signal8-validation/issues)
- **Discussions**: [Join the conversation](https://github.com/yourusername/hko-signal8-validation/discussions)

## Acknowledgments

- Hong Kong Observatory for maintaining public wind data archives
- Open-source software communities (Python, Chart.js, etc.)
- Hong Kong residents interested in weather transparency

---

**Last Updated**: 2025-11-10  
**Analysis Period**: 2023-2025 (6 tropical cyclone events)

Made with ❤️ for transparency and public safety
