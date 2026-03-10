# DistrictGenerator 中文使用指南

## 1. 项目概述

DistrictGenerator 是一个面向社区能源系统建模的 Python 项目。它的核心目标不是做 BIM 级建筑仿真，而是在较低输入门槛下，快速生成社区或建筑级的时序需求数据，并进一步支持设备定容、聚类优化和 KPI 评估。

结合当前仓库中的代码、示例和测试，这个项目更适合以下场景：

- 批量生成多栋建筑的电力、生活热水、内部得热、空间采暖和制冷需求曲线
- 在社区尺度上评估分散式或集中式供能方案
- 对不同气候、时间分辨率、设备配置和能源价格参数做情景对比
- 为后续优化模型提供建筑侧需求输入

当前实现的几个重要边界：

- 采暖/制冷需求是按建筑级输出，不是按房间级输出
- 住宅建筑支持 `5R1C` 和 `7R2C` 热工模型
- 非住宅建筑当前实际走 `5R1C`
- 仓库内测试主要覆盖到示例 `e1` 到 `e5`

## 2. 目录结构

建议先熟悉以下目录：

```text
districtgenerator/
├─ districtgenerator/
│  ├─ classes/           # Datahandler、Envelope、Users、KPI 等核心类
│  ├─ functions/         # 聚类、热工模型、优化相关函数
│  ├─ data_handling/     # 配置模型与全局配置加载
│  └─ data/              # 场景、天气、默认配置、参考数据
├─ examples/             # e1 ~ e9 示例工作流
├─ tests/                # unittest 回归测试
├─ docs/                 # 文档与说明
├─ README.md             # 项目概览
└─ pyproject.toml        # 项目元数据
```

最重要的几个文件：

- `districtgenerator/classes/datahandler.py`：主入口类，串起环境、建筑、需求、优化和 KPI 计算
- `districtgenerator/data/.env.CONFIG.EXAMPLE`：默认示例配置
- `districtgenerator/data/scenarios/example_decentral.csv`：分散式示例场景
- `districtgenerator/data/scenarios/example_central.csv`：集中式示例场景
- `examples/e1_...` 到 `examples/e9_...`：推荐的学习顺序

## 3. 环境准备与安装

### 3.1 Python 版本

建议使用 Python 3.11 及以上版本。

### 3.2 安装方式

在仓库根目录执行：

```bash
python -m pip install -e .
```

如果你只想先验证项目是否能跑通，建议再执行一次示例测试：

```bash
python -m unittest tests.test_examples
```

### 3.3 文档构建

如果你需要构建 Sphinx 文档：

```bash
python -m pip install -r docs/requirements.txt
cd docs
make html
```

Windows 下也可以执行：

```powershell
.\docs\make.bat html
```

## 4. 项目使用思路

这个项目的基本使用方式有两种：

### 方式 A：按步骤执行

适合第一次上手，便于理解每一步产物。

典型顺序如下：

1. 初始化 `Datahandler`
2. 生成环境数据 `generateEnvironment()`
3. 初始化建筑 `initializeBuildings()`
4. 生成建筑热工与用户对象 `generateBuildings()`
5. 生成需求曲线 `generateDemands()`
6. 如有需要，再执行优化与 KPI 计算

### 方式 B：一键生成完整社区

适合已经熟悉配置后直接做场景计算。

对应接口：

```python
data.generateDistrictComplete(calcUserProfiles=True, saveUserProfiles=True)
```

这个方法内部会依次调用：

- `generateEnvironment()`
- `initializeBuildings()`
- `generateBuildings()`
- `generateDemands()`
- `designDecentralDevices(...)`

如果场景里包含 `heater=heat_grid` 的建筑，还会继续进入集中式热网/能源中心相关流程。

## 5. 核心对象说明

### 5.1 Datahandler

`Datahandler` 是整个项目的主入口。初始化时会加载：

