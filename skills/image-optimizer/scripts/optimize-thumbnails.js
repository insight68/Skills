const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const { removeWhiteBackground, removeWhiteBackgroundFromBuffer } = require('./background-removal');

// ============================================
// 默认配置
// ============================================
const DEFAULT_CONFIG = {
  size: 128,           // 默认缩略图尺寸
  quality: 75,         // 缩略图质量（比大图低）
  effort: 6,           // 最大压缩努力
  fit: 'cover',        // 裁剪策略
  position: 'entropy', // 智能裁剪位置
  kernel: 'lanczos3',   // 高质量缩放算法
  concurrency: 6,      // 并发数量（缩略图处理快）
  extension: '.webp',  // 输出格式
  // 透明度配置
  transparency: 'auto', // 透明度模式: auto, preserve, remove, white-to-transparent, add
  background: null,     // 背景色 (如 '#ffffff' 或 {r,g,b,a})
  alphaLevel: 1,        // 添加透明度时的透明度级别 (0-1, 1=不透明)
  nearLossless: false,  // WebP 近无损压缩
  // 白色背景移除配置
  threshold: 240,       // 白色阈值 (0-255, 越高越严格)
  smoothEdges: true,    // 是否平滑边缘（羽化效果）
  // 超采样和边缘平滑配置
  supersample: true,           // 启用2x超采样（显著提升边缘质量）
  gaussianSmoothing: true,     // 使用5x5高斯平滑（false=3x3简单平均）
  edgeSmoothingIterations: 1   // 边缘平滑迭代次数（1-2，过高会过度模糊）
};

