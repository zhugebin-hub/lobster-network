* ======================================================
* 项目：婚姻工资溢价分析
* 课程：计量经济学
* 作者：陈政道
* 日期：2026-06-09
* 数据：WAGE1（Wooldridge教材数据集）
* ======================================================

clear all
set more off
cap log close
log using "marriage_wage_premium.log", replace

* ==========================================
* 1. 导入数据
* ==========================================
use "WAGE1.DTA", clear
describe
codebook

* ==========================================
* 2. 数据清理与变量创建
* ==========================================
sum wage educ exper female married hours tenure

* 检查缺失值
browse if missing(wage) | missing(educ)

* 生成新变量
gen ln_wage = ln(wage)
gen exper_sq = exper^2
gen tenure_sq = tenure^2

* ==========================================
* 3. 描述性统计
* ==========================================
* 总体描述性统计
sum ln_wage educ exper female married hours tenure

* 婚姻状态分组统计
tabstat ln_wage educ exper, by(married) stat(mean sd min max n)

* ==========================================
* 4. 可视化分析
* ==========================================
* 婚姻状态与对数工资的箱线图
graph box ln_wage, over(married) ///
    title("Marriage Status and Log Wage") ///
    ytitle("Log Wage (ln(wage))")
graph export "marriage_boxplot.png", replace

* 工作经验与对数工资散点图（分婚姻状态）
twoway (scatter ln_wage exper if married==0, msymbol(oh) mcolor(blue)) ///
       (scatter ln_wage exper if married==1, msymbol(+) mcolor(green)) ///
       (lfit ln_wage exper if married==0, lpattern(dash) lcolor(blue)) ///
       (lfit ln_wage exper if married==1, lcolor(green)), ///
    title("Experience, Marriage and Log Wage") ///
    ytitle("Log Wage") xtitle("Years of Experience") ///
    legend(label(1 "Unmarried") label(2 "Married") ///
           label(3 "Unmarried fit") label(4 "Married fit"))
graph export "marriage_scatter.png", replace

* ==========================================
* 5. 回归分析 - 逐步加入控制变量
* ==========================================

* 模型1：仅婚姻变量
reg ln_wage married
estimates store model1

* 模型2：加入教育
reg ln_wage married educ
estimates store model2

* 模型3：加入教育、经验及经验平方
reg ln_wage married educ exper exper_sq
estimates store model3

* 模型4：完整模型（加入性别和任期）
reg ln_wage married educ exper exper_sq female tenure tenure_sq
estimates store model4

* ==========================================
* 6. 输出回归结果表格
* ==========================================
esttab model1 model2 model3 model4 using "marriage_regression_results.rtf", replace ///
    b(3) se(3) ///
    r2(3) ar2(3) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    title("婚姻工资溢价回归结果") ///
    mtitles("模型1" "模型2" "模型3" "模型4") ///
    addnotes("括号内为标准误；* p<0.10, ** p<0.05, *** p<0.01")

* 在结果窗口直接查看
esttab model1 model2 model3 model4

* ==========================================
* 7. 检验与稳健性分析
* ==========================================

* 异方差检验
estat hettest

* 多重共线性检验（方差膨胀因子）
estat vif

* ==========================================
* 8. 结束分析
* ==========================================
log close
save "marriage_analysis_data.dta", replace
clear all
exit
