document.addEventListener('DOMContentLoaded', function () {
  var shareDetails = document.querySelectorAll('.post-card__share');
  document.addEventListener('click', function (event) {
    shareDetails.forEach(function (details) {
      if (details.hasAttribute('open') && !details.contains(event.target)) {
        details.removeAttribute('open');
      }
    });
  });

  function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(function (value) {
      var hex = value.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }

  function hexToRgb(hex) {
    if (typeof hex !== 'string') {
      return null;
    }
    var normalized = hex.replace('#', '');
    if (normalized.length === 3) {
      normalized = normalized.split('').map(function (char) {
        return char + char;
      }).join('');
    }
    if (normalized.length !== 6) {
      return null;
    }
    var value = parseInt(normalized, 16);
    if (Number.isNaN(value)) {
      return null;
    }
    return {
      r: (value >> 16) & 255,
      g: (value >> 8) & 255,
      b: value & 255
    };
  }

  function mixHex(baseHex, mixHexValue, amount) {
    var base = hexToRgb(baseHex);
    var overlay = hexToRgb(mixHexValue);
    if (!base || !overlay) {
      return baseHex;
    }
    var ratio = Math.min(Math.max(amount, 0), 1);
    var r = Math.round(base.r + (overlay.r - base.r) * ratio);
    var g = Math.round(base.g + (overlay.g - base.g) * ratio);
    var b = Math.round(base.b + (overlay.b - base.b) * ratio);
    return rgbToHex(r, g, b);
  }

  function averageColorFromImage(image) {
    if (!image || !image.naturalWidth || !image.naturalHeight) {
      return null;
    }
    var canvas = document.createElement('canvas');
    var context = canvas.getContext && canvas.getContext('2d');
    if (!context) {
      return null;
    }
    var sampleSize = 24;
    canvas.width = sampleSize;
    canvas.height = Math.max(1, Math.round(sampleSize * (image.naturalHeight / image.naturalWidth)));
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    var imageData;
    try {
      imageData = context.getImageData(0, 0, canvas.width, canvas.height).data;
    } catch (error) {
      return null;
    }
    var rTotal = 0;
    var gTotal = 0;
    var bTotal = 0;
    var count = 0;
    for (var i = 0; i < imageData.length; i += 4) {
      var alpha = imageData[i + 3];
      if (alpha === 0) {
        continue;
      }
      rTotal += imageData[i];
      gTotal += imageData[i + 1];
      bTotal += imageData[i + 2];
      count += 1;
    }
    if (count === 0) {
      return null;
    }
    var rAvg = Math.round(rTotal / count);
    var gAvg = Math.round(gTotal / count);
    var bAvg = Math.round(bTotal / count);
    return rgbToHex(rAvg, gAvg, bAvg);
  }

  function applyShareAccent(detailsElement, baseColor) {
    if (!detailsElement || !baseColor) {
      return;
    }
    var hoverColor = mixHex(baseColor, '#ffffff', 0.18);
    detailsElement.style.setProperty('--share-accent', baseColor);
    detailsElement.style.setProperty('--share-accent-hover', hoverColor);
  }

  var postPairs = document.querySelectorAll('.post-pair');
  postPairs.forEach(function (pair) {
    var videoCard = pair.querySelector('.post-card--video');
    var videoThumb = videoCard ? videoCard.querySelector('img') : null;
    var sharePanel = pair.querySelector('.post-card__share');
    if (!videoThumb || !sharePanel) {
      return;
    }
    if (videoThumb.complete) {
      var baseColor = averageColorFromImage(videoThumb);
      if (baseColor) {
        applyShareAccent(sharePanel, baseColor);
      }
      return;
    }
    videoThumb.addEventListener('load', function handleLoad() {
      var baseColor = averageColorFromImage(videoThumb);
      if (baseColor) {
        applyShareAccent(sharePanel, baseColor);
      }
      videoThumb.removeEventListener('load', handleLoad);
    });
  });
});
