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
        data: { labels, datasets },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
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


  fetch("/api/match-result-pie/")
    .then(response => response.json())
    .then(data => {
      for (let i=0; i < data.length; i++) {
        const teamPiesContainer = document.getElementById("team-doughnuts");
          const canvas = document.createElement("canvas");
          canvas.width = 200;
          canvas.height = 200;
          canvas.id = `doughnut-${data[i].team}`;
    
          const wrapper = document.createElement("div");
          wrapper.className = "team-doughnut";
          wrapper.appendChild(canvas);
          wrapper.innerHTML += `<h4>${data[i].team}</h4>`;
          teamPiesContainer.appendChild(wrapper);
      }

      const resultLabels = ["Wins", "Draws", "Losses"];
      const resultColors = [
        ["#4facfe", "#00f2fe"],  // FCB
        ["#4facfe", "#00f2fe"],  // RMA
        ["#4facfe", "#00f2fe"],  // ATL
        ["#4facfe", "#00f2fe"],  // ATH
      ];

      data.forEach((team, index) => {
        const ctx = document.getElementById(`doughnut-${team.team}`).getContext("2d");
        const gradient = createGradient(ctx, resultColors[index][0], resultColors[index][1]);

        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: resultLabels,
            datasets: [{
              data: [team.wins, team.draws, team.losses],
              backgroundColor: [
                gradient,
                "rgba(255, 205, 86, 0.8)",  // draw
                "rgba(255, 99, 132, 0.8)",  // loss
              ],
              borderWidth: 1
            }]
          },
          options: {
            plugins: {
              legend: { position: "bottom" }
            }
          }
        });
      });

      function createGradient(ctx, colorStart, colorEnd) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
      }
    });
});
