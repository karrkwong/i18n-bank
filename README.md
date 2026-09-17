# i18n_BANK: Banking App 国际化走查与术语标准库

本项目为 Banking App（手机银行与金融应用）的国际化（i18n）、本地化（L10n）及界面走查（LQA）标准资产库。

## 目录与核心资产

| 文件 | 描述 | 说明 |
| :--- | :--- | :--- |
| **`i18n_BANK_Specification.md`** | 国际化走查与排版标准规范 | 固化央行法定口径（P0）、国际金融标准（P1）、本地化惯例（P2）与基础交互（P3）；包含“组件一字精炼”与“语境省略”规则，以及东南亚多语言排版预算矩阵。 |
| **`banking_termbase_core.csv`** | 概念导向多语言金融术语库 | 收录核心账户、转账清算、信用卡、信贷、安全认证等术语，包含中英对照、禁用词、适用场景及官方法规溯源依据（MAS, BNM, HKMA, ISO 20022 等）。 |
| **`review_rules_and_checklist.json`** | 缺陷分类与机器可读走查规则 | 固化 7 大封闭缺陷枚举（`TRUNCATION`, `LINE_BREAK`, `MIXED_LANG`, `REDUNDANCY`, `FORMAT_GRAMMAR`, `COMPLIANCE`, `PLACEHOLDER`）及合规评估判定标准。 |

## 适用标准与权威来源
- **各国央行/法定监管机构**：新加坡金融管理局 (MAS)、马来西亚国家银行 (BNM)、中国香港金融管理局 (HKMA)、泰国央行 (BOT)、印尼央行 (BI)
- **国际金融标准体系**：ISO 20022 Payments Standard、SWIFT Standards、ISO 30042 (TBX)、Visa/Mastercard Rules
