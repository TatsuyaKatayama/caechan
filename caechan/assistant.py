import subprocess
import multiprocessing
import openai

from caechan.tool import VoiceRecorder
import caechan.brain as brain

keyfile = "/home/katayamata/.openai_key"
with open(keyfile, "r") as file:
    openai.api_key = file.read().splitlines()[0]


class BaseAssistant:
    """Assistantクラスは、入力を受け取り、確認し、実行し、結果を返すという一連の処理を行うクラスです。"""

    def __init__(
        self, brain=None, summary_logger=None, detail_logger=None, cmd_is_running=None
    ):
        self.brain = brain  # AI部
        self.summary_logger = summary_logger  # ロギング用のオブジェクト
        self.detail_logger = detail_logger  # ロギング用のオブジェクト
        self.cmd_is_running = cmd_is_running
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


class BashAssistant(BaseAssistant):
    def exec(self):
        if self.idea is None:
            return

        self.cmd_is_running = True
        p1 = multiprocessing.Process(
            target=self.execute_bash_command,
            args=(self.idea,),
        )
        p1.start()
        p1.join()
        self.cmd_is_running = False

    def execute_bash_command(self, arg):
        summarylogger = self.summary_logger
        detailloger = self.detail_logger
        # 引数がbashで実行可能なコマンドかどうかをチェックする
        try:
            # 引数をbashに渡してプロセスを作成する
            process = subprocess.Popen(
                ["bash", "-c", arg],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # スタートをログに記録する
            if summarylogger is not None:
                summarylogger.info(f"Executed bash command: {arg}")
            # プロセスの出力を逐次読み込む
            for line in iter(process.stdout.readline, ""):
                # 出力をログに記録する
                if detailloger is not None:
                    line = line.replace("\n", "")
                    detailloger.info(f"{line}")
            for line in iter(process.stderr.readline, ""):
                # エラーをログに記録する
                if detailloger is not None:
                    line = line.replace("\n", "")
                    detailloger.error(f"{line}")
            # プロセスの終了コードを取得する
            return_code = process.wait()
            # 終了コードをログに記録する
            if summarylogger is not None:
                summarylogger.info(f"Return code: {return_code}")
        except subprocess.CalledProcessError:
            # エラーが発生した場合はメッセージとエラーコードをログに記録する
            if summarylogger is not None:
                summarylogger.error(f"Invalid bash command: {arg}")
                summarylogger.error(
                    f"Error code: {subprocess.CalledProcessError.returncode}"
                )


class ReadingAssistant(BaseAssistant):
    def set_input(self):
        self.input = input("実行したいコマンドや指示を入力してください。:")


class OpenFOAMAssistant(BaseAssistant):
    def make_idea(self):
        summarylogger = self.summary_logger
        self.idea = self.brain.suggest(self.input)

        if summarylogger is not None:
            summarylogger.info(f"human:{self.input}, ai: {self.idea}")

    def confirm(self):
        """解釈があっているか確認する。"""
        x = input(
            f"""コマンドを実行しますか？
        あなたの指示：{self.input}
        caechanの解釈：{self.idea}
        [y:実行する、n:やめる]:"""
        )

        # yesでない限りアイデアを消す
        if not x == "y":
            self.idea = None


class ListeningAssistant(ReadingAssistant):
    def set_input(self):
        # 録音データを取得
        recorder = VoiceRecorder()
        recorder.record()

        # 録音データをWAVファイルに保存
        audio_file_path = "./temp_your_voice.wav"
        recorder.save_wav_file(audio_file_path)
        self.input = self.wisper(audio_file_path)

    def wisper(self, audio_file_path: str):
        with open(audio_file_path, "rb") as f:
            transcribe = openai.Audio.transcribe("whisper-1", f)
        transcript = transcribe["text"]
        return transcript


class Chatterbox(BaseAssistant):
    def set_input(self):
        self.input = input("雑談：")

    def make_idea(self):
        self.idea = self.brain.suggest(self.input)

    def confirm(self):
        print(self.idea)
        self.idea = None


class ListeningOFBashAssistant(ListeningAssistant, BashAssistant, OpenFOAMAssistant):
    def __init__(
        self, brain=None, summary_logger=None, detail_logger=None, cmd_is_running=None
    ):
        super().__init__(brain, summary_logger, detail_logger, cmd_is_running)


class ReadingOFBashAssistant(ReadingAssistant, BashAssistant, OpenFOAMAssistant):
    def __init__(
        self, brain=None, summary_logger=None, detail_logger=None, cmd_is_running=None
    ):
        super().__init__(brain, summary_logger, detail_logger, cmd_is_running)


if __name__ == "__main__":  # このファイルが直接実行された場合
    from caechan.caeplatform import WSLSystem

    wsl = WSLSystem("./logs")
    wsl.display_logs()

    basher = BashAssistant(
        None, wsl.summary_logger, wsl.detail_logger, wsl.cmd_is_running
    )
    basher.idea = "for i in {1..5}; do echo $i; sleep 1; done"
    basher.exec()

    ofbrain = brain.create_of_on_bash_brain()
    ofoamer = ReadingOFBashAssistant(
        ofbrain, wsl.summary_logger, wsl.detail_logger, wsl.cmd_is_running
    )
    ofoamer.input = "cavityケースをコピーして"
    ofoamer.make_idea()

    ofoamer.input = "ブロックメッシュを実行"
    ofoamer.make_idea()
    ofoamer.confirm()

    chatbrain = brain.create_chatbox()
    chatter = Chatterbox(chatbrain)
    chatter.input = "CAEって何の略語ですか？"
    chatter.make_idea()
    chatter.confirm()
