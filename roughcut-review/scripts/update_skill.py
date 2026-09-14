#!/usr/bin/env python3
"""Check the official repository and update an installed roughcut-review Skill."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
import zipfile
from pathlib import Path, PurePosixPath


DEFAULT_VERSION_URL = (
    "https://raw.githubusercontent.com/MIAOzhenhao2002/"
    "medical-roughcut-review-skill/main/roughcut-review/VERSION"
)
DEFAULT_ARCHIVE_URL = (
    "https://codeload.github.com/MIAOzhenhao2002/"
    "medical-roughcut-review-skill/zip/refs/heads/main"
)
USER_AGENT = "medical-roughcut-review-skill-updater/0.3.0"
MAX_ARCHIVE_FILES = 500
MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024


class UpdateError(RuntimeError):
    """A safe, user-facing update failure."""


def parse_version(value: str) -> tuple[int, int, int]:
    parts = value.strip().split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise UpdateError(f"无法识别版本号：{value!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def read_version(skill_dir: Path) -> str:
    version_file = skill_dir / "VERSION"
    if not version_file.is_file():
        raise UpdateError(f"缺少版本文件：{version_file}")
    value = version_file.read_text(encoding="utf-8").strip()
    parse_version(value)
    return value


def fetch_bytes(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise UpdateError(f"无法访问更新源：{exc}") from exc


def archive_skill_prefix(archive: zipfile.ZipFile) -> PurePosixPath:
    items = archive.infolist()
    if len(items) > MAX_ARCHIVE_FILES:
        raise UpdateError("更新包文件数量异常")
    if sum(item.file_size for item in items) > MAX_UNCOMPRESSED_BYTES:
        raise UpdateError("更新包解压后体积异常")
    candidates: set[PurePosixPath] = set()
    for item in items:
        if "\\" in item.filename:
            raise UpdateError("更新包包含不安全路径")
        path = PurePosixPath(item.filename)
        if path.is_absolute() or ".." in path.parts:
            raise UpdateError("更新包包含不安全路径")
        mode = item.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise UpdateError("更新包不能包含符号链接")
        if len(path.parts) >= 3 and path.parts[-2:] == ("roughcut-review", "SKILL.md"):
            candidates.add(PurePosixPath(*path.parts[:-1]))
    if len(candidates) != 1:
        raise UpdateError("更新包中没有唯一的 roughcut-review/SKILL.md")
    return candidates.pop()


def extract_skill(archive_path: Path, destination: Path, expected_version: str) -> Path:
    skill_dir = destination / "roughcut-review"
    with zipfile.ZipFile(archive_path) as archive:
        prefix = archive_skill_prefix(archive)
        prefix_parts = prefix.parts
        for item in archive.infolist():
            path = PurePosixPath(item.filename)
            if path.parts[: len(prefix_parts)] != prefix_parts:
                continue
            relative = path.parts[len(prefix_parts) :]
            if not relative or item.is_dir():
                continue
            target = skill_dir.joinpath(*relative)
            if skill_dir.resolve() not in target.resolve().parents:
                raise UpdateError("更新包试图写出Skill目录")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)

    required = [skill_dir / "SKILL.md", skill_dir / "VERSION", skill_dir / "scripts" / "update_skill.py"]
    missing = [str(path.relative_to(skill_dir)) for path in required if not path.is_file()]
    if missing:
        raise UpdateError(f"更新包缺少必要文件：{', '.join(missing)}")
    if read_version(skill_dir) != expected_version:
        raise UpdateError("版本文件与更新检查结果不一致")
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "name: roughcut-review" not in skill_text or f'version: "{expected_version}"' not in skill_text:
        raise UpdateError("SKILL.md名称或版本与更新包不一致")
    return skill_dir


def replace_skill(current: Path, staged: Path, current_version: str) -> Path:
    parent = current.parent
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = parent / ".roughcut-review-backups"
    backup = backup_root / f"roughcut-review-{current_version}-{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        backup = backup.with_name(f"{backup.name}-{uuid.uuid4().hex[:8]}")
    shutil.copytree(current, backup)

    old = parent / f".roughcut-review-old-{uuid.uuid4().hex}"
    previous_cwd = Path.cwd()
    try:
        os.chdir(parent)
        os.replace(current, old)
        try:
            os.replace(staged, current)
        except Exception:
            os.replace(old, current)
            raise
        shutil.rmtree(old)
    except Exception as exc:
        raise UpdateError(f"更新替换失败，原版本仍保留在 {backup}：{exc}") from exc
    finally:
        try:
            os.chdir(previous_cwd)
        except OSError:
            os.chdir(parent)
    return backup


def update(
    skill_dir: Path,
    *,
    check_only: bool,
    version_url: str,
    archive_url: str,
    timeout: int,
) -> int:
    skill_dir = skill_dir.resolve()
    if skill_dir.name != "roughcut-review" or not (skill_dir / "SKILL.md").is_file():
        raise UpdateError("安装目录必须是包含 SKILL.md 的 roughcut-review 文件夹")
    if (skill_dir.parent / ".git").exists():
        raise UpdateError("检测到Git源码仓库；请用 git pull --ff-only 更新，避免覆盖开发改动")

    current_version = read_version(skill_dir)
    remote_version = fetch_bytes(version_url, timeout).decode("utf-8").strip()
    current_key = parse_version(current_version)
    remote_key = parse_version(remote_version)

    if remote_key <= current_key:
        print(f"已是最新版本：{current_version}")
        return 0
    if check_only:
        print(f"发现新版本：{current_version} -> {remote_version}")
        return 2

    with tempfile.TemporaryDirectory(prefix="roughcut-review-update-", dir=skill_dir.parent) as temp:
        temp_dir = Path(temp)
        archive_path = temp_dir / "update.zip"
        archive_path.write_bytes(fetch_bytes(archive_url, timeout))
        staged = extract_skill(archive_path, temp_dir / "staged", remote_version)
        backup = replace_skill(skill_dir, staged, current_version)

    print(f"更新完成：{current_version} -> {remote_version}")
    print(f"回滚备份：{backup}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="检查官方仓库；默认在发现新版本后备份并自动更新当前Skill。"
    )
    parser.add_argument(
        "--install-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="roughcut-review安装目录；默认使用本脚本所在Skill。",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只报告是否有新版本，不安装。发现更新时退出码为2。",
    )
    parser.add_argument("--timeout", type=int, default=30, help="网络超时秒数，默认30。")
    parser.add_argument("--version-url", default=DEFAULT_VERSION_URL, help=argparse.SUPPRESS)
    parser.add_argument("--archive-url", default=DEFAULT_ARCHIVE_URL, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0:
        print("更新失败：timeout必须大于0", file=sys.stderr)
        return 1
    try:
        return update(
            args.install_dir,
            check_only=args.check_only,
            version_url=args.version_url,
            archive_url=args.archive_url,
            timeout=args.timeout,
        )
    except (UpdateError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        print(f"更新失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
