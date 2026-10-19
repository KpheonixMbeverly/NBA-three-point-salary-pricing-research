# NBA 如何逐步为三分技能定价：项目简介

**作者：Yukai Zhao、Wenchen Ju｜宁波诺丁汉大学经济学院**

本仓库提供最终海报主模型的 **Python 可复现版本**，研究 2000–2025 年球员常规赛三分能力与相对薪资的关系，按照 **后卫、前锋、中锋 × 四个时代** 分为 12 组估计，采用球队与年份固定效应以及按球员聚类的标准误。

英文 [README](README.md) 是完整的项目说明和运行手册；项目的实证方法和限制详见 [方法说明](docs/METHODOLOGY_AND_LIMITATIONS.md)。

## 研究海报

以下是作者提供的最终海报。点击图片可打开[完整 PDF](assets/research_poster.pdf)。如需公开仓库，请先确认海报模板、球员照片等第三方素材的使用与再分发许可。

<a href="assets/research_poster.pdf"><img src="assets/research_poster.png" alt="NBA 三分技能薪资定价研究海报" width="900"></a>

## 核心发现

在现有样本与模型设定下，后卫的三分能力系数各时期显著为正；前锋在后期的正相关更明显；中锋系数相对较小且不稳定。**这属于控制其他变量后的统计相关性，不等于三分能力对薪资的因果效应。**

## 运行

原始球员数据 CSV **已经包含在仓库内**：`data/raw/NBA Player Stats and Salaries_2000-2025.csv`，无需再手动添加。请注意：原始数据的最终来源及公开再分发授权尚未核实，上传到公共 GitHub 仓库前应先确认许可。

```bash
pip install -e '.[dev]'
nba-pricing audit --input 'data/raw/NBA Player Stats and Salaries_2000-2025.csv'
nba-pricing run --input 'data/raw/NBA Player Stats and Salaries_2000-2025.csv' --compare data/reference/poster_nearmax_coefficients.csv
```

会输出完整回归系数 CSV、模型摘要、时代主线图、十二宫格控制后偏回归图及紧凑回归表。

## 需要特别注意

- 历史计算先按 `Salary / SalaryCap ≥ 1.5%` 筛选，随后计算年平均薪资、球队薪资总和和标准化指标。因此“球队薪资压力”**不是经过核验的真实完整球队 payroll**。
- `NearMax25 = 1` 当球员薪资占工资帽比例不低于 25%，属于简化代理；它本身由因变量薪资构造，加入后 R² 提高**不代表纠正了顶薪制度的内生性或截断问题**。
- “三年滚动”在既往脚本中实际上是每位球员最近三条保留记录的均值，而非严格连续三年；同名球员和多球队记录也可能影响结果。
- **球队上一赛季季后赛层级**只作为可选扩展；目前没有经过独立验证的完整球队季后赛表，代码不会把缺失值伪装成“未进入季后赛”。真正的“球员上一赛季季后赛表现”需要另行提供球员级数据。
- 本次 ZIP **已包含**作者提供的原始球员 CSV，且 `.gitignore` 已允许追踪该文件。**这不代表拥有公开再分发许可**；如果仓库计划公开，应先核实数据来源与授权。

代码库复现了历史结果，但不会把仍有缺陷的历史设定包装成经严格识别的因果结论。
