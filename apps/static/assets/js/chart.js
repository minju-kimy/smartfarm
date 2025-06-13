document.addEventListener("DOMContentLoaded", function () {
  function createChart(ctxId, endpoint, borderColor, gradientColorStops, yMin, yMax, yStep, labelText = '') {
    fetch(endpoint)
      .then(response => response.json())
      .then(data => {
        const ctx = document.getElementById(ctxId).getContext('2d');
        const gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
        gradientStroke.addColorStop(1, gradientColorStops[0]);
        gradientStroke.addColorStop(0.4, gradientColorStops[1]);
        gradientStroke.addColorStop(0, gradientColorStops[2]);

        new Chart(ctx, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              label: labelText || ' ', 
              fill: true,
              backgroundColor: gradientStroke,
              borderColor: borderColor,
              borderWidth: 2,
              pointBackgroundColor: borderColor,
              pointHoverBackgroundColor: borderColor,
              pointBorderColor: 'rgba(255,255,255,0)',
              pointBorderWidth: 20,
              pointHoverRadius: 4,
              pointHoverBorderWidth: 15,
              pointRadius: 4,
              data: data.values
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false,
                labels: {
                  generateLabels: () => [] // 
                }
              },
              tooltip: {
                enabled: true,
                displayColors: false,
                callbacks: {
                  label: function (context) {
                    return `${context.raw}`;
                  }
                },
                backgroundColor: '#f5f5f5',
                titleColor: '#333',
                bodyColor: '#666',
                bodySpacing: 4,
                padding: 12,
                mode: 'index',
                intersect: false,
                position: 'nearest'
              }
            },
            interaction: {
              mode: 'nearest', // 
              intersect: false
            },
            onClick: () => {}, // 
            scales: {
              y: {
                min: yMin,
                max: yMax,
                ticks: { stepSize: yStep, color: "#9a9a9a" },
                grid: { drawBorder: false, color: 'rgba(200, 200, 200, 0.2)' }
              },
              x: {
                ticks: { color: "#9a9a9a", autoSkip: true, maxTicksLimit: 6 },
                grid: { drawBorder: false, color: 'rgba(200, 200, 200, 0.1)' }
              }
            }
          }
        });
      });
  }

  // temperature
  createChart(
    "chartLinePurple",
    "/smartfarm/chart/temperature_data",
    "#d346b1",
    ['rgba(72,72,176,0.2)', 'rgba(72,72,176,0.0)', 'rgba(119,52,169,0)'],
    5, 40, 5,
    "Temperature (°C)"
  );

  // humidity
  createChart(
    "CountryChart",
    "/smartfarm/chart/humidity_data",
    "#42a5f5",
    ['rgba(66, 165, 245, 0.2)', 'rgba(66, 165, 245, 0.0)', 'rgba(66, 165, 245, 0)'],
    4, 9, 1,
    "Humidity (%)"
  );

  // co2
  createChart(
    "chartLineGreen",
    "/smartfarm/chart/co2_data",
    "#66bb6a",
    ['rgba(102, 187, 106, 0.2)', 'rgba(102, 187, 106, 0.0)', 'rgba(102, 187, 106, 0)'],
    0, 4, 0.5,
    "CO₂ (ppm)"
  );
});
