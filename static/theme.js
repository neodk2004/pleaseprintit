// Hell/Dunkel: folgt dem Gerät, bis man umschaltet; Wahl bleibt im Browser gespeichert.
const root = document.documentElement;
if (localStorage.ppTheme) root.dataset.theme = localStorage.ppTheme;
addEventListener('DOMContentLoaded', () => {
  for (const b of document.querySelectorAll('[data-theme-toggle]')) {
    b.addEventListener('click', () => {
      const dark = (root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')) === 'dark';
      root.dataset.theme = localStorage.ppTheme = dark ? 'light' : 'dark';
    });
  }
});
