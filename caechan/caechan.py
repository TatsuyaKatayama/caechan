from caechan.assistant import ListeningOFBashAssistant
from caechan.assistant import ReadingOFBashAssistant
from caechan.assistant import Chatterbox

from caechan.caeplatform import WSLSystem
import caechan.brain as brain
import openai

keyfile = "/home/katayamata/.openai_key"
with open(keyfile, "r") as file:
    openai.api_key = file.read().splitlines()[0]


def run():
    # システム起動
    wsl = WSLSystem("./logs")
    wsl.display_logs()

    # OpenFOAM頭脳
    ofbrain = brain.create_of_on_bash_brain()
    chatboxbrain = brain.create_chatbox_brain(ofbrain.memory)

    # AIを作成
    reading_foamer = ReadingOFBashAssistant(
        ofbrain, wsl.summary_logger, wsl.detail_logger, wsl.cmd_is_running
    )
    listening_foamer = ListeningOFBashAssistant(
        ofbrain, wsl.summary_logger, wsl.detail_logger, wsl.cmd_is_running
    )
    chatbox = Chatterbox(chatboxbrain)

    # モデルを作成
    ai_model = {"v": listening_foamer, "t": reading_foamer, "z": chatbox}

    while True:  # 無限ループ
        x = input("何をしますか？ [v:指示、z:雑談、 t:テキストで指示、q:終了]:")

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
    run()  # 関数を呼び出す
