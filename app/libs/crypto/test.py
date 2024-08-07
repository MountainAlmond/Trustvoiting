from peye import *

"""Юнит-тесты"""
if __name__ == "__main__":

    # Сгенерировать криптограммы
    portion = PortionVoiting(9, 5, 2, 10)
    portion.start_portion()
    open_key = portion.get_open_key()

    encoder = VoiceEncoder(open_key)

    portion.append_enc_voice(encoder.create_voice(10))
    portion.append_enc_voice(encoder.create_voice(1000))

    portion.count_voices()
    portion.dec_res()

    portion2 = PortionVoiting(9, 5, 2, 10)
    portion2.start_portion()
    open_key = portion2.get_open_key()
    encoder = VoiceEncoder(open_key)

    portion2.append_enc_voice(encoder.create_voice(1000))
    portion2.append_enc_voice(encoder.create_voice(100))
    portion2.count_voices()
    portion2.dec_res()
    print(portion.get_dec_res() + portion2.get_dec_res(), "\n")
    print(
        f"Расшированные голоса:{parse_result(portion.get_dec_res()+portion2.get_dec_res())}"
    )
