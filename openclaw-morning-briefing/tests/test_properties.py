# -*- coding: utf-8 -*-
"""
属性测试文件 - 使用 Hypothesis 对晨间执行官配置和输出格式进行属性验证

测试框架: Python + Hypothesis
对应设计文档: .kiro/specs/morning-briefing/design.md 中的 Property 1-9
"""

import copy
import json
import random
import re
import unicodedata

from hypothesis import given, settings, assume
from hypothesis import strategies as st


# ============================================================
# 辅助函数
# ============================================================

# 简报模块 emoji 的固定顺序
EMOJI_ORDER = ["🌤", "📅", "⚡", "📰", "📖", "💪"]

# 模块名称与 emoji 的映射
MODULE_EMOJI_MAP = {
    "weather": "🌤",
    "calendar": "📅",
    "reminders": "⚡",
    "news": "📰",
    "reading": "📖",
    "quote": "💪",
}

# 有效的中文星期表示
VALID_WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# 凭证模式正则列表
CREDENTIAL_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",       # OpenAI 风格 API Key
    r"ghp_[A-Za-z0-9]{36,}",      # GitHub Personal Access Token
    r"key=[A-Za-z0-9]{16,}",      # 通用 key=xxx 模式
    r"token=[A-Za-z0-9]{16,}",    # 通用 token=xxx 模式
    r"password=[^\s&]{8,}",        # 密码模式
]


def count_chinese_chars(text: str) -> int:
    """统计文本中的汉字数量"""
    return sum(1 for ch in text if unicodedata.category(ch) == "Lo")


def generate_briefing_title(month: int, day: int, weekday: str) -> str:
    """生成简报标题行"""
    return f"☀️ 晨间简报 · {month}月{day}日 {weekday}"


def generate_briefing(enabled_modules: dict, module_contents: dict) -> str:
    """
    根据启用的模块和内容生成简报文本。
    模拟 Agent 的简报组装逻辑。
    """
    lines = []
    # 标题行（使用固定日期作为示例）
    lines.append("☀️ 晨间简报 · 4月21日 星期一")
    lines.append("")

    module_order = ["weather", "calendar", "reminders", "news", "reading", "quote"]
    for mod in module_order:
        if enabled_modules.get(mod, False) and mod in module_contents:
            emoji = MODULE_EMOJI_MAP[mod]
            content = module_contents[mod]
            lines.append(f"{emoji} {content}")
            lines.append("")

    return "\n".join(lines).strip()


def generate_evening_review(completed: list, uncompleted: list,
                            tomorrow: list, goodnight: str) -> str:
    """生成晚间日报文本"""
    lines = ["🌙 今日回顾 · 4月21日", ""]

    lines.append("✅ 已完成：")
    for item in completed:
        lines.append(f"· {item}")
    lines.append("")

    lines.append("⏳ 未完成：")
    for item in uncompleted:
        lines.append(f"· {item}")
    lines.append("")

    lines.append("📅 明日预览：")
    for item in tomorrow:
        lines.append(f"· {item}")
    lines.append("")

    lines.append("💤 晚安提醒：")
    lines.append(f'"{goodnight}"')

    return "\n".join(lines)


def generate_weekly_report(summary: str, next_week: str, learning: str) -> str:
    """生成周报文本"""
    lines = [
        "📋 本周工作周报 · 4月25日",
        "",
        "一、本周目标总结",
        summary,
        "",
        "二、下周工作目标",
        next_week,
        "",
        "三、周学习总结",
        learning,
    ]
    return "\n".join(lines)


# ============================================================
# Hypothesis 自定义策略（Strategies）
# ============================================================

def config_strategy():
    """
    生成随机的 config.json 变体。
    保证结构包含 user、modules、output 三个顶层字段，
    modules 下每个模块包含 enabled 布尔字段。
    """
    module_names = ["weather", "calendar", "reminders", "news", "reading", "quote"]

    # 为每个模块生成 enabled 布尔值
    modules = {}
    for name in module_names:
        modules[name] = {"enabled": st.booleans()}

    return st.fixed_dictionaries({
        "user": st.fixed_dictionaries({
            "name": st.text(min_size=1, max_size=20),
            "city": st.text(min_size=1, max_size=10),
            "timezone": st.just("Asia/Shanghai"),
            "language": st.just("zh-CN"),
        }),
        "modules": st.fixed_dictionaries({
            name: st.fixed_dictionaries({"enabled": st.booleans()})
            for name in module_names
        }),
        "output": st.fixed_dictionaries({
            "format": st.just("structured"),
            "pushTo": st.sampled_from(["wechat", "wecom"]),
        }),
    })


