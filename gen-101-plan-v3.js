const pptxgenjs = require('pptxgenjs');

const pres = new pptxgenjs();
pres.defineLayout({ name: 'LAYOUT_16_9', width: 13.33, height: 7.5 });
pres.layout = 'LAYOUT_16_9';

const C = {
  primary: '#1A365D', secondary: '#2B6CB0', accent: '#E8832A',
  light: '#F7F9FC', white: '#FFFFFF', text: '#2D3748',
  muted: '#718096', success: '#38A169', teal: '#319795'
};

// Slide 1: Cover
const s1 = pres.addSlide();
s1.background = { fill: C.primary };
s1.addShape('rect', { x: 0, y: 0, w: '100%', h: 0.12, fill: C.accent });
s1.addText('\u6559\u80b2\u90e8\u201c101\u8ba1\u5212\u201d\u9996\u6279\u6838\u5fc3\u8bfe\u7a0b\u57f9\u80b2\u63a8\u8fdb\u4f1a', {
  x: 1, y: 1.2, w: 11.33, h: 1, fontSize: 34, fontFace: '\u5fae\u8f6f\u96c5\u9ed1',
  color: C.white, bold: true, align: 'center'
});
s1.addText('\u8ba1\u7b97\u673a\u7f51\u7edc\u8bfe\u7a0b\u5efa\u8bbe\u6784\u60f3', {
  x: 1, y: 2.5, w: 11.33, h: 0.7, fontSize: 26, fontFace: '\u5fae\u8f6f\u96c5\u9ed1',
  color: C.accent, bold: true, align: 'center'
});
s1.addText('\u6d59\u6c5f\u5de5\u5546\u5927\u5b66 \u00b7 \u8bf8\u845b\u658c\u56e2\u961f\n2026\u5e746\u670825\u65e5 | \u79d1\u521b\u5927\u697c206', {
  x: 1, y: 5.5, w: 11.33, h: 0.8, fontSize: 15, fontFace: '\u5fae\u8f6f\u96c5\u9ed1',
  color: '#A0AEC0', align: 'center'
});

// Export
pres.writeFile({ outputFileName: '/home/admin/.openclaw/workspace/101-network-course-v2.pptx' })
  .then(() => console.log('SUCCESS'))
  .catch(err => console.error('ERROR:', err));
setTimeout(() => {}, 5000);