- 场景 CSV
- 站点参数
- 时间参数
- 建筑设计参数
- 物性参数
- 分散式设备参数
- 集中式设备参数
- 经济参数
- 日历与假日参数

常见初始化方式：

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_decentral",
    env_path=".env.CONFIG.EXAMPLE"
)
```

说明：

- `scenario_name` 对应 `districtgenerator/data/scenarios/<scenario_name>.csv`
- `env_path` 可以写相对路径，也可以写绝对路径
- 如果不传 `resultPath`，结果默认写到 `districtgenerator/results`

### 5.2 district

`data.district` 是项目运行过程中的核心容器。它是一个列表，每个元素对应一栋建筑，常见结构包括：

- `building["buildingFeatures"]`：来自场景 CSV 的原始建筑属性
- `building["envelope"]`：建筑热工与围护结构对象
- `building["user"]`：用户行为、占用、需求曲线等对象
- `building["thermal_model"]`：当前建筑采用的热工模型

### 5.3 envelope

`envelope` 对象负责保存建筑热工参数，例如：

- 外墙、屋面、地面和窗面积
- 材料层构成
- 热容、传热系数、换气参数
- 设计热负荷、双能源点热负荷、热限负荷

住宅建筑的 envelope 来自 TEASER + TABULA archetype，非住宅建筑来自仓库内建的 archetype 数据。

### 5.4 user

`user` 对象负责生成与用户行为相关的曲线，包括：

- `occ`：占用曲线
- `elec`：用电曲线
- `dhw`：生活热水热需求
- `gains`：内部得热
- `heat`：空间采暖需求
- `cooling`：制冷需求

## 6. 输入数据准备

项目至少需要两类输入：

1. 场景文件 `scenario.csv`
2. 配置文件 `.env.CONFIG.*`

### 6.1 场景文件位置

默认放在：

```text
districtgenerator/data/scenarios/
```

例如仓库内已有：

- `example_decentral.csv`
- `example_central.csv`
- `example_decentral_freiburg.csv`

### 6.2 场景文件格式

场景文件是使用分号分隔的 CSV。示例 `example_decentral.csv` 内容如下：

```csv
id;building;year;retrofit;construction_type;night_setback;area;heater;cooling;EV;f_TES;f_BAT;f_PV1;f_PV2;f_STC;gamma_PV;ev_charging
0;SFH;1960;0;2;0;140;HP;0;0;35;1;0.2;0.2;0;0;on_demand
1;MFH;1960;0;2;0;300;CHP;0;0;35;1;0;0;0;0;on_demand
2;AB;1960;0;2;0;300;BOI;0;1;35;1;0.2;0.2;0.2;0;on_demand
3;TH;1970;0;2;0;300;BOI;0;1;35;1;0.2;0.2;0.2;0;on_demand
```

### 6.3 场景字段说明

下表是当前项目中最常用、最关键的字段：

| 字段 | 含义 | 典型取值 |
|---|---|---|
| `id` | 建筑唯一编号 | 整数，建议不重复 |
| `building` | 建筑类型 | `SFH`、`TH`、`MFH`、`AB`、`OB`、`SC`、`GS`、`RE` |
| `year` | 建造年份 | 不小于 1860 |
| `retrofit` | 改造等级 | `0`、`1`、`2` |
| `construction_type` | 建筑热质量等级 | `0` 轻型，`1` 中型，`2` 重型 |
| `night_setback` | 是否夜间回退温度 | `0` 或 `1` |
| `area` | 建筑面积，单位 m² | 正数 |
| `heater` | 供热设备类型 | `HP`、`BOI`、`CHP`、`EH`、`FC`、`heat_grid` 等 |
| `cooling` | 是否考虑主动制冷 | `0` 或 `1` |
| `EV` | 电动车占比 | `0` 到 `1` |
| `f_TES` | 热储能规模系数 | 数值 |
| `f_BAT` | 电池规模系数 | 数值 |
| `f_PV1` / `f_PV2` | 两个屋面朝向的 PV 面积比例 | `0` 到 `1` |
| `f_STC` | 太阳能集热比例 | `0` 到 `1` |
| `gamma_PV` | 屋面方位角 | 度 |
| `ev_charging` | 充电策略 | `on_demand`、`intelligent`、`bi_directional` |

补充说明：

- `building` 字段必须使用项目约定的缩写
- 当前仓库 README 中还提到一些混合用途缩写，但是否全链路稳定可用，建议先自行验证
- 如果要进入几何热网分支，场景中通常还需要 `position` 信息

### 6.4 已确认的建筑类型

结合当前仓库实现，建议优先使用以下类型：

- 住宅：`SFH`、`TH`、`MFH`、`AB`
- 非住宅：`OB`、`SC`、`GS`、`RE`

其中：

- `SFH`、`TH` 更适合单户或单家庭场景
- `MFH`、`AB` 代表多户住宅，住宅需求会按整栋楼汇总，不会单独输出每一户

## 7. 配置文件说明

### 7.1 配置文件位置

默认配置文件在：

```text
districtgenerator/data/.env.CONFIG.EXAMPLE
districtgenerator/data/.env.CONFIG.FREIBURG
```

推荐做法：

- 不直接改 `.env.CONFIG.EXAMPLE`
- 复制一份作为自己的场景配置
- 只保留需要覆盖的参数

### 7.2 配置文件的作用

`.env.CONFIG.*` 文件中的参数会覆盖 `districtgenerator/data_handling/config.py` 里的默认值。

例如：

```env
SCENARIO_NAME=example_decentral
ZIP=10115
TRYYEAR=TRY2015
TRYTYPE=Jahr
TIMERESOLUTION=3600
DATALENGTH=31536000
T_SET_MIN=20.0
THERMAL_MODEL_TYPE=7R2C
```

### 7.3 最重要的配置项

#### 位置与气象

| 参数 | 说明 |
|---|---|
| `ZIP` | 邮编，用于匹配地点与气象数据 |
| `TRYYEAR` | 参考年，常见为 `TRY2015` 或 `TRY2045` |
| `TRYTYPE` | 参考年类型，常见为 `Jahr`、`Somm`、`Wint` |
| `TIMEZONE` | 时区 |
| `ALBEDO` | 地表反照率 |

#### 时间参数

| 参数 | 说明 |
|---|---|
| `TIMERESOLUTION` | 输出时间分辨率，单位秒 |
| `DATARESOLUTION` | 输入天气数据分辨率，默认通常保持 3600 |
| `DATALENGTH` | 仿真总时长，单位秒 |
| `CLUSTERLENGTH` | 单个聚类片段长度，默认 604800 秒，即 7 天 |
| `CLUSTERNUMBER` | 聚类数量 |

典型时间参数示例：

- 年度小时级：`TIMERESOLUTION=3600`，`DATALENGTH=31536000`
- 7 天 10 分钟：`TIMERESOLUTION=600`，`DATALENGTH=604800`
- 7 天 15 分钟：`TIMERESOLUTION=900`，`DATALENGTH=604800`

#### 建筑热工参数

| 参数 | 说明 |
|---|---|
| `T_SET_MIN` | 白天最小室内设定温度 |
| `T_SET_MIN_NIGHT` | 夜间最小室内温度 |
| `T_SET_MIN_FREE_DAY` | 非工作日最低温度 |
| `T_SET_MAX` | 最大室内温度 |
| `VENTILATION_RATE` | 通风换气率 |
| `THERMAL_MODEL_TYPE` | `5R1C` 或 `7R2C` |

注意：

- `7R2C` 对住宅可用
- 非住宅在当前实现中实际仍走 `5R1C`

#### 求解器参数

如果你要跑优化流程，还要关注：

| 参数 | 说明 |
|---|---|
| `SOLVER_NAME` | 当前示例默认是 `gurobi` |
| `SOLVER_EXECUTABLE` | 求解器可执行文件路径 |
| `SOLVER_OPTIONS__TIME_LIMIT` | 单次优化时间限制 |
| `SOLVER_OPTIONS__MIP_GAP` | MIP gap |
| `SOLVER_OPTIONS__THREADS` | 线程数 |

如果本机没有配置好 Gurobi，需求生成部分可能仍然能用，但优化部分不能保证可执行。

## 8. 从零开始的推荐工作流

### 8.1 第一步：初始化 Datahandler

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_decentral",
    env_path=".env.CONFIG.EXAMPLE"
)
```

