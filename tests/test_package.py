import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "roughcut-review"


class StandaloneSkillTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            ROOT / "AGENTS.md",
            ROOT / "INSTALL.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "select-and-split.md",
            SKILL / "references" / "context-cards.md",
            SKILL / "references" / "medical-review.md",
            SKILL / "references" / "minimal-rewrite.md",
            SKILL / "references" / "independent-review.md",
            SKILL / "assets" / "title-handoff.md",
            ROOT / "LICENSE",
            ROOT / "SECURITY.md",
        ]
        self.assertEqual([str(path) for path in required if not path.is_file()], [])

    def test_frontmatter_and_folder_name_match(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        self.assertIn("name: roughcut-review", match.group(1))
        self.assertRegex(match.group(1), r"description: .+")
        self.assertIn("license: MIT", match.group(1))
        self.assertIn('version: "0.2.0"', match.group(1))
        self.assertIn("standard: Agent Skills", match.group(1))

    def test_markdown_links_are_local_and_resolve(self):
        for source in SKILL.rglob("*.md"):
            text = source.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (source.parent / target).resolve()
                self.assertTrue(resolved.is_file(), f"{source}: missing {target}")
                self.assertTrue(str(resolved).startswith(str(SKILL.resolve())))

    def test_no_mother_project_dependencies_remain(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SKILL.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".json"}
        )
        forbidden = [
            "templates/",
            "config/",
            "profiles/",
            "roughcut-module-map",
            "medical-guideline-brief",
            "clone-minimal-rewrite",
            "roughcut-independent-review",
            "花医生",
        ]
        self.assertEqual([item for item in forbidden if item in text], [])

    def test_assets_and_references_are_generic(self):
        for path in (SKILL / "assets").glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SKILL.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".json"}
        )
        self.assertNotRegex(text, r"\b1[3-9]\d{9}\b")
        self.assertNotRegex(text, r"\b\d{15,18}[0-9Xx]\b")

    def test_implicit_invocation_is_enabled(self):
        yaml_text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: true", yaml_text)
        self.assertIn("$roughcut-review", yaml_text)

    def test_iterative_review_and_context_cards_are_self_contained(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        intake = (SKILL / "references" / "intake-and-state.md").read_text(encoding="utf-8")
        delete = (SKILL / "references" / "delete-and-keep.md").read_text(encoding="utf-8")
        cards = (SKILL / "references" / "context-cards.md").read_text(encoding="utf-8")
        final = (SKILL / "references" / "revise-final-and-handoff.md").read_text(encoding="utf-8")
        combined = "\n".join([skill_text, intake, delete, cards, final])

        self.assertIn("V1、V2、V3", combined)
        self.assertIn("复检次数不预设", combined)
        self.assertIn("只复检变化及其影响到的相邻片段", combined)
        self.assertIn("过度碎剪检查", combined)
        self.assertIn("先修剪辑，再补字", combined)
        self.assertIn("状态：候选 / 待人工看片 / 最终字卡 / 取消 / 不加", combined)
        self.assertIn("每句话必须能追溯", combined)
        self.assertIn("不能把上一轮字卡无条件带入新版本", combined)
        self.assertNotIn("roughcut-context-cards", combined)

    def test_package_is_positioned_as_cross_agent(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        install = (ROOT / "INSTALL.md").read_text(encoding="utf-8")
        entry = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        combined = "\n".join([readme, install, entry])

        self.assertIn("通用 Agent 能力包", readme)
        self.assertIn("Agent Skills 规范", readme)
        self.assertIn("OpenAI Codex", combined)
        self.assertIn("Claude Code", combined)
        self.assertIn("GitHub Copilot", combined)
        self.assertIn("唯一业务入口", entry)
        self.assertIn("可选界面适配", entry)
        self.assertNotIn("一个开源、可独立安装的 Codex Skill", readme)


if __name__ == "__main__":
    unittest.main()
