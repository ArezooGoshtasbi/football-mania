document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const rows = document.querySelectorAll(".user-ranking-table tbody tr");
  
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase();
  
      rows.forEach(row => {
        const usernameCell = row.querySelector(".username");
        const username = usernameCell.textContent.toLowerCase();
  
        if (username.includes(query)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  });
  