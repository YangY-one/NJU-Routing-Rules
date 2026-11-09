# 规则维护脚本

从项目根目录运行。脚本仅使用 Python 3 标准库。

`nju_domains.py` 从公开证书记录发现四标签 `*.nju.edu.cn` 主机名，并在两个网络环境中测试首页。首页可访问不代表站内所有页面均可访问；需结合受限页面提示核实，公开证书记录也不能覆盖全部站点。已有候选名单在 `scripts/data/nju-hosts.txt`；人工确认名单在 `scripts/data/nju-confirmed.txt`。可选地更新候选名单：

```sh
python3 scripts/nju_domains.py discover --seed scripts/data/nju-confirmed.txt --out scripts/data/nju-hosts.txt
```

在校外直连时测试一次，切换到能访问校内资源的网络后使用同一名单再测试一次：

```sh
python3 scripts/nju_domains.py probe --hosts scripts/data/nju-hosts.txt --out results/external.csv --problem-out results/external-problems.txt --proxy direct
python3 scripts/nju_domains.py probe --hosts scripts/data/nju-hosts.txt --out results/internal.csv --problem-out results/internal-problems.txt --proxy system
python3 scripts/nju_domains.py select --external results/external.csv --internal results/internal.csv --confirmed scripts/data/nju-confirmed.txt --out sources/domains.txt
```

`--proxy direct` 只绕过 Python 的 HTTP 代理，不会关闭系统 VPN 或已有网络路由；校外复测前需确认设备确实不在校内网络。`--proxy system` 遵循系统/环境代理；如 Python 未识别，可指定 `--proxy http://127.0.0.1:端口`。`probe` 将连接失败、TLS 错误、HTTP 401/403/5xx、代理错误及校内访问提示页分别记录。提示页也可能返回 HTTP 200。只有校外失败/提示、校内可访问的主机才会进入 `sources/domains.txt`；人工确认名单也会纳入。

10 个公网网段保存在 `sources/ip-cidrs.txt`，来源见项目首页。两条私网网段不参与生成。修改源文件后，生成并校验七种格式：

```sh
python3 scripts/build_rules.py
python3 scripts/build_rules.py --check
```

生成器对域名和 CIDR 做基本校验，为 Surge、Loon、Shadowrocket、Quantumult X、Mihomo 的 IP 规则添加 `no-resolve`，将 V2Ray 的 `routing.domainStrategy` 设为 `AsIs`，并为 Quantumult X 与 V2Ray 使用 `NJU-VPN` 占位策略名。sing-box 规则集不包含 DNS 解析动作；是否主动解析由引用它的路由配置决定。
