![E.ON EBC RWTH Aachen University](./img/EBC_Logo.png)

# DistrictGenerator

[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)
[![Documentation](https://rwth-ebc.github.io/districtgenerator/master/docs/doc.svg)](https://rwth-ebc.github.io/districtgenerator/master/docs/README.html)

DistrictGenerator 是一个基于 Python 的开源工具，面向城市规划人员、能源供应商、住房协会、工程与建筑专业团队，以及科研机构。该工具可为社区能源系统的设计与运行提供关键的负荷需求信息，帮助用户识别并评估供能协同措施。

DistrictGenerator 的核心创新在于：将完整城市建筑存量映射为社区模型，并自动计算建筑负荷曲线与分布式能源系统规模。工具集成了多个开源数据库与工具，例如 [TEASER](https://github.com/RWTH-EBC/TEASER) 与 [richardsonpy](https://github.com/RWTH-EBC/richardsonpy)。

本项目由 [RWTH Aachen University, E.ON Energy Research Center, Institute for Energy Efficient Buildings and Indoor Climate](https://www.ebc.eonerc.rwth-aachen.de/cms/~dmzz/E-ON-ERC-EBC/?lidx=1) 开发维护。

## 研究动机

在社区规划早期阶段，电力、采暖、生活热水与占用等关键时序数据通常缺失，导致能源系统评估不准确。DistrictGenerator 旨在降低建模门槛，提升社区级跨能种系统分析的可用性，尤其强调不同建筑用途之间的协同潜力。主要贡献包括：

- 开源且低输入门槛：依托预设参数与默认值，快速生成时序负荷，并按标准完成分散式热源初步定容。
- 支持自下而上的城市结构建模：可在社区尺度构建足够细致的分析模型。
- 支持运营优化与 KPI 输出：便于比较不同技术组合与渗透率下的社区供能方案。

## 快速开始

### 安装 DistrictGenerator

先克隆仓库：

```bash
git clone https://github.com/RWTH-EBC/districtgenerator
```

再安装项目：

```bash
pip install -e .
```

安装完成后，可参考 [examples](docs/EXAMPLES.md) 学习各模块用法。

### 最小必需输入数据

要生成社区模型，至少需要每栋建筑的基础信息。最小输入集依据 [TABULA archetype approach](https://webtool.building-typology.eu/#bm) 定义：

- `id`：建筑 ID（连续编号即可）
- `building`：建筑类型（`SFH`、`TH`、`MFH`、`AB`、`OB`、`SC`、`GS`、`RE`、`MFH+GR`、`AB+GR`、`MFH+RE`、`AB+RE`）
- `year`：建造年份
- `construction_type`：建筑热质量（`0` 轻型、`1` 中型、`2` 重型）
- `retrofit`：TABULA 改造等级（`0` 现状、`1` 常规改造、`2` 深度改造）
- `area`：参考建筑面积（m²）
- `night_setback`：夜间温度回退（`0` 否、`1` 是）
- `heating`：供热设备（`HP`、`EH`、`CHP`、`FC`、`BOI`、`STC`、`heat_grid`）
- `EV`：电动车占比（0 到 1）
- `fTES`：热储能规模（L/kW，按供热设备容量）
- `fBAT`：电池规模（Wh/W_PV）
- `fPV`：屋顶光伏覆盖比例
- `fSTC`：屋顶太阳能热利用覆盖比例
- `gammaPV`：屋顶方位角（度，`0°` 表示朝南）
- `EV_charging`：充电策略（`bidirectional`、`on-demand`、`intelligent`）

可使用示例模板：`districtgenerator/data/scenarios/example.csv`。

### 其他可选输入

在 [data](https://github.com/RWTH-EBC/districtgenerator/tree/JOSS_submission/districtgenerator/data) 目录中提供了大量默认数据。以下内容可按需求调整：

- `design_building_data.json`：室内温度上下限、通风率
- `site_data.json`：测试参考年与站点条件
- `time_data.json`：时间分辨率

以下文件为固定参数或外部数据，通常不建议修改：

- `design_weather_data.json`：DWD 德国 16 个气候区数据
- `physics_data.json`
- `dhw_stochstical.xlsx`

天气数据位于 [weather](https://github.com/RWTH-EBC/districtgenerator/tree/JOSS_submission/districtgenerator/data/weather)。

## DistrictGenerator 结构

![Library Structure](img/Struktur_Quartiersgenerator.png)

## DistrictGenerator 工作流程

该工具将多个开源工具和数据库整合为统一流程。用户输入最小化建筑信息后，系统会逐步完成环境与建筑参数补全，并生成时序负荷：

1. 输入社区建筑数量与基础信息（类型、建造年代、改造等级、面积等）
2. 可选修改站点位置、时间分辨率、气象参考年
3. 使用 [TEASER](https://rwth-ebc.github.io/TEASER/main/docs/index.html) 结合 [TABULA WebTool](https://webtool.building-typology.eu/#bm) 完成建筑几何与材料参数补全
4. 使用 [richardsonpy](https://github.com/RWTH-EBC/richardsonpy) 生成随机占用与用电曲线
5. 基于 pyCity 相关方法生成生活热水曲线
6. 基于 DIN EN ISO 13790:2008-09 的 5R1C 简化模型计算采暖曲线

![Library Structure](img/Workflow_DistrictGenerator.png)

## 输出结果

DistrictGenerator 可输出每栋建筑的时序需求文件（Excel/CSV 工作流），包括：

- `heat`：空间采暖需求
- `dhw`：生活热水需求
- `elec`：照明与家电用电需求
- `gains`：内部得热
- `occ`：占用曲线

默认结果保存在 `results/demands` 目录，功率单位为 W。

## 示例与功能测试

安装后可先查看 [examples](docs/EXAMPLES.md)。

若要验证工具可执行性，可运行 `tests/test_examples.py`。该功能测试会串行执行示例流程并检查关键输出。

## 如何贡献

欢迎通过 Issue 反馈问题、讨论需求或提交改进。

- 提问或报告问题：请在仓库中创建 Issue
- 提交功能：请创建 Pull Request 并指派评审

## 作者

- [Joel Schoelzel](https://www.ebc.eonerc.rwth-aachen.de/cms/e-on-erc-ebc/das-institut/mitarbeiter/digitale-energie-quartiere/~obome/schoelzel-joel/?allou=1)（通讯作者）
- [Tobias Beckhoelter](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team6/~scaj/Beckhoelter-Tobias/)
- [Carla Wueller](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Digitale-Energie-Quartiere/~beoyus/Wueller-Carla/)
- [Rawad Hamze](https://www.ebc.eonerc.rwth-aachen.de/cms/e-on-erc-ebc/das-institut/mitarbeiter/team6/~birwyf/hamze-rawad/?lidx=1)

## Alumni

- Sarah Henn

## 参考文献

- J. Schoelzel, S. Henn, R. Streblow, D. Mueller. Evaluation of Energy Sharing on a Local Energy Market Through Comparison of Energy Management Techniques. 36th International Conference on Efficiency, Cost, Optimization, Simulation and Environmental Impact of Energy Systems. https://doi.org/10.52202/069564-0307
- J. Schoelzel, T. Beckhoelter, S. Henn, C. Wueller, R. Streblow, D. Mueller. Districtgenerator: A Novel Open-Source Webtool to Generate Building-Specific Load Profiles and Evaluate Energy Systems of Residential Districts. 37th International Conference on Efficiency, Cost, Optimization, Simulation and Environmental Impact of Energy Systems.
- C. Wueller, J. Schoelzel, R. Streblow, D. Mueller. Optimizing Local Energy Trading in Residential Neighborhoods: A Price Signal Approach in Local Energy Markets. 37th International Conference on Efficiency, Cost, Optimization, Simulation and Environmental Impact of Energy Systems.

## 许可证

DistrictGenerator 由 RWTH Aachen University, E.ON Energy Research Center, Institute for Energy Efficient Buildings and Indoor Climate 按 [MIT License](docs/about/LICENSE.md) 发布。

## 致谢

DistrictGenerator 在公开资助项目 “BF2020 Begleitforschung ENERGIEWENDEBAUEN - Modul Quartiere”（资助编号：03EWB003B）框架下开发，并获得德国 BMWK（联邦经济与气候保护部）支持。

<img src="https://www.innovation-beratung-foerderung.de/INNO/Redaktion/DE/Bilder/Titelbilder/titel_foerderlogo_bmwi.jpg?__blob=normal" width="200">
