import openai
import os

from langchain import PromptTemplate
from langchain import FewShotPromptTemplate
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory


keyfile = "/home/katayamata/.openai_key"
with open(keyfile, "r") as file:
    openai.api_key = file.read().splitlines()[0]


class Brain:
    def __init__(self, llm, prompt, memory=None) -> None:
        if memory is None:
            memory = ConversationBufferMemory()
        self.memory = memory
        self.prompt = prompt
        self.llm = llm

    def suggest(self, input):
        prompt_text = self.prompt.format(input=input)
        return self.llm(prompt_text)


def create_of_prompt():
    tut = os.environ.get("FOAM_TUTORIALS")
    current = os.getcwd()
    if tut is None:
        tut = "/usr/lib/openfoam/openfoam2212/tutorials"

    prefix = f"""ubuntuのbash環境でOpenFOAMを実行したい。適切にオプションも考慮したコマンドを提案しなさい。
    OpenFOAMのTutorialディレクトリは{tut}、コマンドを実行する現在のディレクトリは{current}です。
    {current}/caseを計算用のケースディレクトリとし、ディレクトリの位置関係に注意し、コマンドをワンライナーで提案すること。
    """
    examples = [
        {
            "human": "キャビティチュートリアルを現在のディレクトリにコピーして",
            "ai": f"cp -r {tut}/incompressible/icoFoam/cavity/cavity {current}/case",
        },
        {
            "human": "cavity tutorialをコピーして",
            "ai": f"cp -r {tut}/incompressible/icoFoam/cavity/cavity {current}/case",
        },
        {
            "human": "motorBikeのチュートリアルをコピーして",
            "ai": f"cp -r {tut}/incompressible/simpleFoam/motorBike {current}/case",
        },
        {
            "human": "インターアイソフォームのダムブレイクチュートリアルをコピーして",
            "ai": f"cp -r {tut}/multiphase/interIsoFoam/damBreak {current}/case",
        },
        {"human": "コピーしたdamBreak tutorialでAllrunを実行して", "ai": f"{current}/case/Allrun"},
        {"human": "コピーしたチュートリアルでAllrunを実行して", "ai": f"{current}/case/Allrun"},
        {"human": "次にAllrunを実行して", "ai": f"{current}/case/Allrun"},
        {"human": "blockMesh", "ai": f"blockMesh -case {current}/case"},
        {"human": "ブロックメッシュ", "ai": f"blockMesh -case {current}/case"},
        {"human": "メッシュを切って", "ai": f"blockMesh -case {current}/case"},
        {"human": "アイコフォーム", "ai": f"icoFoam -case {current}/case"},
        {"human": "イコフォーム", "ai": f"icoFoam -case {current}/case"},
        {"human": "icoFoam", "ai": f"icoFoam -case {current}/case"},
        {"human": "シンプルフォーム", "ai": f"simpleFoam -case {current}/case"},
        {"human": "チェックメッシュ", "ai": f"checkMesh -case {current}/case"},
        {
            "human": "スナッピーヘックスメッシュ",
            "ai": f"snappyHexMesh -overwrite -case {current}/case",
        },
        {
            "human": "スナッピーヘキサメッシュ",
            "ai": f"snappyHexMesh -overwrite -case {current}/case",
        },
        {
            "human": "snappyメッシュ",
            "ai": f"snappyHexMesh -overwrite -case {current}/case",
        },
        {
            "human": "snappyHexMesh",
            "ai": f"snappyHexMesh -overwrite -case {current}/case",
        },
        {"human": "解析ケースの初期化", "ai": f"foamCleanTutorials {current}/case"},
    ]

    example_formatter_template = """
    human: {human}
    ai: {ai}\n
    """
    example_prompt = PromptTemplate(
        template=example_formatter_template, input_variables=["human", "ai"]
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix="human: {input}\nai:",
        input_variables=["input"],
        example_separator="\n\n",
    )
    return few_shot_prompt


def create_of_on_bash_brain(memory=None):
    of_prompt = create_of_prompt()
    llm = OpenAI(model_name="text-davinci-003")
    of_brain = Brain(llm, of_prompt, memory)
    return of_brain


def create_chatbox_brain(memory=None):
    template = """端的に回答し、話題を広げてください。話題はOpenFOAMや科学計算についてが好ましいです。
    human:{input}
    ai:\n
    """
    prompt = PromptTemplate(template=template, input_variables=["input"])
    llm = OpenAI(model_name="text-davinci-003", temperature=0.9)
    brain = Brain(llm, prompt, memory)
    return brain
