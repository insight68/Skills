const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// Small images to optimize
const imagesToOptimize = [
  'public/prompt/portrait-enhanced.jpg',
  'public/prompt/product-minimal.jpg',
  'public/prompt/fantasy-character.jpg',
  'public/Google-Nano-Banana-AI-Image-Generator-All-You-Need-To-Know.jpg',
];

async function optimizeImage(inputPath) {
  const outputPath = inputPath.replace(/\.(png|jpg|jpeg)$/i, '.webp');

  // Check if WebP version already exists
  if (fs.existsSync(outputPath)) {
    const existingSize = fs.statSync(outputPath).size;
    const originalSize = fs.statSync(inputPath).size;
    const savings = ((originalSize - existingSize) / originalSize * 100).toFixed(2);

    console.log(`✅ ${path.basename(inputPath)} (already optimized)`);
    console.log(`   Original: ${(originalSize / 1024).toFixed(2)} KB`);
    console.log(`   Optimized: ${(existingSize / 1024).toFixed(2)} KB`);
    console.log(`   Savings: ${savings}%\n`);

    return parseFloat(savings);
  }

  // For small images, use high quality
  await sharp(inputPath)
    .webp({
      quality: 90,
      effort: 6,
      nearLossless: true
    })
    .toFile(outputPath);

  const originalSize = fs.statSync(inputPath).size;
  const newSize = fs.statSync(outputPath).size;
  const savings = ((originalSize - newSize) / originalSize * 100).toFixed(2);

  console.log(`✅ ${path.basename(inputPath)}`);
  console.log(`   Original: ${(originalSize / 1024).toFixed(2)} KB`);
  console.log(`   Optimized: ${(newSize / 1024).toFixed(2)} KB`);
  console.log(`   Savings: ${savings}%\n`);

  return parseFloat(savings);
}

async function main() {
  console.log('🖼️  Optimizing Small Images\n');

  let totalSavings = 0;

  for (const image of imagesToOptimize) {
    const fullPath = path.join(process.cwd(), image);

    if (!fs.existsSync(fullPath)) {
      console.error(`❌ File not found: ${image}\n`);
      continue;
    }

    try {
      const savings = await optimizeImage(fullPath);
      totalSavings += savings;
    } catch (error) {
      console.error(`❌ Error optimizing ${image}:`, error.message, '\n');
    }
  }

  console.log(`\n📊 Total savings: ${totalSavings.toFixed(2)}%\n`);
}

main().catch(error => {
  console.error('❌ Optimization failed:', error);
  process.exit(1);
});
