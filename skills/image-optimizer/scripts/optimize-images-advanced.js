const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// ============================================
// 配置区 - 可以修改这些参数
// prompt图片默认：16:9， 800*450或 640px*360px 20251225
// ============================================
const CONFIG = {
  // 并发处理数量（建议 CPU 核心数）
  concurrency: 4,

  // 默认 WebP 配置
  webp: {
    quality: 85,
    effort: 6,
    nearLossless: true,
    smartSubsample: true
  },

  // Resize 配置（null = 不改变尺寸）
  resize: null,  // 或 { width: 128, height: 128, fit: 'cover', position: 'entropy' }

  // 是否显示详细信息
  verbose: true
};

// ============================================
// 图片列表
// ============================================
const imagesToOptimize = [
  'public/tutorials/step3-final-result.png',
  'public/tutorials/nano-banana-multi-turn-example.png',
  'public/tutorials/getting-started-hero.png',
  'public/ai-laboratory-technology-background.png',
  'public/tutorials/nano-banana-before-after-1.png',
  'public/tutorials/step1-original-image.png',
  'public/ai-neural-network-visualization-modern-tech.png',
  'public/tutorials/getting-started-cover.png',
  'public/Cinematic Universes with Nano Banana.png',
];

// ============================================
// 工具函数
// ============================================

/**
 * 格式化文件大小
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 带配置的图片优化
 */
async function optimizeImage(inputPath, config = {}) {
  const {
    resize = null,
    webp = {},
    verbose = true
  } = config;

  if (!fs.existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    return null;
  }

  const outputPath = inputPath.replace(/\.(png|jpg|jpeg)$/i, '.webp');

  // 检查是否已优化
  if (fs.existsSync(outputPath)) {
    const originalSize = fs.statSync(inputPath).size;
    const optimizedSize = fs.statSync(outputPath).size;
    const savings = ((originalSize - optimizedSize) / originalSize * 100).toFixed(2);

    if (verbose) {
      console.log(`✅ ${path.basename(inputPath)} (already optimized)`);
      console.log(`   Original: ${formatBytes(originalSize)}`);
      console.log(`   Optimized: ${formatBytes(optimizedSize)}`);
      console.log(`   Savings: ${savings}%\n`);
    }

    return { savings, originalSize, optimizedSize };
  }

  // 开始处理
  let pipeline = sharp(inputPath);

  // 可选的 resize
  if (resize) {
    const resizeOptions = {
      fit: resize.fit || 'cover',
      position: resize.position || 'entropy',
      kernel: resize.kernel || 'lanczos3'
    };

    if (verbose) {
      console.log(`📐 Resizing to ${resize.width}x${resize.height} (${resize.fit}, ${resize.position})`);
    }

    pipeline = pipeline.resize(resize.width, resize.height, resizeOptions);
  }

  // WebP 配置
  const webpOptions = {
    quality: webp.quality || CONFIG.webp.quality,
    effort: webp.effort || CONFIG.webp.effort,
    nearLossless: webp.nearLossless !== undefined ? webp.nearLossless : CONFIG.webp.nearLossless,
    smartSubsample: webp.smartSubsample !== undefined ? webp.smartSubsample : CONFIG.webp.smartSubsample
  };

  // 执行优化
  await pipeline.webp(webpOptions).toFile(outputPath);

  const originalSize = fs.statSync(inputPath).size;
  const newSize = fs.statSync(outputPath).size;
  const savings = ((originalSize - newSize) / originalSize * 100).toFixed(2);

  if (verbose) {
    console.log(`✅ ${path.basename(inputPath)}`);
    if (resize) {
      console.log(`   Resized: ${resize.width}x${resize.height}`);
    }
    console.log(`   Original: ${formatBytes(originalSize)}`);
    console.log(`   Optimized: ${formatBytes(newSize)}`);
    console.log(`   Savings: ${savings}%\n`);
  }

  return { savings: parseFloat(savings), originalSize, newSize };
}

/**
 * 并发处理图片
 */
async function optimizeImagesConcurrent(imageList, config) {
  const concurrency = config.concurrency || CONFIG.concurrency;
  const chunks = [];

  // 分批处理
  for (let i = 0; i < imageList.length; i += concurrency) {
    chunks.push(imageList.slice(i, i + concurrency));
  }

  let totalSavings = 0;
  let totalCount = 0;
  let totalOriginalSize = 0;
  let totalNewSize = 0;

  for (let i = 0; i < chunks.length; i++) {
    console.log(`\n📦 Processing chunk ${i + 1}/${chunks.length} (${chunks[i].length} images)...`);

    const promises = chunks[i].map(image => {
      const fullPath = path.join(process.cwd(), image);
      return optimizeImage(fullPath, config);
    });

    const results = await Promise.all(promises);

    // 统计结果
    results.forEach(result => {
      if (result) {
        totalSavings += result.savings;
        totalCount++;
        totalOriginalSize += result.originalSize;
        totalNewSize += result.newSize;
      }
    });
  }

  return {
    totalCount,
    totalSavings,
    totalOriginalSize,
    totalNewSize
  };
}

/**
 * 主函数
 */
async function main() {
  console.log('🖼️  Advanced Image Optimization Script\n');
  console.log('Configuration:');
  console.log(`   Concurrency: ${CONFIG.concurrency}`);
  console.log(`   Resize: ${CONFIG.resize ? `${CONFIG.resize.width}x${CONFIG.resize.height}` : 'Disabled'}`);
  console.log(`   Quality: ${CONFIG.webp.quality}`);
  console.log(`   Effort: ${CONFIG.webp.effort}`);
  console.log('\n' + '─'.repeat(60) + '\n');

  const startTime = Date.now();

  const results = await optimizeImagesConcurrent(imagesToOptimize, CONFIG);

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  console.log('─'.repeat(60));
  console.log('\n📊 Optimization Summary:\n');
  console.log(`   Total Images: ${results.totalCount}`);
  console.log(`   Original Size: ${formatBytes(results.totalOriginalSize)}`);
  console.log(`   Optimized Size: ${formatBytes(results.totalNewSize)}`);
  console.log(`   Total Savings: ${formatBytes(results.totalOriginalSize - results.totalNewSize)} (${results.totalSavings.toFixed(2)}%)`);
  console.log(`   Duration: ${duration}s`);
  console.log(`   Speed: ${(results.totalCount / duration).toFixed(2)} images/second\n`);

  console.log('✨ Optimization complete!\n');
}

// 运行主函数
main().catch(error => {
  console.error('❌ Optimization failed:', error);
  process.exit(1);
});
