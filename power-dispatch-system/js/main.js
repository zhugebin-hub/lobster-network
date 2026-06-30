// ===== 主程序入口 =====

// 页面导航
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const pageId = this.dataset.page;
        
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        
        // 切换页面
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById(pageId).classList.add('active');
        
        // 页面切换时重新渲染图表
        if (window.initializeCharts) {
            setTimeout(() => window.initializeCharts(), 100);
        }
    });
});

// 更新时间显示
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false });
    const dateStr = now.toLocaleDateString('zh-CN');
    
    document.getElementById('currentTime').textContent = timeStr;
    document.getElementById('lastUpdate').textContent = `${dateStr} ${timeStr}`;
}

updateTime();
setInterval(updateTime, 1000);

// 刷新数据
function refreshData() {
    showNotification('数据刷新成功', 'success');
    updateKPIData();
    updateAlerts();
}

// 导出报表
function exportReport() {
    showNotification('报表导出中...', 'info');
    setTimeout(() => {
        showNotification('报表导出成功！', 'success');
    }, 1500);
}

// 更新 KPI 数据
function updateKPIData() {
    // 模拟数据更新
    const currentLoad = Math.floor(3000 + Math.random() * 500);
    const powerOutput = Math.floor(currentLoad * (1 + Math.random() * 0.1));
    const systemFreq = (50 + (Math.random() - 0.5) * 0.1).toFixed(2);
    const newEnergyRatio = (25 + Math.random() * 10).toFixed(1);
    const reserveCapacity = Math.floor(300 + Math.random() * 200);
    const todayMaxLoad = Math.floor(4000 + Math.random() * 300);
    
    animateValue('currentLoad', currentLoad);
    animateValue('powerOutput', powerOutput);
    document.getElementById('systemFreq').textContent = systemFreq;
    animateValue('newEnergyRatio', newEnergyRatio, 1);
    animateValue('reserveCapacity', reserveCapacity);
    animateValue('todayMaxLoad', todayMaxLoad);
}

// 动画更新数值
function animateValue(elementId, newValue, decimals = 0) {
    const element = document.getElementById(elementId);
    const currentValue = parseFloat(element.textContent.replace(/,/g, ''));
    const diff = newValue - currentValue;
    const duration = 1000;
    const steps = 30;
    const stepValue = diff / steps;
    const stepTime = duration / steps;
    
    let step = 0;
    const timer = setInterval(() => {
        step++;
        const currentValue = parseFloat(element.textContent.replace(/,/g, ''));
        const newValue = currentValue + stepValue;
        
        if (decimals === 0) {
            element.textContent = Math.round(newValue).toLocaleString();
        } else {
            element.textContent = newValue.toFixed(decimals);
        }
        
        if (step >= steps) {
            clearInterval(timer);
        }
    }, stepTime);
}

// 更新告警
function updateAlerts() {
    const alerts = [
        { type: 'warning', title: '110kV 城东线负荷接近上限', time: getCurrentTime() },
        { type: 'info', title: '3 号发电机组完成检修并网', time: getCurrentTime() },
        { type: 'warning', title: '光伏电站出力波动较大', time: getCurrentTime() }
    ];
    
    const alertsList = document.getElementById('alertsList');
    alertsList.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.type}">
            <i class="fas fa-${alert.type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
            <div class="alert-content">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-info">
                    <span class="alert-time">${alert.time}</span>
                    <span class="alert-level">${alert.type === 'warning' ? '警告' : '提示'}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// 获取当前时间字符串
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// 切换图表类型
function toggleChartType(chartName) {
    showNotification(`已切换${chartName}图表类型`, 'info');
}

// 展开图表
function expandChart(chartId) {
    const chart = document.getElementById(chartId);
    chart.parentElement.classList.toggle('expanded');
}

// 运行负荷预测
function runForecast() {
    const forecastType = document.getElementById('forecastType').value;
    showNotification(`正在运行${forecastType === 'short' ? '短期' : forecastType === 'mid' ? '中期' : '长期'}负荷预测...`, 'info');
    
    setTimeout(() => {
        showNotification('负荷预测完成！', 'success');
        updateForecastChart();
    }, 2000);
}