// ============================================
// 命令行参数解析
// ============================================
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };
  const files = []; // 收集位置参数（文件路径）

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    // 处理等号格式的参数 (如 --size=128)
    if (arg.startsWith('--')) {
      const eqIndex = arg.indexOf('=');
      if (eqIndex !== -1) {
        const key = arg.substring(0, eqIndex);
        const value = arg.substring(eqIndex + 1);

        if (key === '--size') {
          config.size = parseInt(value);
        } else if (key === '--quality') {
          config.quality = parseInt(value);
        } else if (key === '--fit') {
          config.fit = value;
        } else if (key === '--position') {
          config.position = value;
        } else if (key === '--dir') {
          config.dir = value;
        } else if (key === '--output') {
          config.output = value;
        } else if (key === '--concurrency') {
          config.concurrency = parseInt(value);
        } else if (key === '--transparency') {
          config.transparency = value;
        } else if (key === '--background') {
          config.background = value;
        } else if (key === '--alpha') {
          config.alphaLevel = parseFloat(value);
        } else if (key === '--extension') {
          config.extension = value;
        } else if (key === '--near-lossless') {
          config.nearLossless = true;
        } else if (key === '--threshold') {
          config.threshold = parseInt(value);
        } else if (key === '--smooth-edges') {
          config.smoothEdges = value === 'true';
        } else if (key === '--supersample') {
          config.supersample = value === 'true';
        } else if (key === '--gaussian-smoothing') {
          config.gaussianSmoothing = value === 'true';
        } else if (key === '--smoothing-iterations') {
          config.edgeSmoothingIterations = parseInt(value);
        }
        continue;
      }
    }

    // 处理空格格式的参数 (如 --size 128)
    if (arg === '--size' && args[i + 1]) {
      config.size = parseInt(args[++i]);
    } else if (arg === '--quality' && args[i + 1]) {
      config.quality = parseInt(args[++i]);
    } else if (arg === '--fit' && args[i + 1]) {
      config.fit = args[++i];
    } else if (arg === '--position' && args[i + 1]) {
      config.position = args[++i];
    } else if (arg === '--dir' && args[i + 1]) {
      config.dir = args[++i];
    } else if (arg === '--output' && args[i + 1]) {
      config.output = args[++i];
    } else if (arg === '--concurrency' && args[i + 1]) {
      config.concurrency = parseInt(args[++i]);
    } else if (arg === '--transparency' && args[i + 1]) {
      config.transparency = args[++i];
    } else if (arg === '--background' && args[i + 1]) {
      config.background = args[++i];
    } else if (arg === '--alpha' && args[i + 1]) {
      config.alphaLevel = parseFloat(args[++i]);
    } else if (arg === '--extension' && args[i + 1]) {
      config.extension = args[++i];
    } else if (arg === '--near-lossless') {
      config.nearLossless = true;
    } else if (arg === '--threshold' && args[i + 1]) {
      config.threshold = parseInt(args[++i]);
    } else if (arg === '--smooth-edges' && args[i + 1]) {
      config.smoothEdges = args[++i] === 'true';
    } else if (arg === '--supersample' && args[i + 1]) {
      config.supersample = args[++i] === 'true';
    } else if (arg === '--gaussian-smoothing' && args[i + 1]) {
      config.gaussianSmoothing = args[++i] === 'true';
    } else if (arg === '--smoothing-iterations' && args[i + 1]) {
      config.edgeSmoothingIterations = parseInt(args[++i]);
    } else if (arg === '--help' || arg === '-h') {
      console.log(`
🖼️  Thumbnail Generator - Usage:

  node scripts/optimize-thumbnails.js [options] [files...]

Options:
  --size <number>          Thumbnail size (default: 128)
  --quality <number>       WebP quality 1-100 (default: 75)
  --fit <strategy>         Resize fit strategy (default: cover)
                           Options: cover, contain, fill, inside, outside
  --position <strategy>    Crop position (default: entropy)
                           Options: top, bottom, left, right, center, entropy, attention
  --dir <path>             Directory to process (default: public)
  --output <path>          Output directory (default: same as input)
  --concurrency <number>   Parallel processing (default: 6)
  --transparency <mode>    Transparency mode (default: auto)
                           Options: auto, preserve, remove, white-to-transparent, add
  --background <color>     Background color when removing transparency
                           Examples: #ffffff, white, rgb(255,255,255)
  --alpha <0-1>           Alpha level for 'add' mode (default: 1.0)
  --near-lossless         Use near-lossless WebP compression
  --extension <format>     Output format (default: .webp, also supports .png)
  --threshold <number>      White threshold for 'white-to-transparent' (0-255, default: 240)
  --smooth-edges <bool>     Enable edge smoothing for background removal (default: true)
  --supersample <bool>      Enable 2x supersampling for better edge quality (default: true)
  --gaussian-smoothing <bool> Use 5x5 Gaussian smoothing (default: true, false=3x3 simple)
  --smoothing-iterations <number> Edge smoothing iterations (default: 1, range: 1-2)

Examples:
  # Process single file
  pnpm optimize:128 public/banana.png

  # Process multiple files
  pnpm optimize:128 public/banana.png public/apple.png

  # Generate 128x128 thumbnails from public/
  pnpm optimize:128

  # Generate 256x256 thumbnails
  pnpm optimize:256

  # Process specific directory
  node scripts/optimize-thumbnails.js --dir=public/icons --size=128

  # High quality thumbnails
  node scripts/optimize-thumbnails.js --size=128 --quality=85

  # Center crop instead of smart crop
  node scripts/optimize-thumbnails.js --size=128 --position=center

  # Preserve transparency (PNG/WebP input)
  pnpm optimize:128 public/logo.png --transparency=preserve

  # Convert white background to transparent
  pnpm optimize:128 public/icon.png --transparency=white-to-transparent

  # Remove transparency with white background
  pnpm optimize:128 public/image.png --transparency=remove --background=white

  # Add 50% transparency to opaque images
  pnpm optimize:128 public/image.png --transparency=add --alpha=0.5

  # Output as PNG with transparency
  pnpm optimize:128 public/logo.png --transparency=preserve --extension=.png

  # Smart white background removal with custom threshold
  pnpm optimize:128 public/product.png --transparency=white-to-transparent --threshold=245

  # Background removal without edge smoothing (faster)
  pnpm optimize:128 public/icon.png --transparency=white-to-transparent --smooth-edges=false

  # High-quality background removal for product photos
  pnpm optimize:256 public/product.jpg --transparency=white-to-transparent --threshold=250 --quality=90

  # Supersampling + Gaussian smoothing for smooth edges (slower but better quality)
  pnpm optimize:128 public/icon.png --transparency=white-to-transparent --supersample=true --gaussian-smoothing=true

  # Fast processing with simple smoothing
  pnpm optimize:128 public/icon.png --transparency=white-to-transparent --supersample=false --gaussian-smoothing=false

  # Extra smoothing iterations for very jagged edges
  pnpm optimize:128 public/product.png --transparency=white-to-transparent --smoothing-iterations=2

Strategies:
  fit: cover      - 填充整个区域（推荐，精确尺寸）
  fit: inside     - 保持比例，可能不是精确尺寸
  fit: fill       - 强制拉伸（会变形，不推荐）

  position: entropy  - 智能裁剪（推荐，保留主体）
  position: center   - 居中裁剪
  position: top      - 顶部裁剪
  position: attention - AI注意力（需要sharp 0.29+）

Transparency Modes:
  auto                   - Auto-detect based on input format (PNG/WebP preserve, others remove)
  preserve               - Preserve existing transparency channel
  remove                 - Remove transparency and fill with background color
  white-to-transparent   - Smart white background removal (uses threshold & edge smoothing)
  add                    - Add transparency with specified alpha level

Background Removal Tips:
  - Use --threshold=230-245 for off-white backgrounds
  - Use --threshold=250-255 for pure white backgrounds
  - Enable --smooth-edges=true for clean edges (slower)
  - Disable --smooth-edges=false for faster processing
  - Enable --supersample=true for smooth edges (2x resolution, then downscale)
  - Use --gaussian-smoothing=true for best quality (5x5 kernel, spatial weights)
  - Use --gaussian-smoothing=false for faster processing (3x3 simple average)
  - Increase --smoothing-iterations=2 for extra smooth edges (may over-blur)
      `);
      process.exit(0);
    } else if (!arg.startsWith('--')) {
      // 收集位置参数（文件路径）
      files.push(arg);
    }
  }

  // 如果提供了文件路径参数，添加到配置
  if (files.length > 0) {
    config.files = files;
  }

  return config;
}

