const app = getApp();

Page({
  data: {
    weekStart: '',
    weekEnd: '',
    summary: null,
    rankings: [],
    generating: false
  },

  onLoad() {
    // 默认设置为本周一到周日
    const now = new Date();
    const day = now.getDay();
    const diff = now.getDate() - day + (day === 0 ? -6 : 1); // 调整为周一
    const monday = new Date(now.setDate(diff));
    const sunday = new Date(now.setDate(diff + 6));

    this.setData({
      weekStart: monday.toISOString().split('T')[0],
      weekEnd: sunday.toISOString().split('T')[0]
    });
  },

  onStartChange(e) {
    this.setData({ weekStart: e.detail.value });
  },

  onEndChange(e) {
    this.setData({ weekEnd: e.detail.value });
  },

  generateSummary() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 1500);
      return;
    }

    this.setData({ generating: true });

    // 先获取统计数据
    wx.request({
      url: `${app.globalData.apiUrl}/api/stats/weekly`,
      header: { Authorization: `Bearer ${token}` },
      data: { week_start: this.data.weekStart },
      success: (res) => {
        if (res.data) {
          this.setData({ rankings: res.data });
        }
      }
    });

    // 调用 AI 总结接口
    wx.request({
      url: `${app.globalData.apiUrl}/api/ai/weekly-summary`,
      method: 'POST',
      header: { Authorization: `Bearer ${token}` },
      data: {
        week_start: this.data.weekStart,
        week_end: this.data.weekEnd
      },
      success: (res) => {
        if (res.data.summary) {
          this.setData({ summary: res.data.summary });
          wx.showToast({ title: '生成成功' });
        } else {
          wx.showToast({ title: '生成失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ generating: false });
      }
    });
  }
});