此时已经完成：

- 读取场景 CSV
- 加载默认配置与覆盖配置
- 初始化结果路径

### 8.2 第二步：生成环境数据

```python
data.generateEnvironment()
```

这一步会生成：

- 室外温度 `data.site["T_e"]`
- 风速
- 湿度
- 气压
- 直射/散射太阳辐射
- 土壤温度
- 各朝向辐照信息

### 8.3 第三步：初始化建筑清单

```python
data.initializeBuildings()
```

这一步会把场景 CSV 中的每一行转成 `data.district` 中的一个建筑条目，并生成类似下面的唯一名称：

```text
example_decentral_0_SFH
example_decentral_1_MFH
```

### 8.4 第四步：生成建筑热工与用户对象

```python
data.generateBuildings()
```

这一步会完成：

- 住宅建筑通过 TEASER 生成 archetype 建筑
- 非住宅建筑通过项目内置原型数据生成围护结构
- 创建 `envelope`
- 创建 `user`
- 计算设计热负荷、双能源点负荷、热限负荷和设计冷负荷

### 8.5 第五步：生成需求曲线

```python
data.generateDemands(calcUserProfiles=True, saveUserProfiles=True)
```

这一步会生成：

- `elec`
- `dhw`
- `occ`
- `gains`
- `heat`
- `cooling`
- EV 相关曲线

