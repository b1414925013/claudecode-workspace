// Built-in preset images as SVG data URLs for the image puzzle mode

function svgUrl(svg: string): string {
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

const presets = [
  {
    id: 'gradient',
    name: '渐变',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ff6b6b"/>
        <stop offset="50%" stop-color="#ffd93d"/>
        <stop offset="100%" stop-color="#6bcb77"/>
      </linearGradient></defs>
      <rect width="400" height="400" fill="url(#g)"/>
    </svg>`),
  },
  {
    id: 'circles',
    name: '圆点',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <rect width="400" height="400" fill="#2c3e50"/>
      <circle cx="100" cy="100" r="60" fill="#e74c3c" opacity="0.8"/>
      <circle cx="300" cy="120" r="50" fill="#3498db" opacity="0.8"/>
      <circle cx="150" cy="300" r="70" fill="#f39c12" opacity="0.8"/>
      <circle cx="320" cy="320" r="45" fill="#2ecc71" opacity="0.8"/>
      <circle cx="200" cy="200" r="40" fill="#9b59b6" opacity="0.8"/>
    </svg>`),
  },
  {
    id: 'waves',
    name: '波浪',
    url: svgUrl(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
      <rect width="400" height="400" fill="#1a1a2e"/>
      <path d="M0 200 Q50 150 100 200 T200 200 T300 200 T400 200" stroke="#e94560" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 240 Q50 190 100 240 T200 240 T300 240 T400 240" stroke="#0f3460" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 160 Q50 110 100 160 T200 160 T300 160 T400 160" stroke="#533483" stroke-width="8" fill="none" opacity="0.9"/>
      <path d="M0 280 Q50 230 100 280 T200 280 T300 280 T400 280" stroke="#e94560" stroke-width="4" fill="none" opacity="0.5"/>
    </svg>`),
  },
]

export default presets
