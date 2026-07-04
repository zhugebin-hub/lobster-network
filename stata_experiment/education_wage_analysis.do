* ======================================================
* 项目：教育回报率分析
* 课程：计量经济学
* 作者：陈政道
* 日期：2026-06-09
* 数据：WAGE1（Wooldridge教材数据集）
* ======================================================

clear all            // 清空内存
set more off         // 禁止输出分页
cap log close        // 关闭可能已打开的日志文件
log using "education_wage_analysis.log", replace  // 开始记录日志

* ==========================================
* 1. 导入数据
* ==========================================
use "WAGE1.DTA", clear
describe             // 查看数据结构
codebook             // 查看变量详细信息和缺失值

* ==========================================
* 2. 数据清理与变量创建
* ==========================================
sum wage educ exper female   // 对主要变量进行描述性统计

* 检查是否存在异常值或缺失值
browse if missing(wage) | missing(educ)

* 生成新变量：对数工资和经验平方
gen ln_wage = ln(wage)
gen exper_sq = exper^2

* ==========================================
* 3. 描述性统计
* ==========================================
* 生成包含主要变量的描述性统计表格
estpost sum ln_wage educ exper female
esttab using "descriptive_stats.rtf", replace

* ==========================================
* 4. 可视化分析
* ==========================================
* 绘制受教育年限与对数工资的散点图及拟合线
twoway (scatter ln_wage educ) (lfit ln_wage educ), ///
    title("受教育年限与对数工资的关系") ///
    ytitle("对数工资 (ln(wage))") ///
    xtitle("受教育年限 (Years)") ///
    legend(label(1 "观测值") label(2 "拟合线"))
graph export "scatter_plot.png", replace  // 导出图片

* ==========================================
* 5. 回归分析
* ==========================================

* 模型1：最简单的双变量模型
reg ln_wage educ
estimates store model1

* 模型2：加入工作经验及其平方项（标准的明瑟方程）
reg ln_wage educ exper exper_sq
estimates store model2

* 模型3：在模型2基础上加入性别变量
reg ln_wage educ exper exper_sq female
estimates store model3

* ==========================================
* 6. 输出回归结果表格
* ==========================================
esttab model1 model2 model3 using "regression_results.rtf", replace ///
    b(3) se(3) ///
    r2(3) ar2(3) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    title("教育回报率回归结果") ///
    mtitles("模型1" "模型2" "模型3") ///
    addnotes("括号内为标准误；* p<0.10, ** p<0.05, *** p<0.01")

* 在Stata结果窗口直接查看
esttab model1 model2 model3

* ==========================================
* 7. 结束分析
* ==========================================
log close                        // 关闭日志
save "analysis_data.dta", replace  // 保存处理后的数据
clear all
exit
