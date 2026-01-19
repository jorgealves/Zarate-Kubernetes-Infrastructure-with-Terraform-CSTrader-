import "./main.js"

// === Primeiro carrossel (HERO) ===
const slides = document.querySelectorAll(".hero-content");
let current = 0;
const totalSlides = slides.length;

function nextSlide() {
    slides.forEach(slide => slide.classList.remove("active", "exit-left"));

    slides[current].classList.add("exit-left");

    current = (current + 1) % totalSlides;

    slides[current].classList.add("active");
}

setInterval(nextSlide, 6000);

function animarPassos() {
    const passos = document.querySelectorAll('.steps .step');
    if (!passos.length) return;

    let atual = 0;
    setInterval(() => {
        passos[atual].classList.remove('active');
        atual = (atual + 1) % passos.length;
        passos[atual].classList.add('active');
    }, 4000);
}

document.addEventListener('DOMContentLoaded', animarPassos);


// === Segundo carrossel (SKINS) ===
const skinItems = document.querySelectorAll(".carousel-item");
let skinCurrent = 0;

function updateSkinCarousel() {
    const total = skinItems.length;
    skinItems.forEach((item, i) => {
        item.classList.remove("prev2", "prev1", "active", "next1", "next2");
        if (i === skinCurrent) {
            item.classList.add("active");
        } else if (i === (skinCurrent - 1 + total) % total) {
            item.classList.add("prev1");
        } else if (i === (skinCurrent - 2 + total) % total) {
            item.classList.add("prev2");
        } else if (i === (skinCurrent + 1) % total) {
            item.classList.add("next1");
        } else if (i === (skinCurrent + 2) % total) {
            item.classList.add("next2");
        }
    });
}

function nextSkinSlide() {
    skinCurrent = (skinCurrent + 1) % skinItems.length;
    updateSkinCarousel();
}

updateSkinCarousel();
setInterval(nextSkinSlide, 3000);

// === Seção FAQ ===
document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => {
        const item = button.parentElement;
        const isActive = item.classList.contains('active');

        document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));

        if (!isActive) {
            item.classList.add('active');
        }
    });
});