// ============================================
// 图片收集
// ============================================
function collectImages(dir) {
  const targetDir = path.join(process.cwd(), dir);

  if (!fs.existsSync(targetDir)) {
    console.error(`❌ Directory not found: ${targetDir}`);
    process.exit(1);
  }

  const extensions = ['.png', '.jpg', '.jpeg', '.webp'];
  const images = [];

  function scanDir(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);

      if (entry.isDirectory()) {
        // 递归扫描子目录（排除 node_modules, .next 等）
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules' && entry.name !== '.next') {
          scanDir(fullPath);
        }
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (extensions.includes(ext)) {
          // 计算相对路径
          const relPath = path.relative(process.cwd(), fullPath);
          images.push(relPath);
        }
      }
    }
  }

  scanDir(targetDir);
  return images;
}

// ============================================
// 透明度处理
// ============================================

/**
 * 处理图片透明度
 * @param {Sharp} pipeline - Sharp 实例
 * @param {string} inputPath - 输入文件路径
 * @param {object} config - 配置对象
 * @returns {Promise<object>} 处理后的数据 { pipeline, data, info }
 */
async function handleTransparency(pipeline, inputPath, config) {
  const ext = path.extname(inputPath).toLowerCase();

  // 自动模式：根据输入格式判断
  if (config.transparency === 'auto') {
    if (ext === '.png' || ext === '.webp') {
      // PNG/WebP 可能已有透明度，保留它
      return { pipeline: pipeline.ensureAlpha() };
    } else {
      // JPG 等格式保持不透明
      return { pipeline };
    }
  }

  switch (config.transparency) {
    case 'preserve':
      // 保留透明度
      return { pipeline: pipeline.ensureAlpha() };

    case 'remove':
      // 移除透明度，填充背景色
      const bg = config.background || '#ffffff';
      return { pipeline: pipeline.flatten({ background: bg }) };

    case 'add':
      // 添加透明度
      return { pipeline: pipeline.ensureAlpha(config.alphaLevel) };

    case 'white-to-transparent':
      // 标记需要使用 white-to-transparent 处理
      // 返回特殊标记，稍后处理
      return { whiteToTransparent: true };

    default:
      return { pipeline };
  }
}

