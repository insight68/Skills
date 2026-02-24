const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const { removeWhiteBackground, removeWhiteBackgroundFromBuffer } = require('./background-removal');

// ============================================
// 预设比例和尺寸配置
// ============================================
const ASPECT_RATIOS = {
  '16:9': {
    name: '16:9 (Widescreen)',
    description: '宽屏显示器，YouTube 视频缩略图',
    sizes: {
      small: { width: 640, height: 360, description: '网页缩略图' },
      medium: { width: 800, height: 450, description: '标准尺寸' },
      large: { width: 1920, height: 1080, description: 'Full HD' },
      xlarge: { width: 2560, height: 1440, description: '2K QHD' }
    }
  },
  '4:3': {
    name: '4:3 (Traditional)',
    description: '传统显示器，iPad',
    sizes: {
      small: { width: 640, height: 480, description: 'VGA' },
      medium: { width: 800, height: 600, description: 'SVGA' },
      large: { width: 1024, height: 768, description: 'XGA' },
      xlarge: { width: 1600, height: 1200, description: 'UXGA' }
    }
  },
  '21:9': {
    name: '21:9 (Ultrawide)',
    description: '超宽屏显示器',
    sizes: {
      small: { width: 640, height: 274, description: '超宽缩略图' },
      medium: { width: 800, height: 343, description: '标准超宽' },
      large: { width: 2560, height: 1080, description: 'Ultrawide FHD' }
    }
  },
  '1:1': {
    name: '1:1 (Square)',
    description: '正方形，社交媒体',
    sizes: {
      small: { width: 128, height: 128, description: '缩略图' },
      medium: { width: 512, height: 512, description: '标准正方形' },
      large: { width: 1080, height: 1080, description: 'Instagram 正方形' }
    }
  },
  '3:2': {
    name: '3:2 (Photo)',
    description: '传统相机比例',
    sizes: {
      small: { width: 600, height: 400, description: '标准照片' },
      medium: { width: 900, height: 600, description: '高清照片' },
      large: { width: 1800, height: 1200, description: '高质量照片' }
    }
  }
};

// ============================================
// 默认配置
// ============================================
const DEFAULT_CONFIG = {
  ratio: '16:9',          // 默认宽高比
  size: 'small',          // 默认尺寸
  width: null,            // 自定义宽度
  height: null,           // 自定义高度
  quality: 75,            // WebP 质量
  effort: 6,              // 最大压缩努力
  fit: 'cover',           // 裁剪策略
  position: 'entropy',    // 智能裁剪位置
  kernel: 'lanczos3',     // 高质量缩放算法
  concurrency: 6,         // 并发数量
  extension: '.webp',     // 输出格式
  // 透明度配置
  transparency: 'auto',
  background: null,
  alphaLevel: 1,
  nearLossless: false,
  // 白色背景移除配置
  threshold: 240,
  smoothEdges: true,
  supersample: true,
  gaussianSmoothing: true,
  edgeSmoothingIterations: 1
};

