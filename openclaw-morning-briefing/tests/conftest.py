# -*- coding: utf-8 -*-
"""
pytest 配置文件 - 共享 fixtures 和测试配置
"""

import json
import os
import pytest


# config.json 文件的相对路径（从工作区根目录算起）
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "deploy",
    "morning-briefing",
    "config.json",
)


@pytest.fixture
def config():
    """加载 config.json 配置文件并返回解析后的字典"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def config_raw():
    """返回 config.json 的原始文本内容，用于凭证安全检测等场景"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return f.read()
