import logging
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# 脚本目录
SCRIPTS_DIR = Path("app/scripts")

def run_script(script_name: str, params: dict = None):
    """
    运行指定的脚本
    
    Args:
        script_name: 脚本名称
        params: 脚本参数
    
    Returns:
        执行结果
    """
    script_path = SCRIPTS_DIR / f"{script_name}.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"脚本 {script_name} 不存在")
    
    try:
        # 构建命令
        cmd = ["python", str(script_path)]
        
        # 添加参数
        if params:
            for key, value in params.items():
                cmd.extend([f"--{key}", str(value)])
        
        # 执行脚本
        logger.info(f"执行脚本: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"脚本执行失败: {e}")
        return {
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"脚本执行异常: {e}")
        raise