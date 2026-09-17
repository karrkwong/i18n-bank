# Banking App 界面国际化走查与本地化标准规范 (i18n_BANK Specification)

> **数值单一事实源**：缺陷码、合规层级与排版预算的权威数值以 [`references/rules.json`](rules.json) 为准，术语决策以 [`references/termbase.csv`](termbase.csv) 为准。本文件阐述判定逻辑与依据；若数值与 rules.json 不一致，以 rules.json 为准并视为本文件缺陷。

## 1. 概述与适用范围
本规范为银行及金融类 App（包括移动端 iOS/Android、H5 及小程序）界面文案走查（LQA - Localization Quality Assurance）与多语言翻译的权威基准。本规范直接指导 `i18n_BANK` 走查流程，确保金融专业度、监管合规性、前端工程可用性与本地化用户体验的高度平衡。

---

## 2. 核心原则体系

### 2.1 监管与权威性层级 (Hierarchy of Authority)
在文案审查与翻译建议中，必须严格遵循以下权威层级：
1. **P0 级 - 主权国家/地区央行法定表述 (Regulatory Mandatory)**：
   - 必须强制遵循目标市场央行（如新加坡 MAS、马来西亚 BNM、中国香港 HKMA、泰国 BOT、印尼 BI）颁布的法定规范。
   - 典型对象：快速支付系统（PayNow, DuitNow, FPS, PromptPay, BI-FAST）、牌照与法人名称、法定消费者披露（APR/EIR、PDS 提示）。
   - **约束：严禁擅自意译、缩写或改写。**
2. **P1 级 - 全球/区域金融行业通用标准 (Industry Standard)**：
   - 遵循 ISO 20022、SWIFT MT/MX、卡组织（Visa/Mastercard Rules）标准。
   - 典型对象：IBAN, BIC/SWIFT Code, CVV/CVC, Cut-off Time, Beneficiary, Current Account, Fixed Deposit。
3. **P2 级 - 本地化心智表达与惯用语 (Localization Best Practice)** `R-GEN-003`：
   - 符合当地金融消费者的日常理解习惯。区分英联邦英语体系（en-GB/en-SG/en-MY）与美式英语体系（en-US）。优先采用英式拼写（如 *Instalment*, *Cheque*, *Authorised*）。
4. **P3 级 - 基础前端交互用语 (General UI)**：
   - 基础交互按钮、导航、Toast 等，不涉及金融法律风险，侧重简洁明了。

---

### 2.2 前端排版与组件精炼原则 (UI Layout & Conciseness Rules)

#### 标准线一：功能组件一字精炼 (Single-Word Action) `R-GEN-001`
在网格宫格（Grid Tile）、操作按钮（CTA Button）、Tab 标签等空间极度受限组件中，文字尽量压缩为一个核心动词/名词。
- 例：`Card Application` → **`Apply`**
- 例：`Card Activation` → **`Activate`**
- 例：`Bill Enquiry` → **`Bill`**
- 例：`Repay Immediately` → **`Repay`**
*(注：标准金融专有名词如 FPS, DuitNow, IBAN, Instalment 等不受此限)*

#### 标准线二：语境省略，拒绝层级冗余 (Context-Aware Omission) `R-GEN-002`
当组件已经处于明确的父级业务分区或功能模块下时，组件文案不得重复所属分类名称。
- 在 **Cards（信用卡/卡片）** 分区下：使用 `Apply`（非 Card Application），使用 `Activate`（非 Card Activation）。
- 在 **Transfer（转账）** 分区下：使用 `Local`（非 Local Transfer），使用 `Overseas`（非 Overseas Remittance）。
- 在 **Accounts（账户）** 分区下：使用 `Payroll`（非 Payroll Service），使用 `Scheduled`（非 Scheduled Transfer）。
- 去除无实际意义的泛化后缀（如 *Service*, *Management*, *Function*）。

---

## 3. 走查报告输出标准格式

