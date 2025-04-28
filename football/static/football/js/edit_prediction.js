document.addEventListener('DOMContentLoaded', function() {
  const editButtons = document.querySelectorAll('.edit-btn');
  const editForm = document.getElementById('editPredictionForm');

  function openEditModal(button) {
    const predictionId = button.getAttribute('data-id');
    const homeScore = button.getAttribute('data-home');
    const awayScore = button.getAttribute('data-away');
    const result = button.getAttribute('data-result');

    document.getElementById('predictionId').value = predictionId;
    document.getElementById('homeScore').value = homeScore;
    document.getElementById('awayScore').value = awayScore;
    document.getElementById('result').value = result;

    $('#editPredictionModal').modal('show');
  }

  editButtons.forEach(button => {
    button.addEventListener('click', () => openEditModal(button));
  });

  editForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const predictionId = document.getElementById('predictionId').value;
    const homeScore = document.getElementById('homeScore').value;
    const awayScore = document.getElementById('awayScore').value;
    const result = document.getElementById('result').value;

    fetch(`/prediction/${predictionId}/edit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: `home_score=${homeScore}&away_score=${awayScore}&result=${result}`
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        $('#editPredictionModal').modal('hide');

        const predictionCell = document.querySelector(`.prediction-cell-${predictionId}`);
        if (predictionCell) {
          predictionCell.innerHTML = `
            ${homeScore} - ${awayScore}
            <button class="btn btn-sm btn-link edit-btn" data-id="${predictionId}" data-home="${homeScore}" data-away="${awayScore}" data-result="${result}">
              ✏️
            </button>
          `;

          const newEditButton = predictionCell.querySelector('.edit-btn');
          newEditButton.addEventListener('click', () => openEditModal(newEditButton));
        }
      } else {
        alert(data.error || 'Error updating prediction.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Something went wrong.');
    });
  });

});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
