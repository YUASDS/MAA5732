import os
import site
import shutil
import zipfile
from pathlib import Path

from src.core import version

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIRECTORIES = ("adb", "config", "resource", "ui", "MaaCommonAssets")
EXCLUDED_DIRECTORIES = {".git", "__pycache__", "debug", "logs"}


def find_in_site_packages(*parts: str):
    """在 site-packages 中查找指定子目录,找不到返回None"""
    for path in site.getsitepackages():
        potential_path = os.path.join(path, *parts)
        if os.path.exists(potential_path):
            return potential_path
    return None


def iter_release_assets(assets_dir: Path):
    """仅收集运行资源,排除本机配置、日志、调试产物和缓存。"""
    for name in ASSET_DIRECTORIES:
        directory = assets_dir / name
        if not directory.is_dir():
            continue
        for root, dirs, files in os.walk(directory):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRECTORIES)
            for filename in sorted(files):
                path = Path(root) / filename
                relative = path.relative_to(assets_dir)
                if relative.as_posix() == "config/config.json":
                    continue
                if path.suffix.lower() in {".pyc", ".pyo", ".log"}:
                    continue
                yield path, relative


def package_release(exe_path: Path, assets_dir: Path) -> Path:
    """从本次 EXE 和源资源生成 ZIP,不遍历可能含旧版本的 dist。"""
    if not exe_path.is_file():
        raise FileNotFoundError(exe_path)
    if not assets_dir.is_dir():
        raise FileNotFoundError(assets_dir)
    zip_path = exe_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(exe_path, exe_path.name)
        for source, relative in iter_release_assets(assets_dir):
            # 同时更新 EXE 旁的资源,方便本地运行;已有个人配置不覆盖。
            destination = exe_path.parent / "assets" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            archive.write(source, (Path("assets") / relative).as_posix())
    return zip_path


def main(dist_dir: Path = None):
    import PyInstaller.__main__

    dist_dir = Path(dist_dir) if dist_dir is not None else PROJECT_DIR / "dist"
    dist_dir = dist_dir.resolve()
    icon_path = PROJECT_DIR / "assets" / "resource" / "image" / "logo.ico"
    if not icon_path.is_file():
        raise FileNotFoundError(icon_path)

    maa_bin_path = find_in_site_packages("maa", "bin")
    if maa_bin_path is None:
        raise FileNotFoundError("Path containing maa/bin not found")
    agent_bin_path = find_in_site_packages("MaaAgentBinary")
    if agent_bin_path is None:
        raise FileNotFoundError("Path containing MaaAgentBinary not found")

    exe_name = f"MAA_5732_{version}.exe"
    PyInstaller.__main__.run(
        [
            str(PROJECT_DIR / "main.py"),
            "--onefile",
            f"--name={exe_name}",
            f"--add-data={maa_bin_path}{os.pathsep}maa/bin",
            f"--add-data={agent_bin_path}{os.pathsep}MaaAgentBinary",
            f"--distpath={dist_dir}",
            f"--workpath={PROJECT_DIR / 'build'}",
            f"--specpath={PROJECT_DIR}",
            "--clean",
            "--uac-admin",
            f"--icon={icon_path}",
            "--noconsole",
        ]
    )
    zip_path = package_release(dist_dir / exe_name, PROJECT_DIR / "assets")
    print(f"Packaging and compression completed: {zip_path}")


if __name__ == "__main__":
    main()
