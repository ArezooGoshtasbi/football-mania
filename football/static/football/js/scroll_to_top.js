document.addEventListener("DOMContentLoaded", () => {
    const scrollBtn = document.getElementById("scrollToTopBtn");
  
    window.onscroll = function () {
      if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
        scrollBtn.style.display = "block";
      } else {
        scrollBtn.style.display = "none";
      }
    };
  
    scrollBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
  