说明：

- `calcUserProfiles=True` 表示重新计算用户行为与需求
- `saveUserProfiles=True` 表示将结果写入结果目录
- 该步骤使用线程并行按建筑计算

## 9. 最小可运行示例

下面给出一个最常用的“逐步执行”脚本：

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_decentral",
    env_path=".env.CONFIG.EXAMPLE"
)

data.generateEnvironment()
data.initializeBuildings()
data.generateBuildings()
data.generateDemands(calcUserProfiles=True, saveUserProfiles=True)

print(data.district[0]["user"].heat[:10])
print(data.district[0]["user"].elec[:10])
```

## 10. 单家庭 7 天、10 分钟示例

如果你的目标是“只生成一个家庭的 7 天需求，并且时间分辨率为 10 分钟”，这个项目是可以做到的，推荐按以下方式准备。

### 10.1 场景文件

新建一个场景文件，例如：

```text
districtgenerator/data/scenarios/house_7d.csv
```

内容示例：

```csv
id;building;year;retrofit;construction_type;night_setback;area;heater;cooling;EV;f_TES;f_BAT;f_PV1;f_PV2;f_STC;gamma_PV;ev_charging
0;SFH;1995;1;2;0;140;HP;0;0;35;0;0.2;0.2;0;0;on_demand
```

这里使用 `SFH`，因为项目中它代表单户住宅。

### 10.2 配置文件

新建配置文件，例如：

```text
districtgenerator/data/.env.CONFIG.HOUSE7D
```

内容示例：

```env
SCENARIO_NAME=house_7d
ZIP=10115
TRYYEAR=TRY2015
TRYTYPE=Jahr
TIMERESOLUTION=600
DATARESOLUTION=3600
DATALENGTH=604800
T_SET_MIN=20.0
T_SET_MIN_NIGHT=18.0
THERMAL_MODEL_TYPE=7R2C
```

### 10.3 运行脚本

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="house_7d",
    env_path=".env.CONFIG.HOUSE7D"
)

data.generateEnvironment()
data.initializeBuildings()
data.generateBuildings()
data.generateDemands(calcUserProfiles=True, saveUserProfiles=False, gen_cars=False)

house = data.district[0]

print("时间步数:", len(house["user"].heat))
print("采暖需求前10个点:", house["user"].heat[:10])
print("用电需求前10个点:", house["user"].elec[:10])
print("生活热水前10个点:", house["user"].dhw[:10])
```

