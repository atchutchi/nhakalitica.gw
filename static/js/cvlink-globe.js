(() => {
  const canvas = document.querySelector("[data-cvlink-globe]");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  const places = [
    { key: "cv", label: "Cabo Verde", short: "CV", lon: -23.6052, lat: 15.1111, origin: true },
    { key: "gw", label: "Guiné-Bissau", short: "GB", lon: -15.1804, lat: 11.8037 },
    { key: "stp", label: "São Tomé", short: "STP", lon: 6.6131, lat: 0.1864 },
    { key: "ao", label: "Angola", short: "AO", lon: 17.8739, lat: -11.2027 },
    { key: "mz", label: "Moçambique", short: "MZ", lon: 35.5296, lat: -18.6657 },
  ];

  const africa = [
    [-17.6, 34.8], [-6.4, 35.9], [10.3, 37.2], [25.2, 31.6], [34.8, 31.2],
    [36.8, 15.5], [43.2, 11.7], [51.5, 11.8], [49.1, -3.8], [43.3, -12.3],
    [40.1, -25.4], [31.4, -34.8], [18.4, -34.6], [12.3, -28.5], [9.2, -18.4],
    [2.6, -6.6], [-7.8, 4.8], [-16.4, 13.5], [-17.6, 34.8],
  ];

  const madagascar = [
    [47.1, -12.0], [50.4, -15.6], [49.2, -22.2], [45.2, -25.6],
    [43.4, -20.1], [44.8, -14.4], [47.1, -12.0],
  ];

  const europeHint = [
    [-10.0, 35.8], [4.8, 43.2], [18.2, 41.7], [30.0, 39.6],
    [31.0, 36.1], [10.0, 36.0], [-10.0, 35.8],
  ];

  const routes = places.filter((place) => !place.origin).map((target) => ({
    from: places[0],
    to: target,
  }));
  const landRings = Array.isArray(window.CVLINK_GLOBE_LAND) && window.CVLINK_GLOBE_LAND.length
    ? window.CVLINK_GLOBE_LAND
    : [europeHint, africa, madagascar];

  let width = 0;
  let height = 0;
  let radius = 0;
  let centerX = 0;
  let centerY = 0;
  let lonCenter = 8;
  let latCenter = 1;
  let targetLon = 8;
  let targetLat = 1;
  let animationFrame = null;
  let startTime = performance.now();

  function resize() {
    const rect = canvas.getBoundingClientRect();
    width = Math.max(320, rect.width);
    height = Math.max(260, rect.height);
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    radius = Math.min(width * 0.42, height * 0.45);
    centerX = width * 0.5;
    centerY = height * 0.48;
  }

  function toRad(value) {
    return (value * Math.PI) / 180;
  }

  function project(lon, lat) {
    const lambda = toRad(lon - lonCenter);
    const phi = toRad(lat);
    const phi0 = toRad(latCenter);
    const cosPhi = Math.cos(phi);
    const z = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * cosPhi * Math.cos(lambda);

    return {
      x: centerX + radius * cosPhi * Math.sin(lambda),
      y: centerY - radius * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * cosPhi * Math.cos(lambda)),
      z,
      visible: z > -0.08,
    };
  }

  function drawSphere() {
    const ocean = ctx.createRadialGradient(centerX - radius * 0.32, centerY - radius * 0.36, radius * 0.08, centerX, centerY, radius);
    ocean.addColorStop(0, "#1f75bd");
    ocean.addColorStop(0.45, "#0b4b91");
    ocean.addColorStop(1, "#061c3f");

    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fillStyle = ocean;
    ctx.fill();
    ctx.clip();

    const shade = ctx.createLinearGradient(centerX - radius, centerY - radius, centerX + radius, centerY + radius);
    shade.addColorStop(0, "rgba(255,255,255,0.18)");
    shade.addColorStop(0.56, "rgba(255,255,255,0)");
    shade.addColorStop(1, "rgba(0,0,0,0.32)");
    ctx.fillStyle = shade;
    ctx.fillRect(centerX - radius, centerY - radius, radius * 2, radius * 2);
    ctx.restore();

    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255,255,255,0.38)";
    ctx.lineWidth = 1.4;
    ctx.stroke();
    ctx.restore();
  }

  function drawGraticule() {
    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.clip();
    ctx.strokeStyle = "rgba(255,255,255,0.12)";
    ctx.lineWidth = 1;

    for (let lat = -60; lat <= 60; lat += 20) {
      drawLine(Array.from({ length: 145 }, (_, index) => [-70 + index * 0.7, lat]));
    }

    for (let lon = -40; lon <= 60; lon += 20) {
      drawLine(Array.from({ length: 121 }, (_, index) => [lon, -45 + index * 0.75]));
    }

    ctx.restore();
  }

  function drawLine(points) {
    let started = false;
    ctx.beginPath();
    points.forEach(([lon, lat]) => {
      const point = project(lon, lat);
      if (!point.visible) {
        started = false;
        return;
      }
      if (!started) {
        ctx.moveTo(point.x, point.y);
        started = true;
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.stroke();
  }

  function drawLand(points, fill, stroke) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.clip();
    ctx.beginPath();
    let started = false;
    points.forEach(([lon, lat]) => {
      const point = project(lon, lat);
      if (!point.visible) {
        started = false;
        return;
      }
      if (!started) {
        ctx.moveTo(point.x, point.y);
        started = true;
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1.2;
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  function routePoints(from, to) {
    return Array.from({ length: 44 }, (_, index) => {
      const t = index / 43;
      const arc = Math.sin(Math.PI * t) * 8;
      return [
        from.lon + (to.lon - from.lon) * t,
        from.lat + (to.lat - from.lat) * t + arc,
      ];
    });
  }

  function drawRoutes(time) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.clip();

    routes.forEach((route, routeIndex) => {
      const points = routePoints(route.from, route.to).map(([lon, lat]) => project(lon, lat));
      ctx.beginPath();
      let visibleCount = 0;
      points.forEach((point, index) => {
        if (!point.visible) return;
        visibleCount += 1;
        if (index === 0) ctx.moveTo(point.x, point.y);
        else ctx.lineTo(point.x, point.y);
      });
      if (visibleCount < 2) return;

      ctx.strokeStyle = "rgba(255, 137, 8, 0.88)";
      ctx.lineWidth = 2.2;
      ctx.shadowColor = "rgba(255, 137, 8, 0.5)";
      ctx.shadowBlur = 12;
      ctx.stroke();
      ctx.shadowBlur = 0;

      const pulseIndex = Math.floor(((time / 42) + routeIndex * 8) % points.length);
      const pulse = points[pulseIndex];
      if (pulse && pulse.visible) {
        ctx.beginPath();
        ctx.arc(pulse.x, pulse.y, 4.5, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
      }
    });
    ctx.restore();
  }

  function drawPlace(place) {
    const point = project(place.lon, place.lat);
    if (!point.visible) return;

    const size = place.origin ? 12 : 8;
    ctx.beginPath();
    ctx.arc(point.x, point.y, size, 0, Math.PI * 2);
    ctx.fillStyle = place.origin ? "#ef7000" : "#ffffff";
    ctx.strokeStyle = place.origin ? "rgba(255,255,255,0.9)" : "rgba(255,137,8,0.95)";
    ctx.lineWidth = place.origin ? 3 : 2;
    ctx.fill();
    ctx.stroke();

    ctx.font = place.origin ? "800 13px Aptos, Segoe UI, sans-serif" : "800 11px Aptos, Segoe UI, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = place.origin ? "#ffffff" : "#061c3f";
    ctx.fillText(place.short, point.x, point.y);

    ctx.font = "700 12px Aptos, Segoe UI, sans-serif";
    ctx.textAlign = place.origin ? "right" : "left";
    ctx.fillStyle = "rgba(255,255,255,0.92)";
    const labelX = point.x + (place.origin ? -16 : 14);
    ctx.fillText(place.label, labelX, point.y - 18);
  }

  function render(time) {
    if (!reduceMotion) {
      targetLon += 0.012;
    }
    lonCenter += (targetLon - lonCenter) * 0.055;
    latCenter += (targetLat - latCenter) * 0.055;

    ctx.clearRect(0, 0, width, height);
    drawSphere();
    drawGraticule();
    landRings.forEach((ring) => {
      drawLand(ring, "rgba(181, 213, 147, 0.84)", "rgba(255,255,255,0.26)");
    });
    drawRoutes(time - startTime);
    places.forEach(drawPlace);

    if (!reduceMotion) {
      animationFrame = requestAnimationFrame(render);
    }
  }

  canvas.addEventListener("pointermove", (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    targetLon = 8 + x * 22;
    targetLat = 1 - y * 14;
    if (reduceMotion) render(performance.now());
  });

  canvas.addEventListener("pointerleave", () => {
    targetLon = 8;
    targetLat = 1;
    if (reduceMotion) render(performance.now());
  });

  resize();
  window.addEventListener("resize", () => {
    resize();
    if (reduceMotion) render(performance.now());
  });

  render(performance.now());

  window.addEventListener("pagehide", () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
  });
})();
