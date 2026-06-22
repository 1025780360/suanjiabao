// 简约服饰插画 — 品类配图库
// 风格：极简线条 + 暖金米色，匹配 App 设计语言

function svgDataUrl(svg: string): string {
  return 'data:image/svg+xml,' + encodeURIComponent(svg)
}

// ════════════════════  插画库  ════════════════════
const tshirtSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f5ead3"/><path d="M70 55 L100 42 L130 55 L135 75 L130 80 L130 140 L128 145 L72 145 L70 140 L70 80 L65 75 Z" fill="#d4a852" stroke="#b8802a" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 42 L100 52" stroke="#b8802a" stroke-width="2" stroke-linecap="round"/><circle cx="100" cy="95" r="14" fill="none" stroke="#f5ead3" stroke-width="2" opacity="0.6"/><text x="100" y="100" text-anchor="middle" font-size="12" fill="#f5ead3" font-family="sans-serif">T</text></svg>`

const hoodieSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f0e6cf"/><path d="M65 58 L100 40 L135 58 L140 80 L138 148 L62 148 L60 80 Z" fill="#8b7a5e" stroke="#5e4f3a" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 40 L100 58" stroke="#5e4f3a" stroke-width="2" stroke-linecap="round"/><path d="M62 80 Q62 72 68 72 L100 76 L132 72 Q138 72 138 80" fill="#6b5c42" stroke="#5e4f3a" stroke-width="2"/><rect x="78" y="100" width="44" height="34" rx="6" fill="#6b5c42" stroke="#5e4f3a" stroke-width="1.5"/><line x1="100" y1="100" x2="100" y2="134" stroke="#5e4f3a" stroke-width="1.5"/></svg>`

const pantsSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#e8ecf2"/><path d="M72 44 L70 156 L88 156 L92 140 L90 96 L108 96 L108 140 L112 156 L130 156 L128 44 Z" fill="#3a5a7c" stroke="#1e3450" stroke-width="2.5" stroke-linejoin="round"/><line x1="100" y1="44" x2="100" y2="88" stroke="#1e3450" stroke-width="2"/><circle cx="100" cy="48" r="4" fill="#c4953a"/><path d="M72 44 L128 44" stroke="#1e3450" stroke-width="3"/></svg>`

const coatSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#ebe5d8"/><path d="M54 48 L100 32 L146 48 L150 78 L152 156 L146 160 L54 160 L48 156 L50 78 Z" fill="#8b7355" stroke="#5c4428" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 32 L100 52" stroke="#5c4428" stroke-width="2" stroke-linecap="round"/><path d="M52 80 L100 80 L148 80" fill="none" stroke="#5c4428" stroke-width="3"/><line x1="100" y1="80" x2="100" y2="156" stroke="#5c4428" stroke-width="1.5"/><rect x="76" y="58" width="48" height="18" rx="3" fill="#5c4428"/><rect x="86" y="114" width="28" height="18" rx="3" fill="none" stroke="#5c4428" stroke-width="2"/></svg>`

const dressSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f3e6d2"/><path d="M80 50 L100 42 L120 50 L125 70 L122 155 L100 165 L78 155 L75 70 Z" fill="#d4a090" stroke="#a06048" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 42 L100 55" stroke="#a06048" stroke-width="2" stroke-linecap="round"/><path d="M75 90 Q75 80 88 82 L100 88 L112 82 Q125 80 125 90" fill="none" stroke="#f3e6d2" stroke-width="2.5"/></svg>`

const shirtSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#eef0e6"/><path d="M68 50 L100 36 L132 50 L136 80 L132 88 L132 148 L130 154 L70 154 L68 148 L68 88 L64 80 Z" fill="#b8c5c0" stroke="#6b8076" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 36 L100 54 L100 88" stroke="#6b8076" stroke-width="2" stroke-linecap="round"/><path d="M64 80 L100 84 L136 80" fill="none" stroke="#6b8076" stroke-width="2"/><rect x="84" y="62" width="32" height="12" rx="4" fill="#6b8076"/></svg>`

const sweaterSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#eee8da"/><path d="M62 56 L100 36 L138 56 L142 82 L140 152 L136 156 L100 152 L64 156 L60 152 L58 82 Z" fill="#c4956b" stroke="#8b5a3c" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 36 L100 56" stroke="#8b5a3c" stroke-width="2"/><path d="M100 56 Q82 64 70 80" fill="none" stroke="#8b5a3c" stroke-width="2"/><path d="M100 56 Q118 64 130 80" fill="none" stroke="#8b5a3c" stroke-width="2"/><path d="M70 96 Q84 88 100 90 Q116 88 130 96" fill="none" stroke="#d4b896" stroke-width="3"/><line x1="100" y1="152" x2="100" y2="140" stroke="#8b5a3c" stroke-width="1.5"/></svg>`

const vestSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f2ead8"/><path d="M76 48 L100 38 L124 48 L128 70 L130 148 L126 155 L100 152 L74 155 L70 148 L72 70 Z" fill="#9ea898" stroke="#5c6b58" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 38 L100 54" stroke="#5c6b58" stroke-width="2" stroke-linecap="round"/><path d="M76 80 Q100 74 124 80" fill="none" stroke="#5c6b58" stroke-width="2"/></svg>`

const shortsSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f1e6ce"/><path d="M70 68 L68 130 L88 130 L90 120 L88 90 L108 90 L108 120 L110 130 L132 130 L130 68 Z" fill="#8b9e7c" stroke="#4d5e40" stroke-width="2.5" stroke-linejoin="round"/><line x1="100" y1="68" x2="100" y2="90" stroke="#4d5e40" stroke-width="2"/><rect x="72" y="70" width="56" height="4" rx="2" fill="#b8802a"/></svg>`

const jacketSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#e8e4dc"/><path d="M56 56 L100 38 L144 56 L148 82 L148 152 L142 158 L128 154 L128 86 L100 88 L72 86 L72 154 L58 158 L52 152 L52 82 Z" fill="#2d2d2d" stroke="#111" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 38 L100 58" stroke="#111" stroke-width="2" stroke-linecap="round"/><path d="M72 70 L56 82" fill="none" stroke="#e8e4dc" stroke-width="4"/><path d="M128 70 L144 82" fill="none" stroke="#e8e4dc" stroke-width="4"/><line x1="100" y1="86" x2="100" y2="148" stroke="#111" stroke-width="1.5"/><rect x="82" y="108" width="16" height="12" rx="2" fill="#444"/><rect x="102" y="108" width="16" height="12" rx="2" fill="#444"/></svg>`

const downCoatSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#faf5ec"/><path d="M54 46 L100 28 L146 46 L150 76 L152 154 L146 160 L54 160 L48 154 L50 76 Z" fill="#d4683a" stroke="#a04020" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 28 L100 48" stroke="#a04020" stroke-width="2.5"/><path d="M50 84 L100 88 L150 84" fill="none" stroke="#faf5ec" stroke-width="5" stroke-linecap="round"/><path d="M48 108 L100 112 L152 108" fill="none" stroke="#faf5ec" stroke-width="5" stroke-linecap="round"/><path d="M48 132 L100 136 L152 132" fill="none" stroke="#faf5ec" stroke-width="5" stroke-linecap="round"/><rect x="78" y="66" width="44" height="14" rx="7" fill="#a04020"/></svg>`

const sportSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#edeadf"/><path d="M66 48 L100 36 L134 48 L138 72 L136 150 L132 156 L100 152 L68 156 L64 150 L62 72 Z" fill="#6a8ea0" stroke="#2e5060" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 36 L100 54" stroke="#2e5060" stroke-width="2" stroke-linecap="round"/><line x1="70" y1="96" x2="130" y2="96" stroke="#edeadf" stroke-width="3"/><line x1="68" y1="122" x2="132" y2="122" stroke="#edeadf" stroke-width="3"/><circle cx="90" cy="60" r="3" fill="#b8802a"/><circle cx="110" cy="60" r="3" fill="#b8802a"/></svg>`

const defaultSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="16" fill="#f5ecd8"/><path d="M70 50 L100 36 L130 50 L135 70 L138 150 L135 155 L65 155 L62 150 L65 70 Z" fill="#c4b89a" stroke="#8a7d60" stroke-width="2.5" stroke-linejoin="round"/><path d="M100 36 L100 52" stroke="#8a7d60" stroke-width="2" stroke-linecap="round"/><circle cx="100" cy="100" r="20" fill="none" stroke="#f5ecd8" stroke-width="2" opacity="0.5"/><text x="100" y="105" text-anchor="middle" font-size="16" fill="#f5ecd8" font-family="sans-serif" font-weight="bold">衣</text></svg>`

// ════════════════════  映射表  ════════════════════
/** key → 配图 */
const keyImages: Record<string, string> = {
  tshirt:   svgDataUrl(tshirtSvg),
  hoodie:   svgDataUrl(hoodieSvg),
  pants:    svgDataUrl(pantsSvg),
  coat:     svgDataUrl(coatSvg),
  dress:    svgDataUrl(dressSvg),
  skirt:    svgDataUrl(dressSvg),
  shirt:    svgDataUrl(shirtSvg),
  blouse:   svgDataUrl(shirtSvg),
  sweater:  svgDataUrl(sweaterSvg),
  cardigan: svgDataUrl(sweaterSvg),
  knit:     svgDataUrl(sweaterSvg),
  vest:     svgDataUrl(vestSvg),
  tank:     svgDataUrl(vestSvg),
  shorts:   svgDataUrl(shortsSvg),
  jacket:   svgDataUrl(jacketSvg),
  blazer:   svgDataUrl(jacketSvg),
  suit:     svgDataUrl(jacketSvg),
  downcoat: svgDataUrl(downCoatSvg),
  down:     svgDataUrl(downCoatSvg),
  puffer:   svgDataUrl(downCoatSvg),
  sport:    svgDataUrl(sportSvg),
  sportswear: svgDataUrl(sportSvg),
  active:   svgDataUrl(sportSvg),
  default:  svgDataUrl(defaultSvg),
  custom:   svgDataUrl(defaultSvg),
}

/** 名称关键词 → key，按优先级排列 */
const nameKeywords: [string, string][] = [
  // 上装
  ['t恤', 'tshirt'], ['短袖', 'tshirt'], ['t shirt', 'tshirt'], ['tee', 'tshirt'], ['polo', 'tshirt'], ['长袖t', 'tshirt'],
  ['卫衣', 'hoodie'], ['帽衫', 'hoodie'], ['套头衫', 'hoodie'], ['连帽', 'hoodie'], ['hoodie', 'hoodie'], ['sweatshirt', 'hoodie'],
  ['衬衫', 'shirt'], ['衬衣', 'shirt'], ['shirt', 'shirt'], ['blouse', 'shirt'], ['牛津纺', 'shirt'], ['格子衫', 'shirt'],
  ['毛衣', 'sweater'], ['针织', 'sweater'], ['毛衫', 'sweater'], ['sweater', 'sweater'], ['knit', 'sweater'], ['cardigan', 'sweater'], ['开衫', 'sweater'],
  ['背心', 'vest'], ['马甲', 'vest'], ['坎肩', 'vest'], ['吊带', 'vest'], ['tank', 'vest'], ['vest', 'vest'], ['无袖', 'vest'],
  // 外套
  ['羽绒', 'downcoat'], ['棉服', 'downcoat'], ['棉袄', 'downcoat'], ['down', 'downcoat'], ['puffer', 'downcoat'], ['面包服', 'downcoat'],
  ['夹克', 'jacket'], ['jacket', 'jacket'], ['皮衣', 'jacket'], ['棒球服', 'jacket'], ['飞行夹克', 'jacket'],
  ['西装', 'jacket'], ['西服', 'jacket'], ['blazer', 'jacket'], ['suit', 'jacket'], ['正装', 'jacket'],
  ['外套', 'coat'], ['大衣', 'coat'], ['风衣', 'coat'], ['coat', 'coat'], ['trench', 'coat'], ['呢大衣', 'coat'], ['羊绒大衣', 'coat'],
  // 下装
  ['裤子', 'pants'], ['长裤', 'pants'], ['休闲裤', 'pants'], ['西裤', 'pants'], ['pants', 'pants'], ['trousers', 'pants'],
  ['短裤', 'shorts'], ['热裤', 'shorts'], ['shorts', 'shorts'], ['五分裤', 'shorts'], ['七分裤', 'shorts'],
  ['牛仔', 'pants'], ['jeans', 'pants'], ['denim', 'pants'],
  // 裙装
  ['连衣裙', 'dress'], ['裙子', 'dress'], ['长裙', 'dress'], ['短裙', 'dress'], ['dress', 'dress'], ['skirt', 'dress'],
  ['半身裙', 'dress'], ['a字裙', 'dress'], ['百褶裙', 'dress'],
  // 运动
  ['运动', 'sport'], ['sport', 'sport'], ['健身', 'sport'], ['跑步', 'sport'], ['瑜伽', 'sport'], ['训练', 'sport'],
  ['卫裤', 'sport'], ['运动裤', 'sport'], ['legging', 'sport'],
]

// ════════════════════  导出函数  ════════════════════

/** 根据品类 key 获取配图 */
export function getCategoryImage(categoryKey: string): string {
  const key = categoryKey?.toLowerCase().replace(/[^a-z0-9]/g, '') || ''
  if (keyImages[key]) return keyImages[key]
  // key 包含已知品类
  for (const k of Object.keys(keyImages)) {
    if (k === 'default' || k === 'custom') continue
    if (key.includes(k) || k.includes(key)) return keyImages[k]
  }
  return keyImages.default
}

/** 根据品类名称文本智能匹配配图 */
export function matchImageByName(name: string): string {
  const lower = name.toLowerCase().replace(/\s+/g, '')
  for (const [keyword, key] of nameKeywords) {
    if (lower.includes(keyword.replace(/\s+/g, ''))) {
      return keyImages[key] || keyImages.default
    }
  }
  return keyImages.default
}
