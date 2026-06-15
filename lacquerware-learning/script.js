// 中国漆器探索之旅 - 交互脚本

// 导航功能
function navigateTo(sectionId) {
    // 隐藏所有 section
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // 显示目标 section
    document.getElementById(sectionId).classList.add('active');
    
    // 滚动到顶部
    window.scrollTo(0, 0);
    
    // 初始化对应页面的功能
    if (sectionId === 'make') {
        initMakeGame();
    } else if (sectionId === 'create') {
        initDesignCanvas();
    }
}

// 历史时间轴交互
const historyData = {
    1: {
        title: '🌱 新石器时代 - 河姆渡朱漆碗',
        image: '', // 可以添加图片 URL
        desc: '距今约 7000 年，浙江河姆渡遗址出土了最早的漆器——朱漆碗。这件碗虽然简单，但证明我们的祖先已经掌握了采漆和制漆的技术。碗的内外都涂有朱红色的漆，即使在地下埋藏了几千年，依然保持着光泽。'
    },
    2: {
        title: '🏛️ 商周时期 - 礼器出现',
        image: '',
        desc: '商周时期（约公元前 1600-前 256 年），漆器开始被用作重要的礼器。这个时期的漆器多为黑色或红色，上面绘制着精美的纹样。漆器成为贵族身份的象征，常用于祭祀和重要场合。'
    },
    3: {
        title: '🎭 战国汉代 - 繁荣发展',
        image: '',
        desc: '战国到汉代（公元前 475 年 - 公元 220 年）是漆器发展的黄金时期。漆器种类繁多，有饮食器、家具、乐器等。工艺也更加精湛，出现了彩绘、镶嵌、雕刻等装饰技法。马王堆汉墓出土的漆器就是这一时期的代表作。'
    },
    4: {
        title: '🌸 唐宋元明 - 技艺巅峰',
        image: '',
        desc: '唐宋元明时期（公元 618-1644 年），漆器工艺达到了巅峰。唐代创造了"金银平脱"技法，宋代发展了"剔红"工艺，元代出现了"螺钿镶嵌"，明代则有著名的"果园厂"漆器。这个时期的漆器不仅在国内流行，还远销海外。'
    },
    5: {
        title: '🏮 清代至今 - 传承创新',
        image: '',
        desc: '清代（1644-1912 年）漆器工艺继续发展，出现了许多地方特色漆器，如北京雕漆、扬州螺钿、福州脱胎漆器等。现代漆艺家在传承传统技艺的同时，也在不断创新，让古老的漆器艺术焕发新的生机。'
    }
};

// 点击时间轴项目
document.querySelectorAll('.timeline-item').forEach(item => {
    item.addEventListener('click', function() {
        const period = this.getAttribute('data-period');
        const data = historyData[period];
        
        document.getElementById('detail-title').textContent = data.title;
        document.getElementById('detail-desc').textContent = data.desc;
        
        // 如果有图片
        if (data.image) {
            document.getElementById('detail-image').src = data.image;
            document.getElementById('detail-image').style.display = 'block';
        } else {
            document.getElementById('detail-image').style.display = 'none';
        }
        
        document.getElementById('history-detail').classList.add('active');
    });
});

