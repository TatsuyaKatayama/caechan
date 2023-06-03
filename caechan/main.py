import logging
from logging.handlers import RotatingFileHandler
import subprocess
import openai
import multiprocessing

keyfile = "/home/katayamata/.openai_key"
with open(keyfile, "r") as file:
    openai.api_key = file.read().splitlines()[0]


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


class EnvState:
    """システムコマンドの実行状況を記録する"""

    def __init__(self):
        self.isRunnig = False


class FoamerAI:
    """FoamerAIクラスは、入力を受け取り、確認し、実行し、結果を返すという一連の処理を行うクラスです。"""

    def __init__(self, summary_logger, detail_logger, env_state=None):
        self.summary_logger = summary_logger  # ロギング用のオブジェクト
        self.detail_logger = detail_logger  # ロギング用のオブジェクト
        self.env_state = env_state
        self.input = ""
        self.idea = ""

    def set_input(self):
        """入力をセットする。"""
        pass

    def interpret(self):
        """入力を解釈して回答する。"""
        pass

    def confirm(self):
        """解釈があっているか確認する。"""
        pass

    def exec(self):
        """実際にリアクションや指示を実行するメソッド"""
        pass

    def get_respon(self):
        """レスポンスをもらう"""
        pass


class Reading_Runner(FoamerAI):
    def __init__(self):
        super().__init__()  # 親クラスのコンストラクタを呼び出す

    def set_input(self):
        self.input = input("実行したいコマンドや指示を入力してください")

    def make_idea(self):
        # TODO llmモデルで問い合わせ

        return super().interpret()


class Listening_Runner(Reading_Runner):
    def __init__(self):
        super().__init__()  # 親クラスのコンストラクタを呼び出す

    def set_input(self):
        print("listening")


class Chatterbox(FoamerAI):
    def __init__(self):
        super().__init__()  # 親クラスのコンストラクタを呼び出す

    def set_input(self):
        print("chat")


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


def main():
    # ログファイルの最大サイズ（バイト）
    max_size = 1000
    # ログファイルのバックアップ数
    backup_count = 3

    # ロガーを作成する
    summary_log = "./exec_command/log.summary"
    summary_logger = create_logger(summary_log, "summary", max_size, backup_count)
    # 詳細ロガーを作成
    datail_log = "./exec_command/log.detail"
    detail_logger = create_logger(
        datail_log, "detail", max_size, backup_count, format="%(message)s"
    )

    # TODO:EnvStateを起動
    env_state = EnvState()

    # モデルを作成
    ai_model = {
        "v": Listening_Runner(summary_logger, detail_logger, env_state),
        "t": Reading_Runner(summary_logger, detail_logger, env_state),
        "z": Chatterbox(summary_logger, detail_logger, env_state),
    }

    while True:  # 無限ループ
        x = input("何をしますか？ [v:指示、z:雑談、 t:テキストで指示、q:終了]")

        if x not in {"v", "z", "t", "q"}:  # xが"a"でも"b"でもない場合
            print("v,z,t,qのいずれかを入力してください。")
            continue
        elif x == "q":  # 入力値が"q"の場合
            print("終了します。")  # 終了メッセージを出力
            break  # ループを抜ける

        ai_model[x].set_input()
        ai_model[x].make_idea()
        ai_model[x].confirm()
        ai_model[x].exec()
        ai_model[x].get_respon()


if __name__ == "__main__":  # このファイルが直接実行された場合
    main()  # 関数を呼び出す
