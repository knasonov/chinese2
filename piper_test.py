from piper import PiperVoice
voice = PiperVoice.load("voices/zh_CN-huayan-medium.onnx")
wav = voice.synthesize("今天天气很好，让我们开始学习吧！")
open("sample.wav", "wb").write(wav)