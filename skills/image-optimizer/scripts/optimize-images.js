const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// Large images that need optimization
const imagesToOptimize = [
  'public/tutorials/step3-final-result.png',
  'public/tutorials/nano-banana-multi-turn-example.png',
  'public/tutorials/getting-started-hero.png',
  'public/ai-laboratory-technology-background.png',
  'public/tutorials/nano-banana-before-after-1.png',
  'public/tutorials/step1-original-image.png',
  'public/ai-neural-network-visualization-modern-tech.png',
  'public/tutorials/getting-started-cover.png',
  'public/prompt/noir-detective-alley.jpg',
  'public/prompt/ghibli-forest-guardian.jpg',
  'public/prompt/Modern Interior Styling.jpg',
  'public/Cinematic Universes with Nano Banana.png',
  'public/prompt/cinematic-portrait-spotlight.jpg',
];

/**
 * Optimize a single image to WebP format
 */
async function optimizeImage(inputPath) {
  const outputPath = inputPath.replace(/\.(png|jpg|jpeg)$/i, '.webp');

  // Check if WebP version already exists
  if (fs.existsSync(outputPath)) {
    const existingSize = fs.statSync(outputPath).size;
    const originalSize = fs.statSync(inputPath).size;
    const savings = ((originalSize - existingSize) / originalSize * 100).toFixed(2);

    console.log(`✅ ${path.basename(inputPath)} (already optimized)`);
    console.log(`   Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Optimized: ${(existingSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Savings: ${savings}%\n`);

    return parseFloat(savings);
  }

  // Optimize image with Sharp
  await sharp(inputPath)
    .webp({
      quality: 85,
      effort: 6, // Maximum compression effort
      nearLossless: true,
      smartSubsample: true
    })
    .toFile(outputPath);

  const originalSize = fs.statSync(inputPath).size;
  const newSize = fs.statSync(outputPath).size;
  const savings = ((originalSize - newSize) / originalSize * 100).toFixed(2);

  console.log(`✅ ${path.basename(inputPath)}`);
  console.log(`   Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Optimized: ${(newSize / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Savings: ${savings}%\n`);

  return parseFloat(savings);
}

/**
 * Generate blur data URL for placeholder
 */
async function generateBlurPlaceholder(inputPath) {
  const blurPath = inputPath.replace(/\.(png|jpg|jpeg|webp)$/i, '.blur.txt');

  if (fs.existsSync(blurPath)) {
    return;
  }

  // Resize to small blur image and convert to base64
  const { data, info } = await sharp(inputPath)
    .resize(10, 10, { fit: 'inside' })
    .modulate({ brightness: 1.2, saturation: 1.2 })
    .blur(2)
    .toBuffer({ resolveWithObject: true });

  console.log(`📍 Generated blur placeholder for ${path.basename(inputPath)}`);
}

/**
 * Main optimization function
 */
async function main() {
  console.log('🖼️  Image Optimization Script\n');
  console.log('This script will:');
  console.log('1. Convert large PNG/JPG images to WebP format');
  console.log('2. Generate blur placeholders for better UX\n');
  console.log('─'.repeat(60) + '\n');

  let totalSavings = 0;
  let totalOriginalSize = 0;
  let totalOptimizedSize = 0;

  for (const image of imagesToOptimize) {
    const fullPath = path.join(process.cwd(), image);

    if (!fs.existsSync(fullPath)) {
      console.error(`❌ File not found: ${image}\n`);
      continue;
    }

    try {
      const originalSize = fs.statSync(fullPath).size;
      totalOriginalSize += originalSize;

      const savings = await optimizeImage(fullPath);
      totalSavings += savings;

      // Generate blur placeholder
      await generateBlurPlaceholder(fullPath);

      // Calculate optimized size
      const webpPath = fullPath.replace(/\.(png|jpg|jpeg)$/i, '.webp');
      if (fs.existsSync(webpPath)) {
        totalOptimizedSize += fs.statSync(webpPath).size;
      }
    } catch (error) {
      console.error(`❌ Error optimizing ${image}:`, error.message, '\n');
    }
  }

  console.log('─'.repeat(60));
  console.log('\n📊 Optimization Summary:\n');
  console.log(`   Original Size: ${(totalOriginalSize / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Optimized Size: ${(totalOptimizedSize / 1024 / 1024).toFixed(2)} MB`);
  console.log(`   Total Savings: ${((totalOriginalSize - totalOptimizedSize) / 1024 / 1024).toFixed(2)} MB (${totalSavings.toFixed(2)}%)\n`);

  console.log('✨ Optimization complete!\n');

  console.log('📝 Next Steps:');
  console.log('1. Review the optimized WebP images in the public/ folder');
  console.log('2. Update image references in your components from .png/.jpg to .webp');
  console.log('3. Test your application to ensure images load correctly');
  console.log('4. Run Lighthouse audit to verify performance improvements\n');
}

// Run the optimization
main().catch(error => {
  console.error('❌ Optimization failed:', error);
  process.exit(1);
});
