from peye import *

'''Юнит-тесты на полшишки'''
if __name__ == "__main__":

    # generator = KeyGenerator(100000, 10)
    # generator.gen_keys()
    # print(generator.get_open_key())
    # print(generator.get_close_key())

    # generator.gen_keys()

    # print('\n\n\n')
    # print(generator.get_open_key())
    # print(generator.get_close_key())


    #Сгенерировать криптограммы
    portion = PortionVoiting(9, 5, 2, 10)
    portion.start_portion()
    open_key = portion.get_open_key()

    encoder = VoiceEncoder(open_key)

    portion.append_enc_voice(encoder.create_voice(100))
    portion.append_enc_voice(encoder.create_voice(10000))

    portion.count_voices()
    portion.dec_res()
    # dec_res = portion.dec_res()
    # print(f"Расшированные голоса:{portion.dec_res()}")

    portion2 = PortionVoiting(9, 5, 2, 10)
    portion2.start_portion()
    open_key = portion2.get_open_key()
    encoder = VoiceEncoder(open_key)

    portion2.append_enc_voice(encoder.create_voice(100))
    portion2.append_enc_voice(encoder.create_voice(1000))
    portion2.count_voices()
    portion2.dec_res()
    print(portion.get_dec_res()+portion2.get_dec_res(), "\n")
    print(f"Расшированные голоса:{parse_result(portion.get_dec_res()+portion2.get_dec_res())}")

    # print(open_key['y'])
    
    # bit_length = 10  # заданное количество бит
    # found = False
    # while not found:
    #     p = generate_random_prime(bit_length)
    #     q = generate_random_prime(bit_length)
    #     n = p * q
    #     phi_n = (p - 1) * (q - 1)
    #     if gcd(n, (p - 1)*(q - 1)) == 1:
    #         found = True

    # print(f"Найдены простые числа p и q: p={p}, q={q}")
    # print(f"p*q = {p*q}, (p-1)(q-1) = {phi_n}")

    # # n = 10  # Задаем значение n
    # # Zn_ring = get_Zn_ring(n)
    # # print(f"Кольцо Z{str(n)}* состоит из следующих элементов: {Zn_ring}")
    # n = p*q
    # Zn_ring = get_Zn_ring(n)
    # y = get_random_element(Zn_ring)
    # print(f"Сформирован открытый ключ: n={n} y = {y}")

    # lyambda = int(get_Lambda(p,q))
    # x = int(find_x(y, lyambda, n))
    # print(f"Сформирован закрытый ключ: lambda={lyambda} x = {x}")


    # m = int(input("Введите тестовое число для шифрования>\n"))
    # u = get_random_element(Zn_ring)
    # c = (y**m * (u**n))%n**2
    # print(f"Зашифрованное сообщение: {c}")


    # '''Дешифрование'''
    # d = (c**lyambda)%n**2
    # d = d // n
    # d = (d * x) % n
    # print(f"Дешифрованное сообщение: {d}")

    # PayeCryptoOps = PayePrimitiveOperations()