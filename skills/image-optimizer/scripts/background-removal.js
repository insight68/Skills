const sharp = require('sharp');

/**
 * 智能白色背景移除（从文件路径）
 * 使用颜色键控(Chroma Key)算法，可配置阈值和边缘平滑
 *
 * @param {string} inputPath - 输入文件路径
 * @param {object} options - 配置选项
 * @param {number} options.threshold - 白色阈值 (0-255, 默认 240)
 * @param {boolean} options.smoothEdges - 是否平滑边缘 (默认 true)
 * @param {number} options.fuzziness - 模糊容忍度 (默认 15)
 * @returns {Promise<object>} 处理后的数据 { data, info }
 */
async function removeWhiteBackground(inputPath, options = {}) {
  const {
    threshold = 240,        // 白色阈值 (0-255)
    fuzziness = 15,         // 模糊容忍度
    smoothEdges = true      // 是否平滑边缘
  } = options;

  let pipeline = sharp(inputPath).ensureAlpha();

  // 预处理：如果启用边缘平滑，轻微模糊
  if (smoothEdges) {
    pipeline = pipeline.blur(0.5);
  }

  // 获取原始像素数据
  const { data, info } = await pipeline
    .raw()
    .toBuffer({ resolveWithObject: true });

  return processWhiteBackgroundRemoval(data, info, { threshold, fuzziness, smoothEdges });
}

/**
 * 智能白色背景移除（从 Buffer）
 * 
 * @param {Buffer} inputBuffer - 输入图片 Buffer
 * @param {object} inputInfo - 输入图片信息 { width, height, channels }
 * @param {object} options - 配置选项
 * @returns {object} 处理后的数据 { data, info }
 */
async function removeWhiteBackgroundFromBuffer(inputBuffer, inputInfo, options = {}) {
  const {
    threshold = 240,
    fuzziness = 15,
    smoothEdges = true
  } = options;

  return processWhiteBackgroundRemoval(inputBuffer, inputInfo, { threshold, fuzziness, smoothEdges });
}

/**
 * 核心背景移除算法
 * 
 * @param {Buffer} data - 像素数据
 * @param {object} info - 图像信息
 * @param {object} options - 配置选项
 * @returns {object} 处理后的数据 { data, info }
 */
function processWhiteBackgroundRemoval(data, info, options) {
  const { threshold, fuzziness, smoothEdges, gaussianSmoothing = true, smoothingIterations = 1 } = options;
  const { width, height, channels } = info;
  const pixelData = new Uint8ClampedArray(data);

  // 第一步：白色背景检测和移除
  for (let i = 0; i < pixelData.length; i += channels) {
    const r = pixelData[i];
    const g = pixelData[i + 1];
    const b = pixelData[i + 2];

    // 计算亮度和颜色方差
    const brightness = (r + g + b) / 3;
    const colorVariance = Math.max(r, g, b) - Math.min(r, g, b);

    // 检测是否为白色或近白色
    const isWhite = r > threshold && g > threshold && b > threshold;

    // 如果是白色且颜色方差小（纯色，避免误判主体）
    if (isWhite && colorVariance < 10) {
      // 根据亮度计算渐变透明度
      const alpha = Math.max(0, 255 - (brightness - threshold + fuzziness) * 255 / fuzziness);
      pixelData[i + 3] = Math.min(255, Math.max(0, alpha));
    }
  }

  // 如果启用边缘平滑，进行后处理
  if (smoothEdges) {
    // 选择平滑算法
    if (gaussianSmoothing) {
      // 使用高斯平滑（更好的边缘质量）
      return {
        data: Buffer.from(smoothEdgesGaussian(pixelData, width, height, channels, smoothingIterations)),
        info
      };
    } else {
      // 使用简单平滑（更快）
      return {
        data: Buffer.from(smoothEdgesSimple(pixelData, width, height, channels)),
        info
      };
    }
  }

  return {
    data: Buffer.from(pixelData),
    info: { width, height, channels }
  };
}

/**
 * 5x5 高斯边缘平滑算法（质量更好）
 *
 * @param {Uint8ClampedArray} pixelData - 像素数据
 * @param {number} width - 图像宽度
 * @param {number} height - 图像高度
 * @param {number} channels - 通道数
 * @param {number} iterations - 迭代次数
 * @returns {Uint8ClampedArray} 平滑后的像素数据
 */
function smoothEdgesGaussian(pixelData, width, height, channels, iterations = 1) {
  let data = new Uint8ClampedArray(pixelData);

  // 5x5 高斯核权重（近似二维高斯分布）
  const kernel = [
    [1,  4,  7,  4,  1],
    [4, 16, 26, 16,  4],
    [7, 26, 41, 26,  7],
    [4, 16, 26, 16,  4],
    [1,  4,  7,  4,  1]
  ];
  const kernelSum = 273;

  // 迭代平滑
  for (let iter = 0; iter < iterations; iter++) {
    const smoothed = new Uint8ClampedArray(data);

    for (let y = 2; y < height - 2; y++) {
      for (let x = 2; x < width - 2; x++) {
        const idx = (y * width + x) * channels + 3;
        const alpha = data[idx];

        // 只处理半透明像素（边缘区域）
        if (alpha > 0 && alpha < 255) {
          let sum = 0;
          for (let ky = -2; ky <= 2; ky++) {
            for (let kx = -2; kx <= 2; kx++) {
              const nidx = ((y + ky) * width + (x + kx)) * channels + 3;
              sum += data[nidx] * kernel[ky + 2][kx + 2];
            }
          }
          smoothed[idx] = Math.min(255, Math.max(0, Math.floor(sum / kernelSum)));
        }
      }
    }
    data = smoothed;
  }

  return data;
}

/**
 * 简单边缘平滑算法（3x3 平均，更快）
 *
 * @param {Uint8ClampedArray} pixelData - 像素数据
 * @param {number} width - 图像宽度
 * @param {number} height - 图像高度
 * @param {number} channels - 通道数
 * @returns {Uint8ClampedArray} 平滑后的像素数据
 */
function smoothEdgesSimple(pixelData, width, height, channels) {
  const smoothed = new Uint8ClampedArray(pixelData);

  // 边缘羽化处理（3x3 卷积核）
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = (y * width + x) * channels + 3;
      const alpha = pixelData[idx];

      // 只处理半透明像素（边缘区域）
      if (alpha > 0 && alpha < 255) {
        // 计算周围 3x3 区域的平均 alpha
        let sum = 0, count = 0;
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            const nidx = ((y + dy) * width + (x + dx)) * channels + 3;
            sum += pixelData[nidx];
            count++;
          }
        }
        smoothed[idx] = Math.floor(sum / count);
      }
    }
  }

  return smoothed;
}

/**
 * 移除白色背景并输出到文件
 *
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputPath - 输出文件路径
 * @param {object} options - 配置选项
 * @returns {Promise<{success: boolean, outputPath: string}>}
 */
async function removeWhiteBackgroundToFile(inputPath, outputPath, options = {}) {
  try {
    const result = await removeWhiteBackground(inputPath, options);

    await sharp(result.data, {
      raw: {
        width: result.info.width,
        height: result.info.height,
        channels: result.info.channels
      }
    })
    .png()  // 输出为 PNG 以保留透明度
    .toFile(outputPath);

    return { success: true, outputPath };
  } catch (error) {
    throw new Error(`Background removal failed: ${error.message}`);
  }
}

module.exports = {
  removeWhiteBackground,
  removeWhiteBackgroundFromBuffer,
  removeWhiteBackgroundToFile
};
