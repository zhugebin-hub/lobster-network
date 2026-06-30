const app = getApp();

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  login() {
    const { username, password } = this.data;

    if (!username || !password) {
      wx.showToast({ title: '请输入用户名和密码', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    wx.request({
      url: `${app.globalData.apiUrl}/api/login`,
      method: 'POST',
      data: { username, password },
      success: (res) => {
        if (res.data.token) {
          wx.setStorageSync('token', res.data.token);
          wx.setStorageSync('userInfo', res.data.user);
          wx.showToast({ title: '登录成功' });
          setTimeout(() => {
            wx.navigateBack();
          }, 1000);
        } else {
          wx.showToast({ title: res.data.error || '登录失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  }
});
