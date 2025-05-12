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

    let sortAsc = false;

    document.getElementById("sort-score").addEventListener("click", () => {
      const tbody = document.querySelector(".user-ranking-table tbody");
      const rows = Array.from(tbody.querySelectorAll("tr"));
      
      rows.sort((a, b) => {
        const scoreA = parseInt(a.children[2].textContent);
        const scoreB = parseInt(b.children[2].textContent);
    
        return sortAsc ? scoreA - scoreB : scoreB - scoreA;
      });
    
      tbody.innerHTML = "";
      rows.forEach(row => tbody.appendChild(row));
    
      sortAsc = !sortAsc; 
    });
       
  });
  