// 更新预测图表
function updateForecastChart() {
    if (window.forecastChart) {
        window.forecastChart.data.datasets[0].data = generateForecastData();
        window.forecastChart.update();
    }
}

// 生成预测数据
function generateForecastData() {
    const data = [];
    for (let i = 0; i < 24; i++) {
        const baseLoad = 3000 + Math.sin(i * Math.PI / 12) * 1000;
        const random = Math.random() * 200;
        data.push(baseLoad + random);
    }
    return data;
}

// 切换告警音
let alarmSoundEnabled = true;
function toggleAlarmSound() {
    alarmSoundEnabled = !alarmSoundEnabled;
    const btn = document.querySelector('button[onclick="toggleAlarmSound()"]');
    btn.innerHTML = alarmSoundEnabled ? 
        '<i class="fas fa-volume-up"></i> 告警音：开' : 
        '<i class="fas fa-volume-mute"></i> 告警音：关';
    showNotification(alarmSoundEnabled ? '告警音已开启' : '告警音已关闭', 'info');
}

// 刷新实时数据
function refreshRealTime() {
    showNotification('实时数据已刷新', 'success');
    updateGridMap();
    updateVoltageData();
    updateFrequencyData();
}

// 更新电网地图
function updateGridMap() {
    const nodes = document.querySelectorAll('.node-circle');
    nodes.forEach(node => {
        if (Math.random() > 0.8) {
            node.classList.remove('normal', 'warning', 'critical');
            node.classList.add('normal');
        }
    });
}

// 更新电压数据
function updateVoltageData() {
    const voltages = document.querySelectorAll('.voltage-value');
    voltages.forEach(v => {
        const baseValue = parseFloat(v.textContent);
        const newValue = baseValue + (Math.random() - 0.5) * 0.5;
        v.textContent = newValue.toFixed(1) + ' kV';
    });
}

// 更新频率数据
function updateFrequencyData() {
    const freq = (50 + (Math.random() - 0.5) * 0.1).toFixed(2);
    document.getElementById('freqDisplay').textContent = freq + ' Hz';
}

// 启动应急演练
function startEmergencyDrill() {
    showNotification('启动应急演练...', 'warning');
    setTimeout(() => {
        showNotification('演练场景已加载：220kV 线路故障', 'info');
    }, 1000);
}

// 查看应急预案
function viewEmergencyPlan() {
    showNotification('打开应急预案文档...', 'info');
}

// 显示案例详情
function showCaseDetail(caseId) {
    const cases = {
        1: {
            title: '220kV 城东线雷击跳闸',
            content: `
                <div class="case-detail">
                    <h4>故障概况</h4>
                    <p>2026 年 4 月 15 日 14:28，220kV 城东线因雷击导致绝缘子闪络，线路保护动作跳闸，重合闸失败。</p>
                    
                    <h4>处置过程</h4>
                    <ol>
                        <li>14:28:03 - 监控系统告警，调度员确认故障</li>
                        <li>14:29:00 - 启动应急预案，通知巡线</li>
                        <li>14:35:00 - 调整潮流分布，转移负荷</li>
                        <li>14:50:00 - 巡线确认故障点</li>
                        <li>14:58:00 - 故障隔离，恢复供电</li>
                    </ol>
                    
                    <h4>经验总结</h4>
                    <p>加强雷雨季节设备巡视，完善雷电监测预警系统。</p>
                </div>
            `
        },
        2: {
            title: '110kV 主变过载',
            content: `
                <div class="case-detail">
                    <h4>故障概况</h4>
                    <p>2026 年 4 月 10 日 19:15，110kV 主变负载率达到 115%，超过允许过载能力。</p>
                    
                    <h4>处置过程</h4>
                    <ol>
                        <li>19:15:00 - 过载告警，调度员确认</li>
                        <li>19:18:00 - 启动负荷控制预案</li>
                        <li>19:25:00 - 调整运行方式，转移负荷</li>
                        <li>19:30:00 - 负载率恢复正常</li>
                    </ol>
                    
                    <h4>经验总结</h4>
                    <p>优化负荷预测精度，提前安排运行方式。</p>
                </div>
            `
        },
        3: {
            title: '10kV 母线电压偏低',
            content: `
                <div class="case-detail">
                    <h4>故障概况</h4>
                    <p>2026 年 4 月 8 日 10:30，10kV 母线电压降至 9.2kV，低于允许下限。</p>
                    
                    <h4>处置过程</h4>
                    <ol>
                        <li>10:30:00 - 电压异常告警</li>
                        <li>10:32:00 - 投入电容器组</li>
                        <li>10:40:00 - 调整主变分接头</li>
                        <li>10:50:00 - 电压恢复正常</li>
                    </ol>
                    
                    <h4>经验总结</h4>
                    <p>加强无功电压管理，优化 AVC 系统策略。</p>
                </div>
            `
        }
    };
    
    const caseData = cases[caseId];
    document.getElementById('modalTitle').textContent = caseData.title;
    document.getElementById('modalBody').innerHTML = caseData.content;
    document.getElementById('caseModal').classList.add('show');
}