// 工艺卡片详情
const craftData = {
    1: {
        title: '🌳 天然漆 - 大自然的馈赠',
        content: `
            <h3>什么是天然漆？</h3>
            <p>天然漆是从漆树上采集的汁液，被称为"液体黄金"。漆树主要生长在中国南方，如陕西、湖北、四川等地。</p>
            <h4>采漆过程：</h4>
            <ul>
                <li>在漆树上割开 V 形切口</li>
                <li>用容器收集流出的乳白色汁液</li>
                <li>一棵漆树每年只能采集约 250 克漆</li>
                <li>所以漆非常珍贵！</li>
            </ul>
            <h4>漆的特性：</h4>
            <ul>
                <li>接触空气后慢慢变黑</li>
                <li>干燥后坚硬耐用</li>
                <li>防腐、防潮、耐高温</li>
                <li>越用越亮，可以保存几千年</li>
            </ul>
        `
    },
    2: {
        title: '🪵 制胎 - 器物的基础',
        content: `
            <h3>什么是胎体？</h3>
            <p>胎体是漆器的"骨架"，漆要涂在胎体上。常见的胎体材料有：</p>
            <h4>木胎：</h4>
            <p>最常见，用木头雕刻或旋制成型。需要选择不易变形的木材，如榉木、楠木等。</p>
            <h4>竹胎：</h4>
            <p>用竹篾编织成型，轻巧坚固。多用于制作篮子、盒子等。</p>
            <h4>铜胎：</h4>
            <p>用铜铸造或锻造，更加坚固耐用。多用于制作高档漆器。</p>
            <h4>其他胎体：</h4>
            <p>还有陶胎、皮胎、纸胎、脱胎（用麻布和漆灰制成）等。</p>
        `
    },
    3: {
        title: '🖌️ 髹漆 - 层层涂刷的艺术',
        content: `
            <h3>髹（xiū）漆是什么？</h3>
            <p>"髹"就是用刷子涂漆的意思。这是漆器制作中最关键、最耗时的步骤。</p>
            <h4>髹漆过程：</h4>
            <ul>
                <li>用特制的漆刷均匀涂刷</li>
                <li>每层漆厚度约 0.1 毫米</li>
                <li>涂完一层后要放在阴湿的地方晾干（称为"阴干"）</li>
                <li>干透后再涂下一层</li>
                <li>重复几十次甚至上百次！</li>
            </ul>
            <h4>为什么需要这么多层？</h4>
            <p>多层涂刷可以让漆器更加坚固耐用，表面更加光滑平整。一件精美的漆器可能需要几个月的时间来完成髹漆！</p>
        `
    },
    4: {
        title: '✨ 装饰 - 锦上添花',
        content: `
            <h3>漆器的装饰技法</h3>
            <p>漆器做好后，工匠们会用各种方法装饰它，让它更加美丽：</p>
            <h4>彩绘：</h4>
            <p>用彩色漆在器物上绘画，绘制花鸟、人物、山水等图案。</p>
            <h4>描金：</h4>
            <p>用金粉或金箔在漆面上描绘纹样，金光闪闪，非常华丽。</p>
            <h4>雕刻：</h4>
            <p>在厚厚的漆层上雕刻花纹，如著名的"剔红"就是在红色漆层上雕刻。</p>
            <h4>镶嵌：</h4>
            <p>把贝壳、玉石、金银片等材料嵌入漆面，称为"螺钿"或"百宝嵌"。</p>
        `
    },
    5: {
        title: '💎 打磨 - 最后的点睛',
        content: `
            <h3>打磨的重要性</h3>
            <p>打磨是漆器制作的最后一道工序，也是让漆器发光发亮的关键！</p>
            <h4>打磨过程：</h4>
            <ul>
                <li>用不同粗细的磨石或砂纸</li>
                <li>从粗到细慢慢打磨</li>
                <li>最后用头发、木炭粉等抛光</li>
                <li>需要极大的耐心和技巧</li>
            </ul>
            <h4>打磨的效果：</h4>
            <ul>
                <li>表面更加光滑平整</li>
                <li>漆层的光泽显现出来</li>
                <li>摸起来温润如玉</li>
                <li>越用越亮，历久弥新</li>
            </ul>
            <p>经过精心打磨的漆器，会散发出温润内敛的光泽，这就是漆器独特的魅力！</p>
        `
    }
};

function showCraftDetail(id) {
    const data = craftData[id];
    document.getElementById('craft-detail-content').innerHTML = `
        <h2 style="color: #DAA520; margin-bottom: 20px;">${data.title}</h2>
        ${data.content}
    `;
    document.getElementById('craft-modal').classList.add('active');
}

function closeCraftModal() {
    document.getElementById('craft-modal').classList.remove('active');
}

// 测试题
function checkAnswer(option) {
    const feedback = document.getElementById('quiz-feedback');
    
    if (option === 3) {
        feedback.className = 'quiz-feedback correct';
        feedback.innerHTML = '✅ 正确！一件精美的漆器需要涂刷几十层甚至上百层漆，每层都要阴干，所以需要很长时间。这就是漆器珍贵的原因之一！';
    } else {
        feedback.className = 'quiz-feedback wrong';
        feedback.innerHTML = '❌ 不太对哦。漆器需要涂刷很多层漆，每层都很薄，要涂几十层甚至上百层才能达到理想的效果。再试一次吧！';
    }
}

