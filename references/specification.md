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
3. **P2 级 - 本地化心智表达与惯用语 (Localization Best Practice)**：
   - 符合当地金融消费者的日常理解习惯。区分英联邦英语体系（en-GB/en-SG/en-MY）与美式英语体系（en-US）。优先采用英式拼写（如 *Instalment*, *Cheque*, *Authorised*）。
4. **P3 级 - 基础前端交互用语 (General UI)**：
   - 基础交互按钮、导航、Toast 等，不涉及金融法律风险，侧重简洁明了。

---

### 2.2 前端排版与组件精炼原则 (UI Layout & Conciseness Rules)

#### 标准线一：功能组件一字精炼 (Single-Word Action)
在网格宫格（Grid Tile）、操作按钮（CTA Button）、Tab 标签等空间极度受限组件中，文字尽量压缩为一个核心动词/名词。
- 例：`Card Application` → **`Apply`**
- 例：`Card Activation` → **`Activate`**
- 例：`Bill Enquiry` → **`Bill`**
- 例：`Repay Immediately` → **`Repay`**
*(注：标准金融专有名词如 FPS, DuitNow, IBAN, Instalment 等不受此限)*

#### 标准线二：语境省略，拒绝层级冗余 (Context-Aware Omission)
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
| **规则与依据说明** | 判定理由与权威追溯 | 明确说明规则编号、语境省略依据或引用的央行/行业标准 |

---

## 4. 固化缺陷类型体系 (7 Defect Codes)

为便于自动化统计与质量度量，走查缺陷严格限定为以下 7 类：

1. **`TRUNCATION`（界面截断）**
   - **判定**：文本超长被系统以 `...` 截断，或文本超出组件渲染边界被裁剪，导致核心信息丢失。
2. **`LINE_BREAK`（不良折行/断词）**
   - **判定**：英文单词在非连字符处被物理拆裂（如 `Transactio\nns`），或无谓换行导致卡片高度破坏视觉对齐。
3. **`MIXED_LANG`（语言混排/漏翻）**
   - **判定**：当前语言界面残留源语言（如未翻译中文），或未经系统化定义的中英文杂合串（如 `FPS快速支付Transfer`）。
4. **`REDUNDANCY`（文案冗余/未精炼）**
   - **判定**：未遵循语境省略，重复分类前缀（如 Cards 模块下的 `Card Application`）或带有冗余修饰词。
5. **`FORMAT_GRAMMAR`（格式与语法规范）**
   - **判定**：单复数语法错误（如 `1 accounts`）、标点符号错误（孤儿标点、全半角混用、冒号后缺空格）、大小写混乱。
6. **`COMPLIANCE`（术语/合规不符）**
   - **判定**：未采用目标国央行法定表述或行业标准术语，或产生误导性金融承诺（如利率未注明年化、保障性表达违规）。
7. **`PLACEHOLDER`（代码/占位符异常）**
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

---
*版本：v1.1.0 | 维护团队：i18n 术语与界面走查工作组*
