/* ===========================================
   WeatherVerse — 3D Weather Experience
   style.js — Main Application Logic
   =========================================== */

'use strict';

// ─── State ───────────────────────────────────
const state = {
    city: 'London',
    units: 'C',      // 'C' or 'F'
    data: null,
    timeTickerInterval: null,
    canvasAnimId: null,
    particles: [],
    weatherCode: 113,
};

// ─── Weather Code → Metadata ──────────────────
const WEATHER_META = {
    113: { label: 'Sunny',               theme: 'clear-day',   icon: 'sunny',    particles: 'stars'  },
    116: { label: 'Partly Cloudy',       theme: 'clear-day',   icon: 'partly-cloudy', particles: 'stars' },
    119: { label: 'Cloudy',              theme: 'cloudy',      icon: 'cloudy',   particles: 'clouds' },
    122: { label: 'Overcast',            theme: 'cloudy',      icon: 'overcast', particles: 'clouds' },
    143: { label: 'Mist',                theme: 'fog',         icon: 'fog',      particles: 'fog'    },
    176: { label: 'Patchy Rain',         theme: 'rain',        icon: 'drizzle',  particles: 'rain'   },
    179: { label: 'Patchy Snow',         theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    182: { label: 'Sleet',               theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    200: { label: 'Thundery Outbreaks',  theme: 'storm',       icon: 'thunder',  particles: 'storm'  },
    227: { label: 'Blowing Snow',        theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    230: { label: 'Blizzard',            theme: 'snow',        icon: 'blizzard', particles: 'snow'   },
    248: { label: 'Fog',                 theme: 'fog',         icon: 'fog',      particles: 'fog'    },
    260: { label: 'Freezing Fog',        theme: 'fog',         icon: 'fog',      particles: 'fog'    },
    263: { label: 'Light Drizzle',       theme: 'rain',        icon: 'drizzle',  particles: 'rain'   },
    266: { label: 'Drizzle',             theme: 'rain',        icon: 'drizzle',  particles: 'rain'   },
    281: { label: 'Freezing Drizzle',    theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    293: { label: 'Patchy Light Rain',   theme: 'rain',        icon: 'rain',     particles: 'rain'   },
    296: { label: 'Light Rain',          theme: 'rain',        icon: 'rain',     particles: 'rain'   },
    299: { label: 'Moderate Rain',       theme: 'rain',        icon: 'rain',     particles: 'rain'   },
    302: { label: 'Moderate Rain',       theme: 'rain',        icon: 'rain',     particles: 'rain'   },
    305: { label: 'Heavy Rain',          theme: 'rain',        icon: 'heavy-rain', particles: 'rain' },
    308: { label: 'Heavy Rain',          theme: 'rain',        icon: 'heavy-rain', particles: 'rain' },
    311: { label: 'Freezing Rain',       theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    317: { label: 'Light Sleet',         theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    320: { label: 'Moderate Sleet',      theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    323: { label: 'Light Snow',          theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    326: { label: 'Light Snow',          theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    329: { label: 'Moderate Snow',       theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    332: { label: 'Moderate Snow',       theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    335: { label: 'Heavy Snow',          theme: 'snow',        icon: 'snowstorm', particles: 'snow'  },
    338: { label: 'Heavy Snow',          theme: 'snow',        icon: 'snowstorm', particles: 'snow'  },
    350: { label: 'Ice Pellets',         theme: 'snow',        icon: 'sleet',    particles: 'snow'   },
    353: { label: 'Light Showers',       theme: 'rain',        icon: 'rain',     particles: 'rain'   },
    356: { label: 'Heavy Showers',       theme: 'rain',        icon: 'heavy-rain', particles: 'rain' },
    359: { label: 'Torrential Rain',     theme: 'rain',        icon: 'heavy-rain', particles: 'rain' },
    362: { label: 'Sleet Showers',       theme: 'rain',        icon: 'sleet',    particles: 'rain'   },
    368: { label: 'Snow Showers',        theme: 'snow',        icon: 'snow',     particles: 'snow'   },
    371: { label: 'Heavy Snow Showers',  theme: 'snow',        icon: 'snowstorm', particles: 'snow'  },
    386: { label: 'Thundery Rain',       theme: 'storm',       icon: 'thunder',  particles: 'storm'  },
    389: { label: 'Heavy Thunderstorm',  theme: 'storm',       icon: 'thunder',  particles: 'storm'  },
    392: { label: 'Snow with Thunder',   theme: 'storm',       icon: 'thunder',  particles: 'storm'  },
    395: { label: 'Blizzard & Thunder',  theme: 'storm',       icon: 'thunder',  particles: 'storm'  },
};

function getMeta(code) {
    return WEATHER_META[code] || { label: 'Unknown', theme: 'clear-day', icon: 'cloudy', particles: 'stars' };
}

// ─── SVG Weather Icons ─────────────────────────
function buildIcon(type, size = 110) {
    const icons = {
        'sunny': `
<svg viewBox="0 0 110 110" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="sg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fde68a"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </radialGradient>
  </defs>
  <g transform="translate(55,55)">
    ${[0,45,90,135,180,225,270,315].map((a,i) => `
      <line x1="0" y1="-24" x2="0" y2="-32" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round"
            transform="rotate(${a})" opacity="${0.6 + i*0.05}">
        <animateTransform attributeName="transform" type="rotate" from="${a}" to="${a+360}" dur="12s" repeatCount="indefinite"/>
      </line>`).join('')}
    <circle r="18" fill="url(#sg)">
      <animate attributeName="r" values="18;20;18" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle r="18" fill="none" stroke="#fde68a" stroke-width="1" opacity="0.5">
      <animate attributeName="r" values="18;26;18" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0;0.5" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>`,

        'partly-cloudy': `
<svg viewBox="0 0 110 90" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="pcsg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fde68a"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </radialGradient>
    <linearGradient id="pcclg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e0f2fe"/>
      <stop offset="100%" stop-color="#bfdbfe"/>
    </linearGradient>
  </defs>
  <circle cx="40" cy="35" r="18" fill="url(#pcsg)" opacity="0.9">
    <animate attributeName="r" values="18;20;18" dur="4s" repeatCount="indefinite"/>
  </circle>
  <g>
    <ellipse cx="55" cy="65" rx="30" ry="14" fill="url(#pcclg)" opacity="0.9"/>
    <ellipse cx="45" cy="60" rx="18" ry="15" fill="url(#pcclg)"/>
    <ellipse cx="68" cy="60" rx="14" ry="12" fill="url(#pcclg)"/>
    <animate attributeName="transform" type="translate" values="0,0;3,0;0,0" dur="5s" repeatCount="indefinite" attributeType="XML"/>
  </g>
</svg>`,

        'cloudy': `
<svg viewBox="0 0 110 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="clg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#94a3b8"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="52" rx="36" ry="16" fill="url(#clg)" opacity="0.8">
    <animate attributeName="rx" values="36;39;36" dur="6s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="44" cy="44" rx="22" ry="18" fill="url(#clg)"/>
  <ellipse cx="68" cy="46" rx="18" ry="14" fill="url(#clg)"/>
</svg>`,

        'overcast': `
<svg viewBox="0 0 110 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="olg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6b7280"/>
      <stop offset="100%" stop-color="#4b5563"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="55" rx="40" ry="17" fill="url(#olg)" opacity="0.7"/>
  <ellipse cx="42" cy="46" rx="24" ry="20" fill="url(#olg)" opacity="0.9"/>
  <ellipse cx="70" cy="48" rx="20" ry="16" fill="url(#olg)"/>
  <ellipse cx="55" cy="38" rx="16" ry="14" fill="url(#olg)" opacity="0.8"/>
</svg>`,

        'rain': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="rlg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7dd3fc"/>
      <stop offset="100%" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="48" rx="36" ry="16" fill="url(#rlg)" opacity="0.85"/>
  <ellipse cx="44" cy="40" rx="22" ry="18" fill="url(#rlg)"/>
  <ellipse cx="68" cy="42" rx="18" ry="14" fill="url(#rlg)"/>
  ${[[38,72,'0.2s'],[50,78,'0.5s'],[62,74,'0.1s'],[44,84,'0.7s'],[56,88,'0.3s']].map(([x,y,d]) => `
    <line x1="${x}" y1="${y}" x2="${x-4}" y2="${y+10}" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" opacity="0.8">
      <animate attributeName="opacity" values="0;1;0" dur="1.2s" begin="${d}" repeatCount="indefinite"/>
      <animate attributeName="y1" values="${y};${y+5};${y}" dur="1.2s" begin="${d}" repeatCount="indefinite"/>
    </line>`).join('')}
</svg>`,

        'heavy-rain': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hrlg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#475569"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="45" rx="38" ry="16" fill="url(#hrlg)"/>
  <ellipse cx="42" cy="37" rx="24" ry="20" fill="url(#hrlg)"/>
  <ellipse cx="70" cy="40" rx="20" ry="16" fill="url(#hrlg)"/>
  ${[[35,68,'0s'],[44,72,'0.15s'],[53,66,'0.3s'],[62,72,'0.1s'],[71,68,'0.4s'],[40,80,'0.5s'],[56,82,'0.2s'],[66,80,'0.6s']].map(([x,y,d]) => `
    <line x1="${x}" y1="${y}" x2="${x-5}" y2="${y+12}" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round">
      <animate attributeName="opacity" values="0;1;0" dur="0.9s" begin="${d}" repeatCount="indefinite"/>
    </line>`).join('')}
</svg>`,

        'drizzle': `
<svg viewBox="0 0 110 95" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="dlg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cbd5e1"/>
      <stop offset="100%" stop-color="#94a3b8"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="45" rx="36" ry="15" fill="url(#dlg)" opacity="0.9"/>
  <ellipse cx="44" cy="38" rx="21" ry="17" fill="url(#dlg)"/>
  <ellipse cx="68" cy="40" rx="17" ry="13" fill="url(#dlg)"/>
  ${[[40,65,'0.1s'],[53,70,'0.4s'],[65,66,'0.7s']].map(([x,y,d]) => `
    <circle cx="${x}" cy="${y}" r="2" fill="#7dd3fc" opacity="0.7">
      <animate attributeName="cy" values="${y};${y+8};${y}" dur="2s" begin="${d}" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;0;0.7" dur="2s" begin="${d}" repeatCount="indefinite"/>
    </circle>`).join('')}
</svg>`,

        'thunder': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tlg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#312e81"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="42" rx="38" ry="16" fill="url(#tlg)"/>
  <ellipse cx="42" cy="34" rx="24" ry="20" fill="url(#tlg)"/>
  <ellipse cx="70" cy="37" rx="20" ry="16" fill="url(#tlg)"/>
  ${[[36,65,'0.1s'],[60,68,'0.5s']].map(([x,y,d]) => `
    <line x1="${x}" y1="${y}" x2="${x-4}" y2="${y+10}" stroke="#60a5fa" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0;1;0" dur="1s" begin="${d}" repeatCount="indefinite"/>
    </line>`).join('')}
  <polygon points="58,58 50,78 56,78 52,95 68,72 61,72 66,58" fill="#fbbf24">
    <animate attributeName="opacity" values="1;0.3;1" dur="0.8s" repeatCount="indefinite"/>
    <animate attributeName="fill" values="#fbbf24;#ffffff;#fbbf24" dur="0.8s" repeatCount="indefinite"/>
  </polygon>
</svg>`,

        'snow': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="snlg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e0f2fe"/>
      <stop offset="100%" stop-color="#bfdbfe"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="46" rx="36" ry="15" fill="url(#snlg)" opacity="0.85"/>
  <ellipse cx="44" cy="38" rx="21" ry="18" fill="url(#snlg)"/>
  <ellipse cx="68" cy="41" rx="18" ry="14" fill="url(#snlg)"/>
  ${[[38,70,'0.1s'],[52,75,'0.4s'],[66,70,'0.7s'],[44,82,'0.6s'],[60,84,'0.2s']].map(([x,y,d]) => `
    <g transform="translate(${x},${y})">
      <line x1="-5" y1="0" x2="5" y2="0" stroke="white" stroke-width="1.5" opacity="0.8">
        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" begin="${d}" repeatCount="indefinite"/>
      </line>
      <line x1="0" y1="-5" x2="0" y2="5" stroke="white" stroke-width="1.5" opacity="0.8">
        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" begin="${d}" repeatCount="indefinite"/>
      </line>
      <line x1="-4" y1="-4" x2="4" y2="4" stroke="white" stroke-width="1.5" opacity="0.6"/>
      <line x1="4" y1="-4" x2="-4" y2="4" stroke="white" stroke-width="1.5" opacity="0.6"/>
    </g>`).join('')}
</svg>`,

        'snowstorm': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sslg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#94a3b8"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="44" rx="38" ry="16" fill="url(#sslg)"/>
  <ellipse cx="42" cy="36" rx="24" ry="20" fill="url(#sslg)"/>
  <ellipse cx="70" cy="39" rx="20" ry="16" fill="url(#sslg)"/>
  ${[[35,68,'0s'],[48,73,'0.3s'],[60,68,'0.6s'],[72,72,'0.1s'],[42,82,'0.8s'],[64,80,'0.4s']].map(([x,y,d]) => `
    <g transform="translate(${x},${y})">
      <line x1="-5" y1="0" x2="5" y2="0" stroke="#e0f2fe" stroke-width="1.5">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="${d}" repeatCount="indefinite"/>
      </line>
      <line x1="0" y1="-5" x2="0" y2="5" stroke="#e0f2fe" stroke-width="1.5">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="${d}" repeatCount="indefinite"/>
      </line>
    </g>`).join('')}
</svg>`,

        'sleet': `
<svg viewBox="0 0 110 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sllg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7dd3fc"/>
      <stop offset="100%" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
  <ellipse cx="55" cy="46" rx="36" ry="15" fill="url(#sllg)" opacity="0.8"/>
  <ellipse cx="44" cy="38" rx="21" ry="17" fill="url(#sllg)"/>
  <ellipse cx="68" cy="41" rx="18" ry="13" fill="url(#sllg)"/>
  <line x1="38" y1="65" x2="34" y2="75" stroke="#7dd3fc" stroke-width="2" stroke-linecap="round">
    <animate attributeName="opacity" values="0;1;0" dur="1.2s" begin="0.2s" repeatCount="indefinite"/>
  </line>
  <circle cx="53" cy="72" r="2.5" fill="white" opacity="0.8">
    <animate attributeName="opacity" values="0.8;0.1;0.8" dur="1.5s" begin="0.5s" repeatCount="indefinite"/>
  </circle>
  <line x1="62" y1="67" x2="58" y2="77" stroke="#7dd3fc" stroke-width="2" stroke-linecap="round">
    <animate attributeName="opacity" values="0;1;0" dur="1.2s" begin="0.7s" repeatCount="indefinite"/>
  </line>
</svg>`,

        'fog': `
<svg viewBox="0 0 110 80" xmlns="http://www.w3.org/2000/svg">
  ${[22, 36, 50, 64].map((y, i) => `
    <rect x="${10 + i*3}" y="${y}" width="${90 - i*6}" height="6" rx="3" fill="rgba(148,163,184,${0.5 - i*0.08})">
      <animate attributeName="x" values="${10+i*3};${16+i*3};${10+i*3}" dur="${4+i}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="${0.5-i*0.08};${0.8-i*0.1};${0.5-i*0.08}" dur="${3+i}s" repeatCount="indefinite"/>
    </rect>`).join('')}
</svg>`,
    };
    return icons[type] || icons['cloudy'];
}

function buildSmallIcon(type) {
    // Simplified compact icon for hourly/forecast
    const map = {
        'sunny':        '<circle cx="16" cy="16" r="6" fill="#fbbf24"/><g stroke="#fbbf24" stroke-width="1.5" stroke-linecap="round">' + [0,45,90,135,180,225,270,315].map(a=>`<line x1="${16+9*Math.sin(a*Math.PI/180)}" y1="${16-9*Math.cos(a*Math.PI/180)}" x2="${16+11*Math.sin(a*Math.PI/180)}" y2="${16-11*Math.cos(a*Math.PI/180)}"/>`).join('') + '</g>',
        'partly-cloudy':'<circle cx="14" cy="14" r="7" fill="#fbbf24" opacity="0.9"/><ellipse cx="20" cy="20" rx="10" ry="6" fill="#bfdbfe"/><ellipse cx="16" cy="18" rx="7" ry="6" fill="#e0f2fe"/>',
        'cloudy':       '<ellipse cx="18" cy="18" rx="10" ry="6" fill="#94a3b8"/><ellipse cx="13" cy="15" rx="7" ry="6" fill="#94a3b8"/>',
        'overcast':     '<ellipse cx="18" cy="18" rx="11" ry="6" fill="#6b7280"/><ellipse cx="13" cy="14" rx="7" ry="6" fill="#6b7280"/><ellipse cx="18" cy="12" rx="5" ry="5" fill="#6b7280"/>',
        'rain':         '<ellipse cx="18" cy="14" rx="10" ry="5.5" fill="#3b82f6"/><ellipse cx="13" cy="11" rx="7" ry="6" fill="#3b82f6"/><line x1="12" y1="20" x2="10" y2="27" stroke="#60a5fa" stroke-width="1.5" stroke-linecap="round"/><line x1="18" y1="22" x2="16" y2="29" stroke="#60a5fa" stroke-width="1.5" stroke-linecap="round"/><line x1="24" y1="20" x2="22" y2="27" stroke="#60a5fa" stroke-width="1.5" stroke-linecap="round"/>',
        'heavy-rain':   '<ellipse cx="18" cy="13" rx="11" ry="5.5" fill="#1e3a5f"/><ellipse cx="13" cy="10" rx="7" ry="6" fill="#1e3a5f"/><line x1="10" y1="20" x2="8" y2="28" stroke="#60a5fa" stroke-width="2" stroke-linecap="round"/><line x1="16" y1="21" x2="14" y2="29" stroke="#60a5fa" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="20" x2="20" y2="28" stroke="#60a5fa" stroke-width="2" stroke-linecap="round"/>',
        'drizzle':      '<ellipse cx="18" cy="14" rx="10" ry="5.5" fill="#94a3b8"/><ellipse cx="13" cy="11" rx="7" ry="6" fill="#94a3b8"/><circle cx="12" cy="23" r="1.5" fill="#7dd3fc"/><circle cx="18" cy="25" r="1.5" fill="#7dd3fc"/><circle cx="24" cy="23" r="1.5" fill="#7dd3fc"/>',
        'thunder':      '<ellipse cx="18" cy="12" rx="11" ry="5.5" fill="#312e81"/><ellipse cx="13" cy="9" rx="7" ry="6" fill="#312e81"/><polygon points="19,20 15,28 18,28 16,34 23,24 20,24 22,20" fill="#fbbf24"/>',
        'snow':         '<ellipse cx="18" cy="14" rx="10" ry="5.5" fill="#bfdbfe"/><ellipse cx="13" cy="11" rx="7" ry="6" fill="#e0f2fe"/><line x1="12" y1="24" x2="12" y2="24" stroke="white" stroke-width="0"/><text x="10" y="28" font-size="8" fill="white">❆ ❆</text>',
        'snowstorm':    '<ellipse cx="18" cy="13" rx="11" ry="5.5" fill="#64748b"/><ellipse cx="13" cy="10" rx="7" ry="6" fill="#64748b"/><text x="9" y="28" font-size="8" fill="#e0f2fe">❆ ❆ ❆</text>',
        'sleet':        '<ellipse cx="18" cy="14" rx="10" ry="5.5" fill="#7dd3fc"/><ellipse cx="13" cy="11" rx="7" ry="6" fill="#7dd3fc"/><line x1="12" y1="21" x2="10" y2="28" stroke="#7dd3fc" stroke-width="1.5" stroke-linecap="round"/><circle cx="18" cy="25" r="2" fill="white"/><line x1="24" y1="21" x2="22" y2="28" stroke="#7dd3fc" stroke-width="1.5" stroke-linecap="round"/>',
        'blizzard':     '<ellipse cx="18" cy="12" rx="11" ry="5.5" fill="#475569"/><ellipse cx="13" cy="9" rx="7" ry="6" fill="#475569"/><text x="8" y="28" font-size="9" fill="#e0f2fe">❄ ❄</text>',
        'fog':          '<rect x="6" y="10" width="20" height="3" rx="1.5" fill="rgba(148,163,184,0.6)"/><rect x="4" y="16" width="24" height="3" rx="1.5" fill="rgba(148,163,184,0.5)"/><rect x="8" y="22" width="18" height="3" rx="1.5" fill="rgba(148,163,184,0.4)"/>',
    };
    const inner = map[type] || map['cloudy'];
    return `<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
}

// ─── Canvas Particle System ───────────────────
const canvas = document.getElementById('weatherCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

function createParticles(type) {
    state.particles = [];
    const W = canvas.width, H = canvas.height;

    if (type === 'stars') {
        for (let i = 0; i < 120; i++) {
            state.particles.push({
                type: 'star', x: Math.random() * W, y: Math.random() * H,
                r: Math.random() * 2 + 0.5, alpha: Math.random(),
                speed: Math.random() * 0.003 + 0.001,
                color: `hsl(${200 + Math.random()*60},80%,80%)`,
            });
        }
    } else if (type === 'rain') {
        for (let i = 0; i < 220; i++) {
            state.particles.push({
                type: 'rain', x: Math.random() * W, y: Math.random() * H,
                len: Math.random() * 18 + 10, speed: Math.random() * 8 + 10,
                alpha: Math.random() * 0.5 + 0.3, angle: 0.3,
                color: 'rgba(147,197,253,',
            });
        }
    } else if (type === 'snow') {
        for (let i = 0; i < 150; i++) {
            state.particles.push({
                type: 'snow', x: Math.random() * W, y: Math.random() * H,
                r: Math.random() * 4 + 1.5, speed: Math.random() * 1.5 + 0.5,
                dx: (Math.random() - 0.5) * 0.6, alpha: Math.random() * 0.6 + 0.4,
                wobble: Math.random() * Math.PI * 2, wobbleSpeed: Math.random() * 0.02 + 0.01,
            });
        }
    } else if (type === 'storm') {
        for (let i = 0; i < 200; i++) {
            state.particles.push({
                type: 'rain', x: Math.random() * W, y: Math.random() * H,
                len: Math.random() * 20 + 12, speed: Math.random() * 14 + 14,
                alpha: Math.random() * 0.6 + 0.3, angle: 0.5,
                color: 'rgba(99,102,241,',
            });
        }
        for (let i = 0; i < 4; i++) {
            state.particles.push({ type: 'lightning', x: Math.random() * W, y: 0, alpha: 0, timer: Math.random() * 300 + 100 });
        }
    } else if (type === 'fog') {
        for (let i = 0; i < 25; i++) {
            state.particles.push({
                type: 'fog', x: Math.random() * W, y: Math.random() * H,
                w: Math.random() * 300 + 200, h: Math.random() * 30 + 20,
                speed: Math.random() * 0.2 + 0.05,
                alpha: Math.random() * 0.07 + 0.03,
            });
        }
    } else if (type === 'clouds') {
        for (let i = 0; i < 8; i++) {
            state.particles.push({
                type: 'cloud', x: Math.random() * W, y: Math.random() * (H * 0.5),
                r: Math.random() * 80 + 60, speed: Math.random() * 0.3 + 0.05,
                alpha: Math.random() * 0.05 + 0.02,
            });
        }
    }
}

let lastTime = 0;
function animateCanvas(ts) {
    const dt = Math.min(ts - lastTime, 50);
    lastTime = ts;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const W = canvas.width, H = canvas.height;

    for (const p of state.particles) {
        if (p.type === 'star') {
            p.alpha += Math.sin(ts * p.speed) * 0.02;
            p.alpha = Math.max(0.1, Math.min(1, p.alpha));
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color.replace(')', `,${p.alpha})`).replace('hsl', 'hsla');
            ctx.fill();
        } else if (p.type === 'rain') {
            p.y += p.speed * (dt / 16);
            p.x += p.angle * (dt / 16);
            if (p.y > H) { p.y = -20; p.x = Math.random() * W; }
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.x - p.angle * p.len * 0.4, p.y + p.len);
            ctx.strokeStyle = p.color + p.alpha + ')';
            ctx.lineWidth = 1;
            ctx.stroke();
        } else if (p.type === 'snow') {
            p.wobble += p.wobbleSpeed;
            p.y += p.speed * (dt / 16);
            p.x += Math.sin(p.wobble) * 0.5;
            if (p.y > H) { p.y = -10; p.x = Math.random() * W; }
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${p.alpha})`;
            ctx.fill();
        } else if (p.type === 'lightning') {
            p.timer -= dt;
            if (p.timer <= 0) {
                p.alpha = 1; p.x = Math.random() * W;
                p.timer = Math.random() * 400 + 200;
            } else if (p.alpha > 0) {
                p.alpha -= 0.06;
                if (p.alpha < 0) p.alpha = 0;
                ctx.globalAlpha = p.alpha * 0.15;
                ctx.fillStyle = '#a78bfa';
                ctx.fillRect(0, 0, W, H);
                ctx.globalAlpha = 1;
            }
        } else if (p.type === 'fog') {
            p.x += p.speed * (dt / 16);
            if (p.x > W + p.w / 2) p.x = -p.w / 2;
            const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.w / 2);
            grd.addColorStop(0, `rgba(200,210,230,${p.alpha})`);
            grd.addColorStop(1, 'transparent');
            ctx.fillStyle = grd;
            ctx.beginPath();
            ctx.ellipse(p.x, p.y, p.w / 2, p.h / 2, 0, 0, Math.PI * 2);
            ctx.fill();
        } else if (p.type === 'cloud') {
            p.x += p.speed * (dt / 16);
            if (p.x > W + p.r) p.x = -p.r;
            const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
            grd.addColorStop(0, `rgba(180,190,210,${p.alpha})`);
            grd.addColorStop(1, 'transparent');
            ctx.fillStyle = grd;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    state.canvasAnimId = requestAnimationFrame(animateCanvas);
}
state.canvasAnimId = requestAnimationFrame(animateCanvas);

// ─── API ─────────────────────────────────────
async function fetchWeather(city) {
    showLoading();
    try {
        const res = await fetch(`https://wttr.in/${encodeURIComponent(city)}?format=j1`);
        if (!res.ok) throw new Error('Not found');
        const json = await res.json();
        state.data = json;
        state.city = city;
        renderWeather(json);
        showContent();
    } catch (e) {
        showError();
    }
}

async function fetchByCoords(lat, lon) {
    showLoading();
    try {
        const res = await fetch(`https://wttr.in/${lat},${lon}?format=j1`);
        if (!res.ok) throw new Error('err');
        const json = await res.json();
        state.data = json;
        renderWeather(json);
        showContent();
    } catch (e) {
        showError();
    }
}

// ─── Render ───────────────────────────────────
function renderWeather(d) {
    const cur = d.current_condition[0];
    const area = d.nearest_area[0];
    const todayW = d.weather[0];

    // City / Country
    const cityName = area.areaName[0].value;
    const country = area.country[0].value;
    qs('#cityName').textContent = cityName;
    qs('#countryCode').textContent = country;
    document.title = `${cityName} Weather — WeatherVerse`;

    // Weather code + theme
    const code = parseInt(cur.weatherCode);
    state.weatherCode = code;
    const meta = getMeta(code);
    applyTheme(meta.theme, cur);

    // Icon
    qs('#weatherIconWrap').innerHTML = buildIcon(meta.icon);

    // Temperature
    const tempC = parseInt(cur.temp_C);
    const tempF = parseInt(cur.temp_F);
    const feelsC = parseInt(cur.FeelsLikeC);
    const feelsF = parseInt(cur.FeelsLikeF);
    const maxC = parseInt(todayW.maxtempC);
    const minC = parseInt(todayW.mintempC);
    const maxF = parseInt(todayW.maxtempF);
    const minF = parseInt(todayW.mintempF);

    updateTemps({ tempC, tempF, feelsC, feelsF, maxC, minC, maxF, minF });

    // Condition
    qs('#conditionText').textContent = cur.weatherDesc[0].value;

    // Precip
    const hourly0 = todayW.hourly[0];
    qs('#precipChance').textContent = (hourly0.chanceofrain || '0') + '%';

    // Details
    qs('#windSpeed').textContent = cur.windspeedKmph;
    qs('#windDir').textContent = cur.winddir16Point;
    setCompass(dirToAngle(cur.winddir16Point));

    const hum = parseInt(cur.humidity);
    qs('#humidity').textContent = hum;
    animBar('#humidityFill', hum);
    qs('#humidityHint').textContent = humidityLabel(hum);

    const vis = parseInt(cur.visibility);
    qs('#visibility').textContent = vis;
    renderVisDots(vis);

    qs('#pressure').textContent = cur.pressure;

    const uv = parseInt(cur.uvIndex);
    qs('#uvIndex').textContent = uv;
    qs('#uvLevel').textContent = uvLabel(uv);
    qs('#uvPointer').style.left = Math.min(100, (uv / 11) * 100) + '%';

    // Sunrise / Sunset
    const sr = todayW.astronomy[0].sunrise;
    const ss = todayW.astronomy[0].sunset;
    qs('#sunrise').textContent = formatTime12(sr);
    qs('#sunset').textContent = formatTime12(ss);
    animateSunArc(sr, ss);

    // Hourly Forecast
    renderHourly(todayW.hourly, meta.icon);

    // 3-Day Forecast
    renderForecast(d.weather);

    // Start clock
    startClock();
    qs('#currentDate').textContent = formatDate(new Date());

    // Particles
    createParticles(meta.particles);
}

function updateTemps({ tempC, tempF, feelsC, feelsF, maxC, minC, maxF, minF }) {
    const isCelsius = state.units === 'C';
    qs('#tempValue').textContent = isCelsius ? tempC : tempF;
    qs('#tempUnit').textContent = isCelsius ? '°C' : '°F';
    qs('#feelsLike').textContent = (isCelsius ? feelsC : feelsF) + '°';
    qs('#tempMax').textContent = isCelsius ? maxC : maxF;
    qs('#tempMin').textContent = isCelsius ? minC : minF;
    qs('#unitLabel').textContent = isCelsius ? '°C' : '°F';
}

function renderHourly(hourlyArr, defaultIcon) {
    const track = qs('#hourlyTrack');
    track.innerHTML = '';
    const now = new Date().getHours();

    hourlyArr.forEach((h, i) => {
        const hr = parseInt(h.time) / 100;
        const label = hr === 0 ? '12 AM' : hr < 12 ? `${hr} AM` : hr === 12 ? '12 PM' : `${hr-12} PM`;
        const isNow = Math.abs(hr - now) < 3 && i === 0 || (hr <= now && hr + 3 > now);
        const code = parseInt(h.weatherCode);
        const icon = getMeta(code).icon;
        const temp = state.units === 'C' ? h.tempC : h.tempF;
        const precip = h.chanceofrain || '0';

        const el = document.createElement('div');
        el.className = 'hourly-item' + (isNow ? ' now' : '');
        el.innerHTML = `
            <span class="hourly-time">${label}</span>
            <div class="hourly-icon">${buildSmallIcon(icon)}</div>
            <span class="hourly-temp">${temp}°</span>
            ${parseInt(precip) > 10 ? `<span class="hourly-precip">${precip}%</span>` : ''}
        `;
        track.appendChild(el);
    });
}

function renderForecast(weatherArr) {
    const list = qs('#forecastList');
    list.innerHTML = '';
    const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    const today = new Date();

    weatherArr.forEach((w, i) => {
        const d = new Date(today);
        d.setDate(today.getDate() + i);
        const dayLabel = i === 0 ? 'Today' : days[d.getDay()];
        const code = parseInt(w.hourly[4]?.weatherCode || w.hourly[0].weatherCode);
        const meta = getMeta(code);

        const hi = state.units === 'C' ? parseInt(w.maxtempC) : parseInt(w.maxtempF);
        const lo = state.units === 'C' ? parseInt(w.mintempC) : parseInt(w.mintempF);
        const range = hi - lo;

        const row = document.createElement('div');
        row.className = 'forecast-row' + (i === 0 ? ' today' : '');
        row.innerHTML = `
            <span class="forecast-day">${dayLabel}</span>
            <div class="forecast-icon">${buildSmallIcon(meta.icon)}</div>
            <span class="forecast-condition">${meta.label}</span>
            <div class="forecast-temps">
                <span class="fc-hi">${hi}°</span>
                <span class="fc-lo">${lo}°</span>
            </div>
        `;
        list.appendChild(row);
    });
}

// ─── Theme ─────────────────────────────────────
function applyTheme(themeName, cur) {
    const body = document.body;
    const isNight = isNightTime(cur);
    const finalTheme = (themeName === 'clear-day' && isNight) ? 'clear-night' : themeName;

    body.className = `theme-${finalTheme}`;
}

function isNightTime(cur) {
    const h = new Date().getHours();
    return h < 6 || h >= 20;
}

// ─── UI State ─────────────────────────────────
function showLoading() {
    qs('#loadingScreen').classList.remove('hidden');
    qs('#loadingScreen').style.display = 'flex';
    qs('#errorScreen').classList.add('hidden');
    qs('#weatherContent').classList.add('hidden');
}
function showError() {
    qs('#loadingScreen').style.display = 'none';
    qs('#errorScreen').classList.remove('hidden');
    qs('#weatherContent').classList.add('hidden');
}
function showContent() {
    qs('#loadingScreen').style.display = 'none';
    qs('#errorScreen').classList.add('hidden');
    qs('#weatherContent').classList.remove('hidden');
    qs('#weatherContent').style.display = 'grid';
}

// ─── Clock ─────────────────────────────────────
function startClock() {
    if (state.timeTickerInterval) clearInterval(state.timeTickerInterval);
    const el = qs('#currentTime');
    const tick = () => {
        const now = new Date();
        el.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };
    tick();
    state.timeTickerInterval = setInterval(tick, 1000);
}

// ─── Helpers ──────────────────────────────────
function qs(sel) { return document.querySelector(sel); }

function formatDate(d) {
    return d.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
}

function formatTime12(str) {
    // wttr.in gives "06:30 AM" or similar
    return str;
}

function dirToAngle(dir) {
    const dirs = { N:0,NNE:22.5,NE:45,ENE:67.5,E:90,ESE:112.5,SE:135,SSE:157.5,
                   S:180,SSW:202.5,SW:225,WSW:247.5,W:270,WNW:292.5,NW:315,NNW:337.5 };
    return dirs[dir] || 0;
}

function setCompass(angle) {
    const needle = qs('#compassNeedle');
    if (needle) needle.style.transform = `translate(-50%, -100%) rotate(${angle}deg)`;
}

function animBar(sel, pct) {
    setTimeout(() => {
        const el = qs(sel);
        if (el) el.style.width = Math.min(100, pct) + '%';
    }, 400);
}

function renderVisDots(vis) {
    const wrap = qs('#visDots');
    if (!wrap) return;
    wrap.innerHTML = '';
    const total = 10;
    const lit = Math.min(total, Math.round(vis));
    for (let i = 0; i < total; i++) {
        const d = document.createElement('div');
        d.className = 'vis-dot' + (i < lit ? ' lit' : '');
        wrap.appendChild(d);
    }
}

function uvLabel(uv) {
    if (uv <= 2)  return 'Low';
    if (uv <= 5)  return 'Moderate';
    if (uv <= 7)  return 'High';
    if (uv <= 10) return 'Very High';
    return 'Extreme';
}

function humidityLabel(h) {
    if (h < 30)  return 'Dry';
    if (h < 60)  return 'Comfortable';
    if (h < 80)  return 'Humid';
    return 'Very Humid';
}

function animateSunArc(srStr, ssStr) {
    try {
        const parseT = s => {
            const [time, ampm] = s.trim().split(' ');
            let [h, m] = time.split(':').map(Number);
            if (ampm && ampm.toLowerCase() === 'pm' && h !== 12) h += 12;
            if (ampm && ampm.toLowerCase() === 'am' && h === 12) h = 0;
            return h * 60 + m;
        };
        const now = new Date().getHours() * 60 + new Date().getMinutes();
        const sr = parseT(srStr);
        const ss = parseT(ssStr);
        const pct = Math.max(0, Math.min(1, (now - sr) / (ss - sr)));
        const pathLen = 130;
        const offset = pathLen - pct * pathLen;

        setTimeout(() => {
            const path = qs('#sunArcPath');
            const dot = qs('#sunDot');
            if (path) path.style.strokeDashoffset = offset;

            // Move dot along arc
            if (dot) {
                const t = pct;
                const x = 10 + t * 100;
                const y = 55 + (0.5 - 2 * pct * (1 - pct)) * (-50 * 2);  // rough quadratic
                // Parametric: P = (1-t)^2*P0 + 2t(1-t)*P1 + t^2*P2
                const p0x = 10, p0y = 55, p1x = 60, p1y = 5, p2x = 110, p2y = 55;
                const bx = (1-t)*(1-t)*p0x + 2*t*(1-t)*p1x + t*t*p2x;
                const by_ = (1-t)*(1-t)*p0y + 2*t*(1-t)*p1y + t*t*p2y;
                dot.setAttribute('cx', bx);
                dot.setAttribute('cy', by_);
            }
        }, 600);
    } catch(e) {}
}

// ─── 3D Card Tilt ─────────────────────────────
const heroScene = document.getElementById('heroCardScene');
const heroCard  = document.getElementById('heroCard');

if (heroScene && heroCard) {
    heroScene.addEventListener('mousemove', e => {
        const rect = heroScene.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width  - 0.5;
        const y = (e.clientY - rect.top)  / rect.height - 0.5;
        heroCard.style.transform = `
            perspective(1200px)
            rotateX(${-y * 14}deg)
            rotateY(${x * 14}deg)
            translateZ(8px)
        `;
        const glow = qs('#cardGlow');
        if (glow) {
            glow.style.background = `radial-gradient(ellipse at ${(x+0.5)*100}% ${(y+0.5)*100}%, var(--card-glow-color), transparent 70%)`;
        }
    });
    heroScene.addEventListener('mouseleave', () => {
        heroCard.style.transform = 'perspective(1200px) rotateX(0) rotateY(0) translateZ(0)';
        qs('#cardGlow').style.background = '';
    });
}

// ─── Detail Card Hover Tilt ───────────────────
document.querySelectorAll('.detail-card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width  - 0.5;
        const y = (e.clientY - rect.top)  / rect.height - 0.5;
        card.style.transform = `perspective(600px) rotateX(${-y*8}deg) rotateY(${x*8}deg) translateZ(4px)`;
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});

// ─── Search ───────────────────────────────────
const searchInput = qs('#searchInput');
const searchBtn   = qs('#searchBtn');

function doSearch() {
    const val = searchInput.value.trim();
    if (val.length < 2) return;
    qs('#searchSuggestions').classList.remove('show');
    fetchWeather(val);
}

searchBtn.addEventListener('click', doSearch);
searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
});

// ─── Location Button ──────────────────────────
qs('#locationBtn').addEventListener('click', () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
        pos => fetchByCoords(pos.coords.latitude, pos.coords.longitude),
        () => alert('Location access denied.')
    );
});

// ─── Unit Toggle ─────────────────────────────
qs('#unitToggle').addEventListener('click', () => {
    state.units = state.units === 'C' ? 'F' : 'C';
    if (state.data) {
        const cur = state.data.current_condition[0];
        const todayW = state.data.weather[0];
        updateTemps({
            tempC: parseInt(cur.temp_C), tempF: parseInt(cur.temp_F),
            feelsC: parseInt(cur.FeelsLikeC), feelsF: parseInt(cur.FeelsLikeF),
            maxC: parseInt(todayW.maxtempC), minC: parseInt(todayW.mintempC),
            maxF: parseInt(todayW.maxtempF), minF: parseInt(todayW.mintempF),
        });
        const meta = getMeta(state.weatherCode);
        renderHourly(todayW.hourly, meta.icon);
        renderForecast(state.data.weather);
    }
});

// ─── Retry Button ─────────────────────────────
qs('#retryBtn').addEventListener('click', () => {
    fetchWeather(state.city);
});

// ─── Search Suggestions (example cities) ──────
const SAMPLE_CITIES = [
    'New York', 'London', 'Tokyo', 'Paris', 'Sydney',
    'Dubai', 'Singapore', 'Berlin', 'Toronto', 'Bangkok',
    'Los Angeles', 'Mumbai', 'Seoul', 'Chicago', 'Amsterdam',
];

searchInput.addEventListener('input', () => {
    const val = searchInput.value.trim().toLowerCase();
    const sugg = qs('#searchSuggestions');
    if (val.length < 2) { sugg.classList.remove('show'); return; }
    const matches = SAMPLE_CITIES.filter(c => c.toLowerCase().startsWith(val)).slice(0, 5);
    if (!matches.length) { sugg.classList.remove('show'); return; }
    sugg.innerHTML = matches.map(c => `
        <div class="suggestion-item" data-city="${c}">
            <i class="fas fa-location-dot"></i>${c}
        </div>`).join('');
    sugg.classList.add('show');
});

qs('#searchSuggestions').addEventListener('click', e => {
    const item = e.target.closest('.suggestion-item');
    if (!item) return;
    const city = item.dataset.city;
    searchInput.value = city;
    qs('#searchSuggestions').classList.remove('show');
    fetchWeather(city);
});

document.addEventListener('click', e => {
    if (!e.target.closest('.search-wrapper')) {
        qs('#searchSuggestions').classList.remove('show');
    }
});

// ─── Init ─────────────────────────────────────
fetchWeather('London');