// 关闭模态框
function closeModal() {
    document.getElementById('caseModal').classList.remove('show');
}

// 刷新新能源数据
function refreshNewEnergy() {
    showNotification('新能源数据已刷新', 'success');
    updateNEOutputChart();
}

// 更新新能源出力图表
function updateNEOutputChart() {
    if (window.neOutputChart) {
        window.neOutputChart.data.datasets[0].data = generateNEData();
        window.neOutputChart.update();
    }
}

// 生成新能源数据
function generateNEData() {
    const data = [];
    for (let i = 0; i < 24; i++) {
        if (i >= 6 && i <= 18) {
            data.push(300 + Math.sin((i - 6) * Math.PI / 12) * 200 + Math.random() * 50);
        } else {
            data.push(50 + Math.random() * 30);
        }
    }
    return data;
}

// 选择报表类型
function selectReportType(type) {
    const types = {
        'daily': '日报',
        'weekly': '周报',
        'monthly': '月报',
        'analysis': '分析报告'
    };
    showNotification(`已选择${types[type]}`, 'info');
}

// 生成报表
function generateReport() {
    const date = document.getElementById('reportDate').value;
    if (!date) {
        showNotification('请选择日期', 'warning');
        return;
    }
    showNotification(`正在生成${date}的报表...`, 'info');
    setTimeout(() => {
        showNotification('报表生成成功！', 'success');
    }, 2000);
}

// 切换侧边栏
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// 显示帮助
function showHelp() {
    showNotification('帮助文档已打开', 'info');
}

// 切换全屏
function toggleFullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 模态框点击外部关闭
document.getElementById('caseModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// 页面加载完成后初始化
window.addEventListener('load', function() {
    updateKPIData();
    updateAlerts();
    
    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('reportDate').value = today;
    
    // 添加通知样式
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 15px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 3000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-success {
            border-left: 4px solid var(--success-color);
        }
        
        .notification-success i {
            color: var(--success-color);
        }
        
        .notification-info {
            border-left: 4px solid var(--info-color);
        }
        
        .notification-info i {
            color: var(--info-color);
        }
        
        .notification-warning {
            border-left: 4px solid var(--warning-color);
        }
        
        .notification-warning i {
            color: var(--warning-color);
        }
        
        .notification-error {
            border-left: 4px solid var(--danger-color);
        }
        
        .notification-error i {
            color: var(--danger-color);
        }
        
        .case-detail h4 {
            color: var(--accent-color);
            margin: 20px 0 10px 0;
            font-size: 16px;
        }
        
        .case-detail p {
            color: var(--text-secondary);
            line-height: 1.8;
        }
        
        .case-detail ol {
            color: var(--text-secondary);
            padding-left: 20px;
            line-height: 2;
        }
    `;
    document.head.appendChild(style);
});

// 定时自动刷新
setInterval(() => {
    updateKPIData();
    updateGridMap();
    updateVoltageData();
    updateFrequencyData();
}, 5000);
