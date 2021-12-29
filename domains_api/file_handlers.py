import logging
import pickle
import sys
import os
from pathlib import Path


class FileHandlers:
    def __init__(self, path=os.path.abspath(os.path.dirname(__file__))):
        self.log_level = self.set_log_level()
        self.path, self.op_sys = self.file_handling(path)
        self.user_file = os.path.abspath(self.path / "domains.user")
        self.log_file = os.path.abspath(self.path / "domains.log")
        if not os.path.exists(self.log_file) or not os.path.exists(self.user_file):
            try:
                if self.op_sys == "nt":
                    self.make_directories()
                else:
                    self.make_directories()
            except (PermissionError, FileNotFoundError, KeyError) as e:
                print((e))
                print("Run with sudo first time to set permissions")
                sys.exit(1)
        self.sys_log = self.initialize_loggers()

    @staticmethod
    def file_handling(path):
        if os.name == "nt":
            path = Path(os.getenv("LOCALAPPDATA")) / path
            op_sys = "nt"
        else:
            path = Path(path)
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
        # own_log = logging.getLogger(__name__)
        if self.log_level == "debug":
            level = logging.DEBUG
        elif self.log_level == "warning":
            level = logging.WARNING
        else:
            level = logging.INFO
        sys_log.setLevel(level)
        # own_log.setLevel(level)
        fh = logging.FileHandler(self.log_file)
        sh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        sh_formatter = logging.Formatter(
            "[%(name)s][%(levelname)s][%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        sh.setFormatter(sh_formatter)
        sys_log.addHandler(sh)
        sys_log.addHandler(fh)
        # own_log.addHandler(fh)
        sys_log.debug("Loggers initialized")
        return sys_log  # ,  own_log

    def log(self, msg, level="info"):
        if level == "info":
            self.sys_log.info(msg)
            # self.own_log.info(msg)
        elif level == "debug":
            self.sys_log.debug(msg)
            # self.own_log.debug(msg)
        elif level == "warning":
            self.sys_log.warning(msg)
            # self.own_log.warning(msg)

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

        """Delete pickle file (serialized user instance)."""

        if input("Are you sure? (Y/n): ").lower() != "n":
            os.remove(self.user_file)

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
