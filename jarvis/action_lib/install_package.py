from jarvis.action.base_action import BaseAction
import subprocess
import sys


class install_package(BaseAction):
    def __init__(self) -> None:
        super().__init__()
        self._description = "install environment missing package."
        self.action_type = 'BASH'

    def __call__(self, package: str, *args, **kwargs):

        """
        Install a Python package using pip.

        Args:
        package_name (str): Name of the package to install.
        """
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Package '{package}' installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install package '{package}'. Error: {e}")
        
        # try:
        #     # 检查pip是否已安装
        #     print("check pip ...")
        #     subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        # except subprocess.CalledProcessError:
        #     # 安装pip
        #     print("Installing pip...")
        #     subprocess.check_call([sys.executable, '-m', 'ensurepip'])

        # # 安装指定的包
        # try:
        #     print(f"Installing {package}...")
        #     subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        #     print(f"{package} installed successfully.")
        # except subprocess.CalledProcessError:
        #     print(f"Failed to install {package}.")        

