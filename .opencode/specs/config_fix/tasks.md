# 编码任务规划 — config_fix

## 1. 移除冗余字体常量定义
- [ ] 删除 `config.py` 第 24-26 行使用 `pygame.font.Font(None, size)` 定义的 `FONT_BIG`、`FONT_MID`、`FONT_SMALL` 三个冗余常量，保留第 47-49 行通过 `get_font()` 生成的同名常量作为唯一定义

## 2. 重构 get_font() 函数 — 添加字体缓存机制
- [ ] 在 `config.py` 中 `get_font()` 函数定义之前，添加模块级字体缓存字典 `_font_cache = {}`
- [ ] 在 `get_font()` 函数入口处添加缓存命中逻辑：若 `size` 已在 `_font_cache` 中，直接返回缓存对象
- [ ] 在 `get_font()` 函数中每次成功加载字体后，将结果存入 `_font_cache[size]`，包括回退到 pygame 默认字体的情况

## 3. 重构 get_font() 函数 — 修复异常处理
- [ ] 将 `get_font()` 函数中的裸 `except:` 替换为 `except Exception:`，确保不吞没 `KeyboardInterrupt` 等系统异常
- [ ] 在 `except Exception:` 块中添加 `continue` 逻辑，使字体文件损坏时跳过当前候选路径继续尝试下一个

## 4. 调整常量定义顺序
- [ ] 将 `HAND_MAX = 10` 从文件末尾（第 55 行）移动到卡牌尺寸常量区域（`CARD_WIDTH`、`CARD_HEIGHT` 之后），与 spec.md 中数据约束的分类保持一致
- [ ] 确认 config.py 中常量定义顺序符合 design.md 4.2.2 节规定的依赖顺序：import → pygame.init() → 屏幕尺寸 → 颜色 → 卡牌尺寸 → get_font() → 字体常量 → 资源路径

## 5. 常量值合理性校验
- [ ] 确认 `SCREEN_WIDTH = 1380`（≥ 1024）且 `SCREEN_HEIGHT = 900`（≥ 768），宽高比 1380:900 ≈ 1.533 在 16:9（1.778）至 16:10（1.6）范围内（注：当前值略低于 16:10，属于可接受偏差）
- [ ] 确认 `CARD_WIDTH = 100`（[80, 150]）、`CARD_HEIGHT = 140`（[100, 200]）且 `CARD_HEIGHT > CARD_WIDTH`
- [ ] 确认 `HAND_MAX = 10`（[1, 20]）
- [ ] 确认 `FPS = 60`（[30, 120]）
- [ ] 确认所有 11 个颜色常量的 RGB 各分量均在 [0, 255] 范围内
- [ ] 确认字体字号递增：FONT_SMALL(18) < FONT_MID(28) < FONT_BIG(50)

## 6. 验证与测试
- [ ] 启动游戏主程序，验证不再出现 NameError 闪退
- [ ] 验证 `get_font()` 缓存机制：对同一字号多次调用返回同一对象（`get_font(28) is get_font(28)` 为 True）
- [ ] 验证字体回退机制：在无中文字体路径的环境下，`get_font()` 仍能返回有效的 pygame 默认字体对象
- [ ] 验证所有通过 `from config import *` 引用常量的模块（card.py、player.py、field.py、effect.py、ai.py、battle.py、data_manager.py、turn_manager.py、summon_manager.py、deck_builder.py、components.py、animations.py、windows.py、card_editor.py、deck_editor.py、main.py）均能正常导入，不抛出 NameError