结果点数应为：

```text
7 天 × 24 小时 × 6 个 10 分钟点 = 1008
```

### 10.4 需要注意的地方

- 如果你想指定“某一周”而不是“从年初开始的 7 天”，当前更稳妥的方式通常是先生成全年，再按索引切片
- 如果你使用 `MFH` 或 `AB`，结果会按整栋楼汇总，不是按单户输出
- 采暖需求是建筑级热区结果，不是房间级结果

## 11. 一键完整流程示例

如果你已经准备好了场景和配置，也可以直接走完整流程：

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_decentral",
    env_path=".env.CONFIG.EXAMPLE"
)

data.generateDistrictComplete(calcUserProfiles=True, saveUserProfiles=True)
```

这个接口适合：

- 快速批量生成需求
- 为设备定容做输入
- 进入社区级优化前的完整预处理

## 12. 社区优化与 KPI 评估

### 12.1 分散式场景

参考 `examples/e7_decentral_scenario_evaluation.py`：

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_decentral",
    env_path=".env.CONFIG.EXAMPLE"
)

data.generateDistrictComplete(calcUserProfiles=True, saveUserProfiles=False)
data.optimizationClusters()
data.calculateKPIs()
data.KPIs.create_certificate(data=data, result_path=data.resultPath)
```

### 12.2 集中式场景

参考 `examples/e8_central_scenario_evaluation.py`：

```python
from districtgenerator.classes import Datahandler

data = Datahandler(
    scenario_name="example_central",
    env_path=".env.CONFIG.EXAMPLE"
)

data.generateDistrictComplete(calcUserProfiles=True, saveUserProfiles=False)
data.optimizationClusters()
data.calculateKPIs()
```

### 12.3 求解器依赖

社区优化部分依赖 Pyomo 和外部优化求解器。示例配置默认使用 `gurobi`。如果你的环境没有安装并配置 Gurobi，需要先调整配置，否则优化相关步骤可能无法运行。

## 13. 批量运行多个配置

如果你要比较多个情景，可以参考 `examples/e9_exec_multiple_scenarios.py`。

基本思路是：

1. 准备多个 `.env.CONFIG.*` 文件
2. 放在同一个目录
3. 逐个加载
4. 对每个配置生成一套结果

这很适合做：

- 不同城市对比
- 不同 TRY 年份对比
- 不同温度设定值对比
- 不同时间分辨率对比
- 不同能源价格对比

## 14. 结果输出说明

### 14.1 默认结果目录

如果没有显式传入 `resultPath`，结果通常写到：

```text
districtgenerator/results/
```

仓库中也可以看到一些示例结果目录，如：

- `districtgenerator/results_preview`
- `districtgenerator/results_preview_20260305_153934`

### 14.2 需求结果

当 `saveUserProfiles=True` 时，项目会为每栋建筑写出一个 Excel 文件，通常包含以下工作表：

- `Electricity`
- `DHW`
- `Occupancy`
- `Gains`
- `heating`
- `cooling`
- 其他 EV 相关表

### 14.3 在代码中读取结果

最直接的方式是直接从对象读取：

```python
building = data.district[0]

heat = building["user"].heat
elec = building["user"].elec
dhw = building["user"].dhw
occ = building["user"].occ
gains = building["user"].gains
```

### 14.4 常见单位

大多数需求曲线在对象中以功率形式存储，常见单位是 W。

如果要换算成能量，通常需要乘以时间步长。

例如 1 小时分辨率下：

```python
kwh = power_W * 3600 / 3600 / 1000
```

对于任意时间分辨率：

```python
energy_kWh = power_W * timeResolution / 3600 / 1000
```

## 15. 可视化与绘图

