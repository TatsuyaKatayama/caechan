import os
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import multiprocessing


class BasicSystem:
    def __init__(self, log_dir, log_max_size=1000, log_backup_count=3) -> None:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.log_dir = log_dir
        # ログファイルの最大サイズ（バイト）
        self.log_max_size = log_max_size
        # ログファイルのバックアップ数
        self.log_backup_count = log_backup_count

        # ロガーを作成する
        summary_log = f"{self.log_dir}/log.summary"
        self.summary_logger = create_logger(
            summary_log, "summary", self.log_max_size, self.log_backup_count
        )
        # 詳細ロガーを作成
        datail_log = f"{self.log_dir}/log.detail"
        self.detail_logger = create_logger(
            datail_log,
            "detail",
            self.log_max_size,
            self.log_backup_count,
            format="%(message)s",
        )
        # コマンド実行中かどうかを判断するフラグ
        self.cmd_is_running = False

    def display_logs(self):
        pass


class WSLSystem(BasicSystem):
    def display_logs(self):
        p2 = multiprocessing.Process(
            target=tail_log_file_in_gnome,
            args=(
                self.summary_logger.handlers[0].baseFilename,
                '"Breath Darker"',
                "Summary",
                '"100x10+0+0"',
            ),
        )
        p3 = multiprocessing.Process(
            target=tail_log_file_in_gnome,
            args=(
                self.detail_logger.handlers[0].baseFilename,
                '"Breath"',
                "Detail",
                '"80x20+0+0"',
            ),
        )
        p2.start()
        p3.start()
        p2.join()
        p3.join()


def create_logger(
    log_file,
    name_logger,
    max_size,
    backup_count,
    format="%(asctime)s - %(levelname)s - %(message)s",
):
    # ログフォーマットを設定する
    # log_format = "%(asctime)s - %(levelname)s - %(message)s"
    # logging.basicConfig(format=log_format)

    # ログレベルを設定する
    logger = logging.getLogger(name_logger)
    logger.setLevel(logging.INFO)

    # ログローテーションハンドラーを作成する
    handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
    handler.setLevel(logging.INFO)
    # ハンドラーにフォーマットを追加。
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    # ハンドラーをロガーに追加する
    logger.addHandler(handler)

    return logger


def tail_log_file_in_gnome(
    log_file: str, profile="Breath Darker", title="log", positon="80x20+0+0"
):
    # logファイルが存在するかどうかをチェックする
    try:
        # ターミナルのコマンドを作成する
        command = f"gnome-terminal --profile={profile} --geometry={positon} --title={title} -- tail -F {log_file}"
        # コマンドを実行してサブプロセスを作成する
        subprocess.Popen(["bash", "-c", command])
    except subprocess.CalledProcessError:
        # 何かエラーがでたとき
        print("Error at tail_log_file_in_gnome.")


if __name__ == "__main__":  # このファイルが直接実行された場合
    wsl = WSLSystem("./logs")
    wsl.display_logs()
