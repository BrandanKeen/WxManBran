(function() {
  if (typeof document === 'undefined') {
    return;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function setupZoom(container) {
    var target = container.querySelector('[data-zoom-target]');
    var viewport = container.querySelector('[data-zoom-viewport]');
    if (!target || !viewport) {
      return;
    }

    var zoomInButton = container.querySelector('[data-zoom-in]');
    var zoomOutButton = container.querySelector('[data-zoom-out]');
    var resetButton = container.querySelector('[data-zoom-reset]');

    var scale = 1;
    var minScale = 1;
    var maxScale = 3;
    var step = 0.25;

    function applyScale() {
      target.style.transform = 'scale(' + scale + ')';
      if (scale === 1) {
        if (typeof viewport.scrollTo === 'function') {
          viewport.scrollTo({ top: 0, left: 0 });
        } else {
          viewport.scrollTop = 0;
          viewport.scrollLeft = 0;
        }
      }
      if (resetButton) {
        resetButton.disabled = scale === 1;
      }
      if (zoomOutButton) {
        zoomOutButton.disabled = scale <= minScale;
      }
      if (zoomInButton) {
        zoomInButton.disabled = scale >= maxScale;
      }
    }

    function changeScale(delta) {
      scale = clamp(scale + delta, minScale, maxScale);
      applyScale();
    }

    if (zoomInButton) {
      zoomInButton.addEventListener('click', function() {
        changeScale(step);
      });
    }

    if (zoomOutButton) {
      zoomOutButton.addEventListener('click', function() {
        changeScale(-step);
      });
    }

    if (resetButton) {
      resetButton.addEventListener('click', function() {
        scale = 1;
        applyScale();
      });
    }

    container.addEventListener('keydown', function(event) {
      if (event.target !== zoomInButton && event.target !== zoomOutButton && event.target !== resetButton) {
        return;
      }
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        event.target.click();
      }
    });

    applyScale();
  }

  function init() {
    var containers = document.querySelectorAll('[data-zoom-container]');
    containers.forEach(function(container) {
      setupZoom(container);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