需求生成后，可以使用示例 `e5_generate_demands.py` 中的做法，把时序数据转成 `pandas.DataFrame`，再进行：

- 月度汇总
- 峰值分析
- 柱状图
- 时序折线图

项目本身也提供 `data.plot(...)` 接口，但初次使用时更建议先直接读取 `data.district[0]["user"]` 下的数组，用 `pandas` 和 `matplotlib` 自己画图，更直观也更容易调试。

## 16. 测试与验证建议

### 16.1 回归测试

当前仓库中的 `tests/test_examples.py` 主要验证：

- `e1_initialize_datahandler`
- `e2_generate_environment`
- `e3_initialize_buildings`
- `e4_generate_buildings`
- `e5_generate_demands`

执行命令：

```bash
python -m unittest tests.test_examples
```

### 16.2 建议的最小自检项

每次修改配置或场景后，建议至少检查：

- `len(data.district)` 是否与场景建筑数一致
- `len(data.district[0]["user"].heat)` 是否等于 `DATALENGTH / TIMERESOLUTION`
- `data.district[0]["envelope"].heatload` 是否为正数
- `data.district[0]["user"].elec`、`dhw`、`occ` 是否都成功生成

## 17. 常见问题

### 17.1 为什么只提供了建筑级采暖需求，没有房间级结果？

因为当前仓库中的热工求解是按建筑等效热区做的，输出是建筑级 `heat` 序列，不是每个房间单独求解。

### 17.2 能不能生成单个家庭的 7 天需求？

可以。推荐使用单栋 `SFH` 场景，并把：

- `TIMERESOLUTION=600`
- `DATALENGTH=604800`

### 17.3 多户住宅能不能输出每一户的独立需求？

当前默认不会对外输出每一户的独立建筑需求结果，住宅结果主要按整栋楼汇总。

### 17.4 非住宅能不能使用 `7R2C`？

当前实现中，非住宅会回落到 `5R1C`，因为现有参数不足以支持完整的 VDI 6007 建模流程。

### 17.5 场景文件最小建造年份是多少？

当前仓库自带说明写明：最小建造年份为 `1860`。

### 17.6 优化为什么跑不起来？

优先检查以下几项：

- 求解器是否安装，例如 Gurobi
- `.env.CONFIG.*` 中的 `SOLVER_NAME` 是否正确
- 相关 license 是否可用
- 场景中设备字段是否填写完整

## 18. 当前已知限制与建议

根据当前仓库状态，建议注意以下几点：

- 示例测试主要覆盖到 `e1` 到 `e5`，后续优化链路需要你在本地进一步验证
- 需求结果写入 Excel 的流程在某些情况下可能出现兼容性问题，尤其是重复写入已有文件时
- 集中式热网的高级几何优化分支建议谨慎使用，首次跑通时优先从无坐标的简单热网分支开始
- 如果你只是想拿需求曲线，不必先进入优化流程，先跑到 `generateDemands()` 就够了

## 19. 推荐学习顺序

如果你是第一次接触这个项目，建议按下面顺序阅读和运行：

1. 看 `README.md`
2. 跑 `examples/e1_initialize_datahandler.py`
3. 跑 `examples/e2_generate_environment.py`
4. 跑 `examples/e3_initialize_buildings.py`
5. 跑 `examples/e4_generate_buildings.py`
6. 跑 `examples/e5_generate_demands.py`
7. 再根据需要看 `e6`、`e7`、`e8`、`e9`

## 20. 一句话总结

如果你的目标是：

- 快速生成建筑级需求曲线：用 `generateEnvironment()` + `initializeBuildings()` + `generateBuildings()` + `generateDemands()`
- 快速做完整情景计算：用 `generateDistrictComplete()`
- 做单家庭 7 天 10 分钟需求：用单栋 `SFH` 场景，并把 `TIMERESOLUTION=600`、`DATALENGTH=604800`
- 做房间级采暖：当前项目不原生支持，需要二次开发