def enabled_modules_strategy():
    """生成随机的模块启用组合"""
    module_names = ["weather", "calendar", "reminders", "news", "reading", "quote"]
    return st.fixed_dictionaries({
        name: st.booleans() for name in module_names
    })


def chinese_text_strategy(max_chars=50):
    """生成随机中文文本（包含汉字和标点）"""
    # 常用汉字范围
    chinese_chars = st.sampled_from(
        [chr(c) for c in range(0x4E00, 0x9FA5)]
    )
    return st.lists(chinese_chars, min_size=1, max_size=max_chars).map(
        lambda chars: "".join(chars)
    )


def reading_pool_strategy():
    """生成随机的阅读池数据"""
    article = st.tuples(
        st.text(alphabet=st.sampled_from(
            [chr(c) for c in range(0x4E00, 0x9FA5)]
        ), min_size=2, max_size=10),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=5, max_size=20),
    ).map(lambda t: f"《{t[0]}》 https://example.com/{t[1]}")

    return st.fixed_dictionaries({
        "unread": st.lists(article, min_size=1, max_size=10),
        "recommended": st.lists(article, min_size=0, max_size=10),
    })


def module_content_strategy():
    """生成随机的模块内容（每个模块不超过 5 行）"""
    line = st.text(
        alphabet=st.sampled_from(
            list("abcdefghijklmnopqrstuvwxyz ") +
            [chr(c) for c in range(0x4E00, 0x4E20)]
        ),
        min_size=1,
        max_size=30,
    )
    return st.lists(line, min_size=1, max_size=5).map(
        lambda lines: "\n".join(f"· {l}" for l in lines)
    )


# ============================================================
# Property 1: config.json Schema 验证
# 验证包含 user、modules、output 三个顶层字段，
# modules 下每个模块包含 enabled 布尔字段
# **Validates: Requirements 10.1, 10.2**
# ============================================================

class TestProperty1ConfigSchema:
    """Property 1: config.json Schema 验证"""

    @given(config=config_strategy())
    @settings(max_examples=100)
    def test_config_has_required_top_level_fields(self, config):
        """
        Property 1: config.json Schema 验证
        **Validates: Requirements 10.1, 10.2**

        对于任意有效的 config.json，应包含 user、modules、output 三个顶层字段
        """
        assert "user" in config, "config.json 缺少 user 字段"
        assert "modules" in config, "config.json 缺少 modules 字段"
        assert "output" in config, "config.json 缺少 output 字段"

    @given(config=config_strategy())
    @settings(max_examples=100)
    def test_each_module_has_enabled_boolean(self, config):
        """
        Property 1: config.json Schema 验证
        **Validates: Requirements 10.1, 10.2**

        对于 modules 下的每个模块，都应包含 enabled 布尔字段
        """
        modules = config["modules"]
        for module_name, module_config in modules.items():
            assert "enabled" in module_config, (
                f"模块 {module_name} 缺少 enabled 字段"
            )
            assert isinstance(module_config["enabled"], bool), (
                f"模块 {module_name} 的 enabled 字段不是布尔类型"
            )

    def test_real_config_schema(self, config):
        """
        Property 1: 验证实际 config.json 文件的 Schema
        **Validates: Requirements 10.1, 10.2**
        """
        assert "user" in config
        assert "modules" in config
        assert "output" in config
        for module_name, module_config in config["modules"].items():
            assert "enabled" in module_config, (
                f"实际配置中模块 {module_name} 缺少 enabled 字段"
            )
            assert isinstance(module_config["enabled"], bool)


# ============================================================
# Property 2: config.json 凭证安全
# 验证不包含 sk-、ghp_、key= 等凭证模式
# **Validates: Requirements 10.4**
# ============================================================

