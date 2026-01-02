import React, { useEffect, useState } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import highchartsMap from "highcharts/modules/map";

// Highcharts Map Module Initialize
if (typeof Highcharts === 'object' && !Highcharts.maps) {
    highchartsMap(Highcharts);
}

const DengueMap = ({ stats }) => {
    const [topology, setTopology] = useState(null);

    useEffect(() => {
        // Load Pakistan Topology
        fetch("https://code.highcharts.com/mapdata/countries/pk/pk-all.topo.json")
            .then(res => res.json())
            .then(data => setTopology(data))
            .catch(err => console.error("Map Error:", err));
    }, []);

    // --- 🎨 Color Logic ---
    const getCityColor = (cases) => {
        if (cases >= 200) return '#a855f7'; // Purple
        if (cases >= 100) return '#ef4444'; // Red
        if (cases >= 10) return '#3b82f6';  // Blue
        return '#10b981';                   // Green
    };

    // --- 🔄 Data Mapping ---
    const mapData = stats ? stats.map(cityData => {
        const cityName = (cityData.city || cityData.city_name || "Unknown").trim();
        let finalLat = cityData.latitude || cityData.lat;
        let finalLon = cityData.longitude || cityData.lon;

        if (!finalLat || !finalLon) return null;

        const activeCases = parseInt(cityData.active || cityData.cases || 0);
        const recoveredCases = parseInt(cityData.recovered || 0);
        const deathsCases = parseInt(cityData.deaths || 0);

        return {
            name: cityName,
            lat: parseFloat(finalLat),
            lon: parseFloat(finalLon),
            z: activeCases + 5,
            active: activeCases,
            recovered: recoveredCases,
            deaths: deathsCases,
            color: getCityColor(activeCases)
        };
    }).filter(item => item !== null) : [];

    // --- 🛠️ MAP OPTIONS ---
    const options = {
        chart: {
            map: topology,
            backgroundColor: 'transparent',
            height: 550,
            style: { fontFamily: 'inherit' }
        },
        title: { text: undefined },
        credits: { enabled: false },
        mapNavigation: {
            enabled: true,
            buttonOptions: { verticalAlign: 'bottom' }
        },
        tooltip: {
            useHTML: true,
            backgroundColor: 'transparent',
            borderWidth: 0,
            shadow: false,
            padding: 0,
            followPointer: false,
            // 👇 SARA DESIGN YAHAN INLINE STYLES MEIN HAI (Ab CSS file ki zaroorat nahi)
            pointFormat: `
                <div style="
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 16px;
                    padding: 16px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                    min-width: 180px;
                    font-family: 'Segoe UI', sans-serif;
                ">
                    <div style="
                        display: flex; 
                        justify-content: space-between; 
                        align-items: center; 
                        border-bottom: 1px solid #eee; 
                        padding-bottom: 8px; 
                        margin-bottom: 10px;
                    ">
                        <b style="font-size: 16px; color: #1e293b; text-transform: capitalize;">{point.name}</b>
                        <span style="
                            height: 10px; 
                            width: 10px; 
                            background-color: #ef4444; 
                            border-radius: 50%; 
                            box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
                            display: inline-block;
                        "></span>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px;">
                            <span style="color: #64748b; font-weight: 500;">🦟 Active</span>
                            <span style="color: #ef4444; font-weight: 700;">{point.active}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px;">
                            <span style="color: #64748b; font-weight: 500;">🏥 Recovered</span>
                            <span style="color: #10b981; font-weight: 700;">{point.recovered}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px;">
                            <span style="color: #64748b; font-weight: 500;">💀 Deaths</span>
                            <span style="color: #64748b; font-weight: 700;">{point.deaths}</span>
                        </div>
                    </div>
                </div>`
        },
        series: [
            {
                name: 'Basemap',
                borderColor: '#cbd5e1', 
                nullColor: '#f8fafc',
                showInLegend: false,
                states: { hover: { color: '#e2e8f0' } }
            },
            {
                type: 'mappoint',
                name: 'Cities',
                data: mapData,
                minSize: 10,
                maxSize: 30,
                marker: {
                    lineWidth: 2,
                    lineColor: '#ffffff',
                    symbol: 'circle'
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.name}',
                    style: {
                        color: '#334155',
                        fontWeight: '600',
                        fontSize: '10px',
                        textOutline: 'none'
                    },
                    y: -8
                }
            }
        ]
    };

    return (
        <div className="h-full w-full bg-white rounded-3xl border border-slate-200 p-4 relative flex flex-col shadow-sm">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-2 px-2 gap-2">
                <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#6366F1]"></span>
                    <h3 className="font-bold text-slate-800 text-sm">Live Heatmap</h3>
                </div>
                
                {/* Legend */}
                <div className="flex flex-wrap gap-2 text-[10px] font-bold bg-slate-50 p-1.5 rounded-lg border border-slate-100">
                    <span className="flex items-center gap-1 text-slate-500">
                        <span className="w-2 h-2 rounded-full bg-[#10b981]"></span> &lt;10 (Safe)
                    </span>
                    <span className="flex items-center gap-1 text-slate-500">
                        <span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span> 10+ (Blue)
                    </span>
                    <span className="flex items-center gap-1 text-slate-500">
                        <span className="w-2 h-2 rounded-full bg-[#ef4444]"></span> 100+ (Red)
                    </span>
                    <span className="flex items-center gap-1 text-slate-500">
                        <span className="w-2 h-2 rounded-full bg-[#a855f7]"></span> 200+ (Purple)
                    </span>
                </div>
            </div>

            {/* Map Container */}
            <div className="flex-1 rounded-2xl overflow-hidden relative">
                {!topology ? (
                    <div className="h-full flex items-center justify-center text-slate-400 text-xs">Loading Map...</div>
                ) : (
                    <HighchartsReact
                        highcharts={Highcharts}
                        constructorType={'mapChart'}
                        options={options}
                    />
                )}
            </div>
        </div>
    );
};

export default DengueMap;