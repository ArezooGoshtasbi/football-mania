document.addEventListener("DOMContentLoaded", () => {
    const timeElements = Array.from(document.querySelectorAll(".match-card .time"));
    const timerDiv = document.getElementById("next-match-timer");
    if (!timerDiv || timeElements.length === 0) return;
  
    function findNextMatchTime() {
      const now = new Date();
  
      for (let elem of timeElements) {
        const matchTime = new Date(elem.dataset.datetime);
        if (matchTime > now) {
          return matchTime;
        }
      }
      return null;
    }
  
    function updateCountdown() {
      const nextMatchTime = findNextMatchTime();
  
      if (!nextMatchTime) {
        timerDiv.textContent = "No upcoming matches 💤";
        clearInterval(timer);
        return;
      }
  
      const now = new Date();
      const diff = nextMatchTime - now;
  
      if (diff <= 0) {
        return;
      }
  
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);
  
      timerDiv.textContent =
        `Next Match starts in: ${days}d ${hours}h ${minutes}m ${seconds}s ⏰`;
      
      const minutesLeft = diff / (1000 * 60);  
      timerDiv.classList.remove("timer-green", "timer-yellow", "timer-red", "pulse");
      if (minutesLeft > 120) {
        timerDiv.classList.add("timer-green");
      } else if (minutesLeft > 30) {
        timerDiv.classList.add("timer-yellow");
      } else {
        timerDiv.classList.add("timer-red", "pulse");
      }
    }
    const timer = setInterval(updateCountdown, 1000);
  });
  