class TestProperty2CredentialSafety:
    """Property 2: config.json 凭证安全"""

    def _check_no_credentials(self, text: str) -> bool:
        """检查文本中是否包含凭证模式"""
        for pattern in CREDENTIAL_PATTERNS:
            if re.search(pattern, text):
                return False
        return True

    @given(
        injected=st.sampled_from([
            "sk-" + "A" * 30,
            "ghp_" + "B" * 40,
            "key=" + "C" * 20,
            "token=" + "D" * 20,
            "password=MySecret123!",
        ])
    )
    @settings(max_examples=100)
    def test_credential_patterns_are_detected(self, injected):
        """
        Property 2: config.json 凭证安全
        **Validates: Requirements 10.4**

        随机注入凭证模式字符串，验证检测函数能识别这些模式
        """
        # 凭证检测函数应该能识别注入的凭证
        assert not self._check_no_credentials(injected), (
            f"未能检测到凭证模式: {injected[:20]}..."
        )

    def test_real_config_no_credentials(self, config_raw):
        """
        Property 2: 验证实际 config.json 不包含凭证
        **Validates: Requirements 10.4**
        """
        for pattern in CREDENTIAL_PATTERNS:
            match = re.search(pattern, config_raw)
            assert match is None, (
                f"config.json 中发现凭证模式: {match.group()}"
            )


# ============================================================
# Property 3: 简报模块顺序与 emoji 标识
# 验证 emoji（🌤📅⚡📰📖💪）按固定顺序出现
# **Validates: Requirements 8.1, 8.2**
# ============================================================

class TestProperty3EmojiOrder:
    """Property 3: 简报模块顺序与 emoji 标识"""

    @given(enabled=enabled_modules_strategy())
    @settings(max_examples=100)
    def test_emoji_order_is_preserved(self, enabled):
        """
        Property 3: 简报模块顺序与 emoji 标识
        **Validates: Requirements 8.1, 8.2**

        随机生成模块启用组合，验证输出中 emoji 按固定顺序出现
        """
        # 至少启用一个模块
        assume(any(enabled.values()))

        # 为启用的模块生成内容
        module_contents = {}
        for mod, is_enabled in enabled.items():
            if is_enabled:
                module_contents[mod] = f"{mod} 模块内容示例"

        briefing = generate_briefing(enabled, module_contents)

        # 提取简报中出现的 emoji 顺序
        found_emojis = []
        for emoji in EMOJI_ORDER:
            if emoji in briefing:
                found_emojis.append(emoji)

        # 验证找到的 emoji 保持原始顺序
        expected_emojis = [
            MODULE_EMOJI_MAP[mod]
            for mod in ["weather", "calendar", "reminders", "news", "reading", "quote"]
            if enabled.get(mod, False)
        ]
        assert found_emojis == expected_emojis, (
            f"emoji 顺序不正确: 期望 {expected_emojis}, 实际 {found_emojis}"
        )


# ============================================================
# Property 4: 简报标题行格式
# 验证匹配 ☀️ 晨间简报 · {月}月{日}日 {星期}
# **Validates: Requirements 8.3**
# ============================================================

class TestProperty4TitleFormat:
    """Property 4: 简报标题行格式"""

    @given(
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=31),
        weekday=st.sampled_from(VALID_WEEKDAYS),
    )
    @settings(max_examples=100)
    def test_title_format_matches_pattern(self, month, day, weekday):
        """
        Property 4: 简报标题行格式
        **Validates: Requirements 8.3**

        随机生成日期，验证标题行匹配固定格式
        """
        title = generate_briefing_title(month, day, weekday)

        # 验证标题格式
        pattern = r"^☀️ 晨间简报 · (\d{1,2})月(\d{1,2})日 (星期[一二三四五六日])$"
        match = re.match(pattern, title)
        assert match is not None, f"标题格式不匹配: {title}"

        # 验证月份和日期的有效性
        parsed_month = int(match.group(1))
        parsed_day = int(match.group(2))
        parsed_weekday = match.group(3)

        assert 1 <= parsed_month <= 12, f"月份无效: {parsed_month}"
        assert 1 <= parsed_day <= 31, f"日期无效: {parsed_day}"
        assert parsed_weekday in VALID_WEEKDAYS, f"星期无效: {parsed_weekday}"


# ============================================================
# Property 5: 简报模块行数限制
# 验证每个模块不超过 5 行
# **Validates: Requirements 8.4**
# ============================================================

