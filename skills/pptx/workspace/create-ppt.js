const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/chunjun/.claude/skills/pptx/scripts/html2pptx.js');

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Claude Code';
  pptx.title = '5-Layer AI Architecture Framework';

  // Create slide from HTML
  await html2pptx('workspace/framework-slide.html', pptx);

  // Save
  await pptx.writeFile({ fileName: 'workspace/ai-framework.pptx' });
  console.log('Presentation created: workspace/ai-framework.pptx');
}

createPresentation().catch(console.error);
