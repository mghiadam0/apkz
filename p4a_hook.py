from pythonforandroid.toolchain import info, warning
from os.path import join, exists
import shutil

def before_apk_build(toolchain):
    """Modify build.gradle before APK build to force Kotlin version."""
    dist_dir = toolchain.ctx.dist_dir
    build_gradle = join(dist_dir, 'build.gradle')
    
    if exists(build_gradle):
        with open(build_gradle, 'r') as f:
            content = f.read()
        
        force_block = """
allprojects {
    configurations.all {
        resolutionStrategy {
            force 'org.jetbrains.kotlin:kotlin-stdlib:1.8.22'
            force 'org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.8.22'
            force 'org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.22'
        }
    }
}
"""
        
        if 'kotlin-stdlib:1.8.22' not in content:
            content += force_block
            with open(build_gradle, 'w') as f:
                f.write(content)
            info("Patched build.gradle with Kotlin version force")
