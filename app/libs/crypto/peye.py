import random
from collections import namedtuple

VOTE_UPPER_BOUND=9
VOTE_LOWER_BOUND=0

"""Класс, объединяющий в себе все примитивные операции для реализации схемы Пейэ"""


class PayePrimitiveOperations:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PayePrimitiveOperations, cls).__new__(cls)
            return cls._instance
        else:
            return cls._instance

    """Алгоритм Евклида (НОД)"""

    @staticmethod
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    """Проверка числа на простоту с помощью теста Миллера-Рабина"""

    @staticmethod
    def is_prime(num, k=25):
        if num < 2:
            return False
        if num == 2 or num == 3:
            return True
        if num % 2 == 0:
            return False

        def check(a, s, d, n):
            x = pow(a, d, n)
            if x == 1:
                return True
            for i in range(s - 1):
                if x == n - 1:
                    return True
                x = pow(x, 2, n)
            return x == n - 1

        s = 0
        d = num - 1
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(k):
            a = random.randint(2, num - 1)
            if not check(a, s, d, num):
                return False
        return True

    """Генерация случайного рандомного числа заданной длины в битах с проверкой на простоту"""

    @staticmethod
    def generate_random_prime(bit_length):
        while True:
            num = random.getrandbits(bit_length)
            if PayePrimitiveOperations.is_prime(num):
                return num

    """Примитивный алгоритм поиска кольца вычетов взаимно простых с n (от 1 до n-1)"""

    @staticmethod
    def get_Zn_ring(n):
        Zn_ring = [i for i in range(1, n) if PayePrimitiveOperations.gcd(i, n) == 1]
        return Zn_ring

    """Выбор случайного элемента из кольца вычетов"""

    @staticmethod
    def get_random_element(Zn_ring):
        return random.choice(Zn_ring)

    """Получение лямбды (часть закрытого ключа) по известным p и q"""

    @staticmethod
    def get_lyambda(p, q):
        return int((p - 1) * (q - 1) / PayePrimitiveOperations.gcd(p - 1, q - 1))

    """Применение расширенного алгоритма Евклида для поиска обратного элемента в кольце вычетов по модулю n"""

    @staticmethod
    def extended_euclidean_algorithm(a, b):
        if b == 0:
            return a, 1, 0
        else:
            d, x, y = PayePrimitiveOperations.extended_euclidean_algorithm(b, a % b)
            return d, y, x - (a // b) * y

    @staticmethod
    def find_inverse_element(a, n):
        d, x, y = PayePrimitiveOperations.extended_euclidean_algorithm(a, n)
        if d == 1:
            return x % n
        else:
            return None

    """Поиск ближайшего целого"""

    @staticmethod
    def find_s(u, n):
        s = (u - 1) // n
        return s

    """Поиск x (часть закрытого ключа)"""

    @staticmethod
    def find_x(y, lyambda, n):
        s = PayePrimitiveOperations.find_s(y**lyambda % n**2, n)
        x = PayePrimitiveOperations.find_inverse_element(s, n)
        return int(x)


"""Класс, отвечающий за генерацию ключей для одной сессии шифрования"""


class KeyGenerator:
    def __init__(self, p_down_border_n, p_bit_lenght):
        self._PayePrimitiveOps = PayePrimitiveOperations()
        self._down_border_n = p_down_border_n
        self._bit_lenght = p_bit_lenght
        """Части ключей"""

        """Открытый ключ"""
        self._n = 0
        self._y = 0

        """Закрытый ключ (остается на сервере)"""
        self._lyambda = 0
        self._x = 0

    """Метод генерации ключей"""

    def gen_keys(self):
        find_x = False
        while not find_x:
            found_n = False
            while not found_n:
                p = self._PayePrimitiveOps.generate_random_prime(self._bit_lenght)
                q = self._PayePrimitiveOps.generate_random_prime(self._bit_lenght)
                n = p * q
                if (
                    n > self._down_border_n
                    and self._PayePrimitiveOps.gcd(n, (p - 1) * (q - 1)) == 1
                ):
                    found_n = True
                    self._n = n

            print(self._n)
            z_ring = self._PayePrimitiveOps.get_Zn_ring(self._n)
            self._y = self._PayePrimitiveOps.get_random_element(z_ring)
            print(self._y)

            self._lyambda = self._PayePrimitiveOps.get_lyambda(p, q)
            self._x = self._PayePrimitiveOps.find_x(self._y, self._lyambda, self._n)
            if self._x != None:
                find_x = True

    """Геттер для экспорта открытого ключа (n, y)"""

    def get_open_key(self):
        open_key_tuple = namedtuple("open_key", ["n", "y"])
        return open_key_tuple(n=self._n, y=self._y)

    """Геттер для экспорта закрытого ключа (lyambda, x)"""

    def get_close_key(self):
        close_key_tuple = namedtuple("closed_key", ["lyambda", "x"])
        return close_key_tuple(lyambda=self._lyambda, x=self._x)


"""Класс, который отвечает за порцию голосования (подсчет голосов 9 избирателей)
    К объекту данного класса должны быть прикреплены:
        - закрытый ключ, который был сгенерирован для данной порции
    
    Объект порции голосования "одноразовый" - принимает список из 9 (или меньше) шифро-голосов, расшифровывает результат
    и отдает его в открытом виде

"""


class PortionVoiting:
    def __init__(self, Nv, Nc, max_voices_elector, bit_lenght):
        self._down_border_n = sum(
            [10**i for i in range(Nc, max_voices_elector - 1, -1)]
        )
        self._generator = KeyGenerator(self._down_border_n, bit_lenght)
        self._Nv = Nv
        self._Nc = Nc
        self._b = Nv + 1
        self._enc_voices = []
        self._enc_res = 1
        self._dec_res = 0

    def start_portion(self):
        self._generator.gen_keys()
        print(self._generator.get_open_key())

    def get_open_key(self):
        open_key = self._generator.get_open_key()
        return open_key

    def get_closed_key(self):
        closed_key = self._generator.get_close_key()
        return closed_key

    def append_enc_voice(self, enc_voice):
        self._enc_voices.append(enc_voice)

    def set_enc_voices(self, enc_voices):
        self._enc_voices = enc_voices

    def count_voices(self):
        if len(self._enc_voices) > VOTE_UPPER_BOUND or len(self._enc_voices) <= VOTE_LOWER_BOUND:
            raise ValueError(
                "Некорректный размер порции голосования! Размер порции должен быть не более 9 голосов и строго не меньше 0."
            )
        for voice in self._enc_voices:
            self._enc_res *= voice

    def dec_res(self):
        closed_key = self.get_closed_key()
        open_key = self.get_open_key()
        self._dec_res = (self._enc_res ** closed_key[0]) % open_key[0] ** 2
        self._dec_res = self._dec_res // open_key[0]
        self._dec_res = (self._dec_res * closed_key[1]) % open_key[0]

    def get_dec_res(self):
        return self._dec_res


"""Класс, который отвечает за все голосование (подсчет по сессиям)

    Объект отвечает за все голосование.
        - Генерирует сессии для порций голосования:
            -пока поступают голоса
            -пока не закончилось голосование
        - Может отдавать промежуточный результат

"""

"""В классе голосования можно придумать следующую реализацию
        -Нужно периодически чекать, заполнилась ли порция
        -Пока есть необработанные голоса, создавать новые порции"""


class Voiting:
    pass


"""Тестовые вспомогатеьные функции генерации шифротекстов"""


class VoiceEncoder:
    def __init__(self, open_key):
        self._open_key = open_key

    def get_u(self, n):
        Zn_ring = PayePrimitiveOperations.get_Zn_ring(self._open_key[0])
        return random.choice(Zn_ring)

    def create_voice(self, m):
        u = self.get_u(self._open_key[0])
        enc_voice = (self._open_key[1] ** m * u ** self._open_key[0]) % self._open_key[
            0
        ] ** 2
        return enc_voice


"""Разбор результата голосоания"""


def parse_result(n):
    digits_count = {}
    number_str = str(n)
    for i in range(len(number_str)):
        place = 10 ** (len(number_str) - i - 1)
        digit = int(number_str[i])
        digits_count[place] = digit
    return digits_count
