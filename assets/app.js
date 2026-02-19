(function(){
  const links = [...document.querySelectorAll('.links a[href^="#"]')];
  const sections = links
    .map(link => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);
  const sectionsByTop = [...sections].sort((a, b) => a.offsetTop - b.offsetTop);

  function setActiveById(sectionId){
    links.forEach(link => {
      const isActive = link.getAttribute('href') === `#${sectionId}`;
      link.classList.toggle('active', isActive);
    });
  }

  function updateActiveFromScroll(){
    const nav = document.querySelector('.nav');
    const navOffset = (nav ? nav.offsetHeight : 0) + 24;
    const y = window.scrollY + navOffset;
    const probeY = y + (window.innerHeight * 0.3);
    const doc = document.documentElement;
    const atBottom = window.innerHeight + window.scrollY >= doc.scrollHeight - 2;

    let currentSection = sectionsByTop[0];
    let bestTop = -Infinity;
    for (const section of sectionsByTop){
      const top = section.offsetTop;
      if (top <= probeY && top > bestTop){
        bestTop = top;
        currentSection = section;
      }
    }

    if (atBottom){
      const lastVisible = [...sectionsByTop].reverse().find(section => {
        const rect = section.getBoundingClientRect();
        return rect.top < window.innerHeight - navOffset;
      });
      if (lastVisible){
        currentSection = lastVisible;
      }
    }

    if (currentSection && currentSection.id){
      setActiveById(currentSection.id);
    }
  }

  window.addEventListener('scroll', updateActiveFromScroll, { passive: true });
  window.addEventListener('resize', updateActiveFromScroll);
  document.addEventListener('DOMContentLoaded', updateActiveFromScroll);
  updateActiveFromScroll();
})();