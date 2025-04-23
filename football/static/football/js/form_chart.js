document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/form-chart/")
    .then(response => response.json())
    .then(data => {
      const labels = ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5"];
      const resultMap = { "W": 3, "D": 1, "L": 0 };

      const ctx = document.getElementById("formChart").getContext("2d");

      const gradients = [
        createGradient(ctx, "#4facfe", "#00f2fe"),  // FCB
        createGradient(ctx, "#f093fb", "#f5576c"),  // RMA
        createGradient(ctx, "#f6d365", "#fda085"),  // ATL
        createGradient(ctx, "#c471f5", "#fa71cd"),  // ATH
      ];

      const datasets = data.map((team, index) => ({
        label: team.team,
        data: team.form.map(r => resultMap[r]),
        backgroundColor: gradients[index],
        borderRadius: 10,
        borderSkipped: false,
        barPercentage: 0.6
      }));

      new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top"
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const value = context.raw;
                  return `${context.dataset.label}: ${value === 3 ? 'Win' : value === 1 ? 'Draw' : 'Loss'}`;
                }
              }
            },
            title: {
              display: true,
              text: 'Recent Form of Top 4 Teams',
              color: '#2e7d32',
              font: { size: 20 }
            }
          },
          scales: {
            y: {
              ticks: {
                stepSize: 1,
                callback: value => value === 3 ? "W" : value === 1 ? "D" : "L"
              },
              beginAtZero: true,
              min: 0,
              max: 3,
              title: {
                display: true,
                text: 'Result'
              }
            }
          }
        }
      });

      function createGradient(ctx, colorStart, colorEnd) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
      }
    });
});
