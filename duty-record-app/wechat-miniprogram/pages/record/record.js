const app = getApp();

Page({
  data: {
    date: '',
    timePeriods: [],
    periodIndex: 0,
    classes: [],
    classIndex: 0,
    hygiene: 5,
    discipline: 5,
    study: 5,
    notes: '',
    photoPath: null,
    photoFile: null,
    submitting: false
  },

  onLoad() {
    const today = new Date().toISOString().split('T')[0];
    this.setData({ date: today });
    this.loadTimePeriods();
    this.loadClasses();
  },

  loadTimePeriods() {
    wx.request({
      url: `${app.globalData.apiUrl}/api/time-periods`,
      success: (res) => {
        if (res.data) {
          // 根据当前时间自动选择时段
          const hour = new Date().getHours();
          let defaultIndex = 0;
          if (hour >= 7 && hour < 8) defaultIndex = 0;
          else if (hour >= 8 && hour < 9) defaultIndex = 1;
          else if (hour >= 9 && hour < 10) defaultIndex = 2;
          else if (hour >= 11 && hour < 12) defaultIndex = 3;
          else if (hour >= 12 && hour < 14) defaultIndex = 4;
          else if (hour >= 14 && hour < 17) defaultIndex = 5;
          else if (hour >= 17 && hour < 18) defaultIndex = 6;
          else if (hour >= 18 && hour < 18.5) defaultIndex = 7;
          else if (hour >= 18.5) defaultIndex = 8;

          this.setData({ timePeriods: res.data, periodIndex: defaultIndex });
        }
      }
    });
  },

  loadClasses() {
    wx.request({
      url: `${app.globalData.apiUrl}/api/classes`,
      success: (res) => {
        if (res.data) {
          this.setData({ classes: res.data });
        }
      }
    });
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value });
  },

  onPeriodChange(e) {
    this.setData({ periodIndex: e.detail.value });
  },

  onClassChange(e) {
    this.setData({ classIndex: e.detail.value });
  },

  setHygiene(e) {
    this.setData({ hygiene: e.currentTarget.dataset.score });
  },

  setDiscipline(e) {
    this.setData({ discipline: e.currentTarget.dataset.score });
  },

  setStudy(e) {
    this.setData({ study: e.currentTarget.dataset.score });
  },

  onNotesInput(e) {
    this.setData({ notes: e.detail.value });
  },

  choosePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera', 'album'],
      success: (res) => {
        if (res.tempFiles && res.tempFiles.length > 0) {
          this.setData({ 
            photoPath: res.tempFiles[0].tempFilePath,
            photoFile: res.tempFiles[0].tempFilePath
          });
        }
      }
    });
  },

  submitRecord() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 1500);
      return;
    }

    const { date, timePeriods, periodIndex, classes, classIndex, hygiene, discipline, study, notes, photoFile } = this.data;

    if (classIndex === null || classIndex === undefined) {
      wx.showToast({ title: '请选择班级', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    const formData = {
      date,
      time_period: timePeriods[periodIndex].name,
      class_id: classes[classIndex].id,
      hygiene_score: hygiene,
      discipline_score: discipline,
      study_score: study,
      notes
    };

    // 使用 FormData 上传
    wx.request({
      url: `${app.globalData.apiUrl}/api/records`,
      method: 'POST',
      header: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      },
      data: formData,
      success: (res) => {
        if (res.data.id) {
          wx.showToast({ title: '记录成功', icon: 'success' });
          // 重置表单
          this.setData({
            notes: '',
            photoPath: null,
            photoFile: null,
            hygiene: 5,
            discipline: 5,
            study: 5
          });
        } else {
          wx.showToast({ title: res.data.error || '提交失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ submitting: false });
      }
    });
  }
});
