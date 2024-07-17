const container = document.getElementById("container");
const overlayCon = document.getElementById("overlayCon");
const overlayBtn = document.getElementById("overlayBtn");

overlayBtn.addEventListener("click", () => {
  container.classList.toggle("right-panel-active");

  overlayBtn.classList.remove("btnScaled");
  window.requestAnimationFrame(() => {
    overlayBtn.classList.add("btnScaled");
  });
});

// carousel
const carouselInner = document.getElementById("carousel-inner");
const prevButton = document.getElementById("prev");
const nextButton = document.getElementById("next");

let currentIndex = 0;

prevButton.addEventListener("click", () => {
  if (currentIndex > 0) {
    currentIndex--;
    updateCarousel();
  }
});

nextButton.addEventListener("click", () => {
  if (currentIndex < carouselInner.children.length - 1) {
    currentIndex++;
    updateCarousel();
  }
});

function updateCarousel() {
  const offset = -currentIndex * carouselInner.children[0].clientWidth;
  carouselInner.style.transform = `translateX(${offset}px)`;
}

window.addEventListener("resize", updateCarousel);
