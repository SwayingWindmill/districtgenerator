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

## 当前能力清单

以下清单基于当前仓库中的 `districtgenerator/classes`、`examples` 与本地示例执行结果整理，描述的是现在代码已经具备的能力，而不是计划功能。

### 1. 场景与配置建模

- 可通过场景 CSV 为每栋建筑输入基础属性，并通过 `.env.CONFIG.*` 文件覆盖默认配置。
- 可配置地点、德国邮编、TRY2015 / TRY2045 测试参考年、时间分辨率、聚类参数、经济参数、集中式与分散式设备参数。
- 支持批量读取多个 `.env` 配置文件，顺序执行多个场景。

### 2. 环境与气象数据生成

- 可根据邮编匹配站点并加载 DWD 测试参考年天气数据。
- 可生成室外温度、直散射太阳辐照、风速、湿度、气压、土壤温度等环境时序。
- 可根据位置和朝向计算建筑各朝向太阳辐射。

### 3. 建筑类型与建筑模型

- 住宅建筑已明确支持：`SFH`、`TH`、`MFH`、`AB`。
- 非住宅建筑已明确支持：`OB`、`SC`、`GS`、`RE`。
- 住宅建筑可通过 TEASER + TABULA 自动补全围护结构、面积、楼层、材料等热工参数。
- 非住宅建筑可通过仓库内 archetype 数据生成围护结构模型。
- 热工模型支持 `5R1C` 与 `7R2C`；其中非住宅当前实际走 `5R1C`。

### 4. 用户行为与需求曲线生成

- 可生成年尺度占用曲线、照明与设备用电曲线、生活热水曲线、内部得热曲线。
- 可计算空间采暖需求曲线。
- 当场景中启用 `cooling=1` 时，可计算制冷需求曲线。
- 可生成电动车与燃油车相关曲线，包括车辆可用性、充电需求、燃油消耗等。

### 5. 设备定容与可再生能源

- 可为单栋建筑的分散式设备进行初步定容，包括热泵、锅炉、燃料电池、CHP、电加热器、储热、水箱、电池、EV 等。
- 可计算建筑侧 PV / STC 的理论发电或产热曲线。
- 若场景包含 `heat_grid` 建筑，可进一步进入集中式能源系统计算流程。

### 6. 社区级聚类、优化与评估

- 可对全年时序做聚类压缩，用于后续优化计算。
- 可基于 Pyomo 执行社区级设备运行优化。
- 可对集中式能源中心进行设备选型与容量优化。
- 可计算 KPI，包括峰值负荷、谷峰差、购售电量、覆盖率、成本、CO2 排放等。
- 可输出 PDF 证书，总结社区参数与 KPI。

### 7. 结果输出与可视化

- 可将建筑需求结果写入 `results/demands`。
- 可保存建筑侧与中心侧的发电曲线。
- 可生成需求与发电相关图表。
- 可保存/加载社区对象的 pickle 结果。

## 当前验证状态与限制

### 已验证的示例链路

- `e1_initialize_datahandler.py`：可执行。
- `e2_generate_environment.py`：可执行。
- `e3_initialize_buildings.py`：可执行。
- `e4_generate_buildings.py`：可执行。

### 当前已知限制

- `e5_generate_demands.py` 在当前代码下可能在写入 Excel 结果时失败，错误表现为 `zipfile.BadZipFile`。这说明需求曲线计算主流程已进入执行，但结果落盘为 Excel 仍有稳定性问题。
- `generateDistrictComplete()` 中，当场景提供建筑坐标时，会调用 `generateNetwork()` 和 `optimization_heatingnetwork()`；当前仓库中未找到这两个方法定义，因此带几何坐标的热网优化分支目前不能视为已完整实现。
- README 与配置中列出了 `MFH+GR`、`AB+GR`、`MFH+RE`、`AB+RE` 等混合用途类型，但当前仓库内未明确验证其 archetype 数据和完整流程可用性，因此不建议将其视为已确认支持的建筑类型。

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