// ============================================
// 命令行参数解析
// ============================================
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };
  const files = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    // 处理等号格式的参数
    if (arg.startsWith('--')) {
      const eqIndex = arg.indexOf('=');
      if (eqIndex !== -1) {
        const key = arg.substring(0, eqIndex);
        const value = arg.substring(eqIndex + 1);

        if (key === '--ratio') {
          config.ratio = value;
        } else if (key === '--size') {
          config.size = value;
        } else if (key === '--width') {
          config.width = parseInt(value);
        } else if (key === '--height') {
          config.height = parseInt(value);
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

    // 处理空格格式的参数
    if (arg === '--ratio' && args[i + 1]) {
      config.ratio = args[++i];
    } else if (arg === '--size' && args[i + 1]) {
      config.size = args[++i];
    } else if (arg === '--width' && args[i + 1]) {
      config.width = parseInt(args[++i]);
    } else if (arg === '--height' && args[i + 1]) {
      config.height = parseInt(args[++i]);
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
🎬 Aspect Ratio Image Optimizer - Usage:

  node scripts/optimize-aspect-ratio.js [options] [files...]

Aspect Ratio Options:
  --ratio <ratio>      Aspect ratio (default: 16:9)
                       Options: 16:9, 4:3, 21:9, 1:1, 3:2, custom
  --size <size>        Preset size (default: small)
                       Options: small, medium, large, xlarge
  --width <number>     Custom width (overrides ratio/size)
  --height <number>    Custom height (overrides ratio/size)

Image Quality Options:
  --quality <number>   WebP quality 1-100 (default: 75)
  --fit <strategy>     Resize fit strategy (default: cover)
                       Options: cover, contain, fill, inside, outside
  --position <strategy> Crop position (default: entropy)
                       Options: top, bottom, left, right, center, entropy, attention
  --near-lossless      Use near-lossless WebP compression

File Processing:
  --dir <path>         Directory to process (default: public)
  --output <path>      Output directory (default: same as input)
  --concurrency <number> Parallel processing (default: 6)
  --extension <format> Output format (default: .webp, also supports .png)

Transparency Options:
  --transparency <mode> Transparency mode (default: auto)
                       Options: auto, preserve, remove, white-to-transparent, add
  --background <color> Background color when removing transparency
  --alpha <0-1>       Alpha level for 'add' mode (default: 1.0)

Background Removal:
  --threshold <number>      White threshold for 'white-to-transparent' (0-255, default: 240)
  --smooth-edges <bool>     Enable edge smoothing (default: true)
  --supersample <bool>      Enable 2x supersampling (default: true)
  --gaussian-smoothing <bool> Use 5x5 Gaussian smoothing (default: true)
  --smoothing-iterations <number> Edge smoothing iterations (default: 1)

Examples:
  # Generate 16:9 thumbnails (640x360, default)
  pnpm optimize:16-9

  # Generate medium 16:9 (800x450)
  pnpm optimize:16-9 --size=medium

  # Generate large 16:9 (1920x1080)
  pnpm optimize:16-9 --size=large

  # Process single file
  pnpm optimize:16-9 public/image.jpg

  # Generate 4:3 ratio
  pnpm optimize:4-3

  # Custom dimensions
  pnpm optimize:ratio --width=1280 --height=720

  # Custom ratio (3:2)
  node scripts/optimize-aspect-ratio.js --ratio=3:2 --size=medium

  # High quality with background removal
  pnpm optimize:16-9 public/product.jpg \\
    --size=medium \\
    --quality=90 \\
    --transparency=white-to-transparent \\
    --threshold=250

  # Batch process directory
  node scripts/optimize-aspect-ratio.js \\
    --ratio=16:9 \\
    --size=medium \\
    --dir=public/uploads \\
    --output=public/thumbnails

Available Aspect Ratios:
  16:9  - Widescreen (YouTube, modern displays)
         small: 640x360, medium: 800x450, large: 1920x1080, xlarge: 2560x1440

  4:3   - Traditional (iPad, classic displays)
         small: 640x480, medium: 800x600, large: 1024x768, xlarge: 1600x1200

  21:9  - Ultrawide (cinematic displays)
         small: 640x274, medium: 800x343, large: 2560x1080

  1:1   - Square (Instagram, social media)
         small: 128x128, medium: 512x512, large: 1080x1080

  3:2   - Photo (traditional cameras)
         small: 600x400, medium: 900x600, large: 1800x1200

Strategies:
  fit: cover      - Fill entire area (recommended)
  fit: inside     - Keep aspect ratio, may not fill completely
  fit: fill       - Force stretch (distorts image, not recommended)

  position: entropy  - Smart crop (recommended, keeps subject)
  position: center   - Center crop
  position: attention - AI attention (requires sharp 0.29+)

Transparency Modes:
  auto                   - Auto-detect based on input format
  preserve               - Preserve existing transparency
  remove                 - Remove transparency and fill with background
  white-to-transparent   - Smart white background removal
  add                    - Add transparency with alpha level

Tips:
  - Use --ratio and --size for quick preset combinations
  - Use --width and --height for complete custom control
  - Higher quality (90+) for product photos
  - Standard quality (75) for web use
  - Enable supersample for smooth edges
  - Use entropy position for smart cropping
      `);
      process.exit(0);
    } else if (!arg.startsWith('--')) {
      // 收集位置参数（文件路径）
      files.push(arg);
    }
  }

  if (files.length > 0) {
    config.files = files;
  }

  return config;
}

// ============================================
// 计算目标尺寸
// ============================================
function calculateDimensions(config) {
  // 如果明确指定了宽度和高度，直接使用
  if (config.width && config.height) {
    return { width: config.width, height: config.height };
  }

  // 如果只指定了宽度或高度，根据比例计算另一个
  if (config.width || config.height) {
    const ratio = config.ratio;
    if (ASPECT_RATIOS[ratio]) {
      const preset = ASPECT_RATIOS[ratio].sizes.medium;
      const aspectRatio = preset.width / preset.height;

      if (config.width) {
        return {
          width: config.width,
          height: Math.round(config.width / aspectRatio)
        };
      } else {
        return {
          width: Math.round(config.height * aspectRatio),
          height: config.height
        };
      }
    }
  }

  // 使用预设的比例和尺寸
  const ratio = config.ratio;
  const size = config.size;

  if (!ASPECT_RATIOS[ratio]) {
    console.error(`❌ Unsupported ratio: ${ratio}`);
    console.error(`   Supported ratios: ${Object.keys(ASPECT_RATIOS).join(', ')}`);
    process.exit(1);
  }

  const ratioConfig = ASPECT_RATIOS[ratio];
  if (!ratioConfig.sizes[size]) {
    console.error(`❌ Unsupported size: ${size} for ratio ${ratio}`);
    console.error(`   Available sizes: ${Object.keys(ratioConfig.sizes).join(', ')}`);
    process.exit(1);
  }

  return ratioConfig.sizes[size];
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
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules' && entry.name !== '.next') {
          scanDir(fullPath);
        }
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (extensions.includes(ext)) {
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
// 透明度处理（从 optimize-thumbnails.js 复用）
// ============================================
async function handleTransparency(pipeline, inputPath, config) {
  const ext = path.extname(inputPath).toLowerCase();

  if (config.transparency === 'auto') {
    if (ext === '.png' || ext === '.webp') {
      return { pipeline: pipeline.ensureAlpha() };
    } else {
      return { pipeline };
    }
  }

  switch (config.transparency) {
    case 'preserve':
      return { pipeline: pipeline.ensureAlpha() };
    case 'remove':
      const bg = config.background || '#ffffff';
      return { pipeline: pipeline.flatten({ background: bg }) };
    case 'add':
      return { pipeline: pipeline.ensureAlpha(config.alphaLevel) };
    case 'white-to-transparent':
      return { whiteToTransparent: true };
    default:
      return { pipeline };
  }
}

// ============================================
// 生成缩略图
// ============================================
async function generateThumbnail(inputPath, config, dimensions) {
  const fullPath = path.join(process.cwd(), inputPath);

  if (!fs.existsSync(fullPath)) {
    console.error(`❌ File not found: ${fullPath}`);
    return null;
  }

  // 生成输出文件名
  const parsedPath = path.parse(inputPath);
  const sizeSuffix = config.width && config.height
    ? `${config.width}x${config.height}`
    : `${config.ratio}-${config.size}`;
  const outputFilename = `${parsedPath.name}-${sizeSuffix}${config.extension}`;
  const outputPath = config.output
    ? path.join(process.cwd(), config.output, outputFilename)
    : path.join(parsedPath.dir, outputFilename);

  // 检查是否已存在
  if (fs.existsSync(outputPath)) {
    const inputStat = fs.statSync(fullPath);
    const outputStat = fs.statSync(outputPath);

    if (outputStat.mtime > inputStat.mtime) {
      console.log(`✅ ${path.basename(inputPath)} (thumbnail already up-to-date)`);
      return { skipped: true, inputSize: inputStat.size, outputSize: outputStat.size };
    }
  }

  try {
    let pipeline = sharp(fullPath);

    // 处理透明度（在 resize 之前）
    const transparencyResult = await handleTransparency(pipeline, inputPath, config);

    // 如果是 white-to-transparent 模式，使用特殊处理流程
    if (transparencyResult.whiteToTransparent) {
      const targetWidth = dimensions.width;
      const targetHeight = dimensions.height;
      const supersampleWidth = config.supersample ? targetWidth * 2 : targetWidth;
      const supersampleHeight = config.supersample ? targetHeight * 2 : targetHeight;

      // Step 1: 超采样 resize
      const resizeOptions = {
        fit: config.fit,
        position: config.position === 'entropy' ? sharp.strategy.entropy : config.position,
        kernel: config.kernel
      };

      const resized = await sharp(fullPath)
        .resize(supersampleWidth, supersampleHeight, resizeOptions)
        .ensureAlpha()
        .raw()
        .toBuffer({ resolveWithObject: true });

      // Step 2: 背景移除
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

      // Step 3: 下采样到目标尺寸
      let finalPipeline = sharp(bgRemoved.data, { raw: bgRemoved.info });

      if (config.supersample) {
        finalPipeline = finalPipeline.resize(targetWidth, targetHeight, {
          fit: 'inside',
          kernel: 'lanczos3'
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
      // 其他透明度模式，使用标准流程
      pipeline = transparencyResult.pipeline;

      const resizeOptions = {
        fit: config.fit,
        position: config.position === 'entropy' ? sharp.strategy.entropy : config.position,
        kernel: config.kernel,
        background: config.background || { r: 255, g: 255, b: 255, alpha: 0 }
      };

      if (config.extension === '.webp') {
        await pipeline
          .resize(dimensions.width, dimensions.height, resizeOptions)
          .webp({
            quality: config.quality,
            effort: config.effort,
            nearLossless: config.nearLossless,
            smartSubsample: true,
            lossless: config.transparency === 'preserve' && config.quality >= 90
          })
          .toFile(outputPath);
      } else if (config.extension === '.png') {
        await pipeline
          .resize(dimensions.width, dimensions.height, resizeOptions)
          .png({
            compressionLevel: 9,
            adaptiveFiltering: true,
            palette: false
          })
          .toFile(outputPath);
      } else {
        await pipeline
          .resize(dimensions.width, dimensions.height, resizeOptions)
          .jpeg({ quality: config.quality })
          .toFile(outputPath);
      }
    }

    const inputSize = fs.statSync(fullPath).size;
    const outputSize = fs.statSync(outputPath).size;

    console.log(`✅ ${path.basename(inputPath)} → ${outputFilename}`);
    console.log(`   ${dimensions.width}x${dimensions.height}, ${formatBytes(inputSize)} → ${formatBytes(outputSize)}`);

    return { inputSize, outputSize, resized: true };
  } catch (error) {
    console.error(`❌ Error processing ${path.basename(inputPath)}:`, error.message);
    return null;
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// ============================================
// 并发处理
// ============================================
async function generateThumbnails(images, config, dimensions) {
  const chunks = [];
  const concurrency = config.concurrency;

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

    const promises = chunks[i].map(image => generateThumbnail(image, config, dimensions));
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
  const dimensions = calculateDimensions(config);

  console.log('🎬 Aspect Ratio Image Optimizer\n');
  console.log('Configuration:');
  console.log(`   Ratio: ${config.ratio}`);
  console.log(`   Size: ${config.size}`);
  console.log(`   Dimensions: ${dimensions.width}x${dimensions.height}`);
  console.log(`   Quality: ${config.quality}`);
  console.log(`   Fit: ${config.fit}`);
  console.log(`   Position: ${config.position}`);
  console.log(`   Concurrency: ${config.concurrency}`);
  console.log(`   Directory: ${config.dir || 'public'}`);
  if (config.files) {
    console.log(`   Files: ${config.files.join(', ')}`);
  }
  console.log('\n' + '─'.repeat(60) + '\n');

  // 收集图片
  console.log('📂 Collecting images...\n');
  let images = [];

  if (config.files) {
    images = config.files.filter(p => fs.existsSync(path.join(process.cwd(), p)));
    if (images.length !== config.files.length) {
      const missing = config.files.filter(f => !images.includes(f));
      console.warn(`⚠️  Warning: These files were not found:\n   ${missing.join('\n   ')}\n`);
    }
  } else if (config.dir) {
    images = collectImages(config.dir);
  } else {
    images = [
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
  const results = await generateThumbnails(images, config, dimensions);

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
