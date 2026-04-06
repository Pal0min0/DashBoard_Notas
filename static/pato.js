(function () {
  const css = `
    #duck {
      position: fixed;
      width: 64px; height: 64px;
      image-rendering: pixelated;
      z-index: 9998;
      pointer-events: auto;
      cursor: pointer;
      filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));
    }
    #duck.flip { transform: scaleX(-1); }

    .duck-postit {
      position: fixed;
      z-index: 9997;
      background: #fff9c4;
      color: #333;
      font-family: 'M PLUS Rounded 1c', Arial, sans-serif;
      font-size: 11px;
      font-weight: 700;
      padding: 8px 10px;
      max-width: 160px;
      box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
      border-left: 4px solid #f9a825;
      line-height: 1.5;
      cursor: pointer;
      animation: postitPop 0.3s ease;
    }
    @keyframes postitPop {
      from { transform: scale(0.5) rotate(-8deg); opacity:0; }
      to   { transform: scale(1) rotate(-2deg);   opacity:1; }
    }

    #honkText {
      position: fixed;
      font-family: 'Press Start 2P', monospace;
      font-size: 13px;
      font-weight: 900;
      color: #fff200;
      text-shadow: 1px 1px 0 #e65100, 0 0 8px #f9a825;
      z-index: 9999;
      pointer-events: none;
      opacity: 0;
      transform: translateY(0) scale(0.5);
      transition: opacity 0.1s, transform 0.15s cubic-bezier(0.34,1.56,0.64,1);
      white-space: nowrap;
    }
    #honkText.show {
      opacity: 1;
      transform: translateY(-8px) scale(1);
    }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  const duck = document.createElement('img');
  duck.id  = 'duck';
  duck.src = '/static/pato.gif';
  duck.alt = '🦆';
  document.body.appendChild(duck);

  const honkEl = document.createElement('div');
  honkEl.id          = 'honkText';
  honkEl.textContent = 'HONK!';
  document.body.appendChild(honkEl);

  function playHonk() {
    try {
      const ctx  = new (window.AudioContext || window.webkitAudioContext)();
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(320, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.25, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.35);
    } catch(e) {}
  }

  const MSGS = [
    'Todos somos pasajeros, menos el chofer 🦆',
    'El cafe con leche es como el cafe... pero con leche ☕',
    'La lluvia cae cuando llueve 🌧️',
    'Si la empanada es tu poder, que eres sin la empanada 🫓',
    'No puedes romper algo que ya esta rompido 💀',
    'El amor no sana, lo que sana es la colita de rana 🐸',
    'La gente siempre te va a ver con los ojos 👀',
    'Matanga ... -La Changa 🦆',
    'Aveces las personas mas calladas son las que menos hablan 🤫',
    'Un mudo dijo: 💬',
    'Lo malo de comprar es gastar dinero 💸',
    'Una cosa es una cosa, otra cosa es otra cosa, son cosas muy diferentes 🤔',
    'Comediantes... Son aquellos que comen un dia antes 🍽️',
    'A veces quisiera tirar la toalla, pero luego con que me seco 🏳️',
    'A veces me siento mal, luego acomodo la silla y ya me siento bien 🪑',
    'Cuando estes triste lee esto: Ahorita no pendejo, cuando estes trsite 😢',
    'Podria adivinar tu edad, tan solo sabiendo cuantos años tienes 🎂',
    'La unica forma de vivir es naciendo 👶',
    'Lo que todos hacen en un dia, yo lo puedo hacer en 24H ⏰',
    'El humor negro es como las piernas, algunos tienen y otros no 🦆',
  ];

  const NAV_H = 64;
  let px = 120, py = window.innerHeight / 2;
  let vx = 0.4,  vy = 0.3;
  let mouseX = 0, mouseY = 0;
  let frame     = 0;
  let fleeing   = false;
  let honkTimer = null;

  let lastPostit = Date.now() - 15000;
  let lastHonk   = Date.now() - 18000;

  document.addEventListener('mousemove', e => { mouseX = e.clientX; mouseY = e.clientY; });

  function doHonk() {
    playHonk();
    honkEl.style.left = (px + 32) + 'px';
    honkEl.style.top  = (py - 22) + 'px';
    honkEl.classList.add('show');
    clearTimeout(honkTimer);
    honkTimer = setTimeout(() => honkEl.classList.remove('show'), 900);
  }

  function spawnPostit() {
    const msg = MSGS[Math.random() * MSGS.length | 0];
    const p   = document.createElement('div');
    p.className   = 'duck-postit';
    p.textContent = msg;
    p.style.left  = Math.max(10, Math.min(window.innerWidth - 180, px)) + 'px';
    p.style.top   = Math.max(NAV_H + 10, py - 90) + 'px';
    document.body.appendChild(p);
    p.addEventListener('click', () => p.remove());
    setTimeout(() => {
      p.style.transition = 'opacity 0.5s';
      p.style.opacity    = '0';
      setTimeout(() => p.remove(), 500);
    }, 8000);
  }

  duck.addEventListener('click', doHonk);

  function update() {
    frame++;
    const W = window.innerWidth;
    const H = window.innerHeight;
    const dx = mouseX - px, dy = mouseY - py;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < 120) {
      fleeing = true;
      const angle = Math.atan2(dy, dx);
      vx = -Math.cos(angle) * 1.5;
      vy = -Math.sin(angle) * 1.5;
    } else if (fleeing && dist > 200) {
      fleeing = false;
      const angle = Math.random() * Math.PI * 2;
      const spd   = 0.3 + Math.random() * 0.4;
      vx = Math.cos(angle) * spd;
      vy = Math.sin(angle) * spd;
    }

    px += vx; py += vy;

    if (px < 0)      { px = 0;      vx =  Math.abs(vx); }
    if (px > W - 64) { px = W - 64; vx = -Math.abs(vx); }
    if (py < NAV_H)  { py = NAV_H;  vy =  Math.abs(vy); }
    if (py > H - 64) { py = H - 64; vy = -Math.abs(vy); }

    if (frame % 240 === 0 && !fleeing) {
      const angle = Math.random() * Math.PI * 2;
      const spd   = 0.3 + Math.random() * 0.4;
      vx = Math.cos(angle) * spd;
      vy = Math.sin(angle) * spd;
    }

    if (vx < -0.2)     duck.classList.add('flip');
    else if (vx > 0.2) duck.classList.remove('flip');

    duck.style.left = (px | 0) + 'px';
    duck.style.top  = (py | 0) + 'px';

    if (honkEl.classList.contains('show')) {
      honkEl.style.left = (px + 32) + 'px';
      honkEl.style.top  = (py - 22) + 'px';
    }

    const now = Date.now();
    if (now - lastPostit > 18000) { lastPostit = now; spawnPostit(); }
    if (now - lastHonk   > 22000) { lastHonk   = now; doHonk();     }

    requestAnimationFrame(update);
  }

  duck.style.left = px + 'px';
  duck.style.top  = py + 'px';
  update();
})();