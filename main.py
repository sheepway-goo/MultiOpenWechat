import sys
import os
import subprocess
import winreg
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QSpinBox,
                             QFileDialog, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon



# 解决打包后找不到图片资源的问题
def resource_path(relative_path):
    """ 获取资源的绝对路径，适配开发环境和 PyInstaller 打包后的环境 """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



class WeChatMultiOpener(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyPyTools", "WeChatOpener")
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon(resource_path("wechat.ico")))


        self.setWindowTitle('微信多开小工具 - 最终版')
        self.setGeometry(300, 300, 500, 250)
        self.setFixedSize(500, 250)

        main_layout = QVBoxLayout()

        # ... (中间的布局代码保持不变，省略以节省空间) ...
        # ... (Path Group, Count Group, Button Layout) ...

        # 1. 路径部分
        path_group = QGroupBox("微信路径设置")
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        saved_path = self.settings.value("wechat_path", "")
        if saved_path and os.path.exists(saved_path):
            initial_path = saved_path
        else:
            initial_path = self.get_wechat_path_from_registry()
        self.path_input.setText(initial_path)
        self.btn_browse = QPushButton("浏览...")
        self.btn_browse.clicked.connect(self.select_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.btn_browse)
        path_group.setLayout(path_layout)

        # 2. 数量部分
        count_group = QGroupBox("多开数量设置")
        count_layout = QHBoxLayout()
        lbl_count = QLabel("开启数量:")
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10)
        saved_count = self.settings.value("open_count", 2, type=int)
        self.spin_count.setValue(saved_count)
        self.spin_count.setFixedWidth(100)
        count_layout.addWidget(lbl_count)
        count_layout.addWidget(self.spin_count)
        count_layout.addStretch()
        count_group.setLayout(count_layout)

        # 3. 按钮部分
        btn_layout = QVBoxLayout()
        self.btn_start = QPushButton("立即启动")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #07C160; color: white; border-radius: 5px;")
        self.btn_start.clicked.connect(self.start_wechat)
        btn_layout.addWidget(self.btn_start)

        main_layout.addWidget(path_group)
        main_layout.addWidget(count_group)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)


    def get_wechat_path_from_registry(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat")
            path, _ = winreg.QueryValueEx(key, "InstallPath")
            # 防止 InstallPath 记录的只是目录
            exe_path = os.path.join(path, "WeChat.exe")
            if os.path.exists(exe_path): return exe_path

            # 兼容 Weixin.exe
            exe_path_new = os.path.join(path, "Weixin.exe")
            if os.path.exists(exe_path_new): return exe_path_new
        except Exception:
            pass
        return ""


    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择微信启动程序", "", "Executable Files (*.exe)")
        if file_path:
            self.path_input.setText(file_path)


    def start_wechat(self):
        path = self.path_input.text().strip()
        count = self.spin_count.value()

        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "错误", "路径无效或未找到执行文件！")
            return

        file_name = os.path.basename(path)
        if file_name.lower() not in ["wechat.exe", "weixin.exe"]:
            reply = QMessageBox.question(self, "确认",
                                         f"检测到文件名是 {file_name}，而不是标准的 WeChat.exe 或 Weixin.exe。\n\n是否继续启动？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return

        self.settings.setValue("wechat_path", path)
        self.settings.setValue("open_count", count)

        try:
            for i in range(count):
                subprocess.Popen(f'"{path}"', shell=True, cwd=os.path.dirname(path))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = WeChatMultiOpener()
    window.show()
    sys.exit(app.exec_())
