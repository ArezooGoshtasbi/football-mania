document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/goals-bar-chart/")
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById("goalsChart").getContext("2d");

      const gradients = [
        createGradient(ctx, "#4facfe", "#00f2fe"),  // FCB
        createGradient(ctx, "#4facfe", "#00f2fe"),  // RMA
        createGradient(ctx, "#4facfe", "#00f2fe"),  // ATL
        createGradient(ctx, "#4facfe", "#00f2fe"),  // ATH
      ];

      const borderRadius = 12;

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.map(t => t.team),
          datasets: [
            {
              label: "Goals For",
              data: data.map(t => t.goals_for),
              backgroundColor: gradients,
              borderRadius: borderRadius,
              borderSkipped: false,
            },
            {
              label: "Goals Against",
              data: data.map(t => t.goals_against),
              backgroundColor: "rgba(255, 99, 132, 0.5)",
              borderRadius: borderRadius,
              borderSkipped: false,
            },
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top"
            },
            tooltip: {
              callbacks: {
                label: context => `${context.dataset.label}: ${context.raw}`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: "Goals"
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
    
      data.forEach((team, index) => {
        const ctx = document.getElementById(`doughnut-${team.team}`).getContext("2d");
        const gradientBlue = createGradient(ctx, "#4facfe", "#00f2fe"); // Wins
        const gradientYellow = createGradient(ctx, "#fcd34d", "#facc15"); // Draws 
        const gradientPink = createGradient(ctx, "#fda4af", "#fb7185");  // Losses

        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: resultLabels,
            datasets: [{
              data: [team.wins, team.draws, team.losses],
              backgroundColor: [gradientBlue, gradientYellow, gradientPink],
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
