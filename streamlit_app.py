import streamlit as st
import pandas as pd
import numpy as np
import akshare as ak
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import os
from judge_strategy import get_stock_data, calculate_macd_indicators_new, plot_macd_system_new

# 设置缓存
@st.cache_data(ttl=3600)  # 缓存1小时
def get_cached_stock_data(stock_code):
    """缓存股票数据获取"""
    return get_stock_data(stock_code)

@st.cache_data(ttl=3600)  # 缓存1小时
def get_cached_macd_indicators(df):
    """缓存MACD指标计算"""
    return calculate_macd_indicators_new(df)

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="多指数定量结构公式分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .chart-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* 修复按钮对齐问题 */
    .stButton > button {
        margin-top: 1.5rem;
    }
    
    /* 确保selectbox和button在同一行对齐 */
    .row-widget.stHorizontal {
        align-items: end;
    }
</style>
""", unsafe_allow_html=True)

# 指数配置 - 使用akshare要求的完整代码格式
INDICES_CONFIG = {
    "上证指数 (000001.SH)": "sh000001",
    "深证成指 (399001.SZ)": "sz399001", 
    "创业板指 (399006.SZ)": "sz399006",
    "沪深300 (000300.SH)": "sh000300",
    "上证50 (000016.SH)": "sh000016",
    "中证500 (000905.SH)": "sh000905",
    "中证1000 (000852.SH)": "sh000852",
    "中证2000 (000680.SH)": "sh000680",
    "中证1000ETF (000985.SH)": "sh000985"
}

def get_latest_data_info():
    """获取最新数据信息"""
    try:
        # 尝试获取一个指数的数据来检查最新日期
        import akshare as ak
        test_df = ak.stock_zh_index_daily(symbol="sh000001")
        if not test_df.empty:
            # 检查是否有date列
            if 'date' in test_df.columns:
                latest_date = test_df['date'].iloc[-1].strftime('%Y-%m-%d')
            else:
                latest_date = test_df.index[-1].strftime('%Y-%m-%d')
            return f"最新数据截止至{latest_date},正在尝试补充当日数据..."
        else:
            return "数据获取中..."
    except:
        return "数据获取中..."

def plot_macd_analysis_streamlit(df, stock_code, analysis_period):
    """为Streamlit优化的MACD分析图表"""
    # 设置中文字体 - 使用更兼容的字体
    import matplotlib.font_manager as fm
    
    # 尝试设置中文字体，按优先级尝试
    font_options = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'DejaVu Sans', 'Arial Unicode MS']
    font_found = False
    
    for font in font_options:
        try:
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False
            # 测试字体是否可用
            test_font = fm.FontProperties(family=font)
            if test_font.get_name() != 'DejaVu Sans':
                font_found = True
                break
        except:
            continue
    
    # 如果没有找到中文字体，使用默认字体并添加字体回退
    if not font_found:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[1, 1.5])
    
    # 创建连续的数字索引
    x_index = range(len(df))
    
    # 绘制K线图
    ax1.plot(x_index, df['close'], label='收盘价', color='blue', linewidth=1)
    ax1.set_title(f'{stock_code} 定量结构公式分析', fontsize=14, fontproperties=fm.FontProperties(family='SimHei' if 'SimHei' in font_options else 'DejaVu Sans'))
    
    # 添加买卖信号到价格图
    buy_signals = df[df['低位金叉'] | df['二次金叉']]
    sell_signals = df[df['TG']]
    
    if not buy_signals.empty:
        buy_x = [x_index[df.index.get_loc(idx)] for idx in buy_signals.index]
        buy_y = buy_signals['close'].values
        ax1.scatter(buy_x, buy_y, color='red', marker='^', s=100, zorder=5, label='买入信号')
    
    if not sell_signals.empty:
        sell_x = [x_index[df.index.get_loc(idx)] for idx in sell_signals.index]
        sell_y = sell_signals['close'].values
        ax1.scatter(sell_x, sell_y, color='green', marker='v', s=100, zorder=5, label='卖出信号')
    
    # 设置x轴标签 - 优化显示
    date_labels = df.index.strftime('%m-%d')
    step = max(1, len(df) // 15)  # 减少标签数量
    ax1.set_xticks(x_index[::step])
    ax1.set_xticklabels(date_labels[::step], rotation=45, fontsize=8)
    
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 绘制MACD
    ax2.plot(x_index, df['DIF'], label='DIF线', color='blue', linewidth=1)
    ax2.plot(x_index, df['DEA'], label='DEA线', color='orange', linewidth=1)
    
    # 绘制零轴线
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='零轴线')
    
    # 绘制MACD柱状图
    colors = ['red' if x >= 0 else 'green' for x in df['MACD']]
    ax2.bar(x_index, df['MACD'], color=colors, width=0.8, alpha=0.6, label='MACD柱')
    
    # 绘制买卖信号
    for i, idx in enumerate(df.index):
        x_pos = x_index[i]
        
        # 买入信号
        if df.loc[idx, '低位金叉'] or df.loc[idx, '二次金叉']:
            ax2.scatter(x_pos, df.loc[idx, 'DIF'], color='red', marker='^', s=100, zorder=5)
        
        # 卖出信号（顶背离确认）
        if df.loc[idx, 'TG']:
            ax2.scatter(x_pos, df.loc[idx, 'DIF'], color='green', marker='v', s=100, zorder=5)
    
    # 设置图例
    ax2.legend(loc='upper left', ncol=3, fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 设置x轴标签
    ax2.set_xticks(x_index[::step])
    ax2.set_xticklabels(date_labels[::step], rotation=45, fontsize=8)
    
    plt.tight_layout()
    return fig

def main():
    # 主标题
    st.markdown('<h1 class="main-header">多指数定量结构公式分析系统</h1>', unsafe_allow_html=True)
    
    # 简化的参数设置
    with st.sidebar:
        st.header("系统设置")
        
        # 分析周期选择
        analysis_period = st.selectbox(
            "分析周期",
            ["最近30天", "最近60天", "最近90天", "全部数据"],
            index=0
        )
        
        # 图表样式选择
        chart_style = st.selectbox(
            "图表样式",
            ["标准样式", "暗色主题", "简洁样式"],
            index=0
        )
    
    # 主内容区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 指数选择
        selected_index = st.selectbox(
            "选择指数",
            list(INDICES_CONFIG.keys()),
            index=3  # 默认选择沪深300
        )
    
    with col2:
        # 计算按钮 - 添加垂直间距
        st.write("")  # 添加空行来对齐
        if st.button("计算指标", type="primary"):
            st.session_state.calculate_clicked = True
        else:
            st.session_state.calculate_clicked = False
    
    # 状态信息
    status_info = get_latest_data_info()
    st.markdown(f'<div class="status-box">{status_info}</div>', unsafe_allow_html=True)
    
    # 如果点击了计算按钮
    if st.session_state.get('calculate_clicked', False):
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("正在获取数据...")
            progress_bar.progress(25)
            
            # 获取股票代码
            stock_code = INDICES_CONFIG[selected_index]
            
            # 获取数据
            df = get_cached_stock_data(stock_code)
            if df is None:
                st.error("数据获取失败，请检查网络连接或股票代码")
                return
            
            status_text.text("正在计算指标...")
            progress_bar.progress(50)
            
            # 计算指标
            df = get_cached_macd_indicators(df)
            
            status_text.text("正在生成图表...")
            progress_bar.progress(75)
            
            # 显示图表
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 根据分析周期过滤数据
            if analysis_period == "最近30天":
                df_display = df.tail(30)
            elif analysis_period == "最近60天":
                df_display = df.tail(60)
            elif analysis_period == "最近90天":
                df_display = df.tail(90)
            else:
                df_display = df
            
            # 创建图表
            fig = plot_macd_analysis_streamlit(df_display, selected_index, analysis_period)
            st.pyplot(fig)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            status_text.text("完成!")
            progress_bar.progress(100)
            
            # 显示关键指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("当前DIF", f"{df['DIF'].iloc[-1]:.3f}")
            
            with col2:
                st.metric("当前DEA", f"{df['DEA'].iloc[-1]:.3f}")
            
            with col3:
                st.metric("当前MACD", f"{df['MACD'].iloc[-1]:.3f}")
            
            with col4:
                latest_close = df['close'].iloc[-1]
                prev_close = df['close'].iloc[-2]
                change_pct = ((latest_close - prev_close) / prev_close) * 100
                st.metric("收盘价", f"{latest_close:.2f}", f"{change_pct:+.2f}%")
            
            # 数据表格显示
            st.subheader("详细数据")
            
            # 选择要显示的列
            display_columns = [
                'close', 'DIF', 'DEA', 'MACD',
                '低位金叉', '二次金叉', 'TG', 'BG',
                '直接顶背离', '隔峰顶背离', '直接底背离', '隔峰底背离',
                '主升'
            ]
            
            # 过滤存在的列
            available_columns = [col for col in display_columns if col in df.columns]
            
            # 根据分析周期显示数据
            if analysis_period == "最近30天":
                recent_df = df[available_columns].tail(30)
            elif analysis_period == "最近60天":
                recent_df = df[available_columns].tail(60)
            elif analysis_period == "最近90天":
                recent_df = df[available_columns].tail(90)
            else:
                recent_df = df[available_columns]
            
            # 格式化数据
            formatted_df = recent_df.copy()
            if 'close' in formatted_df.columns:
                formatted_df['close'] = formatted_df['close'].round(2)
            if 'DIF' in formatted_df.columns:
                formatted_df['DIF'] = formatted_df['DIF'].round(3)
            if 'DEA' in formatted_df.columns:
                formatted_df['DEA'] = formatted_df['DEA'].round(3)
            if 'MACD' in formatted_df.columns:
                formatted_df['MACD'] = formatted_df['MACD'].round(3)
            
            st.dataframe(formatted_df, use_container_width=True)
            
            # 下载数据功能
            csv = df[available_columns].to_csv(index=True)
            st.download_button(
                label="下载完整数据 (CSV)",
                data=csv,
                file_name=f'{stock_code}_macd_data.csv',
                mime='text/csv'
            )
            
            # 保存图表功能
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("保存分析图表"):
                    try:
                        plot_macd_system_new(df, stock_code)
                        st.success(f"图表已保存为: stock_{stock_code}_macd_chart_new.png")
                    except Exception as e:
                        st.error(f"保存图表时出错: {e}")
            
            with col2:
                if st.button("保存Excel数据"):
                    try:
                        # 确保有openpyxl依赖
                        try:
                            import openpyxl
                        except ImportError:
                            st.error("缺少openpyxl依赖，请运行: pip install openpyxl")
                            return
                        
                        excel_path = f'stock_{stock_code}_macd_analysis_new.xlsx'
                        
                        # 选择要导出的列
                        export_columns = [
                            'close', 'DIF', 'DEA', 'MACD',
                            '低位金叉', '二次金叉', 'TG', 'BG',
                            '直接顶背离', '隔峰顶背离', '直接底背离', '隔峰底背离',
                            '主升', 'DIF顶转折', 'DIF底转折'
                        ]
                        
                        # 过滤存在的列
                        available_export_columns = [col for col in export_columns if col in df.columns]
                        
                        # 创建要导出的数据框
                        export_df = df[available_export_columns].copy()
                        
                        # 格式化数值列
                        if 'close' in export_df.columns:
                            export_df['close'] = export_df['close'].round(2)
                        if 'DIF' in export_df.columns:
                            export_df['DIF'] = export_df['DIF'].round(3)
                        if 'DEA' in export_df.columns:
                            export_df['DEA'] = export_df['DEA'].round(3)
                        if 'MACD' in export_df.columns:
                            export_df['MACD'] = export_df['MACD'].round(3)
                        
                        # 保存到Excel
                        export_df.to_excel(excel_path, engine='openpyxl')
                        st.success(f"数据已保存为: {excel_path}")
                        
                        # 提供下载链接
                        with open(excel_path, 'rb') as f:
                            excel_data = f.read()
                        
                        st.download_button(
                            label="下载Excel文件",
                            data=excel_data,
                            file_name=excel_path,
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        
                    except Exception as e:
                        st.error(f"保存Excel时出错: {e}")
                        st.error("请确保已安装openpyxl: pip install openpyxl")
        
        except Exception as e:
            st.error(f"计算过程中出现错误: {e}")
            st.exception(e)

if __name__ == "__main__":
    main() 