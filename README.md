# Venera / VeneraX 漫画源配置库 (Enhanced)

本项目是 [venera-app/venera-configs](https://github.com/venera-app/venera-configs) 的社区维护与增强分支，主要针对原版漫画源中存在的**接口失效、内存污染崩溃、风控拦截超时、旧版客户端指纹**等问题进行持续修复与体验优化，适配 Venera 及衍生客户端（如 VeneraX）。

---

## 🚀 订阅源地址

在 Venera / VeneraX 应用内进入：**设置 → 漫画源管理 → 添加漫画源库（右上角）**，填入以下任意订阅链接：

- **jsDelivr CDN（国内直连加速，推荐）**：
  ```text
  https://cdn.jsdelivr.net/gh/Souitou-iop/venera-configs@main/index.json
  ```
- **GitHub Raw 订阅地址**：
  ```text
  https://raw.githubusercontent.com/Souitou-iop/venera-configs/main/index.json
  ```

---

## 🛠️ 近期重点修复日志 (Changelog)

### 拷贝漫画 (`copy_manga.js`) - v1.5.0

针对原版 1.4.1 源在日常阅读中暴露的多个严重痛点进行了全面重构与风控加固：

1. **根治“看完一话后切换下一话必报 Network error 崩溃”的内存污染 Bug**
   - **问题原因**：原脚本启动时在后台异步请求 `system/network2` 接口，官方服务端下发了防爬混淆域名（`t66y.com`）。脚本直接将其赋给 `this.settings.base_url`，导致原本是对象的配置数据结构被破坏为纯字符串，切换章节时 Dart 层解析配置直接抛出 `NoSuchMethodError` 崩溃。
   - **修复方案**：彻底切断该异常覆盖逻辑，固定可靠的官方主 API 节点并增加底层配置解析防护。

2. **解决 HTTP 210 限频死锁与 30 秒超时冲突**
   - **问题原因**：原脚本遇到服务端 210 状态码时固定 `sleep 40s`，而阅读器底层硬编码了 30 秒超时阈值，导致重试尚未完成就必然触发界面报错。
   - **修复方案**：优化为 1.5~3 秒的智能微退避抖动重试（单次最高不超过 4 秒），彻底消除因超时被截断报 `Network error` 的情况。

3. **客户端请求特征升级（3.0.9 指纹伪装）**
   - 将原版已被服务端列入重点拦截名单的 `3.0.6` 请求头（User-Agent、Referer、Version）全面升级至官方最新正式版 `3.0.9` 特征。

4. **动态设备指纹自愈（Device Fingerprint Auto-Rotation）**
   - 改变原版设备指纹永久固定的缺陷。当偶发触发风控信号时，自动在内存中重新生成全新合规的随机设备特征，重置在服务端风控系统中的黑名单权重。

5. **多镜像节点自动故障转移（Multi-endpoint Failover）**
   - 内置三组官方主备 API 节点集群（`api.copy2000.online`、`api.copy-manga.com`、`api.mangacopy.com`），遇到单一节点限频或网络波动时自动无感切换。

6. **优化海外线路通道（`region: 0`）**
   - 切换为海外线路时，自动剥离非必要的大陆广告参数，直连干净通道。

---

## 📱 适配测试与问题反馈

### 已测试环境
本项目目前**仅经过本人在以下设备与系统环境中的实际测试与验证**：
- **Mac** (macOS 26.6)
- **Windows**
- **iPhone** (iOS 27)
- **安卓手机** (Android 16 / HyperOS 3)
- **安卓平板** (Android 16 / HyperOS 3)

### 问题反馈指南
其他设备或系统环境下如果出现问题，欢迎提交 Issue 反映。提 Issue 时**请务必说明清楚**：
1. **使用的具体设备型号与系统版本**（如：具体品牌、操作系统版本、Venera/VeneraX 客户端版本）；
2. **遇到的具体问题特征与复现步骤**（如：无法获取章节、切章卡死、具体报错提示文案）；
3. **导出的日志文件**（客户端内：设置 → 导出日志）或具体报错截图。

---

## ⚖️ 免责声明 (Disclaimer)

1. 本项目仅为开源漫画阅读器（Venera / VeneraX）提供网络接口解析规则脚本（Parser），**本项目不提供、不托管、不存储、亦不传播任何漫画图像、文本或媒体资源**。
2. 脚本中所有网络请求均由客户端直接发起并连接至公开的第三方网络服务，本项目不对第三方内容的可用性、准确性、合法性承担任何责任。
3. 本项目所有代码仅供开源技术研究与个人学习交流使用，请在遵循当地法律法规的前提下合法使用。
