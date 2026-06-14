document.addEventListener("DOMContentLoaded", function () {

   // Helper to render bar charts
function renderBarChart(elemId, seriesConfig, titleText) {
    const barElem = document.querySelector(`#${elemId}`);
    if (barElem) {
        const gameData = JSON.parse(barElem.getAttribute('data-chart-data'));
        const opponents = gameData.map(g => g.game_date);

        

        const barOptions = {
            series: seriesConfig,
            chart: { type: 'bar', height: 200, toolbar: { show: false } },
            colors: ['#06a829', '#e30117'],
            plotOptions:{ bar: { borderRadius:4, dataLabels: { position: 'top' } }},
            dataLabels: {
                        enabled: true,
                        formatter: function (val) {
                            return val;
                        },
                        offsetY: -16, // Adjusts the distance above the bar
                        style: {
                            fontSize: '12px',
                            colors: ["#304758"] // Dark color so it's readable on the background
                        }
                    },
            xaxis: { categories: opponents },
            
            title: { text: titleText, align: 'center' }
        };
        new ApexCharts(barElem, barOptions).render();
    }
}

// Render FG, 3P, FT bar charts
const gameData = JSON.parse(document.querySelector("#fgBarChart").getAttribute('data-chart-data'));

renderBarChart("fgBarChart", [
    { name: "FGM", data: gameData.map(g => g.fgm) },
    { name: "FGA", data: gameData.map(g => g.fga) }
], "Last 5 Games: Field Goals");

renderBarChart("threeBarChart", [
    { name: "3PM", data: gameData.map(g => g.p3m) },
    { name: "3PA", data: gameData.map(g => g.p3a) }
], "Last 5 Games: 3-Pointers");

renderBarChart("ftBarChart", [
    { name: "FTM", data: gameData.map(g => g.ftm) },
    { name: "FTA", data: gameData.map(g => g.fta) }
], "Last 5 Games: Free Throws");

// Donut charts (works for all FG, 3P, FT groups)
const donutContainers = document.querySelectorAll(".shooting-donut");

donutContainers.forEach((container) => {
    const made = parseInt(container.getAttribute('data-made'));
    const attempts = parseInt(container.getAttribute('data-attempts'));
    const missed = attempts - made;
    const pct = attempts > 0 ? ((made / attempts) * 100).toFixed(1) : 0;
    const label = container.getAttribute('data-label') || '';

    const donutOptions = {
        series: [made, missed],
        chart: { type: 'donut', height: 100 },
        colors: ['#06a829', '#e30117'],
        labels: ['Made', 'Missed'],
        legend: { show: false },
        dataLabels: {
            enabled: false // This hides those overlapping percentages on the rings
        },
        plotOptions: {
            pie: {
                donut: {
                    labels: {
                        show: true,
                        name: {
                            show: true,
                            fontSize: '1px', // Shorter "FG%" label
                            offsetY: -10
                        },
                        value: {
                            show: true,
                            fontSize: '10px', // Smaller percentage value
                            offsetY: 5,
                            formatter: (val) => val + ''
                        },
                        total: {
                            show: true,
                            label: label,
                            formatter: () => pct + '%'
                        }
                    }
                }
            }
        }
    };
    new ApexCharts(container, donutOptions).render();
});


    
});




