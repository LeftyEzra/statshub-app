//******************************* */
// Search Form For Filtering Players Begin
//******************************** */

document.getElementById('searchForm').addEventListener('submit', function(e) {
  e.preventDefault(); // stop page reload

  const query = document.getElementById('rd-search-form-input').value;

  fetch("{% url 'search-result' %}?s=" + encodeURIComponent(query))
    .then(response => response.text())
    .then(html => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const results = doc.querySelector('.rd-search-results');

      document.getElementById('resultsContent').innerHTML = results ? results.innerHTML : "<p>No results found.</p>";

      new bootstrap.Collapse(document.getElementById('searchResults'), { show: true });
    })
    .catch(err => {
      document.getElementById('resultsContent').innerHTML = "<p>Error loading results.</p>";
      console.error(err);
    });
});
//*********************************** */
// Search Form For Filtering Players End
//*********************************** */





// Example Matrix Starts

// Example Matrix Ends




// Example Matrix Starts



//Average Example Matrix Ends


// Player Game Summary Begin


// Catching the Pandas .describe() results




// Player Game Summary Ends
// Total Game Summary Statistics
// 1. Bar Chart
// 1. MUST register the plugin at the top
Chart.register(ChartDataLabels);

// 2. Bar Chart Logic


// 2. Shared Doughnut Options


// 2. Shared Doughnut Options

// 3. Initialize ALL Three Doughnuts



// Total Game summary End






