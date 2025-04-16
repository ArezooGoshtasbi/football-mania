document.addEventListener("DOMContentLoaded", () => {
    const matchTime = "2025-04-18T21:00:00"; 
  
    function updateCountdown() {
      const now = new Date();
      const matchDate = new Date(matchTime);
      const diff = matchDate - now;
  
      if (diff <= 0) {
        document.getElementById("next-match-timer").textContent = "Match is starting!";
        clearInterval(timer);
        return;
      }
  
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);
  
      document.getElementById("next-match-timer").textContent =
        `Next Match starts in: ${days}d ${hours}h ${minutes}m ${seconds}s ⏰`;
    }
  
    const timer = setInterval(updateCountdown, 1000);
  });
  