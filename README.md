# ErisPulse-Echo

回显消息内容的 ErisPulse 模块。

## 功能

- 回显文本：`/echo hello world`
- 回显媒体：发送 `/echo` 并附带图片/视频/文件
- 引用回显：回复一条消息并发送 `/echo`，回显被引用的消息内容
- 支持文本 + 媒体混合回显

## 引用回显限制

仅支持回显当前会话最近 **10** 条消息，超出范围会提示。

可在 `config.toml` 中修改：

```toml
[Echo]
max_history = 20
```

## 安装

```bash
epsdk install Echo
```

## 用法

```
/echo hello              # 回显文本
/echo                    # 回显附带的图片/视频/文件
回复消息 → /echo          # 回显被引用的消息
```
