(function() {
  if (typeof document === 'undefined') {
    return;
  }

  function setupZoomToggle(container) {
    var target = container.querySelector('[data-zoom-target]');
    var figure = container.querySelector('.storm-multi-panels__figure');
    if (!target) {
      return;
    }

    container.setAttribute('role', 'button');
    container.setAttribute('aria-pressed', 'false');
    container.setAttribute('aria-label', 'Toggle zoom on storm plot');
    if (!container.hasAttribute('tabindex')) {
      container.setAttribute('tabindex', '0');
    }

    function setZoomState(isZoomed) {
      if (isZoomed) {
        container.classList.add('is-zoomed');
        container.setAttribute('aria-pressed', 'true');
      } else {
        container.classList.remove('is-zoomed');
        container.setAttribute('aria-pressed', 'false');
        if (figure) {
          figure.scrollTop = 0;
          figure.scrollLeft = 0;
        }
      }
    }

    function toggleZoom() {
      var nextState = !container.classList.contains('is-zoomed');
      setZoomState(nextState);
    }

    container.addEventListener('click', function(event) {
      if (event.button !== undefined && event.button !== 0) {
        return;
      }
      toggleZoom();
    });

    container.addEventListener('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleZoom();
      }
    });

    setZoomState(container.classList.contains('is-zoomed'));
  }

  function init() {
    var containers = document.querySelectorAll('[data-zoom-toggle]');
    containers.forEach(function(container) {
      setupZoomToggle(container);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