每一次走查结果必须严格输出为 Markdown 表格，包含以下 8 项字段：

| 字段名称 | 说明 | 约束要求 |
| :--- | :--- | :--- |
| **#** | 问题序号 | 顺序递增数字，与截图红框编号强绑定 |
| **组件位置** | 界面物理定位 | 明确所在组件与层级（如：首页九宫格02、账户详情卡片标题） |
| **界面现状** | 走查发现的原文字符 | 必须忠实还原现场（含折行、断词、省略号） |
| **缺陷类型** | 固化的 7 大枚举类型 | 必须属于标准枚举代码（见第 4 节） |
| **严重级** | 问题影响程度 | 高 (High) / 中 (Medium) / 低 (Low)；定级与升降级遵循 3.1 仲裁规则 |
| **修复建议 (Fix)** | 推荐的新译法/新文案 | 符合金融标准与组件字符限制的最优解 |
| **合规性评估** | 法律合规与监管分类 | 必须在 4 级准则中选一（见第 5 节） |
| **规则与依据说明** | 判定理由与权威追溯 | 明确说明规则编号（R-GEN / R-DEF / R-LAY）、语境省略依据或引用的央行/行业标准 |

### 3.1 严重级仲裁规则 (Severity Arbitration) `R-GEN-004`
以 `rules.json` 中各缺陷码的 `default_severity` 为基线定级：
- **强制升级**：字符串处于支付 / 确认 / 法定披露链路，或涉及 MANDATORY 词条、触发合规预警时，升一级。
- **降级须说明**：纯装饰性、无信息损失场景可降一级，但必须在「规则与依据说明」列写明理由。

---

## 4. 固化缺陷类型体系 (7 Defect Codes)

为便于自动化统计与质量度量，走查缺陷严格限定为以下 7 类；各缺陷码的稳定编号（`R-DEF-001` ~ `R-DEF-007`）、默认严重级与机器初筛模式统一定义于 `rules.json`。`typical_pattern` 命中仅作机器初筛候选提示，命中后必须按下列判定标准复核定性并剔除误报，方可写入走查报告：

1. **`TRUNCATION`（界面截断）** `R-DEF-001`
   - **判定**：文本超长被系统以 `...` 截断，或文本超出组件渲染边界被裁剪，导致核心信息丢失。
2. **`LINE_BREAK`（不良折行/断词）** `R-DEF-002`
   - **判定**：英文单词在非连字符处被物理拆裂（如 `Transactio\nns`），或无谓换行导致卡片高度破坏视觉对齐；连字符处折行（如 `Inter-\nnational`）不视为缺陷。
3. **`MIXED_LANG`（语言混排/漏翻）** `R-DEF-003`
   - **判定**：当前语言界面残留源语言（如未翻译中文），或未经系统化定义的多语种杂合串（如 `FPS快速支付Transfer`、泰文界面夹杂英文 `แอป Transfer`）。检测覆盖中日韩文与泰文等非拉丁文字；马来语 / 印尼语等拉丁字母语种无法按文字范围识别，须采用源串残留比对策略。
4. **`REDUNDANCY`（文案冗余/未精炼）** `R-DEF-004`
   - **判定**：未遵循语境省略，重复分类前缀（如 Cards 模块下的 `Card Application`）或带有冗余修饰词。
5. **`FORMAT_GRAMMAR`（格式与语法规范）** `R-DEF-005`
   - **判定**：单复数语法错误（如 `1 accounts`）、标点符号错误（孤儿标点、全半角混用、冒号后缺空格）、大小写混乱。
6. **`COMPLIANCE`（术语/合规不符）** `R-DEF-006`
   - **判定**：未采用目标国央行法定表述或行业标准术语，或产生误导性金融承诺（如利率未注明年化、保障性表达违规）。
7. **`PLACEHOLDER`（代码/占位符异常）** `R-DEF-007`
   - **判定**：动态变量名直接外露（如 `{0}`, `%s`），或多语言语序硬拼接导致语法颠倒。

