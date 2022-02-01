import logging
from logging.handlers import RotatingFileHandler
import pickle
import sys
import os
from pathlib import Path
from typing import Optional


class FileHandlers:
    def __init__(self, path: Optional[str] = None):
        self.log_level = self.set_log_level()
        self.path, self.op_sys = self.file_handling(path)
        self.user_file = os.path.abspath(self.path / "domains.user")
        self.log_file = str(os.path.abspath(self.path / "domains.log"))
        if not os.path.exists(self.log_file) or not os.path.exists(self.user_file):
            self.make_directories()
        self.sys_log = self.initialize_loggers()

    @staticmethod
    def file_handling(path: Optional[str] = None):
        if os.name == "nt":
            path = path or "domains"
            path = Path(os.getenv("LOCALAPPDATA")) / path
            op_sys = "nt"
        else:
            path = path or ".domains"
            path = Path(os.path.abspath(os.getenv("HOME"))) / path
            op_sys = "pos"
        return path, op_sys

    def make_directories(self):
        os.makedirs(self.path, exist_ok=True)

    @staticmethod
    def file_or_dir(path):
        if os.path.isdir(path):
            os.chmod(path, 0o770)
        elif os.path.isfile(path):
            os.chmod(path, 0o665)

    def initialize_loggers(self):
        sys_log = logging.getLogger("Domains DDNS API")
        if self.log_level == "debug":
            level = logging.DEBUG
        elif self.log_level == "warning":
            level = logging.WARNING
        else:
            level = logging.INFO
        sys_log.setLevel(level)
        fh = RotatingFileHandler(
            self.log_file,
            mode="a",
            maxBytes=100 * 1024,
            backupCount=2,
            encoding=None,
        )
        sh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(name)s][%(asctime)s][%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        sh_formatter = logging.Formatter(
            "[%(name)s][%(asctime)s][%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        sh.setFormatter(sh_formatter)
        sys_log.addHandler(sh)
        sys_log.addHandler(fh)
        sys_log.debug("Loggers initialized")
        return sys_log

    def log(self, msg, level="info"):
        if level.lower() == "info":
            self.sys_log.info(msg)
        elif level.lower() == "debug":
            self.sys_log.debug(msg)
        elif level.lower() == "warning":
            self.sys_log.warning(msg)
        elif level.lower() == "error":
            self.sys_log.error(msg)

    def set_log_level(self, level="info"):
        self.log_level = level
        return self.log_level

    def save_user(self, user):
        """Pickle (serialize) user instance."""
        with open(self.user_file, "wb") as pickle_file:
            pickle.dump(user, pickle_file)
        self.log("User saved.", "debug")

    @staticmethod
    def load_user(user_file):
        """Unpickle (deserialize) user instance."""
        with open(user_file, "rb") as pickle_file:
            return pickle.load(pickle_file)

    def delete_user(self):
        """Delete user pickle file (serialized user instance)."""
        if (
            input("Are you sure you want to delete the current user? [Y/n] ").lower()
            == "n"
        ):
            return
        os.remove(self.user_file)
        self.log("User deleted", "info")
        print(
            "Run the script without options to create a new user, or "
            '"domains-api -l path/to/pickle" to load one from file'
        )

    def clear_logs(self):
        with open(self.log_file, "r") as r:
            lines = r.readlines()
            if len(lines) > 100:
                tail = r.readlines()[-10:]
                with open(self.log_file, "w") as w:
                    w.writelines(tail)


if __name__ == "__main__":
    fhs = FileHandlers()
    fhs.log("Testing", "info")
