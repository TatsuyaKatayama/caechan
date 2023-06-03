import soundcard as sc
import numpy as np
import wave
import fire
import time


class VoiceRecorder:
    def __init__(self) -> None:
        # 録音のパラメータ
        self.sample_rate = 48000
        self.block_duration = 100
        self.silence_duration = 2.0
        self.silence_threshold = 0.01
        self.max_time = 6.0

        # 録音データを保存するリスト
        self.recorded_data = []

        # 録音デバイスの取得
        self.default_mic = sc.default_microphone()

    def record(self):
        # 沈黙の長さをブロック数に変換
        silence_blocks = int(self.silence_duration * 1000 / self.block_duration)

        # 録音データを保存するリスト
        recorded_data = []

        # 録音ループ用変数
        silent_blocks = 0

        # 開始時間
        start_time = time.time()

        # マイクロフォンで録音を開始
        with self.default_mic.recorder(samplerate=self.sample_rate) as mic:
            print(f"録音を開始しました。沈黙が{self.silence_duration}秒続くと録音が終了します。")
            while silent_blocks < silence_blocks:
                # 録音データを取得
                data = mic.record(
                    numframes=int(self.sample_rate * self.block_duration / 1000)
                )
                recorded_data.append(data)

                # 音量を計算
                volume = np.linalg.norm(data)

                # 音量が閾値より低い場合、沈黙と判断
                if volume < self.silence_threshold:
                    silent_blocks += 1
                elif time.time() - start_time > self.max_time:
                    break
                else:
                    silent_blocks = 0

            print("録音が終了しました。")

        # 録音データをnumpy配列に変換
        self.recorded_data = np.concatenate(recorded_data, axis=0)

    def save_wav_file(self, file_path):
        # 録音データを16ビット整数に変換
        data = (self.recorded_data * np.iinfo(np.int16).max).astype(np.int16)

        # WAVファイルを開いて保存
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(data.tobytes())


def main(outputfile: str):
    # 録音データを取得
    recorder = VoiceRecorder()
    recorder.record()

    # 録音データをWAVファイルに保存
    file_path = "{}.wav".format(outputfile)
    recorder.save_wav_file(file_path)


if __name__ == "__main__":
    fire.Fire(main)