---

## 5. 合规性评估 4 级判定标准

每个修复建议必须标注以下四类之一：

* **`[法定合规]` (Regulatory Mandatory)**：
  - 适用：受国家央行、金融监管条例直接约束的专有名词（如 MAS PayNow, BNM DuitNow, HKMA FPS, 法定反洗钱/KYC 字段）。
  - 处理要求：**严禁任意发挥，必须严格与官方标准字字对齐。**
* **`[行业标准]` (Industry Standard)**：
  - 适用：遵循 ISO 20022、SWIFT、国际卡组织规则的银行通行用语（如 IBAN, Cut-off Time, Fixed Deposit, Instalment）。
  - 处理要求：遵循金融行业惯例，避免产生跨行歧义。
* **`[基础表达]` (General UI / Low Risk)**：
  - 适用：通用前端交互按钮、导航标签、提示性文案（如 Apply, Confirm, Details, Next）。
  - 处理要求：侧重空间平衡与用户易读性，无合规监管处罚风险。
* **`[合规预警]` (Compliance Risk Alert)**：
  - 适用：原有文案或轻率修改可能涉嫌误导用户、遗漏监管强制披露要求（如贷款利率未标明 EIR/APR、把预期收益简化为确定性收益）。
  - 处理要求：必须标注提示业务合规团队二次复审。

---

## 6. 东南亚多语言扩展与排版预算体系

### 6.1 前端组件字符限制矩阵 (Expansion & Constraint Matrix)
针对当前英文及未来东南亚语种（马来语、印尼语、泰语、越南语）的长度膨胀，制定各组件标准阈值：

| 组件类型 | 建议行数 | 英文上限 (Chars) | 东南亚扩展预算 (Chars) | 推荐语法形态 |
| :--- | :--- | :--- | :--- | :--- |
| **底部导航 (Tab Bar)** | 单行 | ≤ 10 | ≤ 14 | 单个核心名词 (Accounts, Pay, Cards) |
| **金刚区宫格 (Grid Tile)** | ≤ 2 行 (单行优先) | ≤ 12 (每行≤6) | ≤ 16 | 精炼动词优先 (Apply, Pay, Transfer) |
| **主按钮 (Primary CTA)** | 单行 | ≤ 14 | ≤ 20 | 祈使动词短语 (Confirm, Pay Now) |
| **表单项标签 (Form Label)** | 单行 | ≤ 16 | ≤ 24 | 名词短语 (Account No., Mobile No.) |
| **卡片/列表标题 (List Title)** | 单行 | ≤ 22 | ≤ 30 | 简练名词短语 (Demand Deposit - HKD) |
| **页面主标题 (Page Header)** | 单行 | ≤ 24 | ≤ 32 | 完整业务概念 (Card Application) |
| **弹窗与提示 (Dialog / Toast)**| ≤ 2 行 | ≤ 60 | ≤ 90 | 规范主谓宾语句，占位符规范 |

各组件排版预算的稳定编号 `R-LAY-001` ~ `R-LAY-007`（依上表顺序：Tab Bar → Dialog / Toast）定义于 `rules.json` `layout_constraints` 各键的 `rule_id`，供报告「规则与依据说明」列引用。

---

## 7. 术语库治理与词表缺口流程 (Termbase Governance & Gap Process)

### 7.1 治理字段与生命周期
术语库每条词条携带三个治理字段，由发布门禁 `validate.py` 强制校验；阈值以 `rules.json` `governance` 为单一事实源：
- **`status`**：`ACTIVE`（生效词条，走查术语仲裁的查询范围）/ `RETIRED`（退役词条，仅为 ID 占位保留，内容供历史追溯）。走查中只查询 `ACTIVE` 词条。
- **`review_date`**：最近一次对照权威来源核验的日期。任意 ACTIVE 词条超过 `governance.stale_warning_days` 未核验触发门禁警告；MANDATORY 词条超过 `governance.mandatory_max_age_days` 未核验直接阻断发布——法定术语必须周期性复核。
- **`source_url`**：权威来源官方站点入口。所有 ACTIVE 的 MANDATORY 词条必须提供，保证法定口径可追溯核验。