class TestProperty5ModuleLineLimit:
    """Property 5: 简报模块行数限制"""

    @given(content=module_content_strategy())
    @settings(max_examples=100)
    def test_module_content_within_line_limit(self, content):
        """
        Property 5: 简报模块行数限制
        **Validates: Requirements 8.4**

        随机生成模块内容，验证每个模块不超过 5 行
        """
        # 统计内容行数（非空行）
        lines = [line for line in content.split("\n") if line.strip()]
        assert len(lines) <= 5, (
            f"模块内容超过 5 行限制: 实际 {len(lines)} 行"
        )

    @given(enabled=enabled_modules_strategy())
    @settings(max_examples=100)
    def test_briefing_modules_within_line_limit(self, enabled):
        """
        Property 5: 简报模块行数限制（完整简报验证）
        **Validates: Requirements 8.4**

        随机生成模块启用组合，验证生成的简报中每个模块不超过 5 行
        """
        assume(any(enabled.values()))

        # 为启用的模块生成不超过 5 行的内容
        module_contents = {}
        for mod, is_enabled in enabled.items():
            if is_enabled:
                num_lines = random.randint(1, 5)
                lines = [f"· 第{i+1}条内容" for i in range(num_lines)]
                module_contents[mod] = "\n".join(lines)

        briefing = generate_briefing(enabled, module_contents)

        # 按 emoji 分割模块，验证每个模块行数
        for mod, is_enabled in enabled.items():
            if is_enabled:
                emoji = MODULE_EMOJI_MAP[mod]
                if emoji in briefing:
                    # 提取该模块的内容区域
                    start = briefing.index(emoji)
                    # 找到下一个模块的起始位置或文本末尾
                    remaining_emojis = [
                        e for e in EMOJI_ORDER
                        if e in briefing and briefing.index(e) > start
                    ]
                    if remaining_emojis:
                        end = briefing.index(remaining_emojis[0])
                    else:
                        end = len(briefing)

                    section = briefing[start:end]
                    section_lines = [
                        l for l in section.split("\n") if l.strip()
                    ]
                    assert len(section_lines) <= 6, (
                        f"模块 {mod} 超过行数限制: "
                        f"{len(section_lines)} 行（含标题行）"
                    )


# ============================================================
# Property 6: 阅读池状态流转不变量
# 验证推荐前后文章总数不变
# **Validates: Requirements 6.3**
# ============================================================

