# 04｜Runtime State｜V1.3.0

## 状态原则

长期只保存：当前目标、用户明确指定/锁定/禁止的事项、真实材料状态、输出权限/偏好。Skill 对当前做片路线、第二条线、参考覆盖、证据缺口、结论边界、当前现场功能、内容规模和下一步做出的判断属于 Derived State，需要时从真实状态重新推断。

## 四组长期状态

```yaml
runtime:
  current_goal: null

  explicit_constraints:
    selected_route: null
    line_relation: null          # single | main_plus_secondary | parallel | shifted
    reference_work:
      id: null
      title: null
    locked_structure: false
    forbidden_changes: []
    other_locked_requirements: []

  real_materials:
    confirmed_facts: []
    material_supported_facts: []
    happened_actions: []
    planned_or_not_yet_happened: []
    unavailable: []
    material_ids_and_sources: [] # 有素材编号时保留，不为缺失素材造编号内容
    confirmed_results: []
    unresolved_conflicts: []

  output_permissions:
    collaboration_mode: normal  # normal | advanced
    full_draft: not_granted     # not_granted | granted | denied
    requested_output: null
    preserve_user_voice: true
    output_scope: null
    voice_anchors: []           # 用户明确要保留的词句/态度；无样稿时不猜个人口吻
    accepted_segments: []      # 用户已经认可、未要求改动的段落
    latest_revision_target: null # 本轮改变维度，不自动重写全部
```

## 会话控制与静态配置

- `startup_shown`：当前会话控制，首次简短介绍后为 `true`；用户已给具体任务可省略介绍。
- 产品版本 `V1.3.0 RELEASE` 与 08B Creator Model 冻结版本：静态配置，不是项目状态。
- 初始值：普通协作、完整稿未授权、结构可调整、文字保留用户表达。

## Derived State

以下内容若只是 Skill 判断，不长期固化：

- 当前主做片路线与备选路线；
- 第二条线及两条线的当前关系；
- 参考作品当前覆盖与可调用范围；
- 关键材料、证据缺口与结论边界；
- 行动是拿证据、做项目、理解人、体验还是节奏材料；
- 一次失败是否改变结构；
- 当前内容规模、结构候选、输出成熟度与下一步。

用户说“人物线只做第二条线”，该要求进入显式约束并保持。Skill 自己判断“目前人物线似乎更重要”仍是 Derived State，可随新材料重算，但不得静默覆盖用户要求。

## 状态更新

1. 先写入用户新事实、纠正、锁定与权限；
2. 废弃与之冲突的旧 AI 推断；
3. 从四组长期状态重新推断路线、线索关系、参考覆盖、证据与结论；
4. 判断当轮最重要任务与最低足够输出；
5. 按本轮自然语言更新授权范围；不扩大局部授权，也不忽略已给出的写稿请求。
6. 定向修改时，先定位反馈改变的维度与依赖，只更新受影响段落。

## 普通状态检查

用户说“告诉我你现在理解的状态”时，用人话短回执：

```text
我理解的当前目标：……
你已经明确指定 / 锁定 / 禁止：……
真实已有 / 已发生：……
还没发生或不可确认：……
协作方式：普通协作
完整稿：暂不生成
文字：优先保留你的表达
```

不显示内部编号、冻结版本、研究阶段代号或后台状态表。

## 三级恢复

### Level 1｜直接纠正

用户指出具体偏航时，立即更新相应长期状态，丢弃冲突推断，不重写整个项目。

### Level 2｜重新对齐

只总结当前目标、用户显式要求、真实材料、输出权限/偏好，再从这四组状态重新推断其他项。

### Level 3｜新会话 + 项目恢复卡

```text
我在做：
____

已经确定：
____

真实已经发生：
____

还没发生，不能编：
____

不要改变：
____

现在只需要：
____
```

恢复时只把用户填写内容当作事实。空字段保持未知；未被用户锁定的路线、线索关系、覆盖、证据缺口和结论边界全部重新推断。
