"""
Hook to fix Kotlin stdlib duplicate class errors in p4a builds.
"""

from os.path import join, exists
from pythonforandroid.logger import info, warning


FORCE_BLOCK = """
allprojects {
    configurations.all {
        resolutionStrategy {
            force 'org.jetbrains.kotlin:kotlin-stdlib:1.8.22'
            force 'org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.8.22'
            force 'org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.22'
            force 'org.jetbrains.kotlin:kotlin-stdlib-common:1.8.22'
        }
        exclude group: 'org.jetbrains.kotlin', module: 'kotlin-stdlib-jdk7'
        exclude group: 'org.jetbrains.kotlin', module: 'kotlin-stdlib-jdk8'
    }
}
"""


def _patch_build_gradle(path):
    if not exists(path):
        return False
    with open(path, "r") as f:
        content = f.read()
    if "kotlin-stdlib:1.8.22" in content:
        info(f"[p4a_hook] {path} already patched")
        return True
    # Append force block at end of file (Gradle allows allprojects anywhere in root build.gradle)
    content = content.rstrip() + "\n\n" + FORCE_BLOCK + "\n"
    with open(path, "w") as f:
        f.write(content)
    info(f"[p4a_hook] Patched {path}")
    return True


def before_apk_build(toolchain):
    """Called by p4a before running Gradle to build the APK."""
    try:
        ctx = toolchain.ctx
        dist_dir = ctx.dist_dir
    except Exception as e:
        warning(f"[p4a_hook] Cannot access toolchain.ctx: {e}")
        return

    candidates = [
        join(dist_dir, "build.gradle"),
        join(dist_dir, "build", "build.gradle"),
    ]
    for c in candidates:
        if _patch_build_gradle(c):
            return
    warning(f"[p4a_hook] build.gradle not found in {dist_dir}")
