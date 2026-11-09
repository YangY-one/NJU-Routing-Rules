# 南京大学校内资源分流规则

南京大学校内资源的分流规则，供已配置校园网或 VPN 出站策略的客户端使用。规则包含精确域名和 IPv4 网段。规则本身不提供 VPN 连接。

## 选择规则文件

| 客户端 | 规则文件 | 接入方式 |
| --- | --- | --- |
| Surge | [`rules/surge/nju.list`](rules/surge/nju.list) | `RULE-SET` |
| Loon | [`rules/loon/nju.list`](rules/loon/nju.list) | `RULE-SET` |
| Shadowrocket | [`rules/shadowrocket/nju.list`](rules/shadowrocket/nju.list) | `RULE-SET` |
| Quantumult X | [`rules/quantumultx/nju.list`](rules/quantumultx/nju.list) | `filter_remote` |
| Mihomo / Clash Meta | [`rules/mihomo/nju.yaml`](rules/mihomo/nju.yaml) | `classical` rule-provider |
| V2Ray / V2Fly | [`rules/v2ray/nju-routing.json`](rules/v2ray/nju-routing.json) | `routing` JSON 配置片段 |
| sing-box | [`rules/sing-box/nju.json`](rules/sing-box/nju.json) | source rule-set JSON |

## 接入方法

先在客户端配置能访问校内资源的出站策略。下例中的 `NJU-VPN` 是示例策略名，请替换为你实际使用的名称。Surge 可在 `[Rule]` 中引用对应文件：

```ini
RULE-SET,https://raw.githubusercontent.com/YangY-one/NJU-Routing-Rules/main/rules/surge/nju.list,NJU-VPN
```

Loon 和 Shadowrocket 请引用表中各自的 `.list` 文件。其他格式需要按客户端配置接入：

- **Quantumult X：**文件内使用 `NJU-VPN` 作为策略名；请配置同名策略或修改文件中的名称。
- **Mihomo / Clash Meta：**将 YAML 文件配置为 `behavior: classical` 的 rule-provider，再使用 `RULE-SET,nju,NJU-VPN` 引用。
- **V2Ray / V2Fly：**将文件中的 `routing.rules` 合并到现有配置，把 `outboundTag` 改为你的出站标签，并使用文件中的 `routing.domainStrategy: AsIs`。
- **sing-box：**将 JSON 文件作为 source rule-set 引用，并在客户端路由配置中指定出站策略。

具体接入语法可参见 [Surge](https://manual.nssurge.com/rules/ruleset.html)、[Mihomo](https://wiki.metacubex.one/en/config/rule-providers/)、[V2Fly](https://www.v2fly.org/en_US/config/routing.html) 和 [sing-box](https://sing-box.sagernet.org/configuration/rule-set/source-format/) 文档。

## 匹配范围

域名规则只匹配列出的主机名，不覆盖整个 `nju.edu.cn`。IP 规则仅匹配目标 IP，默认不会为了判断网段归属而主动解析域名：Surge、Loon、Shadowrocket、Quantumult X 和 Mihomo 的 IP 规则带有 `no-resolve`；V2Ray 使用 `AsIs`。sing-box 规则集本身不包含 DNS 解析动作；如果你的路由配置另有 `resolve` 动作，仍以该配置为准。

10 个 IP 网段收录自[个人 BRAS 路由配置文章](https://www.yaoge123.com/blog/archives/3376)。原文中的 `10.0.0.0/8` 和 `172.16.0.0/12` 未纳入规则。使用 IP 规则前，请按实际网络环境判断这些网段是否适用。

如需更新域名或网段、重新生成规则，请阅读 [`scripts/README.md`](scripts/README.md)。

## Tips

对 Surge 可以设定代理组（下方的 `NJU-LAN`），该代理组设置当设备在校园内（有线连接的网关 IP 或者无线网的 SSID 判定）时走直连，只有其它情况下（即校外）才走代理（`NJU-VPN`）。

```INI
NJU-LAN = subnet, default = NJU-VPN, "ROUTER:114.212.1.0" = DIRECT, "SSID:NJU-WLAN" = DIRECT
```
