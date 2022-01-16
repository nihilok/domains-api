import logging
import pickle
import sys
import os
from pathlib import Path


class FileHandlers:
    def __init__(self):
        self.log_level = self.set_log_level()
        self.path, self.op_sys = self.file_handling()
        self.user_file = os.path.abspath(self.path / "domains.user")
        self.log_file = os.path.abspath(self.path / "domains.log")
        if not os.path.exists(self.log_file) or not os.path.exists(self.user_file):
            try:
                self.make_directories()
            except (PermissionError, FileNotFoundError, KeyError) as e:
                print("Run with sudo first time to set permissions")
                raise e
        self.sys_log = self.initialize_loggers()

    @staticmethod
    def file_handling():
        if os.name == "nt":
            path = "domains-api"
            path = Path(os.getenv("LOCALAPPDATA")) / path
            op_sys = "nt"
        else:
            path = Path(os.path.abspath(os.getenv("HOME"))) / ".domains-api"
            op_sys = "pos"
        return path, op_sys

    def make_directories(self):
        os.makedirs(self.path, exist_ok=True)

    def set_permissions(self, path, gid=33):
        try:
            os.chown(path, int(os.environ["SUDO_GID"]), gid)
            self.file_or_dir(path)
        except KeyError:
            try:
                os.chown(path, int(os.getuid()), gid)
                self.file_or_dir(path)
            except PermissionError as e:
                raise e

    @staticmethod
    def file_or_dir(path):
        if os.path.isdir(path):
            os.chmod(path, 0o770)
        elif os.path.isfile(path):
            os.chmod(path, 0o665)

    def initialize_loggers(self):
        sys_log = logging.getLogger("Domains API")
        if self.log_level == "debug":
            level = logging.DEBUG
        elif self.log_level == "warning":
            level = logging.WARNING
        else:
            level = logging.INFO
        sys_log.setLevel(level)
        fh = logging.FileHandler(self.log_file)
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
        if level == "info":
            self.sys_log.info(msg)
        elif level == "debug":
            self.sys_log.debug(msg)
        elif level == "warning":
            self.sys_log.warning(msg)

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
