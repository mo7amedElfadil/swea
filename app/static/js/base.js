// WARNING: if you try declare the variable as (let/const)
// an error will occur, reason is unknown
var burgerMenu = document.getElementById('menu-burger');

// menu toggle
burgerMenu.addEventListener('click', function() {
  burgerMenu.children[0].classList.toggle('opacity-0');
  burgerMenu.children[1].classList.toggle('rotate-45');
  burgerMenu.children[2].classList.toggle('-rotate-45');
  burgerMenu.children[2].classList.toggle('-translate-y-[195%]');
  document.getElementById('menu-container').classList.toggle('-translate-y-full');

  for (const elem of burgerMenu.children) {
    elem.classList.toggle('bg-primary-700');
    elem.classList.toggle('bg-white');
  }

});

// language switcher
document.addEventListener('htmx:afterRequest', function(evt) {
  const path = evt.detail.pathInfo.requestPath;
  if (path.match('set_language') && evt.detail.successful) {
    const locale = path.match('(?<=lang=)[a-z]{2}')[0];
    document.documentElement.lang = locale;
    if (locale === 'ar') {
      document.dir = 'rtl';
    } else {
      document.dir = 'ltr';
    }
  }
})

// initial page load
document.addEventListener('DOMContentLoaded', function() {
  const locale = document.documentElement.lang;
  if (locale === 'ar') {
    document.dir = 'rtl';
  } else {
    document.dir = 'ltr';
  }
})
  document.querySelector('main').style.paddingTop = document.querySelector('header').offsetHeight + 'px';
