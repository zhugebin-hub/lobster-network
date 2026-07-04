const app = getApp();

Page({
  data: {
    userInfo: null,
    todayCount: 0,
    todayAvg: 0,
    date: ''
  },

  onLoad() {
    const today = new Date().toISOString().split('T')[0];
    this.setData({ date: today });
    this.loadUserInfo();
    this.loadTodayStats();
  },

  onShow() {
    this.loadUserInfo();
    this.loadTodayStats();
  },

  loadUserInfo() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    }
  },

  loadTodayStats() {
    const token = wx.getStorageSync('token');
    if (!token) return;

    wx.request({
      url: `${app.globalData.apiUrl}/api/records`,
      header: { Authorization: `Bearer ${token}` },
      data: { date: this.data.date },
      success: (res) => {
        if (res.data) {
          const records = res.data;
          const count = records.length;
          const avg = count > 0 
            ? (records.reduce((sum, r) => sum + r.hygiene_score + r.discipline_score + r.study_score, 0) / count / 3).toFixed(1)
            : 0;
          this.setData({ todayCount: count, todayAvg: avg });
        }
      }
    });
  },

  goToRecord() {
    if (!this.data.userInfo) {
      wx.navigateTo({ url: '/pages/login/login' });
    } else {
      wx.navigateTo({ url: '/pages/record/record' });
    }
  },

  goToView() {
    wx.navigateTo({ url: '/pages/view/view' });
  },

  goToWeekly() {
    if (!this.data.userInfo) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '/pages/weekly/weekly' });
  },

  goToLogin() {
    wx.navigateTo({ url: '/pages/login/login' });
  },

  quickRecord() {
    if (!this.data.userInfo) {
      wx.navigateTo({ url: '/pages/login/login' });
      return;
    }
    wx.navigateTo({ url: '/pages/record/record' });
  },

  viewToday() {
    wx.navigateTo({ url: `/pages/view/view?date=${this.data.date}` });
  },

  logout() {
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    this.setData({ userInfo: null, todayCount: 0, todayAvg: 0 });
    wx.showToast({ title: '已退出登录' });
  }
});
