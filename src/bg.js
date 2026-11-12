// خلفيات التطبيق: سماء وكنيسة، الهيكل، الشموع والصليب، البخور، أيقونة، تسبيح وموسيقى
const smoke = n => Array.from({length: n}, (_, i) => `<i class="smk" style="left:${6 + i * (88 / n)}%;animation-delay:${-i * 4.3}s"></i>`).join('');
const churchSvg = (fill = '#232c63') => `<svg class="church" viewBox="0 0 400 180" preserveAspectRatio="xMidYMax meet"><g fill="${fill}">
<rect x="20" y="132" width="360" height="48"/>
<rect x="150" y="84" width="100" height="50"/><path d="M150 84a50 50 0 0 1 100 0z"/><rect x="198.6" y="10" width="2.8" height="26"/><rect x="192" y="16" width="16" height="2.8"/>
<rect x="62" y="104" width="56" height="30"/><path d="M62 104a28 28 0 0 1 56 0z"/><rect x="88.6" y="58" width="2.8" height="20"/><rect x="83" y="63" width="14" height="2.6"/>
<rect x="282" y="104" width="56" height="30"/><path d="M282 104a28 28 0 0 1 56 0z"/><rect x="308.6" y="58" width="2.8" height="20"/><rect x="303" y="63" width="14" height="2.6"/>
<rect x="30" y="112" width="18" height="22"/><path d="M30 112a9 9 0 0 1 18 0z"/><rect x="352" y="112" width="18" height="22"/><path d="M352 112a9 9 0 0 1 18 0z"/></g>
<g fill="#f6c453" opacity=".85"><path d="M186 134v-26a14 14 0 0 1 28 0v26z"/><path d="M76 134v-14a8 8 0 0 1 16 0v14z"/><path d="M308 134v-14a8 8 0 0 1 16 0v14z"/><path d="M168 100a4 8 0 0 1 8 0v8h-8z M224 100a4 8 0 0 1 8 0v8h-8z"/></g></svg>`;
const censerSvg = `<svg class="censer" viewBox="0 0 60 150"><path d="M30 0v46M30 46L14 66M30 46l16 20" stroke="#c9a24a" stroke-width="2" fill="none"/><path d="M8 68h44a22 22 0 0 1-44 0z" fill="#c9a24a"/><path d="M14 68a16 16 0 0 1 32 0z" fill="#e8c46a"/><rect x="28.5" y="42" width="3" height="10" fill="#e8c46a"/></svg>`;
const crossSvg = `<svg viewBox="0 0 100 150" style="position:absolute;left:50%;top:12%;width:34%;transform:translateX(-50%);filter:drop-shadow(0 0 18px #ffcc5588)"><path d="M43 4h14v38h30v14H57v90H43V56H13V42h30z" fill="none" stroke="#e3b85a" stroke-width="3"/><path d="M43 4h14v38h30v14H57v90H43V56H13V42h30z" fill="#e3b85a" opacity=".18"/></svg>`;
const notes = n => Array.from({length: n}, (_, i) => `<i class="note" style="left:${5 + i * (90 / n)}%;animation-delay:${-i * 3.1}s">${['♪', '♫', '♬', '♩'][i % 4]}</i>`).join('');

export const BG = {
  sky: {n: 'السماء والكنيسة', h: `<div class="layer sky"></div><div class="layer sun"></div><div class="layer rays"></div><div class="layer cloud"></div>${censerSvg}${churchSvg()}${smoke(5)}`},
  sanct: {n: 'الهيكل والقدس', h: `<div class="layer sanct"></div><div class="arch"></div><div class="lamp" style="left:22%;height:90px"><i></i></div><div class="lamp" style="left:50%;height:130px"><i></i></div><div class="lamp" style="left:78%;height:90px"><i></i></div>${crossSvg}${smoke(4)}`},
  candles: {n: 'الشموع والصليب', h: `<div class="layer candl"></div>${crossSvg}<div class="cdl" style="left:12%;height:90px"></div><div class="cdl" style="left:26%;height:60px"></div><div class="cdl" style="left:64%;height:70px"></div><div class="cdl" style="left:78%;height:100px"></div><div class="cdl" style="left:88%;height:55px"></div>`},
  incense: {n: 'البخور', h: `<div class="layer incs"></div>${censerSvg}${smoke(7)}`},
  icon: {n: 'أيقونة الأنبا كاراس', h: `<div class="layer iconbg"><img src="logo.png" alt=""></div>${smoke(3)}`},
  music: {n: 'التسبيح والموسيقى', h: `<div class="layer music"></div><div class="layer staff"></div>${notes(8)}`}
};
export const getBgKey = () => { const k = localStorage.getItem('bgk'); return BG[k] ? k : 'sky'; };
export const setBg = k => { if (BG[k]) localStorage.setItem('bgk', k); document.getElementById('bg').innerHTML = BG[getBgKey()].h; };
export const preview = k => BG[k].h;
export const splashBg = () => BG.sanct.h;
