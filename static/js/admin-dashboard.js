// This wrapper is essential when using an external file
document.addEventListener("DOMContentLoaded", function () {


// Line Chart
// --- 1. REVENUE TREND LINE (Financial Growth Trajectory) ---
const lineElem = document.querySelector("#topProductsChart");

if (lineElem) {
    const lineData = JSON.parse(lineElem.getAttribute('data-series'));
    const lineLabels = JSON.parse(lineElem.getAttribute('data-labels'));

    const lineOptions = {
    series: [{
        name: 'Total Revenue',
        data: lineData
    }],
    chart: {
        type: 'area',
        height: 250,
        foreColor: '#ffffff',
        toolbar: { show: false },
        zoom: { enabled: true },
        background: 'linear-gradient(135deg, #004d61, #001f3f)', 
    },
    colors: ['#ffc107','#17a2b8','#28a745',  '#ffc107'], // info, success, warning
    stroke: {
        curve: 'smooth',
        width: 3
    },
    fill: {
        type: 'gradient',
        gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.8,
            opacityTo: 0.2,
            stops: [0, 90, 100]
        }
    },
    dataLabels: { enabled: false },
    yaxis: {
        labels: {
            formatter: function (val) {
                return "$" + (val ? val.toFixed(2) : "0.00");
            },
            style: { colors: '#f4f0f0' }
        }
    },
    xaxis: {
        categories: lineLabels,
        axisBorder: { show: false },
        axisTicks: { show: true },
        labels: { style: { colors: '#f4f0f0' } }
    },
    grid: {
        borderColor: '#90A4AE',
        position: 'back',
        strokeDashArray: 2,
        yaxis: { lines: { show: true } },
        
    },
    tooltip: {
        theme: 'dark',
        y: {
            formatter: function (val) {
                return "$" + val.toFixed(2);
            }
        }
    }
};


    const revenueChart = new ApexCharts(lineElem, lineOptions);
    revenueChart.render();

    console.log(lineData);
    console.log(lineLabels);
    console.log(lineElem.getAttribute('data-series'));
    console.log(lineElem.getAttribute('data-labels'));

}






// --- 2. SPORT CATEGORY CHART ---
const sportElem = document.querySelector("#sportCategoryChart");

if (sportElem) {
    const sLabels = JSON.parse(sportElem.getAttribute('data-labels'));
    const sValues = JSON.parse(sportElem.getAttribute('data-values'));

    // Map data for ApexCharts format
    const sportSeriesData = sLabels.map((label, index) => ({
        x: label,
        y: sValues[index]
    }));

    const maxValue = Math.max(...sValues);
    const dynamicMax = maxValue + 10;

    new ApexCharts(sportElem, {
        series: [{ name: 'Units Sold', data: sportSeriesData }],
        chart: { 
            type: 'bar', 
            height: 250, 
            foreColor: '#0e0e0e', 
            toolbar: { show: false } 
        },
        plotOptions: {
            bar: {
                horizontal: true,
                borderRadius: 2,
                barHeight: '70%',
                dataLabels: { position: 'top' }
            }
        },
        colors: ['#098524'], 
        dataLabels: {
            enabled: true,
            offsetX: 5, 
            textAnchor: 'start',
            style: { fontSize: '15px', colors: ["#ffffff"] },
            forceNiceScale: true,
        },
        yaxis: {
            labels: {
                style: { colors: '#f4f0f0' }
            }
        },
        xaxis: { 
            type: 'numeric', // Correct type for the value axis in horizontal charts
            min: 0,          // Forces the chart scale to start cleanly at 0 instead of dropping below
            max: dynamicMax,
            labels: { style: { colors: '#f4f0f0' } },
            axisBorder: { show: false },
            axisTicks: { show: true },
        },
        grid: { borderColor: 'rgba(255,255,255,0.1)' },
        tooltip: {
            theme: 'dark',
            y: {
                formatter: function (val) {
                    return "$" + val.toFixed(2);
                }
            }
        }
    }).render();
}


// --- 3. PRODUCT VELOCITY TREEMAP ---
const treeElem = document.querySelector("#productCategoryChart");

if (treeElem) {
    const labels = JSON.parse(treeElem.getAttribute('data-labels'));
    const values = JSON.parse(treeElem.getAttribute('data-values'));

    // Format for Treemap [ {x: 'Name', y: 10}, ... ]
    const treemapData = labels.map((label, index) => ({
        x: label,
        y: values[index]
    }));

    new ApexCharts(treeElem, {
        series: [{ data: treemapData }],
        chart: {
            height: 350,
            type: 'treemap',
            toolbar: { show: true }
        },
        dataLabels: {
            enabled: true,
            style: {
                fontSize: '12px',
                fontWeight: 'bold',
                colors: ['#0d0d0d']
            },
            formatter: function(text, op) {
                return [text, op.value]; // Product Name on top, Value below
            },
            offsetY: -4
        },
        plotOptions: {
            treemap: {
                enableShades: true,
                shadeIntensity: 0.5,
                colorScale: {
                    ranges: [
                        { from: 0, to: 1, color: '#CD363A' }, // Warning Red
                        { from: 2, to: 3, color: '#fba00e' }, // Success Teal
                        { from: 4, to: 10, color: '#3e9b04' }
                    ]
                }
            }
        },
        tooltip: {
                        theme: 'dark',
                        y: {
                            formatter: function (val) {
                                return "" + val.toFixed(2);
                            }
                        }
                    },

                 

        stroke: { width: 1, colors: ['#ffffff33'] } // Subtle borders
    }).render();
}




// --- 4. PAYMENT STATUS RADIAL BAR ---
const payElem = document.querySelector("#paymentStatusChart");

if (payElem) {
    const paymentLabels = JSON.parse(payElem.getAttribute('data-labels'));
    const paymentValues = JSON.parse(payElem.getAttribute('data-series'));

    const paymentRadialOptions = {
        series: paymentValues, 
        labels: paymentLabels,
        chart: {
            height: 280,
            type: 'radialBar',
            foreColor: '#a10909'
        },
        plotOptions: {
            radialBar: {
                offsetY: 0,
                startAngle: 0,
                endAngle: 270,
                hollow: {
                    margin: 5,
                    size: '30%',
                    background: 'transparent',
                },
                dataLabels: {
                    name: { show: true },
                    value: { show: false }
                },
                barLabels: {
                    enabled: true,
                    useSeriesColors: true,
                    offsetX: -8,
                    fontSize: '14px',
                    formatter: function(seriesName, opts) {
                        return seriesName + ":  " + opts.w.globals.series[opts.seriesIndex] + "%";
                    },
                },
            }
        },
        // Using Command Center Green (#2d5a3f) and Gold (#f1b44c)
        colors: ['#1d7702', '#f9a007'], 
        responsive: [{
            breakpoint: 480,
            options: {
                legend: { show: true }
            }
        }]
    };

    new ApexCharts(payElem, paymentRadialOptions).render();
}



});