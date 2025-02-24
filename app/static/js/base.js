// WARNING: if you try declare the variable as (let/const)
// an error will occur, reason is unknown
var burgerMenu = document.getElementById('menu-burger');
var isOpen = false;

// menu toggle
burgerMenu.addEventListener('click', function() {
  isOpen = !isOpen;
  burgerMenu.children[0].classList.toggle('opacity-0');
  burgerMenu.children[1].classList.toggle('rotate-45');
  burgerMenu.children[2].classList.toggle('-rotate-45');
  burgerMenu.children[2].classList.toggle('-translate-y-[195%]');
  document.getElementById('menu-container').classList.toggle('-translate-y-full');
  if (isOpen) {
    document.getElementById('menu-container').style.transform = `translateY(${document.querySelector('header').offsetHeight}px)`;
  } else {
    document.getElementById('menu-container').style.transform = `translateY(-100%)`;
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
});

// initial page load
document.querySelector('main').style.paddingTop = document.querySelector('header').offsetHeight + 'px';
document.addEventListener('DOMContentLoaded', function() {
  const locale = document.documentElement.lang;
  if (locale === 'ar') {
    document.dir = 'rtl';
  } else {
    document.dir = 'ltr';
  }
});

// header shadow on scroll
window.addEventListener('scroll', function() {
  document.querySelector('header')
    .classList
    .toggle('header-shadow', document.documentElement.scrollTop > 50);
});

// ws
(function() {
  const socket = new WebSocket("ws://localhost:8080/ws");

  socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    //document.querySelector(data.selector).outerHTML = data.fragment;
    window.location.reload();
    //console.log(data);
  };
})();
