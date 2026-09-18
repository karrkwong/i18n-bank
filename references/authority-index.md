# Authority Source Index (权威源索引)

> **定位**：术语治理评审（specification.md 第 7.3 节）与 MANDATORY 词条周期复核的导航层——按市场列出监管方、文书族与入口级 URL，回答"去哪查"。
> **边界**：只收入口，不收录文书正文。正文受版权与修订时效约束（ISO / 卡组织 / SWIFT 文件为付费或会员文件，不得再分发），静态副本会脱离权威来源静默过期；文书级深链只在词条落库与到期复核时记入 `termbase.csv` 的 `source_url`。
> **维护**：入口链接随 MANDATORY 复核周期一并核验；失效即修正本文件并过门禁（`validate.py` 对本文件的规则编号与词条编号引用执行一致性校验）。

## 使用规则

1. **辖区优先**：按词条 `scope` 与走查界面目标市场锁定区块——LOCAL_XX 查对应市场，REGIONAL_SEA 查所涉市场，GLOBAL 先查国际标准区块。
2. **文书族映射合规级**：在文书族内找到强制条款 → MANDATORY；仅标准或惯例背书 → STANDARD；查无背书 → GENERAL。完整判定树见 specification.md 7.3。
3. **引用落库**：`source_url` 须指向具体文书页面，不得填本表入口页或站点首页；定位不到文书页的，按 7.3 宁降勿升纪律处理。

## SG — 新加坡

| 机构 | 角色 | 文书族（示例） | 入口 |
| :--- | :--- | :--- | :--- |
| MAS 金融管理局 | 央行 / 统一金融监管 | Notices（如 Notice 635 无抵押消费信贷、Notice 637 银行资本充足率）、Guidelines、Codes of Practice | https://www.mas.gov.sg/regulation/notices |
| ABS 新加坡银行公会 | 银行业自律组织 / 支付计划运营方 | PayNow Scheme Rules、GIRO 付费计划规则 | https://www.abs.org.sg |
| SSO 新加坡法规库（AGC） | 法定文书库 | Banking Act 1970、Payment Services Act 2019 | https://sso.agc.gov.sg |
| CPF 公积金局 | 法定计划运营方 | CPF Act 及计划条款 | https://www.cpf.gov.sg |
| ICA 移民与关卡局 | 身份证件主管机关 | NRIC / FIN 规格与法规 | https://www.ica.gov.sg |
| MOM 人力部 | 外籍证件签发方 | FIN 准证体系 | https://www.mom.gov.sg |
| AXS | 本地缴费渠道运营方 | AXS 渠道服务说明 | https://www.axs.com.sg |

## MY — 马来西亚

| 机构 | 角色 | 文书族（示例） | 入口 |
| :--- | :--- | :--- | :--- |
| BNM 马来西亚国家银行 | 央行 | 政策文件（Policy Documents，含消费者保护）、指引、通告 | https://www.bnm.gov.my |
| PayNet | 国家支付基础设施运营方（BNM 属下清算机构） | DuitNow 运营规则、Interoperable Credit Transfer Framework、MyClear 清算规则 | https://www.paynet.my |
| JPN 国民登记局 | 身份证件主管机关 | MyKad / NRIC 法定规格 | https://www.jpn.gov.my |

## HK — 香港

| 机构 | 角色 | 文书族（示例） | 入口 |
| :--- | :--- | :--- | :--- |
| HKMA 香港金融管理局 | 央行 / 银行监管 | Supervisory Policy Manuals、监管指引与通告 | https://www.hkma.gov.hk |
| e-Legislation（HKELEG） | 法定文书库 | Banking Ordinance（Cap. 155）、Payment Systems and Stored Value Facilities Ordinance（Cap. 584） | https://www.elegislation.gov.hk |
| HKICL 香港银行同业结算 | 清算 / 系统运营方 | 转数快 FPS 系统规则、清算运作规则 | https://www.hkicl.com.hk |
| FPS 转数快官方站 | 系统官方入口 | FPS 参与机构与使用规则说明 | https://www.fps.hk |
| MPFA 积金局 | 强积金监管 | MPF Schemes Ordinance（Cap. 485）及规则指引 | https://www.mpfa.org.hk |
| ImmD 入境事务处 | 身份证件主管机关 | HKID 法定规格 | https://www.immd.gov.hk |

## TH — 泰国

| 机构 | 角色 | 文书族（示例） | 入口 |
| :--- | :--- | :--- | :--- |
| BOT 泰国银行 | 央行 | Payment Systems Act B.E. 2560 (2017) 及实施通告、消费者保护通告 | https://www.bot.or.th |

> TH 注意：PromptPay 由 National ITMX（NITMX）依据 BOT 授权运营，其参与规则属运营方文书；NITMX 官网入口待核验后补录，当前 TH 支付文书检索以 BOT 为准。BOT 官网经历过站群重构，英文区深链不稳定，检索通告（Notifications / ประกาศ）建议用站内搜索。

## ID — 印度尼西亚

| 机构 | 角色 | 文书族（示例） | 入口 |
| :--- | :--- | :--- | :--- |
| BI 印度尼西亚银行 | 央行 | PBI（印尼银行条例）、PADG（行长理事会条例）、BI-FAST 实施框架、QRIS 国家标准 | https://www.bi.go.id |

> ID 注意：BI 官网 2024 年重构后深链变化频繁，检索 Peraturan（法规）建议用站内搜索，印尼语关键词优先。

## 国际标准（GLOBAL 词条）

| 机构 | 角色 | 文书族（示例） | 入口 | 授权说明 |
| :--- | :--- | :--- | :--- | :--- |
| ISO 20022 RMG | 支付报文标准组织 | ISO 20022 报文标准（Payments Initiation 等） | https://www.iso20022.org | 标准公开摘要；全文需授权 |
| ISO | 国际标准组织 | ISO 13616（IBAN）、ISO 9362（BIC）、ISO 4217（货币代码） | https://www.iso.org | 付费标准；仅可引用目录条目 |
| SWIFT | 报文网络运营方 | SWIFT Standards（MT / MX） | https://www.swift.com | 会员授权文件 |
| Visa | 卡组织 | Visa Core Rules | https://www.visa.com | 会员授权文件 |
| Mastercard | 卡组织 | Mastercard Rules | https://www.mastercard.com | 会员授权文件 |

> ISO 4217 是 `rules.json` `format_rules` 货币代码（R-FMT-001 ~ R-FMT-005）的权威依据。

---
*版本：v1.3.1 | 维护团队：i18n 术语与界面走查工作组*