词条生命周期：走查报告中的 TERMBASE_GAP 建议（`FIN-XXX-NNN (proposed)` 格式）仅为提案，不得直接写入术语库；经术语工作组评审通过后以 `ACTIVE` 状态入库。`entry_id` 永久不变，退役词条不得删除、编号不得复用。

### 7.2 TERMBASE_GAP 输出格式
走查中发现术语库未覆盖的术语时，在报告汇总区按下表输出，不得静默编造判定：

| 术语 | 所在语境 | 建议作用域 | 建议 entry_id | 建议权威来源 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Credit Limit | 卡片详情页标题 | GLOBAL | FIN-CRD-007 (proposed) | 国际卡组织标准 | 提案仅供参考，须治理评审后入库 |

- 建议 entry_id 取该业务域编号段的下一个空位，并强制带 `(proposed)` 后缀。
- 发布门禁校验：`(proposed)` 编号不得与现有词条冲突；若该编号已入库，规范与黄金样例中的缺口示例须同步更新。

---

## 8. 数字、货币与日期格式规范 (Number, Currency & Date Formats)

各市场货币代码、符号、千分位/小数分隔符与日期格式的权威数值定义于 `rules.json` `format_rules`（`R-FMT-001` ~ `R-FMT-005`，覆盖 SG / MY / HK / TH / ID），本节阐述判定逻辑：
- **金额表达**：金额须使用货币符号或 ISO 4217 代码之一，不得混用；代码与金额之间有且仅有一个空格（`SGD 100.00`、`S$100.00` 合规；`SGD100.00`、`S$ SGD 100` 违规）。见 `R-FMT-006`。
- **风格一致性**：同一界面内金额风格（符号 vs 代码、分隔符体系）必须统一，混用记 `R-DEF-005`。见 `R-FMT-007`。
- **分隔符随语区**：千分位与小数分隔符跟随界面语言语区而非目标市场——印尼语界面为 `Rp1.500.000,00`（点千分位/逗号小数），英语界面为 `1,500,000.00`。
- **泰国佛历**：泰语界面日期默认佛历（公历年 +543，如 2569）；泰国市场的英语界面用公历。历法与语区错配（泰语界面出现公历年份、或英语界面出现佛历年份）记 `R-DEF-005`。见 `R-FMT-004`。
- **缺陷归类**：金额/日期格式问题记 `R-DEF-005`（FORMAT_GRAMMAR），依据列引用对应 `R-FMT` 编号；若金额错误引发披露歧义（如币种缺失导致金额误导），按 `R-GEN-004` 升级并走合规复审。

## 9. 走查质量度量 (Quality Metrics)

走查报告汇总区除缺陷计数外，必须输出以下度量；计算口径以 `rules.json` `metrics` 为单一事实源，保证跨团队可比：
- **`R-MET-001` 缺陷密度**：缺陷总数 / 走查屏数，衡量单屏问题浓度。
- **`R-MET-002` 严重级分布**：High / Medium / Low 三级计数。
- **`R-MET-003` 缺陷码分布**：7 类缺陷码各自计数，用于定位系统性问题。
- **`R-MET-004` 一次通过率**：零缺陷屏数 / 走查屏数。
- **`R-MET-005` 合规升级数**：路由至人工合规复审的 ALERT 发现数。
- **`R-MET-006` 词表缺口数**：本次走查提出的 TERMBASE_GAP 提案数。

度量目标值（如一次通过率达标线）由业务方按发布节奏另行制定，本规范只固化计算口径。

---
*版本：v1.3.0 | 维护团队：i18n 术语与界面走查工作组*
