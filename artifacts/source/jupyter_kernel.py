import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import time
import signal
import psutil
import socket

from jupyter_client.manager import KernelManager


class ExecutionResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    images: Optional[List[str]] = None


def get_host_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return "0.0.0.0"


class JupyterKernel:
    def __init__(self):
        self.km = None
        self.kc = None
        self.connection_file = None
        self._start_kernel()

    def _start_kernel(self):
        try:
            if self.km:
                self.shutdown()

            self.km = KernelManager(ip=get_host_ip())
            self.km.start_kernel()
            self.connection_file = self.km.connection_file
            self.kc = self.km.client()
            self.kc.start_channels()

            # 等待 kernel 完全准备好
            timeout = 30
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    raise Exception("Timeout waiting for kernel to start")
                try:
                    self.kc.wait_for_ready(timeout=timeout)
                    break
                except Exception as e:
                    if "Timeout" not in str(e):
                        raise
                    continue

            # 初始化必要的包和配置
            init_code = """
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from IPython.display import display
%matplotlib inline

# 设置 matplotlib 中文字体支持
plt.style.use('default')
plt.rcParams['figure.figsize'] = [8, 6]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['savefig.edgecolor'] = 'none'

# 配置中文字体
# 强制重新初始化字体管理器以识别新安装的字体
fm.fontManager.__init__()

# 查找可用的 CJK 字体
cjk_fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name]
if cjk_fonts:
    # 优先使用简体中文字体，如果没有则使用日文字体（也支持中文）
    preferred_fonts = ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'Noto Sans CJK JP']
    selected_font = None
    for font in preferred_fonts:
        if font in cjk_fonts:
            selected_font = font
            break

    if selected_font:
        plt.rcParams['font.family'] = selected_font
    else:
        # 使用找到的第一个 CJK 字体
        plt.rcParams['font.family'] = list(set(cjk_fonts))[0]
else:
    # 回退到默认配置
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False
"""
            self.execute(init_code)
        except Exception as e:
            print(f"Kernel initialization error: {str(e)}")
            self.shutdown()
            raise

    def _ensure_kernel_alive(self):
        """确保 kernel 是活跃的，如果不是则重启"""
        try:
            if not self.kc or not self.km:
                raise Exception("Kernel not initialized")

            # 检查 kernel 是否还在运行
            if not self.km.is_alive():
                raise Exception("Kernel is not alive")

            # 检查 kernel 是否响应
            try:
                self.kc.kernel_info()
            except Exception:
                raise Exception("Kernel is not responding")

        except Exception as e:
            print(f"Kernel check failed: {str(e)}")
            self._start_kernel()

    def execute(self, code: str, timeout: int = 30) -> ExecutionResult:
        try:
            # 确保 kernel 是活跃的
            self._ensure_kernel_alive()

            # 执行用户代码
            if not self.kc:
                raise Exception("Kernel not initialized")

            msg_id = self.kc.execute(code)

            # 等待执行结果
            output = []
            error = None
            images = []
            start_time = time.time()
            removed_prefix = False

            while True:
                try:
                    if time.time() - start_time > timeout:
                        return ExecutionResult(
                            success=False,
                            output="",
                            error=f"Executing code timed out, timeout: {timeout} seconds",
                            images=[],
                        )

                    msg = self.kc.get_iopub_msg(timeout=timeout + 1)
                    msg_type = msg["header"]["msg_type"]

                    if msg_type == "stream":
                        # 直接添加 stream 输出，不需要清理
                        output.append(msg["content"]["text"])
                    elif msg_type == "error":
                        error = "\n".join(msg["content"]["traceback"])
                    elif msg_type == "execute_result":
                        if isinstance(msg["content"]["data"], dict):
                            if "text/plain" in msg["content"]["data"]:
                                text = msg["content"]["data"]["text/plain"]
                                # # 去除第一个行号字符
                                # if not removed_prefix:
                                #     text = text[1:]
                                #     removed_prefix = True
                                output.append(text)
                            if "image/png" in msg["content"]["data"]:
                                images.append(msg["content"]["data"]["image/png"])
                    elif msg_type == "display_data":
                        if isinstance(msg["content"]["data"], dict):
                            if "image/png" in msg["content"]["data"]:
                                images.append(msg["content"]["data"]["image/png"])
                            elif "text/plain" in msg["content"]["data"]:
                                text = msg["content"]["data"]["text/plain"]
                                output.append(text)

                    if (
                        msg["parent_header"]["msg_id"] == msg_id
                        and msg_type == "status"
                        and msg["content"]["execution_state"] == "idle"
                    ):
                        break
                except Exception as e:
                    if str(e) == "Timeout waiting for message":
                        continue
                    raise e

            # 合并输出，保持换行符
            final_output = "".join(output).strip()
            return ExecutionResult(
                success=error is None,  # 如果有错误，则 success 为 False
                output=final_output,
                error=error,
                images=images,
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Execution error: {e.__class__.__name__} {str(e)}")
            # 如果执行出错，尝试重启 kernel
            try:
                self._start_kernel()
            except Exception as restart_error:
                print(f"Failed to restart kernel: {str(restart_error)}")
            raw_error = f"{e.__class__.__name__}: {str(e)}"
            if "empty" in raw_error.lower():
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Executing code timed out, timeout: {timeout} seconds",
                    images=[],
                )
            else:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"{e.__class__.__name__}: {str(e)}",
                    images=[],
                )

    def reset_kernel(self) -> Dict[str, Any]:
        """重置 kernel"""
        try:
            print("Resetting kernel...")
            old_connection_file = self.connection_file
            self.shutdown()
            self._start_kernel()
            return {
                "success": True,
                "message": "Kernel reset successfully",
                "old_connection_file": old_connection_file,
                "new_connection_file": self.connection_file,
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to reset kernel: {str(e)}"}

    def interrupt_kernel(self) -> Dict[str, Any]:
        """中断 kernel 执行"""
        try:
            if not self.km:
                return {"success": False, "message": "Kernel not initialized"}

            # 获取 kernel 进程 ID
            kernel_id = self._get_kernel_pid()

            if kernel_id:
                # 发送 SIGINT 信号中断 kernel
                try:
                    process = psutil.Process(kernel_id)
                    process.send_signal(signal.SIGINT)
                    print(f"Sent SIGINT to kernel process {kernel_id}")
                except psutil.NoSuchProcess:
                    print(f"Kernel process {kernel_id} not found")
                except Exception as e:
                    print(f"Error sending signal to kernel process: {str(e)}")

            # 也可以通过 jupyter client 发送中断
            try:
                if self.kc and hasattr(self.kc, "interrupt"):
                    self.kc.interrupt()  # type: ignore
            except (AttributeError, Exception):
                # 某些版本的 client 可能没有 interrupt 方法或者方法调用失败
                pass

            return {
                "success": True,
                "message": "Kernel interrupted successfully",
                "kernel_pid": kernel_id,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to interrupt kernel: {str(e)}",
            }

    def get_connection_info(self) -> Dict[str, Any]:
        """获取 kernel 连接信息"""
        try:
            if not self.km or not self.connection_file:
                return {"success": False, "message": "Kernel not initialized"}

            # 读取连接文件内容
            connection_info = {}
            if os.path.exists(self.connection_file):
                with open(self.connection_file, "r") as f:
                    connection_info = json.load(f)

            return {
                "success": True,
                "connection_file": self.connection_file,
                "connection_info": connection_info,
                "kernel_alive": self.km.is_alive() if self.km else False,
                "kernel_pid": self._get_kernel_pid(),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get connection info: {str(e)}",
            }

    def debug_kernel_manager(self) -> Dict[str, Any]:
        """调试 KernelManager 的状态和属性"""
        debug_info = {
            "km_exists": self.km is not None,
            "km_type": str(type(self.km)) if self.km else None,
            "km_alive": self.km.is_alive() if self.km else False,
            "attributes": {},
            "methods_tried": {},
        }

        if self.km:
            # 检查各种属性
            for attr in ["kernel", "kernel_id", "connection_file", "provisioner"]:
                if hasattr(self.km, attr):
                    try:
                        value = getattr(self.km, attr)
                        debug_info["attributes"][attr] = {
                            "exists": True,
                            "value": str(value),
                            "type": str(type(value)),
                            "is_none": value is None,
                        }

                        # 如果是 provisioner，进一步检查
                        if attr == "provisioner" and value:
                            debug_info["attributes"]["provisioner"]["process"] = {
                                "exists": hasattr(value, "process"),
                                "value": str(getattr(value, "process", None)),
                                "type": str(type(getattr(value, "process", None))),
                            }
                            if hasattr(value, "process") and value.process:
                                debug_info["attributes"]["provisioner"]["process"][
                                    "pid"
                                ] = {
                                    "exists": hasattr(value.process, "pid"),
                                    "value": getattr(value.process, "pid", None),
                                }

                        # 如果是 kernel，进一步检查
                        if attr == "kernel" and value:
                            debug_info["attributes"]["kernel"]["pid"] = {
                                "exists": hasattr(value, "pid"),
                                "value": getattr(value, "pid", None),
                            }

                    except Exception as e:
                        debug_info["attributes"][attr] = {
                            "exists": True,
                            "error": str(e),
                        }
                else:
                    debug_info["attributes"][attr] = {"exists": False}

        return debug_info

    def _get_kernel_pid(self) -> Optional[int]:
        """安全地获取 kernel 进程 ID"""
        if not self.km:
            return None

        try:
            # 方法1: 通过 provisioner (jupyter-client >= 7.0)
            if hasattr(self.km, "provisioner"):
                provisioner = getattr(self.km, "provisioner", None)
                if provisioner and hasattr(provisioner, "process"):
                    process = getattr(provisioner, "process", None)
                    if process and hasattr(process, "pid"):
                        return getattr(process, "pid", None)

            # 方法2: 直接从 kernel 属性 (旧版本)
            if hasattr(self.km, "kernel"):
                kernel = getattr(self.km, "kernel", None)
                if kernel and hasattr(kernel, "pid"):
                    return getattr(kernel, "pid", None)

            # 方法3: 通过 kernel_id 和系统进程查找
            if hasattr(self.km, "kernel_id") and self.km.kernel_id:
                import psutil

                # 查找包含 kernel_id 的 python 进程
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    try:
                        if proc.info["name"] and "python" in proc.info["name"].lower():
                            cmdline = proc.info["cmdline"] or []
                            for arg in cmdline:
                                if self.km.kernel_id in str(arg):
                                    return proc.info["pid"]
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            # 方法4: 通过连接文件查找相关进程
            if hasattr(self.km, "connection_file") and self.km.connection_file:
                import os
                import psutil

                connection_file = os.path.basename(self.km.connection_file)
                kernel_name = connection_file.replace("kernel-", "").replace(
                    ".json", ""
                )

                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    try:
                        if proc.info["name"] and "python" in proc.info["name"].lower():
                            cmdline = proc.info["cmdline"] or []
                            for arg in cmdline:
                                if kernel_name in str(arg) or connection_file in str(
                                    arg
                                ):
                                    return proc.info["pid"]
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

        except Exception as e:
            print(f"Error getting kernel PID: {str(e)}")

        return None

    def get_kernel_status(self) -> Dict[str, Any]:
        """获取 kernel 状态信息"""
        try:
            status = {
                "kernel_alive": False,
                "kernel_pid": None,
                "connection_file": self.connection_file,
                "client_connected": False,
            }

            if self.km:
                status["kernel_alive"] = self.km.is_alive()
                status["kernel_pid"] = self._get_kernel_pid()

            if self.kc:
                try:
                    # 尝试获取 kernel 信息来检查连接状态
                    self.kc.kernel_info()
                    status["client_connected"] = True
                except:
                    status["client_connected"] = False

            return {"success": True, **status}
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get kernel status: {str(e)}",
            }

    def shutdown(self):
        """安全地关闭 kernel"""
        try:
            if self.kc:
                self.kc.stop_channels()
            if self.km:
                self.km.shutdown_kernel()
        except Exception as e:
            print(f"Error during kernel shutdown: {str(e)}")
        finally:
            self.kc = None
            self.km = None
            self.connection_file = None


kernel = JupyterKernel()