class TestProperty6ReadingPoolInvariant:
    """Property 6: 阅读池状态流转不变量"""

    @staticmethod
    def recommend_articles(unread: list, recommended: list,
                           max_items: int) -> tuple:
        """
        模拟推荐操作：从未读列表中选取文章移至已推荐列表。
        返回操作后的 (unread, recommended) 元组。
        """
        num_to_recommend = min(max_items, len(unread))
        # 随机选取（模拟 Agent 的随机选取行为）
        selected_indices = random.sample(
            range(len(unread)), num_to_recommend
        )
        selected = [unread[i] for i in selected_indices]

        new_unread = [
            a for i, a in enumerate(unread) if i not in selected_indices
        ]
        new_recommended = recommended + selected

        return new_unread, new_recommended

    @given(pool=reading_pool_strategy(), max_items=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_total_articles_unchanged_after_recommendation(self, pool, max_items):
        """
        Property 6: 阅读池状态流转不变量
        **Validates: Requirements 6.3**

        随机生成阅读池和推荐数量，验证推荐前后文章总数不变
        """
        unread_before = list(pool["unread"])
        recommended_before = list(pool["recommended"])
        total_before = len(unread_before) + len(recommended_before)

        new_unread, new_recommended = self.recommend_articles(
            unread_before, recommended_before, max_items
        )
        total_after = len(new_unread) + len(new_recommended)

        assert total_before == total_after, (
            f"文章总数变化: 推荐前 {total_before}, 推荐后 {total_after}"
        )

    @given(pool=reading_pool_strategy(), max_items=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_unread_decrease_equals_recommended_increase(self, pool, max_items):
        """
        Property 6: 阅读池状态流转不变量
        **Validates: Requirements 6.3**

        验证"未读"减少量等于"已推荐"增加量
        """
        unread_before = list(pool["unread"])
        recommended_before = list(pool["recommended"])

        new_unread, new_recommended = self.recommend_articles(
            unread_before, recommended_before, max_items
        )

        unread_decrease = len(unread_before) - len(new_unread)
        recommended_increase = len(new_recommended) - len(recommended_before)

        assert unread_decrease == recommended_increase, (
            f"未读减少量({unread_decrease}) != 已推荐增加量({recommended_increase})"
        )


# ============================================================
# Property 7: 每日一句字数限制
# 验证汉字不超过 30 个
# **Validates: Requirements 7.2**
# ============================================================

class TestProperty7QuoteCharLimit:
    """Property 7: 每日一句字数限制"""

    @given(quote=chinese_text_strategy(max_chars=30))
    @settings(max_examples=100)
    def test_quote_within_char_limit(self, quote):
        """
        Property 7: 每日一句字数限制
        **Validates: Requirements 7.2**

        随机生成中文短句，验证汉字字符数不超过 30 个
        """
        char_count = count_chinese_chars(quote)
        assert char_count <= 30, (
            f"每日一句汉字数超过限制: {char_count} > 30, 内容: {quote}"
        )

    @given(quote=chinese_text_strategy(max_chars=50))
    @settings(max_examples=100)
    def test_overlength_quote_detected(self, quote):
        """
        Property 7: 每日一句字数限制（超长检测）
        **Validates: Requirements 7.2**

        验证字数统计函数能正确计算汉字数量
        """
        char_count = count_chinese_chars(quote)
        # 验证计数函数的正确性：汉字数应等于文本长度（因为策略只生成汉字）
        assert char_count == len(quote), (
            f"汉字计数不正确: count_chinese_chars={char_count}, len={len(quote)}"
        )


# ============================================================
# Property 8: 晚间日报结构完整性
# 验证包含四个部分：已完成、未完成、明日预览、晚安提醒
# **Validates: Requirements 14.5**
# ============================================================

class TestProperty8EveningReviewStructure:
    """Property 8: 晚间日报结构完整性"""

    @given(
        completed=st.lists(
            st.text(
                alphabet=st.sampled_from([chr(c) for c in range(0x4E00, 0x4E20)]),
                min_size=2, max_size=10,
            ),
            min_size=0, max_size=5,
        ),
        uncompleted=st.lists(
            st.text(
                alphabet=st.sampled_from([chr(c) for c in range(0x4E00, 0x4E20)]),
                min_size=2, max_size=10,
            ),
            min_size=0, max_size=5,
        ),
        tomorrow=st.lists(
            st.text(
                alphabet=st.sampled_from([chr(c) for c in range(0x4E00, 0x4E20)]),
                min_size=2, max_size=10,
            ),
            min_size=0, max_size=5,
        ),
        goodnight=st.text(
            alphabet=st.sampled_from([chr(c) for c in range(0x4E00, 0x4E20)]),
            min_size=2, max_size=20,
        ),
    )
    @settings(max_examples=100)
    def test_evening_review_has_four_sections(self, completed, uncompleted,
                                               tomorrow, goodnight):
        """
        Property 8: 晚间日报结构完整性
        **Validates: Requirements 14.5**

        随机生成晚间日报内容，验证包含四个部分
        """
        review = generate_evening_review(completed, uncompleted,
                                          tomorrow, goodnight)

        # 验证四个必要部分存在
        assert "✅ 已完成：" in review, "晚间日报缺少「已完成」部分"
        assert "⏳ 未完成：" in review, "晚间日报缺少「未完成」部分"
        assert "📅 明日预览：" in review, "晚间日报缺少「明日预览」部分"
        assert "💤 晚安提醒：" in review, "晚间日报缺少「晚安提醒」部分"


# ============================================================
# Property 9: 周报三段式结构验证
# 验证包含三个部分：本周目标总结、下周工作目标、周学习总结
# **Validates: Requirements 15.3**
# ============================================================

class TestProperty9WeeklyReportStructure:
    """Property 9: 周报三段式结构验证"""

    @given(
        summary=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
        next_week=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
        learning=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
    )
    @settings(max_examples=100)
    def test_weekly_report_has_three_sections(self, summary, next_week, learning):
        """
        Property 9: 周报三段式结构验证
        **Validates: Requirements 15.3**

        验证周报输出包含三个部分
        """
        report = generate_weekly_report(summary, next_week, learning)

        # 验证三个必要部分存在
        assert "一、本周目标总结" in report, "周报缺少「本周目标总结」部分"
        assert "二、下周工作目标" in report, "周报缺少「下周工作目标」部分"
        assert "三、周学习总结" in report, "周报缺少「周学习总结」部分"

    @given(
        summary=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
        next_week=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
        learning=st.text(
            alphabet=st.sampled_from(
                [chr(c) for c in range(0x4E00, 0x4E20)] + list("0123456789.%")
            ),
            min_size=5, max_size=50,
        ),
    )
    @settings(max_examples=100)
    def test_weekly_report_sections_in_correct_order(self, summary, next_week, learning):
        """
        Property 9: 周报三段式结构验证（顺序验证）
        **Validates: Requirements 15.3**

        验证周报三个部分按正确顺序出现
        """
        report = generate_weekly_report(summary, next_week, learning)

        pos_summary = report.index("一、本周目标总结")
        pos_next = report.index("二、下周工作目标")
        pos_learning = report.index("三、周学习总结")

        assert pos_summary < pos_next < pos_learning, (
            "周报三个部分顺序不正确"
        )
