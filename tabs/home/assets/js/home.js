document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('theme-classic');
  document.body.dataset.color = 'values';

  const statusHeader = document.querySelector('#wx-dashboard > header.site-header');
  if (statusHeader) {
    statusHeader.classList.remove('is-fixed');
  }
});
