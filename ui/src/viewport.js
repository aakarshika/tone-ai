// Function to set the app height based on window height
function setAppHeight() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Set initial height
setAppHeight();

// Update height on resize and orientation change
window.addEventListener('resize', setAppHeight);
window.addEventListener('orientationchange', setAppHeight); 