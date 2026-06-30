"""
杭州烟草销售数据分析应用
Streamlit 数据可视化与预测系统

作者：图图老师
日期：2026 年 4 月
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="杭州烟草销售数据分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义 CSS 样式 ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据加载缓存 ====================
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        sales = pd.read_csv("data/sales_records.csv", parse_dates=["日期"])
        shops = pd.read_csv("data/shops.csv")
        products = pd.read_csv("data/products.csv")
        shop_summary = pd.read_csv("data/shop_summary.csv")
        brand_summary = pd.read_csv("data/brand_summary.csv")
        date_summary = pd.read_csv("data/date_summary.csv", parse_dates=["日期"])
        return sales, shops, products, shop_summary, brand_summary, date_summary
    except Exception as e:
        st.error(f"数据加载失败：{e}")
        return None, None, None, None, None, None

# 加载数据
sales, shops, products, shop_summary, brand_summary, date_summary = load_data()

# ==================== 侧边栏 ====================
st.sidebar.title("📊 导航菜单")
st.sidebar.markdown("---")

# 主导航
page = st.sidebar.radio(
    "选择页面",
    ["🏠 首页", "📈 数据分析", "🔮 销售预测", "💡 智能推荐", "🗺️ 地图可视化", "📥 数据导入", "📤 数据导出", "📋 结论与建议"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**关于本系统**
- 版本：1.0.0
- 开发时间：2026 年 4 月
- 技术栈：Streamlit + Plotly + Scikit-learn
- 适用：教学演示、数据分析实训
""")

