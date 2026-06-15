// ==UserScript==
// @name         大麦抢票助手
// @namespace    http://openclaw.ai/
// @version      1.0
// @description  大麦网抢票辅助工具：自动刷新、自动填信息、快速下单
// @match        https://detail.damai.cn/item?*
// @match        https://m.damai.cn/item?*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_notification
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 配置区 ====================
    const CONFIG = {
        // 自动刷新间隔（毫秒），默认 2 秒
        refreshInterval: GM_getValue('refreshInterval', 2000),
        // 最大刷新间隔（毫秒）
        maxRefreshInterval: 3000,
        // 是否启用自动刷新
        autoRefresh: GM_getValue('autoRefresh', false),
        // 观演人信息（提前填好，逗号分隔）
        buyers: GM_getValue('buyers', ''),
        // 是否自动勾选观演人
        autoSelectBuyer: GM_getValue('autoSelectBuyer', false),
        // 是否自动点击购买
        autoBuy: GM_getValue('autoBuy', false),
        // 通知声音
        notifySound: true,
        // 默认选择的票档（留空则选第一个有票的）
        defaultTicket: GM_getValue('defaultTicket', ''),
    };

    // ==================== 样式 ====================
    GM_addStyle(`
        #damai-helper-panel {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 999999;
            background: #fff;
            border: 2px solid #ff4400;
            border-radius: 12px;
            padding: 16px;
            width: 260px;
            box-shadow: 0 4px 20px rgba(255,68,0,0.3);
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        #damai-helper-panel .dh-title {
            font-size: 15px;
            font-weight: bold;
            color: #ff4400;
            margin-bottom: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }
        #damai-helper-panel .dh-row {
            display: flex;
            align-items: center;
            margin: 8px 0;
            gap: 8px;
        }
        #damai-helper-panel .dh-label {
            min-width: 70px;
            color: #666;
            font-size: 12px;
        }
        #damai-helper-panel .dh-input {
            flex: 1;
            padding: 6px 8px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 12px;
            outline: none;
        }
        #damai-helper-panel .dh-input:focus {
            border-color: #ff4400;
        }
        #damai-helper-panel .dh-btn {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 8px;
            transition: all 0.2s;
        }
        #damai-helper-panel .dh-btn-primary {
            background: linear-gradient(135deg, #ff4400, #ff6633);
            color: #fff;
        }
        #damai-helper-panel .dh-btn-primary:hover {
            background: linear-gradient(135deg, #e63e00, #ff5522);
            transform: scale(1.02);
        }
        #damai-helper-panel .dh-btn-danger {
            background: linear-gradient(135deg, #333, #555);
            color: #fff;
        }
        #damai-helper-panel .dh-toggle {
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 6px 0;
            font-size: 12px;
            color: #666;
        }
        #damai-helper-panel .dh-toggle input[type="checkbox"] {
            accent-color: #ff4400;
            width: 16px;
            height: 16px;
        }
        #damai-helper-panel .dh-status {
            text-align: center;
            padding: 6px;
            border-radius: 6px;
            font-size: 12px;
            margin-top: 8px;
        }
        #damai-helper-panel .dh-status.waiting {
            background: #fff3e0;
            color: #ff6600;
        }
        #damai-helper-panel .dh-status.ready {
            background: #e8f5e9;
            color: #4caf50;
        }
        #damai-helper-panel .dh-status.success {
            background: #ff4400;
            color: #fff;
            animation: dh-pulse 0.5s infinite alternate;
        }
        #damai-helper-panel .dh-minimize {
            position: absolute;
            top: 8px;
            right: 12px;
            cursor: pointer;
            font-size: 16px;
            color: #999;
        }
        #damai-helper-panel .dh-minimize:hover {
            color: #ff4400;
        }
        #damai-helper-panel .dh-section {
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px dashed #eee;
        }
        #damai-helper-panel .dh-section-title {
            font-size: 11px;
            color: #999;
            margin-bottom: 6px;
        }
        @keyframes dh-pulse {
            from { opacity: 1; }
            to { opacity: 0.7; }
        }
        .dh-flash {
            animation: dh-flash-anim 0.3s ease-in-out 3;
        }
        @keyframes dh-flash-anim {
            0%, 100% { background-color: transparent; }
            50% { background-color: #ff4400; }
        }
    `);

    // ==================== 面板 UI ====================
    function createPanel() {
        const panel = document.createElement('div');
        panel.id = 'damai-helper-panel';
        panel.innerHTML = `
            <span class="dh-minimize" id="dh-min-btn">−</span>
            <div class="dh-title">🦞 大麦抢票助手</div>

            <div class="dh-section">
                <div class="dh-section-title">📋 观演人信息</div>
                <div class="dh-row">
                    <span class="dh-label">姓名</span>
                    <input class="dh-input" id="dh-name" placeholder="真实姓名" value="${GM_getValue('buyerName', '')}">
                </div>
                <div class="dh-row">
                    <span class="dh-label">身份证</span>
                    <input class="dh-input" id="dh-idcard" placeholder="身份证号" value="${GM_getValue('buyerIdCard', '')}">
                </div>
                <div class="dh-row">
                    <span class="dh-label">手机号</span>
                    <input class="dh-input" id="dh-phone" placeholder="手机号" value="${GM_getValue('buyerPhone', '')}">
                </div>
            </div>

            <div class="dh-section">
                <div class="dh-section-title">⚙️ 抢票设置</div>
                <div class="dh-row">
                    <span class="dh-label">刷新间隔</span>
                    <input class="dh-input" id="dh-interval" type="number" value="${CONFIG.refreshInterval}" min="500" max="5000" step="500">
                    <span style="font-size:11px;color:#999">ms</span>
                </div>
                <label class="dh-toggle">
                    <input type="checkbox" id="dh-auto-buyer" ${CONFIG.autoSelectBuyer ? 'checked' : ''}>
                    自动勾选观演人
                </label>
                <label class="dh-toggle">
                    <input type="checkbox" id="dh-auto-buy" ${CONFIG.autoBuy ? 'checked' : ''}>
                    ⚠️ 自动点击购买（谨慎开启）
                </label>
            </div>

            <div class="dh-section">
                <button class="dh-btn dh-btn-primary" id="dh-start-btn">🚀 开始监控</button>
                <button class="dh-btn dh-btn-danger" id="dh-stop-btn" style="display:none">⏹️ 停止监控</button>
                <div class="dh-status waiting" id="dh-status">⏸️ 未启动</div>
            </div>
        `;
        document.body.appendChild(panel);

        // 保存配置
        function saveConfig() {
            GM_setValue('buyerName', document.getElementById('dh-name').value);
            GM_setValue('buyerIdCard', document.getElementById('dh-idcard').value);
            GM_setValue('buyerPhone', document.getElementById('dh-phone').value);
            CONFIG.refreshInterval = parseInt(document.getElementById('dh-interval').value) || 2000;
            GM_setValue('refreshInterval', CONFIG.refreshInterval);
            CONFIG.autoSelectBuyer = document.getElementById('dh-auto-buyer').checked;
            GM_setValue('autoSelectBuyer', CONFIG.autoSelectBuyer);
            CONFIG.autoBuy = document.getElementById('dh-auto-buy').checked;
            GM_setValue('autoBuy', CONFIG.autoBuy);
        }

        // 开始监控
        document.getElementById('dh-start-btn').addEventListener('click', function() {
            saveConfig();
            startMonitoring();
        });

        // 停止监控
        document.getElementById('dh-stop-btn').addEventListener('click', function() {
            stopMonitoring();
        });

        // 最小化
        document.getElementById('dh-min-btn').addEventListener('click', function() {
            const content = panel.querySelectorAll('.dh-title, .dh-section, .dh-status, #dh-min-btn');
            const isHidden = panel.dataset.minimized === 'true';
            content.forEach(el => el.style.display = isHidden ? '' : 'none');
            panel.dataset.minimized = isHidden ? 'false' : 'true';
            document.getElementById('dh-min-btn').textContent = isHidden ? '−' : '+';
        });

        // 拖拽
        let isDragging = false, offsetX, offsetY;
        panel.addEventListener('mousedown', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'LABEL') return;
            isDragging = true;
            offsetX = e.clientX - panel.offsetLeft;
            offsetY = e.clientY - panel.offsetTop;
        });
        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            panel.style.left = (e.clientX - offsetX) + 'px';
            panel.style.top = (e.clientY - offsetY) + 'px';
            panel.style.right = 'auto';
        });
        document.addEventListener('mouseup', function() {
            isDragging = false;
        });
    }

    // ==================== 核心逻辑 ====================
    let monitorTimer = null;
    let refreshCount = 0;

    function startMonitoring() {
        document.getElementById('dh-start-btn').style.display = 'none';
        document.getElementById('dh-stop-btn').style.display = '';
        updateStatus('running', '🔄 监控中... 刷新: 0 次');

        monitorTimer = setInterval(() => {
            refreshCount++;
            updateStatus('running', `🔄 监控中... 刷新: ${refreshCount} 次`);

            checkAndBuy();
        }, CONFIG.refreshInterval);
    }

    function stopMonitoring() {
        if (monitorTimer) {
            clearInterval(monitorTimer);
            monitorTimer = null;
        }
        document.getElementById('dh-start-btn').style.display = '';
        document.getElementById('dh-stop-btn').style.display = 'none';
        updateStatus('waiting', `⏸️ 已停止（共刷新 ${refreshCount} 次）`);
        refreshCount = 0;
    }

    function updateStatus(type, text) {
        const el = document.getElementById('dh-status');
        el.className = 'dh-status ' + type;
        el.textContent = text;
    }

    function checkAndBuy() {
        // 1. 尝试选择票档
        selectTicket();

        // 2. 尝试选择观演人
        if (CONFIG.autoSelectBuyer) {
            selectBuyer();
        }

        // 3. 尝试点击购买按钮
        if (CONFIG.autoBuy) {
            tryAutoBuy();
        }
    }

    // 选择票档
    function selectTicket() {
        // 大麦的票档按钮选择器（可能需要根据实际页面调整）
        const ticketBtns = document.querySelectorAll(
            '.dm-item-selector__item, ' +
            '.sale-btn-block .sale-btn, ' +
            '.perform-project-schedule .sale-btn, ' +
            '[class*="ticket"] [class*="btn"], ' +
            '.perform-buy__bottom .buy-btn-wrapper .buy-btn'
        );

        for (const btn of ticketBtns) {
            // 跳过已售罄的
            if (btn.textContent.includes('已售罄') || btn.textContent.includes('缺货') ||
                btn.classList.contains('disabled') || btn.classList.contains('unsale')) {
                continue;
            }

            // 点击可选的票档
            if (btn.offsetParent !== null && btn.textContent.trim()) {
                if (!btn.classList.contains('active') && !btn.classList.contains('selected')) {
                    btn.click();
                    console.log('[抢票助手] 已选择票档:', btn.textContent.trim());
                    return;
                }
            }
        }
    }

    // 选择观演人
    function selectBuyer() {
        const buyerCheckbox = document.querySelectorAll(
            '.dm-checkbox__input, ' +
            '.perform-buy__person .dm-checkbox-wrapper, ' +
            '[class*="buyer"] [class*="check"], ' +
            '.buyer-list .buyer-item'
        );

        const name = document.getElementById('dh-name').value;
        for (const cb of buyerCheckbox) {
            if (name && cb.textContent.includes(name)) {
                if (!cb.classList.contains('dm-checkbox__input--checked')) {
                    cb.click();
                    console.log('[抢票助手] 已勾选观演人:', name);
                }
                return;
            }
        }

        // 如果没找到匹配的，勾选第一个可用的
        for (const cb of buyerCheckbox) {
            if (!cb.classList.contains('dm-checkbox__input--checked') && cb.offsetParent !== null) {
                cb.click();
                console.log('[抢票助手] 已勾选第一个观演人');
                return;
            }
        }
    }

    // 自动点击购买
    function tryAutoBuy() {
        const buyBtn = document.querySelector(
            '.buy-btn, ' +
            '.perform-buy__bottom .buy-btn, ' +
            '.buy-btn-wrapper .buy-btn, ' +
            '[class*="buy"][class*="btn"]'
        );

        if (buyBtn && buyBtn.offsetParent !== null && !buyBtn.disabled) {
            const btnText = buyBtn.textContent.trim();
            if (!btnText.includes('缺货') && !btnText.includes('售罄') &&
                !btnText.includes('即将开抢') && !btnText.includes('不可')) {
                buyBtn.click();
                console.log('[抢票助手] 🎉 已点击购买按钮！');
                updateStatus('success', '🎉 已点击购买！请确认支付！');
                playNotificationSound();
                showNotification('大麦抢票助手', '票已抢到！请确认支付！');
                stopMonitoring();
            }
        }
    }

    // 通知声音
    function playNotificationSound() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.3;

        oscillator.start();
        setTimeout(() => oscillator.stop(), 200);
    }

    // 浏览器通知
    function showNotification(title, body) {
        if (typeof GM_notification === 'function') {
            GM_notification({ title, text: body, timeout: 10000 });
        } else if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body });
        }
    }

    // ==================== 初始化 ====================
    createPanel();

    // 请求通知权限
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }

    console.log('[🦞 大麦抢票助手] 已加载！');

})();
