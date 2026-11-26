function createGalaxy(canvas) {
  const {width, height, tilt, particlesPerFrame, particles} = spiralGalaxyData;
  const ctx = canvas.getContext('2d', {alpha: false});
  if (!ctx) throw new Error('Canvas 2D unavailable');
  canvas.width = width;
  canvas.height = height;
  const cosTilt = Math.cos(tilt);
  const sinTilt = Math.sin(tilt);
  const stars = particles.map(([first, second, radius, rgb, background]) => ({
    first, second, radius, color: `rgb(${rgb.join(',')})`, background
  }));
  const frameLength = 1000 / 60;
  let elapsed = frameLength;
  let lastTime;
  let animation;

  function circle(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  function draw(frame) {
    ctx.fillStyle = '#03030b';
    ctx.fillRect(0, 0, width, height);
    const visible = Math.min(stars.length, frame * particlesPerFrame);
    const spin = frame * 0.008;
    for (let i = 0; i < visible; i++) {
      const {first, second, radius, color, background} = stars[i];
      if (background) {
        circle(first, second, radius, color);
        continue;
      }
      const x = first * Math.cos(second + spin);
      const y = first * Math.sin(second + spin) * 0.55;
      circle(
        Math.trunc(width / 2 + x * cosTilt - y * sinTilt),
        Math.trunc(height / 2 + x * sinTilt + y * cosTilt),
        radius, color
      );
    }
    if (visible >= stars.length - 40) {
      circle(Math.floor(width / 2), Math.floor(height / 2), 13, '#fff3c4');
    }
  }

  function animate(time) {
    if (lastTime !== undefined) elapsed += Math.min(time - lastTime, 100);
    lastTime = time;
    draw(Math.floor(elapsed / frameLength));
    animation = requestAnimationFrame(animate);
  }

  function play() {
    lastTime = undefined;
    animation = requestAnimationFrame(animate);
  }

  function pause() {
    cancelAnimationFrame(animation);
    animation = undefined;
  }

  function reset() {
    pause();
    elapsed = frameLength;
  }

  return {play, pause, reset, get playing() { return animation !== undefined; }};
}
