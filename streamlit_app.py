import streamlit as st
import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import warnings
import os
from judge_strategy import get_stock_data, calculate_macd_indicators_new

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
    "中证2000ETF (159531.SZ)": "sz159531",
    "科创综指 (000680.SH)": "sh000688"
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
        

    
    # 主内容区域
    # 指数选择
    selected_index = st.selectbox(
        "选择指数",
        list(INDICES_CONFIG.keys()),
        index=3  # 默认选择沪深300
    )
    
    # 计算按钮 - 移到指数列表框下面
    if st.button("计算指标", type="primary", use_container_width=True):
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
            
            status_text.text("正在处理数据...")
            progress_bar.progress(75)
            
            # 根据分析周期过滤数据
            if analysis_period == "最近30天":
                df_display = df.tail(30)
            elif analysis_period == "最近60天":
                df_display = df.tail(60)
            elif analysis_period == "最近90天":
                df_display = df.tail(90)
            else:
                df_display = df
            
            status_text.text("完成!")
            progress_bar.progress(100)
            
            # 显示关键指标
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
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
            
            with col5:
                # 显示顶结构值
                tg_value = df['TG_数值'].iloc[-1] if 'TG_数值' in df.columns else 0
                tg_color = "red" if tg_value == 1 else "gray"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border: 2px solid {tg_color}; border-radius: 5px;">
                    <div style="font-size: 14px; color: #666;">顶结构值</div>
                    <div style="font-size: 24px; font-weight: bold; color: {tg_color};">{tg_value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                # 显示底结构值
                bg_value = df['BG_数值'].iloc[-1] if 'BG_数值' in df.columns else 0
                bg_color = "green" if bg_value == -1 else "gray"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border: 2px solid {bg_color}; border-radius: 5px;">
                    <div style="font-size: 14px; color: #666;">底结构值</div>
                    <div style="font-size: 24px; font-weight: bold; color: {bg_color};">{bg_value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 数据表格显示
            st.subheader("详细数据")
            
            # 选择要显示的列
            display_columns = [
                'close', 'DIF', 'DEA', 'MACD',
                '低位金叉', '二次金叉', 'TG', 'BG', 'TG_数值', 'BG_数值',
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
            
            # 重命名界面显示的列名
            display_column_mapping = {
                'TG': '顶结构',
                'BG': '底结构',
                'TG_数值': '顶结构_数值',
                'BG_数值': '底结构_数值'
            }
            formatted_df = formatted_df.rename(columns=display_column_mapping)
            
            st.dataframe(formatted_df, use_container_width=True)
            
            # 下载数据功能
            # 创建CSV数据框并转换TG和BG
            csv_df = df[available_columns].copy()
            if 'TG' in csv_df.columns:
                csv_df['TG'] = csv_df['TG'].astype(int)  # True->1, False->0
            if 'BG' in csv_df.columns:
                csv_df['BG'] = -csv_df['BG'].astype(int)  # True->-1, False->0
            
            csv = csv_df.to_csv(index=True)
            st.download_button(
                label="下载完整数据 (CSV)",
                data=csv,
                file_name=f'{stock_code}_macd_data.csv',
                mime='text/csv'
            )
            
            # Excel下载功能
            try:
                # 确保有openpyxl依赖
                import openpyxl
                
                # 选择要导出的列
                export_columns = [
                    'close', 'DIF', 'DEA', 'MACD',
                    '低位金叉', '二次金叉', 'TG', 'BG', 'TG_数值', 'BG_数值',
                    '直接顶背离', '隔峰顶背离', '直接底背离', '隔峰底背离',
                    '主升', 'DIF顶转折', 'DIF底转折'
                ]
                
                # 过滤存在的列
                available_export_columns = [col for col in export_columns if col in df.columns]
                
                # 创建要导出的数据框
                export_df = df[available_export_columns].copy()
                
                # 转换TG和BG为数值
                if 'TG' in export_df.columns:
                    export_df['TG'] = export_df['TG'].astype(int)  # True->1, False->0
                if 'BG' in export_df.columns:
                    export_df['BG'] = -export_df['BG'].astype(int)  # True->-1, False->0
                
                # 重命名列
                column_mapping = {
                    'TG': '顶结构',
                    'BG': '底结构',
                    'TG_数值': '顶结构_数值',
                    'BG_数值': '底结构_数值'
                }
                export_df = export_df.rename(columns=column_mapping)
                
                # 格式化数值列
                if 'close' in export_df.columns:
                    export_df['close'] = export_df['close'].round(2)
                if 'DIF' in export_df.columns:
                    export_df['DIF'] = export_df['DIF'].round(3)
                if 'DEA' in export_df.columns:
                    export_df['DEA'] = export_df['DEA'].round(3)
                if 'MACD' in export_df.columns:
                    export_df['MACD'] = export_df['MACD'].round(3)
                
                # 将数据转换为Excel格式的字节流
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=True, sheet_name='MACD分析数据')
                excel_data = output.getvalue()
                
                # 提供Excel下载按钮
                st.download_button(
                    label="下载Excel数据",
                    data=excel_data,
                    file_name=f'{stock_code}_macd_analysis.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
            except ImportError:
                st.error("缺少openpyxl依赖，请运行: pip install openpyxl")
            except Exception as e:
                st.error(f"生成Excel文件时出错: {e}")
        
        except Exception as e:
            st.error(f"计算过程中出现错误: {e}")
            st.exception(e)

if __name__ == "__main__":
    main() 