import logging
import os
import shutil
import pickle
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from domains_api.constants import HOME_PATH_DIR_NAME


class FileHandlers:
    def __init__(self, log_level: str = "info"):
        self.log_level = self.set_log_level(log_level)
        self.path = Path(os.path.abspath(os.path.dirname(__file__)))
        self.user_file = self.path / "domains.user"
        self.home_path = Path(os.getenv("HOME"))
        self.log_path = self.home_path / HOME_PATH_DIR_NAME

        if not os.path.exists(self.user_file):
            self._migrate_old_versions()
        if not os.path.exists(self.log_path):
            self.make_directories()
        self.sys_log = self.initialize_loggers()

    def make_directories(self):
        os.makedirs(self.log_path, exist_ok=True)

    def _migrate_old_versions(self):
        self.make_directories()
        os.system(f'mv {self.home_path / ".domains" / "domains.user"} {self.path}')
        os.system(f'mv {self.home_path / ".domains" / "domains.log"} {self.log_path}')
        shutil.rmtree(self.home_path / '.domains')

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
            self.log_path / 'domains.log',
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
        with open(self.user_file, "wb") as pickle_file:
            pickle.dump(user, pickle_file)
        self.log("User saved.", "debug")

    @staticmethod
    def load_user(user_file):
        with open(user_file, "rb") as pickle_file:
            return pickle.load(pickle_file)

    def delete_user(self):
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


if __name__ == "__main__":
    fhs = FileHandlers()
    fhs.log("Testing", "info")