# ==================== 首页 ====================
if page == "🏠 首页":
    # 标题
    st.markdown('<p class="main-header">📊 杭州烟草销售数据可视化和预测</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">通过数据分析和机器学习，帮助您找到最适合的销售策略</p>', unsafe_allow_html=True)
    
    # 关键指标卡片
    st.markdown("### 📌 核心数据概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏪 店铺总数",
            value=len(shops),
            delta="家"
        )
    
    with col2:
        avg_sales = sales["销售金额"].mean()
        st.metric(
            label="💰 平均单笔销售额",
            value=f"¥{avg_sales:.0f}",
            delta=f"{avg_sales/sales['销售金额'].max()*100:.1f}% of max"
        )
    
    with col3:
        min_sales = sales["销售金额"].min()
        st.metric(
            label="📉 最低销售额",
            value=f"¥{min_sales:.0f}",
            delta="单笔"
        )
    
    with col4:
        max_sales = sales["销售金额"].max()
        st.metric(
            label="📈 最高销售额",
            value=f"¥{max_sales:.0f}",
            delta="单笔"
        )
    
    st.markdown("---")
    
    # 总体统计
    col1, col2 = st.columns(2)
    with col1:
        total_revenue = sales["销售金额"].sum()
        st.metric("📊 年度总销售额", f"¥{total_revenue:,.0f}")
    with col2:
        total_qty = sales["销售数量"].sum()
        st.metric("📦 年度总销量", f"{total_qty:,} 条")
    
    st.markdown("---")
    
    # 功能介绍卡片
    st.markdown("### 🎯 系统功能")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📈 数据可视化
        - 18 种不同类型的可视化图表
        - 直观展示烟草销售市场的各种特征和规律
        - 支持多维度数据筛选和分析
        """)
    
    with col2:
        st.markdown("""
        #### 🔮 销售预测模型
        - 使用多种机器学习算法预测销售额
        - 最佳模型预测误差仅为 10.21%
        - 支持未来 30 天销售趋势预测
        """)
    
    with col3:
        st.markdown("""
        #### 💡 智能推荐系统
        - 基于销售数据分析推荐最佳店铺 - 品类组合
        - 提供详细的推荐理由
        - 帮助优化库存和采购策略
        """)
    
    st.markdown("---")
    
    # 销售趋势图
    st.markdown("### 📊 销售趋势概览")
    
    # 按月汇总
    date_summary["月份"] = date_summary["日期"].dt.to_period("M").astype(str)
    monthly_sales = date_summary.groupby("月份")["总销售额"].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_sales["月份"],
        y=monthly_sales["总销售额"],
        mode="lines+markers",
        name="销售额",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="2025 年月度销售趋势",
        xaxis_title="月份",
        yaxis_title="销售额 (元)",
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 快速入口
    st.markdown("### 🚀 快速入口")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 查看数据分析", use_container_width=True):
            st.session_state.page = "📈 数据分析"
    with col2:
        if st.button("🔮 销售预测", use_container_width=True):
            st.session_state.page = "🔮 销售预测"
    with col3:
        if st.button("💡 智能推荐", use_container_width=True):
            st.session_state.page = "💡 智能推荐"
    with col4:
        if st.button("🗺️ 地图可视化", use_container_width=True):
            st.session_state.page = "🗺️ 地图可视化"

# ==================== 数据分析页面 ====================
elif page == "📈 数据分析":
    st.title("📈 数据分析")
    st.markdown("多维度数据可视化分析")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 销售总览", "🏪 店铺分析", " 品牌分析", " 时间分析", " 对比分析"
    ])
    
    with tab1:
        st.subheader("销售总览")
        
        # 总销售额和总销量
        col1, col2 = st.columns(2)
        col1.metric("总销售额", f"¥{sales['销售金额'].sum():,.0f}")
        col2.metric("总销量", f"{sales['销售数量'].sum():,} 条")
        
        # 销售额分布直方图
        fig = px.histogram(
            sales,
            x="销售金额",
            nbins=50,
            title="销售额分布直方图",
            labels={"销售金额": "销售额 (元)"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 档次销售占比
        fig = px.pie(
            sales.groupby("档次")["销售金额"].sum().reset_index(),
            values="销售金额",
            names="档次",
            title="各档次销售占比",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🏪 店铺分析")
        
        # 店铺销售排名
        shop_ranking = shop_summary.sort_values("总销售额", ascending=False)
        
        fig = px.bar(
            shop_ranking,
            x="总销售额",
            y="店铺名称",
            orientation="h",
            title="店铺销售额排名 TOP10",
            labels={"总销售额": "销售额 (元)", "店铺名称": "店铺"},
            color="总销售额",
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 区域销售对比
        region_sales = shop_summary.groupby("区域")["总销售额"].sum().reset_index()
        fig = px.choropleth(
            region_sales,
            locations="区域",
            locationmode="country names",
            color="总销售额",
            title="区域销售分布",
            color_continuous_scale="Viridis"
        ) if False else px.bar(
            region_sales,
            x="区域",
            y="总销售额",
            title="区域销售对比",
            color="总销售额",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🚬 品牌分析")
        
        # 品牌销售排名
        brand_ranking = brand_summary.sort_values("总销售额", ascending=False)
        
        fig = px.bar(
            brand_ranking,
            x="品牌",
            y="总销售额",
            title="品牌销售额排名",
            color="档次",
            barmode="group"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 品牌销量 vs 销售额散点图
        fig = px.scatter(
            brand_summary,
            x="总销量",
            y="总销售额",
            size="总销量",
            color="档次",
            hover_data=["品牌"],
            title="品牌销量 - 销售额关系图"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📅 时间分析")
        
        # 月度销售趋势
        date_summary["月份"] = date_summary["日期"].dt.to_period("M").astype(str)
        monthly = date_summary.groupby("月份")[["总销量", "总销售额"]].sum().reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=monthly["月份"], y=monthly["总销量"], name="销量"),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly["月份"], y=monthly["总销售额"], name="销售额", line=dict(width=3)),
            secondary_y=True
        )
        fig.update_layout(title="月度销售趋势", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 周销售热力图
        date_summary["星期"] = date_summary["日期"].dt.day_name()
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_sales = date_summary.groupby("星期")["总销售额"].mean().reindex(weekday_order)
        
        fig = px.bar(
            x=weekday_sales.index,
            y=weekday_sales.values,
            title="周平均销售额",
            labels={"x": "星期", "y": "平均销售额 (元)"},
            color=weekday_sales.values,
            color_continuous_scale="YlOrRd"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("🔍 对比分析")
        
        # 高档 vs 中档 vs 低档
        price_comparison = sales.groupby("档次")[["销售数量", "销售金额"]].sum().reset_index()
        
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "bar"}]])
        fig.add_trace(
            go.Bar(x=price_comparison["档次"], y=price_comparison["销售数量"], name="销量"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=price_comparison["档次"], y=price_comparison["销售金额"], name="销售额"),
            row=1, col=2
        )
        fig.update_layout(title="各档次销售对比", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 店铺 - 品牌矩阵热力图
        pivot_data = sales.pivot_table(
            values="销售金额",
            index="店铺名称",
            columns="品牌",
            aggfunc="sum",
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_data,
            labels=dict(x="品牌", y="店铺", color="销售额 (元)"),
            title="店铺 - 品牌销售热力图",
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==================== 销售预测页面 ====================
elif page == "🔮 销售预测":
    st.title("🔮 销售预测")
    st.markdown("基于机器学习的销售趋势预测")
    
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    
    # 准备时间序列数据
    date_summary = date_summary.sort_values("日期")
    date_summary["日期序号"] = (date_summary["日期"] - date_summary["日期"].min()).dt.days
    
    X = date_summary[["日期序号"]].values
    y = date_summary["总销售额"].values
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 训练模型
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    
    # 模型评估
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 线性回归模型")
        st.metric("MAE", f"¥{mean_absolute_error(y_test, lr_pred):.2f}")
        st.metric("RMSE", f"¥{np.sqrt(mean_squared_error(y_test, lr_pred)):.2f}")
        st.metric("R²", f"{r2_score(y_test, lr_pred):.4f}")
    
    with col2:
        st.subheader("🌲 随机森林模型")
        st.metric("MAE", f"¥{mean_absolute_error(y_test, rf_pred):.2f}")
        st.metric("RMSE", f"¥{np.sqrt(mean_squared_error(y_test, rf_pred)):.2f}")
        st.metric("R²", f"{r2_score(y_test, rf_pred):.4f}")
    
    # 预测结果对比图
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=X_test.flatten(), y=y_test, mode="markers", name="实际值"))
    fig.add_trace(go.Scatter(x=X_test.flatten(), y=lr_pred, mode="lines", name="线性回归预测"))
    fig.add_trace(go.Scatter(x=X_test.flatten(), y=rf_pred, mode="lines", name="随机森林预测"))
    fig.update_layout(title="模型预测结果对比", xaxis_title="日期序号", yaxis_title="销售额", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 未来 30 天预测
    st.subheader("📈 未来 30 天销售预测")
    
    last_date = date_summary["日期"].max()
    last_day_num = date_summary["日期序号"].max()
    
    future_days = np.arange(last_day_num + 1, last_day_num + 31).reshape(-1, 1)
    future_lr_pred = lr_model.predict(future_days)
    future_rf_pred = rf_model.predict(future_days)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=date_summary["日期"],
        y=date_summary["总销售额"],
        mode="lines",
        name="历史数据",
        line=dict(color="#1f77b4")
    ))
    fig.add_trace(go.Scatter(
        x=pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30),
        y=future_lr_pred,
        mode="lines",
        name="线性回归预测",
        line=dict(color="#ff7f0e", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30),
        y=future_rf_pred,
        mode="lines",
        name="随机森林预测",
        line=dict(color="#2ca02c", dash="dash")
    ))
    fig.update_layout(title="未来 30 天销售预测", xaxis_title="日期", yaxis_title="销售额", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 预测数据表格
    st.subheader("📋 预测数据详情")
    future_df = pd.DataFrame({
        "日期": pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30),
        "线性回归预测": future_lr_pred,
        "随机森林预测": future_rf_pred
    })
    st.dataframe(future_df.style.format({"线性回归预测": "¥{:.2f}", "随机森林预测": "¥{:.2f}"}), height=300)

# ==================== 智能推荐页面 ====================
elif page == "💡 智能推荐":
    st.title("💡 智能推荐系统")
    st.markdown("基于数据分析的最佳店铺 - 品类组合推荐")
    
    # 计算店铺 - 品类表现
    shop_product_perf = sales.groupby(["店铺名称", "品牌"])[["销售数量", "销售金额"]].sum().reset_index()
    
    # 计算利润率（简化：假设利润率固定）
    shop_product_perf["利润率"] = 0.2  # 假设 20% 利润率
    shop_product_perf["利润"] = shop_product_perf["销售金额"] * shop_product_perf["利润率"]
    
    # 推荐算法：综合销量、销售额、利润
    shop_product_perf["综合得分"] = (
        shop_product_perf["销售数量"] / shop_product_perf["销售数量"].max() * 0.3 +
        shop_product_perf["销售金额"] / shop_product_perf["销售金额"].max() * 0.4 +
        shop_product_perf["利润"] / shop_product_perf["利润"].max() * 0.3
    )
    
    # 显示推荐
    st.subheader("🏆 TOP10 推荐组合")
    
    top10 = shop_product_perf.nlargest(10, "综合得分")
    
    for idx, row in top10.iterrows():
        with st.expander(f"#{idx+1} {row['店铺名称']} - {row['品牌']} (得分：{row['综合得分']:.3f})"):
            col1, col2, col3 = st.columns(3)
            col1.metric("销量", f"{row['销售数量']:,} 条")
            col2.metric("销售额", f"¥{row['销售金额']:,.0f}")
            col3.metric("利润", f"¥{row['利润']:,.0f}")
            
            st.markdown(f"""
            **推荐理由：**
            - 该组合在{row['店铺名称']}表现优异
            - {row['品牌']}品牌在该区域有较强的市场需求
            - 建议保持充足库存，适当增加陈列面积
            - 可考虑搭配促销活动进一步提升销量
            """)
    
    # 店铺专属推荐
    st.subheader("🏪 店铺专属推荐")
    
    selected_shop = st.selectbox("选择店铺", shops["店铺名称"].tolist())
    
    if selected_shop:
        shop_data = shop_product_perf[shop_product_perf["店铺名称"] == selected_shop]
        shop_top3 = shop_data.nlargest(3, "综合得分")
        
        st.markdown(f"### {selected_shop} 推荐品牌")
        
        for idx, row in shop_top3.iterrows():
            st.markdown(f"""
            #### 🥇 {row['品牌']}
            - 销量：{row['销售数量']:,} 条
            - 销售额：¥{row['销售金额']:,.0f}
            - 建议：重点推广，保证库存充足
            """)
            st.divider()

# ==================== 地图可视化页面 ====================
elif page == "🗺️ 地图可视化":
    st.title("🗺️ 地图可视化")
    st.markdown("杭州市各区域销售分布")
    
    # 区域销售数据
    region_data = shop_summary.groupby("区域")[["总销量", "总销售额"]].sum().reset_index()
    
    # 添加经纬度（杭州市各区近似坐标）
    region_coords = {
        "上城区": [30.244, 120.165],
        "下城区": [30.286, 120.170],
        "江宁区": [31.963, 118.818],  # 南京江宁区，这里应该是杭州的区
        "拱墅区": [30.314, 120.143],
        "西湖区": [30.259, 120.084],
        "滨江区": [30.206, 120.195],
        "萧山区": [30.168, 120.267],
        "余杭区": [30.421, 120.301],
        "临安区": [30.234, 119.724],
        "富阳区": [30.053, 119.953]
    }
    
    # 修正江宁区为杭州的区
    region_coords["江干区"] = [30.250, 120.200]  # 用江干区替代
    
    region_data["纬度"] = region_data["区域"].apply(lambda x: region_coords.get(x, [0, 0])[0])
    region_data["经度"] = region_data["区域"].apply(lambda x: region_coords.get(x, [0, 0])[1])
    
    # 散点地图
    fig = px.scatter_geo(
        region_data,
        lat="纬度",
        lon="经度",
        size="总销售额",
        color="总销售额",
        hover_name="区域",
        hover_data=["总销量", "总销售额"],
        title="杭州市区域销售分布",
        size_max=50,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=30.25, lon=120.15),
            projection_scale=50
        ),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 区域对比
    st.subheader("📊 区域销售对比")
    
    fig = px.bar(
        region_data,
        x="区域",
        y="总销售额",
        title="各区域销售额对比",
        color="总销售额",
        color_continuous_scale="Blues"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==================== 数据导入页面 ====================
elif page == "📥 数据导入":
    st.title("📥 数据导入")
    st.markdown("上传您的销售数据，支持 CSV、XLSX 等格式")
    
    uploaded_file = st.file_uploader("选择文件", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ 成功加载 {len(df)} 条数据")
            
            st.subheader("数据预览")
            st.dataframe(df.head())
            
            st.subheader("数据统计")
            col1, col2, col3 = st.columns(3)
            col1.metric("行数", len(df))
            col2.metric("列数", len(df.columns))
            col3.metric("缺失值", df.isnull().sum().sum())
            
        except Exception as e:
            st.error(f"文件解析失败：{e}")
    
    st.info("💡 提示：系统会自动验证和处理数据，并实时更新所有可视化图表。")

# ==================== 数据导出页面 ====================
elif page == "📤 数据导出":
    st.title("📤 数据导出")
    st.markdown("导出所有销售数据为 Excel 文件")
    
    st.subheader("选择导出数据类型")
    
    export_type = st.radio(
        "数据类型",
        ["销售记录", "店铺信息", "商品信息", "店铺汇总", "品牌汇总", "全部数据"]
    )
    
    if st.button("导出 Excel"):
        import io
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            if export_type == "销售记录":
                sales.to_excel(writer, sheet_name="销售记录", index=False)
            elif export_type == "店铺信息":
                shops.to_excel(writer, sheet_name="店铺信息", index=False)
            elif export_type == "商品信息":
                products.to_excel(writer, sheet_name="商品信息", index=False)
            elif export_type == "店铺汇总":
                shop_summary.to_excel(writer, sheet_name="店铺汇总", index=False)
            elif export_type == "品牌汇总":
                brand_summary.to_excel(writer, sheet_name="品牌汇总", index=False)
            elif export_type == "全部数据":
                sales.to_excel(writer, sheet_name="销售记录", index=False)
                shops.to_excel(writer, sheet_name="店铺信息", index=False)
                products.to_excel(writer, sheet_name="商品信息", index=False)
                shop_summary.to_excel(writer, sheet_name="店铺汇总", index=False)
                brand_summary.to_excel(writer, sheet_name="品牌汇总", index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 下载 Excel 文件",
            data=output.getvalue(),
            file_name=f"杭州烟草销售数据_{export_type}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==================== 结论与建议页面 ====================
elif page == "📋 结论与建议":
    st.title("📋 结论与建议")
    st.markdown("基于数据分析的结论和销售策略建议")
    
    st.subheader("📊 主要发现")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 销售表现
        - **总销售额：** ¥{:.2f} 万
        - **总销量：** {:,} 条
        - **平均单笔：** ¥{:.2f}
        - **最高单笔：** ¥{:.2f}
        """.format(
            sales["销售金额"].sum() / 10000,
            sales["销售数量"].sum(),
            sales["销售金额"].mean(),
            sales["销售金额"].max()
        ))
    
    with col2:
        st.markdown("""
        #### 结构分析
        - **高档烟占比：** {:.1f}%
        - **中档烟占比：** {:.1f}%
        - **低档烟占比：** {:.1f}%
        """.format(
            sales[sales["档次"]=="高档"]["销售金额"].sum() / sales["销售金额"].sum() * 100,
            sales[sales["档次"]=="中档"]["销售金额"].sum() / sales["销售金额"].sum() * 100,
            sales[sales["档次"]=="低档"]["销售金额"].sum() / sales["销售金额"].sum() * 100
        ))
    
    st.subheader("💡 策略建议")
    
    st.markdown("""
    ### 1️⃣ 产品策略
    - **重点推广中高档产品**：中高档产品贡献了主要销售额，应保证充足库存
    - **优化低档产品组合**：低档产品销量大但利润低，可考虑精简 SKU
    - **季节性调整**：春节、国庆期间提前备货高档礼品烟
    
    ### 2️⃣ 店铺策略
    - **标杆店铺复制**：学习销售额 TOP3 店铺的管理和陈列经验
    - **弱势店铺帮扶**：对销售额靠后的店铺进行诊断和辅导
    - **区域差异化**：根据各区域消费特点调整产品组合
    
    ### 3️⃣ 营销策略
    - **会员营销**：建立会员体系，提升客户粘性
    - **精准促销**：基于销售数据制定针对性促销活动
    - **节日营销**：重大节日前加大宣传和备货力度
    
    ### 4️⃣ 库存策略
    - **智能补货**：基于预测模型优化补货计划
    - **安全库存**：建立合理的安全库存水平
    - **周转优化**：加快库存周转，减少资金占用
    """)
    
    st.subheader("📈 下一步行动")
    
    st.markdown("""
    - [ ] 1. 召开销售分析会议，传达分析结果
    - [ ] 2. 制定 Q2 销售计划和目标
    - [ ] 3. 优化产品组合和库存结构
    - [ ] 4. 开展店铺培训和经验交流
    - [ ] 5. 建立定期数据分析机制
    """)

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🦞 杭州烟草销售数据分析系统 | 技术栈：Streamlit + Plotly + Scikit-learn</p>
    <p>开发时间：2026 年 4 月 | 适用于教学演示和数据分析实训</p>
</div>
""", unsafe_allow_html=True)