// 制作游戏状态
let makeState = {
    currentStep: 1,
    shape: '',
    material: '',
    layers: 0,
    decoration: '',
    polishProgress: 0
};

function initMakeGame() {
    makeState = {
        currentStep: 1,
        shape: '',
        material: '',
        layers: 0,
        decoration: '',
        polishProgress: 0
    };
    
    updateStepIndicator();
    showMakeStep(1);
}

function updateStepIndicator() {
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index + 1 <= makeState.currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function showMakeStep(step) {
    document.querySelectorAll('.make-step').forEach(s => {
        s.classList.remove('active');
    });
    document.querySelector(`.make-step[data-step="${step}"]`).classList.add('active');
    updateStepIndicator();
}

function selectShape(shape) {
    makeState.shape = shape;
    document.querySelectorAll('.shape-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.closest('.shape-option').classList.add('selected');
    
    // 更新后续步骤中的器物显示
    updatePaintObject();
    
    setTimeout(() => {
        nextMakeStep();
    }, 500);
}

function selectMaterial(material) {
    makeState.material = material;
    document.querySelectorAll('.material-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.closest('.material-option').classList.add('selected');
    
    setTimeout(() => {
        nextMakeStep();
    }, 500);
}

function updatePaintObject() {
    const paintObj = document.getElementById('paint-object');
    const polishObj = document.getElementById('polish-object');
    
    // 根据选择的器型设置形状
    if (makeState.shape === 'bowl') {
        paintObj.style.borderRadius = '50% 50% 40% 40%';
        polishObj.style.borderRadius = '50% 50% 40% 40%';
    } else if (makeState.shape === 'box') {
        paintObj.style.borderRadius = '10px';
        polishObj.style.borderRadius = '10px';
    } else if (makeState.shape === 'vase') {
        paintObj.style.borderRadius = '40% 40% 50% 50%';
        polishObj.style.borderRadius = '40% 40% 50% 50%';
    }
}

// 涂漆交互
let paintClickCount = 0;
document.getElementById('paint-object')?.addEventListener('click', function() {
    paintClickCount++;
    makeState.layers++;
    document.getElementById('layer-count').textContent = makeState.layers;
    
    // 增加光泽效果
    const brightness = 100 + Math.min(paintClickCount * 5, 50);
    this.style.filter = `brightness(${brightness}%)`;
    this.style.boxShadow = `0 10px ${40 + paintClickCount * 2}px rgba(218, 165, 32, ${0.3 + paintClickCount * 0.02})`;
});

function selectDecoration(decoration) {
    makeState.decoration = decoration;
    document.querySelectorAll('.decoration-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.closest('.decoration-option').classList.add('selected');
    
    setTimeout(() => {
        nextMakeStep();
    }, 500);
}

// 打磨交互
let polishClickCount = 0;
document.getElementById('polish-object')?.addEventListener('mousemove', function(e) {
    if (polishClickCount < 100) {
        polishClickCount++;
        makeState.polishProgress = Math.min(polynomialClickCount, 100);
        
        const progress = Math.min(polynomialClickCount, 100);
        document.getElementById('polish-progress').style.width = progress + '%';
        document.getElementById('polish-percent').textContent = progress;
        
        // 增加光泽
        const brightness = 100 + progress * 0.8;
        this.style.filter = `brightness(${brightness}%)`;
        this.style.boxShadow = `0 15px ${60 + progress * 0.5}px rgba(218, 165, 32, ${0.5 + progress * 0.005})`;
    }
    
    // 防止计数过快
    if (polishClickCount % 5 === 0) {
        polishClickCount--;
    }
});

// 修正打磨计数
polynomialClickCount = 0;
document.getElementById('polish-object')?.addEventListener('mouseenter', function() {
    this.isPolishing = true;
});

document.getElementById('polish-object')?.addEventListener('mouseleave', function() {
    this.isPolishing = false;
});

// 重新设置打磨交互
function setupPolishInteraction() {
    const polishObj = document.getElementById('polish-object');
    if (!polishObj) return;
    
    let lastPolishTime = 0;
    
    polishObj.addEventListener('mousemove', function(e) {
        const now = Date.now();
        if (now - lastPolishTime < 100) return; // 限制频率
        lastPolishTime = now;
        
        if (polishClickCount < 100) {
            polishClickCount++;
            const progress = polishClickCount;
            
            document.getElementById('polish-progress').style.width = progress + '%';
            document.getElementById('polish-percent').textContent = progress;
            
            const brightness = 100 + progress * 0.8;
            this.style.filter = `brightness(${brightness}%)`;
            this.style.boxShadow = `0 15px ${60 + progress * 0.5}px rgba(218, 165, 32, ${0.5 + progress * 0.005})`;
            
            if (progress >= 100) {
                setTimeout(() => {
                    nextMakeStep();
                }, 1000);
            }
        }
    });
}

function nextMakeStep() {
    makeState.currentStep++;
    if (makeState.currentStep <= 6) {
        showMakeStep(makeState.currentStep);
        
        if (makeState.currentStep === 3) {
            paintClickCount = 0;
            makeState.layers = 0;
            document.getElementById('layer-count').textContent = '0';
            document.getElementById('paint-object').style.filter = 'brightness(100%)';
            updatePaintObject();
        } else if (makeState.currentStep === 5) {
            polishClickCount = 0;
            makeState.polishProgress = 0;
            document.getElementById('polish-progress').style.width = '0%';
            document.getElementById('polish-percent').textContent = '0';
            document.getElementById('polish-object').style.filter = 'brightness(100%)';
            setupPolishInteraction();
        } else if (makeState.currentStep === 6) {
            showFinishedProduct();
        }
    }
}

function showFinishedProduct() {
    const shapeNames = { 'bowl': '碗', 'box': '盒', 'vase': '瓶' };
    const materialNames = { 'wood': '木胎', 'bamboo': '竹胎', 'copper': '铜胎' };
    const decorationNames = { 'none': '素面', 'gold': '描金', 'carve': '雕刻', 'inlay': '镶嵌' };
    
    document.getElementById('final-shape').textContent = shapeNames[makeState.shape] || makeState.shape;
    document.getElementById('final-material').textContent = materialNames[makeState.material] || makeState.material;
    document.getElementById('final-decoration').textContent = decorationNames[makeState.decoration] || makeState.decoration;
    document.getElementById('final-layers').textContent = makeState.layers;
    
    const finishedProduct = document.getElementById('finished-product');
    finishedProduct.style.borderRadius = makeState.shape === 'bowl' ? '50% 50% 40% 40%' : 
                                          makeState.shape === 'vase' ? '40% 40% 50% 50%' : '15px';
    
    // 根据装饰添加效果
    if (makeState.decoration === 'gold') {
        finishedProduct.style.border = '5px solid #DAA520';
        finishedProduct.style.background = 'linear-gradient(135deg, #8B0000, #2d0000), linear-gradient(45deg, transparent 40%, rgba(218, 165, 32, 0.5) 50%, transparent 60%)';
    } else {
        finishedProduct.style.border = '5px solid #DAA520';
    }
}

function saveProduct() {
    const product = {
        shape: makeState.shape,
        material: makeState.material,
        decoration: makeState.decoration,
        layers: makeState.layers,
        date: new Date().toLocaleString()
    };
    
    // 保存到 localStorage
    let products = JSON.parse(localStorage.getItem('lacquerProducts') || '[]');
    products.push(product);
    localStorage.setItem('lacquerProducts', JSON.stringify(products));
    
    alert('🎉 作品已保存！你可以在创意工坊查看。');
}

// 艺术品详情
const artworkData = {
    1: {
        title: '战国·彩绘漆瑟',
        description: '这是战国时期的漆器乐器，表面绘有精美的龙凤纹样和云气纹。瑟是古代的一种弦乐器，这件漆瑟不仅具有实用价值，更是一件艺术品。彩绘图案历经两千多年依然清晰可见，展现了古代工匠高超的技艺。',
        features: ['彩绘工艺', '龙凤纹样', '乐器功能', '保存完好']
    },
    2: {
        title: '汉代·云气纹漆盒',
        description: '汉代漆盒，盒盖上绘制着流动的云气纹，象征着仙境和长寿。汉代漆器以黑、红两色为主，这件漆盒是典型代表。云气纹线条流畅，富有动感，体现了汉代人对神仙世界的向往。',
        features: ['云气纹装饰', '黑红配色', '实用器皿', '汉代风格']
    },
    3: {
        title: '唐代·金银平脱漆镜',
        description: '唐代独创的"金银平脱"工艺代表作。将金银薄片剪成花纹，贴在漆器表面，然后上漆打磨，使金银花纹与漆面平齐。这件漆镜背面装饰着精美的金银花纹，华丽非凡，体现了唐代的富丽堂皇。',
        features: ['金银平脱', '创新工艺', '唐代风格', '奢华精美']
    },
    4: {
        title: '明代·剔红牡丹纹盒',
        description: '"剔红"是明代著名的漆器工艺，在器物上涂几十层红漆，然后雕刻花纹。这件漆盒上雕刻着盛开的牡丹花，层次分明，立体感强。牡丹象征富贵，整件作品既实用又美观，是明代漆器的精品。',
        features: ['剔红工艺', '牡丹纹样', '立体雕刻', '明代精品']
    }
};

function showArtwork(id) {
    const data = artworkData[id];
    document.getElementById('artwork-detail').innerHTML = `
        <h2 style="color: #DAA520; margin-bottom: 20px; font-size: 1.8em;">${data.title}</h2>
        <p style="font-size: 1.1em; line-height: 1.8; margin-bottom: 20px;">${data.description}</p>
        <h3 style="color: #DAA520; margin-bottom: 10px;">特点：</h3>
        <ul style="text-align: left; line-height: 2;">
            ${data.features.map(f => `<li>✨ ${f}</li>`).join('')}
        </ul>
    `;
    document.getElementById('artwork-modal').classList.add('active');
}

function closeArtworkModal() {
    document.getElementById('artwork-modal').classList.remove('active');
}

function submitLike() {
    const message = document.getElementById('like-message').value;
    if (message.trim()) {
        alert('💭 感谢你的分享！你的留言已提交。');
        document.getElementById('like-message').value = '';
    } else {
        alert('请先写下你的想法哦！');
    }
}

// 创意工坊画布
let canvas, ctx;
let isDrawing = false;
let currentTool = 'brush';
let currentColor = '#8B0000';

function initDesignCanvas() {
    canvas = document.getElementById('design-canvas-element');
    if (!canvas) return;
    
    canvas.style.display = 'block';
    document.querySelector('.canvas-placeholder').style.display = 'none';
    
    // 设置画布大小
    const container = document.getElementById('design-canvas');
    canvas.width = container.clientWidth - 40;
    canvas.height = 400;
    
    ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绑定绘画事件
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // 触摸支持
    canvas.addEventListener('touchstart', handleTouchStart);
    canvas.addEventListener('touchmove', handleTouchMove);
    canvas.addEventListener('touchend', stopDrawing);
}

function startDrawing(e) {
    isDrawing = true;
    draw(e);
}

function draw(e) {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    ctx.lineWidth = currentTool === 'brush' ? 3 : 20;
    ctx.lineCap = 'round';
    ctx.strokeStyle = currentTool === 'brush' ? currentColor : '#ffffff';
    
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function stopDrawing() {
    isDrawing = false;
    ctx.beginPath();
}

function handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

function handleTouchMove(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

function setTool(tool) {
    currentTool = tool;
}

function clearCanvas() {
    if (confirm('确定要清空画布吗？')) {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
}

function selectColor(color) {
    currentColor = color;
    document.getElementById('brush-color').value = color;
    
    document.querySelectorAll('.color-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.classList.add('selected');
}

function selectPattern(pattern) {
    document.querySelectorAll('.pattern-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.classList.add('selected');
}

function submitDesign() {
    const shape = document.getElementById('design-shape').value;
    const desc = document.getElementById('design-desc').value;
    
    if (!desc.trim()) {
        alert('请写下你的设计说明哦！');
        return;
    }
    
    // 保存设计
    const design = {
        shape: shape,
        color: currentColor,
        description: desc,
        date: new Date().toLocaleString(),
        canvasData: canvas.toDataURL()
    };
    
    let designs = JSON.parse(localStorage.getItem('lacquerDesigns') || '[]');
    designs.push(design);
    localStorage.setItem('lacquerDesigns', JSON.stringify(designs));
    
    alert('🎨 你的设计已提交！太棒了！');
    
    // 导航到完成页
    setTimeout(() => {
        navigateTo('complete');
    }, 1000);
}

// 颜色选择器同步
document.getElementById('brush-color')?.addEventListener('change', function() {
    currentColor = this.value;
});

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('中国漆器探索之旅已加载！');
});
