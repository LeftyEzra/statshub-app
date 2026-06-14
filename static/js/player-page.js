// This wrapper is essential when using an external file
document.addEventListener("DOMContentLoaded", function () {




$(document).ready(function () {
    console.log("Document is ready");

    // Function to hide all sections
    function resetTables() {
        $("#overView, #biography, #last5games, ").hide();
    }

    // Run resetTables() on page load
    resetTables();

    // Click event for navigation links
    $(".nav-link").click(function (event) {
        event.preventDefault(); // Prevent default behavior
        console.log("Nav link clicked:", $(this).attr("id"));


        $(".nav-link").removeClass("active"); // Remove active class from all links
        $(this).addClass("active"); // Add active class to the clicked link

        resetTables(); // Hide all sections

        // Show the appropriate section based on the clicked link
        if ($(this).attr("id") === "bio") {
            console.log("Biography link clicked");
            $("#biography").fadeIn("slow");
        } else if ($(this).attr("id") === "overviewDiv") {
            console.log("Overview link clicked");
            $("#overView").fadeIn("slow");
         
        } else if ($(this).attr("id") === "last5games") {
            console.log("L5G link clicked");
            $("#last5games").show()
        
        } else {
            console.log($(this).text() + " link clicked");
            window.location.href = $(this).attr("href");
        }
    });

    // Default display: Show the Home content
    $("#overView").show();
    

});




// Line Chart
// --- 1. POINTS TREND LINE ---
const lineElem = document.querySelector("#pointsChart");

if (lineElem) {
    const lineData = JSON.parse(lineElem.getAttribute('data-series'));
    const lineLabels = JSON.parse(lineElem.getAttribute('data-labels'));

    const lineOptions = {
    series: [{
        name: 'Points',
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
    colors: ['#ffc107','#28a745','#17a2b8','#28a745'], // info, success, warning
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
                return (val ? val.toFixed(0) : "0");
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
    markers: {
    size: 4,
    colors: ['#ffc107'],
    strokeColors: '#fff',
    strokeWidth: 2,
    hover: { size: 7 }
},
    tooltip: {
        theme: 'dark',
        y: {
            formatter: function (val) {
                return "" + val.toFixed(0);
            }
        }
    }
};


    const pointsChart = new ApexCharts(lineElem, lineOptions);
    pointsChart.render();

    console.log(lineData);
    console.log(lineLabels);
    console.log(lineElem.getAttribute('data-series'));
    console.log(lineElem.getAttribute('data-labels'));

}




});






document.addEventListener('DOMContentLoaded', function () {
    const hiddenCards = [
      document.getElementById('card4'),
      document.getElementById('card5'),
      document.getElementById('card6')
    ];
    const viewMoreBtn = document.getElementById('viewMoreBtn');
    const viewLessBtn = document.getElementById('viewLessBtn');
    const careerRecordSection = document.getElementById('careerRecordSection');

    viewLessBtn.classList.add('hidden');

    viewMoreBtn.addEventListener('click', function () {
      hiddenCards.forEach(card => card.classList.remove('hidden'));
      viewMoreBtn.classList.add('hidden');
      viewLessBtn.classList.remove('hidden');
    });

    viewLessBtn.addEventListener('click', function () {
      hiddenCards.forEach(card => card.classList.add('hidden'));
      viewLessBtn.classList.add('hidden');
      viewMoreBtn.classList.remove('hidden');
      careerRecordSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });



    function scrollG(distance) {
    // Target the WRAPPER, not the row
    const container = document.querySelector('.game-slider-wrapper');
    if (container) {
        container.scrollBy({
            left: distance,
            behavior: 'smooth'
        });
    } else {
        console.error("Slider wrapper not found!");
    }
    }




function scrollPlayers(distance) {
    const container = document.querySelector('.player-slider-wrapper');
    if (container) {
        container.scrollBy({
            left: distance,
            behavior: 'smooth'
        });
    }
}






document.addEventListener("DOMContentLoaded", function() {
    const navWrapper = document.querySelector('.player-nav-wrapper');
    const navTabs = navWrapper.querySelector('.nav-tabs');
    const btnNext = navWrapper.querySelector('[data-nav-next]');
    const btnPrev = navWrapper.querySelector('[data-nav-prev]');

    const scrollAmount = 150; // Adjust based on tab width

    btnNext.addEventListener('click', () => {
        navTabs.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });

    btnPrev.addEventListener('click', () => {
        navTabs.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
});


