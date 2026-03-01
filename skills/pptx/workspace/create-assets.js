const sharp = require('sharp');

// Layer colors from bottom to top
const layers = [
  { name: 'Knowledge', color1: '#6A5ACD', color2: '#7B68EE' },      // Purple
  { name: 'Skills', color1: '#3498DB', color2: '#5DADE2' },         // Blue
  { name: 'Orchestration', color1: '#4A90A4', color2: '#5C9ead' },  // Teal
  { name: 'Decision', color1: '#FF6B6B', color2: '#FF8C42' },       // Orange-Red
  { name: 'Strategy', color1: '#FFA500', color2: '#FFD700' }        // Gold
];

async function createLayerGradients() {
  for (let i = 0; i < layers.length; i++) {
    const layer = layers[i];
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="80">
      <defs>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:${layer.color1}"/>
          <stop offset="100%" style="stop-color:${layer.color2}"/>
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#g)"/>
    </svg>`;

    await sharp(Buffer.from(svg))
      .png()
      .toFile(`workspace/layer-${i}-gradient.png`);

    console.log(`Created gradient for layer ${i}: ${layer.name}`);
  }
}

createLayerGradients().catch(console.error);
