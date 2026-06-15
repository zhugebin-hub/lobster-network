"""
杭州烟草销售数据分析系统 - 教学简化版

说明：
- 这是简化版本，代码更易读，适合学生学习
- 包含详细注释，解释每个步骤
- 功能精简但保留核心功能

作者：图图老师
日期：2026 年 4 月
"""

# ==================== 导入必要的库 ====================
import streamlit as st          # Web 界面
import pandas as pd             # 数据处理
import plotly.express as px     # 数据可视化

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="杭州烟草销售数据分析",
    page_icon="📊",
    layout="wide"
)

# ==================== 加载数据 ====================
@st.cache_data  # 缓存数据，避免重复加载
def load_data():
    """加载销售数据"""
    try:
        # 读取 CSV 文件
        sales = pd.read_csv("data/sales_records.csv", parse_dates=["日期"])
        return sales
    except Exception as e:
        st.error(f"数据加载失败：{e}")
        return None

# 加载数据
sales = load_data()

# ==================== 侧边栏 ====================
st.sidebar.title("📊 导航")
page = st.sidebar.radio(
    "选择页面",
    ["🏠 首页", "📈 销售分析", "🏪 店铺排名", "📅 时间趋势"]
)

# ==================== 首页 ====================
if page == "🏠 首页":
    st.title("📊 杭州烟草销售数据分析系统")
    st.markdown("### 欢迎使用数据分析系统！")
    
    # 显示关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    if sales is not None:
        # 计算指标
        total_sales = sales["销售金额"].sum()
        total_qty = sales["销售数量"].sum()
        avg_sales = sales["销售金额"].mean()
        shop_count = sales["店铺名称"].nunique()
        
        # 显示指标卡片
        col1.metric("💰 总销售额", f"¥{total_sales:,.0f}")
        col2.metric("📦 总销量", f"{total_qty:,} 条")
        col3.metric("📊 平均单笔", f"¥{avg_sales:.0f}")
        col4.metric("🏪 店铺数", f"{shop_count} 家")
    
    # 显示数据预览
    st.markdown("### 📋 数据预览")
    if sales is not None:
        st.dataframe(sales.head())
        
        st.info(f"""
        **数据说明：**
        - 数据量：{len(sales):,} 条销售记录
        - 时间范围：{sales['日期'].min()} 至 {sales['日期'].max()}
        - 包含字段：{', '.join(sales.columns)}
        """)

# ==================== 销售分析 ====================
elif page == "📈 销售分析":
    st.title("📈 销售分析")
    
    if sales is not None:
        # 按档次分析
        st.markdown("### 各档次销售占比")
        
        # 按档次汇总
        category_sales = sales.groupby("档次")["销售金额"].sum().reset_index()
        
        # 绘制饼图
        fig = px.pie(
            category_sales,
            values="销售金额",
            names="档次",
            title="各档次销售占比",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 按品牌分析
        st.markdown("### 各品牌销售额")
        
        brand_sales = sales.groupby("品牌")["销售金额"].sum().reset_index()
        brand_sales = brand_sales.sort_values("销售金额", ascending=False)
        
        fig = px.bar(
            brand_sales,
            x="品牌",
            y="销售金额",
            title="品牌销售额排名",
            color="销售金额",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== 店铺排名 ====================
elif page == "🏪 店铺排名":
    st.title("🏪 店铺销售排名")
    
    if sales is not None:
        # 按店铺汇总
        shop_sales = sales.groupby("店铺名称")[["销售数量", "销售金额"]].sum().reset_index()
        shop_sales = shop_sales.sort_values("销售金额", ascending=False)
        
        # 显示排名表格
        st.markdown("### 📋 店铺销售排名")
        st.dataframe(shop_sales.style.format({
            "销售数量": "{:,}",
            "销售金额": "¥{:,}"
        }))
        
        # 绘制排名图
        fig = px.bar(
            shop_sales.head(10),
            x="销售金额",
            y="店铺名称",
            orientation="h",
            title="TOP10 店铺销售额",
            color="销售金额",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==================== 时间趋势 ====================
elif page == "📅 时间趋势":
    st.title("📅 销售时间趋势")
    
    if sales is not None:
        # 按日期汇总
        daily_sales = sales.groupby("日期")["销售金额"].sum().reset_index()
        
        # 绘制折线图
        fig = px.line(
            daily_sales,
            x="日期",
            y="销售金额",
            title="每日销售趋势",
            labels={"日期": "日期", "销售金额": "销售额 (元)"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 按月汇总
        sales["月份"] = sales["日期"].dt.to_period("M").astype(str)
        monthly_sales = sales.groupby("月份")["销售金额"].sum().reset_index()
        
        fig = px.bar(
            monthly_sales,
            x="月份",
            y="销售金额",
            title="月度销售趋势",
            color="销售金额",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🦞 杭州烟草销售数据分析系统（教学版）</p>
    <p>技术栈：Streamlit + Pandas + Plotly</p>
</div>
""", unsafe_allow_html=True)
