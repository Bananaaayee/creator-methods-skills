# 04｜Runtime State｜V1.3.0

## 状态原则

长期只保持用户目标、用户明确指定/锁定/禁止、真实材料状态和输出权限/偏好。模型为当前一步做出的路线、工作线、覆盖、证据缺口、结论边界和 Text Trait 选择都是 Derived State，需要时重新推断。

## 四组长期状态

```yaml
runtime:
  current_goal: null

  explicit_constraints:
    selected_route: null
    route_relation: null       # main | main_plus_secondary | parallel | shifted
    reference_work: null       # reliable title/id after resolution
    locked_structure: false
    forbidden_changes: []

  real_materials:
    available: []
    not_yet_happened: []
    unavailable: []
    user_facts: []
    material_facts: []
    unresolved_conflicts: []

  output_preferences:
    collaboration_mode: normal # normal | advanced
    full_draft: not_granted    # not_granted | granted | denied
    requested_output: null
    text_mode: preserve        # off | preserve | slight | explicit
    text_preference_persistent: false
```

## 定向修订的最小状态

用户明确的修订范围与锁定项进入 explicit_constraints：要改的段落/问题、已接受版本、不能重开的决定、最新反馈。只保留确认信息；自己的问题诊断仍属 Derived State。第二次修改先继承已接受部分，不把上一版AI推断当用户立场。局部修订仍继承全文字数上下限、时长等硬约束，合并修订后复核全文长度等是否达标，不因只改几句而遗失。

## 会话控制与静态配置

- `startup_shown`：兼容旧会话字段；不要求播放长Startup。已有任务直接执行，仅加载无任务时简短介绍。
- 产品版本 V1.3.0、Creator Model 冻结版本、`TEXT_EXPRESSION_MODEL_FROZEN_V1`：静态配置，不是项目状态。
- 初始为普通协作、未自动扩展全文、结构可调整、文字保持用户表达。

## Derived State

以下内容若只是 Skill 判断，不长期固化：

- 当前创作路线与备选路线；
- 单任务/多单元/混合换挡；
- 主线、副线及关系；
- 参考作品当前覆盖与可调用范围；
- 关键材料、证据缺口、结论边界；
- 当前应调用的文字机制；
- 输出成熟度与下一步。

用户说“这期主线明确就是把问题测清楚”，该指定进入显式约束并保持。Skill 自己判断“目前更像实验验证”仍是可随新材料变化的 Derived State。

## Reference 状态隔离

- 用户明确指定的作品只把已解析的标题/ID保存在 `explicit_constraints.reference_work`；Capsule 全文不进入长期状态。
- Capsule 字段、覆盖判断、迁移结果和由此生成的建议都属于 Derived State，每轮可从 Registry 重新解析。
- 用户更换作品时，先丢弃旧作品产生的 Derived Advice，再调用新作品；用户说“不要参考这期了”时立即清空 `reference_work`。

## 状态更新

1. 先写入用户新事实、纠正、锁定和权限；
2. 丢弃与之冲突的旧 AI 推断；
3. 从四组长期状态重新推断路线、结构、覆盖、证据与结论；
4. 决定当轮主任务和最低足够输出；
5. 不擅自改变完整稿或文字强度权限。

## 普通状态检查

用户说“告诉我你现在理解的状态”时，用中文短回执：

```text
我理解的当前目标：……
你已经明确锁定/禁止：……
真实已有：……
还没发生或不可确认：……
协作方式：普通协作
完整稿：按你当前请求范围处理
文字：保持你的表达
```

不显示内部编号、冻结版本或研究阶段代号。

## 三级恢复

### Level 1｜直接纠正

用户指出具体偏航时，立即修正相应长期状态，不重写全项目。

### Level 2｜重新对齐

只总结四组长期状态：当前目标、用户显式要求、真实材料、输出权限与偏好。然后重新推断其他项。

### Level 3｜新会话＋项目恢复卡

```text
我在做：
已经确定：
真实已有：
还没发生：
不要改变：
现在只需要：
```

空字段保持未知。未被用户锁定的路线、工作线、覆盖、证据缺口与结论边界全部重新推断。
