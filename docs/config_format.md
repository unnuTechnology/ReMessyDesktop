# ReMessyDesktop 配置文件格式

|   最后更新时间   |   最后更新者    |                                  适用版本                                   |
|:----------:|:----------:|:-----------------------------------------------------------------------:|
| 2026/02/14 | MacrosMeng | 从 `0.1.0pre1 Codename Cherry Grove` 到 `0.1.0pre1 Codename Cherry Grove` |

## 配置文件格式

ReMessyDesktop 的配置文件格式是 JSON 格式，一般存放在 `/config/config.json` 中。
以下是其主要架构：

### API版本 1

```json5
{
  "api_version": 1,  // API 版本
  "app": {
    "detect_path": str  // 要检测的文件夹的路径
  },
  "classification": {
    "cses_classifier": {
      "cses_path": str // CSES 课表文件的路径
    },
    "regex_classifier": {
      "patterns": {
        str: str,  // 正则表达式模式，键为科目名称，值为正则表达式
        ...
      }
    }
  }
}
```

## API 版本对应速查表

| API 版本 |                                   适用版本                                    |
|--------|:-------------------------------------------------------------------------:|
| 1      | 从 `0.1.0pa1 Codename Sanshan Island` 到 `0.1.0pa1 Codename Sanshan Island` |