// ============================================
// 生成缩略图
// ============================================
async function generateThumbnail(inputPath, config) {
  const fullPath = path.join(process.cwd(), inputPath);

  if (!fs.existsSync(fullPath)) {
    console.error(`❌ File not found: ${fullPath}`);
    return null;
  }

  // 生成输出文件名
  const parsedPath = path.parse(inputPath);
  const outputFilename = `${parsedPath.name}-${config.size}${config.extension}`;
  const outputPath = config.output
    ? path.join(process.cwd(), config.output, outputFilename)
    : path.join(parsedPath.dir, outputFilename);

  // 检查是否已存在
  if (fs.existsSync(outputPath)) {
    const inputStat = fs.statSync(fullPath);
    const outputStat = fs.statSync(outputPath);

    // 只在输入文件更新时重新生成
    if (outputStat.mtime > inputStat.mtime) {
      console.log(`✅ ${path.basename(inputPath)} (thumbnail already up-to-date)`);
      return { skipped: true, inputSize: inputStat.size, outputSize: outputStat.size };
    }
  }

  try {
    let pipeline = sharp(fullPath);

    // 处理透明度（在 resize 之前）
    const transparencyResult = await handleTransparency(pipeline, inputPath, config);

    // 如果是 white-to-transparent 模式，使用新的处理流程
    if (transparencyResult.whiteToTransparent) {
      // 新的处理流程：超采样 + 背景移除 + 下采样

      const targetSize = config.size;
      const supersampleSize = config.supersample ? targetSize * 2 : targetSize;

      // Step 1: 超采样 resize 到 2x 目标尺寸（在原始 RGB 图像上使用 entropy）
      const resizeOptions = {
        fit: config.fit,
        position: config.position === 'entropy' ? sharp.strategy.entropy : config.position,
        kernel: config.kernel
      };

      const resized = await sharp(fullPath)
        .resize(supersampleSize, supersampleSize, resizeOptions)
        .ensureAlpha()  // 确保有 alpha 通道
        .raw()
        .toBuffer({ resolveWithObject: true });

      // Step 2: 在超采样图像上做背景移除（应用高斯边缘平滑）
      const bgRemoved = await removeWhiteBackgroundFromBuffer(
        resized.data,
        resized.info,
        {
          threshold: config.threshold,
          fuzziness: 15,
          smoothEdges: config.smoothEdges,
          gaussianSmoothing: config.gaussianSmoothing,
          smoothingIterations: config.edgeSmoothingIterations
        }
      );

      // Step 3: 如果启用了超采样，缩小到目标尺寸（自然抗锯齿）
      let finalPipeline = sharp(bgRemoved.data, { raw: bgRemoved.info });

      if (config.supersample) {
        finalPipeline = finalPipeline.resize(targetSize, targetSize, {
          fit: 'inside',
          kernel: 'lanczos3'  // 使用高质量下采样
        });
      }

      // Step 4: 输出格式转换
      if (config.extension === '.webp') {
        await finalPipeline
          .webp({
            quality: config.quality,
            effort: config.effort,
            nearLossless: config.nearLossless,
            smartSubsample: true
          })
          .toFile(outputPath);
      } else if (config.extension === '.png') {
        await finalPipeline
          .png({
            compressionLevel: 9,
            adaptiveFiltering: true,
            palette: false
          })
          .toFile(outputPath);
      }
    } else {
      // 其他透明度模式，使用 pipeline
      pipeline = transparencyResult.pipeline;

      // Resize 配置
      const resizeOptions = {
        fit: config.fit,
        position: config.position === 'entropy' ? sharp.strategy.entropy : config.position,
        kernel: config.kernel,
        background: config.background || { r: 255, g: 255, b: 255, alpha: 0 }
      };

      // 根据输出格式执行转换
      if (config.extension === '.webp') {
        await pipeline
          .resize(config.size, config.size, resizeOptions)
          .webp({
            quality: config.quality,
            effort: config.effort,
            nearLossless: config.nearLossless,
            smartSubsample: true,
            // 保留透明度时考虑无损或高质量
            lossless: config.transparency === 'preserve' && config.quality >= 90
          })
          .toFile(outputPath);
      } else if (config.extension === '.png') {
        await pipeline
          .resize(config.size, config.size, resizeOptions)
          .png({
            compressionLevel: 9,
            adaptiveFiltering: true,
            palette: false  // 使用完整色彩以支持透明度
          })
          .toFile(outputPath);
      } else {
        // JPEG 等格式会自动移除透明度
        await pipeline
          .resize(config.size, config.size, resizeOptions)
          .jpeg({ quality: config.quality })
          .toFile(outputPath);
      }
    }

    const inputSize = fs.statSync(fullPath).size;
    const outputSize = fs.statSync(outputPath).size;
    const ratio = ((config.size * config.size) / (inputSize * 8 * 1024)).toFixed(2); // 估算

    console.log(`✅ ${path.basename(inputPath)} → ${outputFilename}`);
    console.log(`   ${config.size}x${config.size}, ${formatBytes(inputSize)} → ${formatBytes(outputSize)}`);

    return { inputSize, outputSize, resized: true };
  } catch (error) {
    console.error(`❌ Error processing ${path.basename(inputPath)}:`, error.message);
    return null;
  }
}

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
 * 并发处理
 */
async function generateThumbnails(images, config) {
  const chunks = [];
  const concurrency = config.concurrency;

  // 分批
  for (let i = 0; i < images.length; i += concurrency) {
    chunks.push(images.slice(i, i + concurrency));
  }

  let processed = 0;
  let skipped = 0;
  let totalInputSize = 0;
  let totalOutputSize = 0;

  const startTime = Date.now();

  for (let i = 0; i < chunks.length; i++) {
    console.log(`\n📦 Processing chunk ${i + 1}/${chunks.length} (${chunks[i].length} images)...`);

    const promises = chunks[i].map(image => generateThumbnail(image, config));
    const results = await Promise.all(promises);

    results.forEach(result => {
      if (result) {
        if (result.skipped) {
          skipped++;
        } else {
          processed++;
          totalInputSize += result.inputSize;
          totalOutputSize += result.outputSize;
        }
      }
    });
  }

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  return {
    processed,
    skipped,
    total: images.length,
    totalInputSize,
    totalOutputSize,
    duration
  };
}

// ============================================
// 主函数
// ============================================
async function main() {
  const config = parseArgs();

  console.log('🖼️  Thumbnail Generator\n');
  console.log('Configuration:');
  console.log(`   Size: ${config.size}x${config.size}`);
  console.log(`   Quality: ${config.quality}`);
  console.log(`   Fit: ${config.fit}`);
  console.log(`   Position: ${config.position}`);
  console.log(`   Concurrency: ${config.concurrency}`);
  console.log(`   Directory: ${config.dir || 'public'}`);
  // 显示文件路径（如果直接传递了文件）
  if (config.files) {
    console.log(`   Files: ${config.files.join(', ')}`);
  }
  console.log('\n' + '─'.repeat(60) + '\n');

  // 收集图片 - 按优先级
  console.log('📂 Collecting images...\n');
  let images = [];

  if (config.files) {
    // 优先级1：直接传递的文件路径
    images = config.files.filter(p => fs.existsSync(path.join(process.cwd(), p)));
    if (images.length !== config.files.length) {
      const missing = config.files.filter(f => !images.includes(f));
      console.warn(`⚠️  Warning: These files were not found:\n   ${missing.join('\n   ')}\n`);
    }
  } else if (config.dir) {
    // 优先级2：扫描目录
    images = collectImages(config.dir);
  } else {
    // 优先级3：默认文件
    images = [
      // 默认处理一些常见图片
      'public/banana.png',
      'public/favicon.ico',
      'public/apple-touch-icon.png'
    ].filter(p => fs.existsSync(path.join(process.cwd(), p)));
  }

  if (images.length === 0) {
    console.log('⚠️  No images found to process.');
    console.log('   Use --dir to specify a directory or provide image paths.\n');
    return;
  }

  console.log(`Found ${images.length} image(s)\n`);

  // 生成缩略图
  const results = await generateThumbnails(images, config);

  // 统计结果
  console.log('─'.repeat(60));
  console.log('\n📊 Summary:\n');
  console.log(`   Processed: ${results.processed}`);
  console.log(`   Skipped: ${results.skipped}`);
  console.log(`   Total: ${results.total}`);
  console.log(`   Input Size: ${formatBytes(results.totalInputSize)}`);
  console.log(`   Output Size: ${formatBytes(results.totalOutputSize)}`);
  console.log(`   Compression: ${((1 - results.totalOutputSize / results.totalInputSize) * 100).toFixed(1)}%`);
  console.log(`   Duration: ${results.duration}s\n`);

  console.log('✨ Thumbnail generation complete!\n');
}

// 运行
main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});
