import os
import csv
import torch.distributed as dist
import pickle
import config
from phe import paillier
import random

NUM_TRIPLES = 10  # Количество троек для генерации


def init_distributed():
    """Инициализация torch.distributed"""
    rank = int(os.environ.get('RANK', 0))
    world_size = int(os.environ.get('WORLD_SIZE', 2))
    master_addr = os.environ.get('MASTER_ADDR', 'localhost')
    master_port = os.environ.get('MASTER_PORT', '29500')

    os.environ['MASTER_ADDR'] = master_addr
    os.environ['MASTER_PORT'] = master_port

    dist.init_process_group(
        backend='gloo',
        rank=rank,
        world_size=world_size
    )

    return rank, world_size


def send_object(obj, dst):
    """Отправка объекта через torch.distributed"""
    data = pickle.dumps(obj)
    size_tensor = torch.tensor([len(data)], dtype=torch.long)
    dist.send(size_tensor, dst=dst)

    data_tensor = torch.ByteTensor(list(data))
    dist.send(data_tensor, dst=dst)


def recv_object(src):
    """Получение объекта через torch.distributed"""
    size_tensor = torch.tensor([0], dtype=torch.long)
    dist.recv(size_tensor, src=src)
    size = size_tensor.item()

    data_tensor = torch.ByteTensor([0] * size)
    dist.recv(data_tensor, src=src)

    data = bytes(data_tensor.tolist())
    return pickle.loads(data)


def generate_beaver_triple_party1(public_key, private_key):
    """
    Party 1: Генерация своей части тройки Бивера
    Возвращает: (a_1, b_1, c_1)
    """
    # Генерируем случайные a_1 и b_1
    a_1 = random.randint(0, config.MPC_MODULO - 1)
    b_1 = random.randint(0, config.MPC_MODULO - 1)

    # Вычисляем локальную часть произведения
    c_1_local = (a_1 * b_1) % config.MPC_MODULO

    # Шифруем a_1 и b_1
    enc_a_1 = public_key.encrypt(a_1)
    enc_b_1 = public_key.encrypt(b_1)

    # Отправляем зашифрованные значения Party 2
    send_object((enc_a_1, enc_b_1), dst=1)

    # Получаем зашифрованное cross_term от Party 2
    enc_cross_term = recv_object(src=1)

    # Расшифровываем cross_term
    cross_term = private_key.decrypt(enc_cross_term) % config.MPC_MODULO

    # Вычисляем финальную долю c_1
    c_1 = (c_1_local + cross_term) % config.MPC_MODULO

    return (a_1, b_1, c_1)


def generate_beaver_triple_party2(public_key):
    """
    Party 2: Генерация своей части тройки Бивера
    Возвращает: (a_2, b_2, c_2)
    """
    # Получаем зашифрованные значения от Party 1
    enc_a_1, enc_b_1 = recv_object(src=0)

    # Генерируем случайные a_2 и b_2
    a_2 = random.randint(0, config.MPC_MODULO - 1)
    b_2 = random.randint(0, config.MPC_MODULO - 1)

    # Вычисляем локальную часть произведения
    c_2_local = (a_2 * b_2) % config.MPC_MODULO

    # Вычисляем перекрестные члены с использованием гомоморфных свойств
    # E(a_1 * b_2) = E(a_1)^b_2
    enc_a1_b2 = enc_a_1 * b_2

    # E(a_2 * b_1) = E(b_1)^a_2
    enc_a2_b1 = enc_b_1 * a_2

    # E(a_1*b_2 + a_2*b_1) = E(a_1*b_2) * E(a_2*b_1)
    enc_cross_sum = enc_a1_b2 + enc_a2_b1

    # Генерируем случайную маску
    r_2 = random.randint(0, config.MPC_MODULO - 1)

    # E(cross_term - r_2) = E(cross_sum) * E(-r_2)
    enc_cross_term = enc_cross_sum - r_2

    # Отправляем зашифрованное значение Party 1
    send_object(enc_cross_term, dst=0)

    # Вычисляем финальную долю c_2
    c_2 = (c_2_local + r_2) % config.MPC_MODULO

    return (a_2, b_2, c_2)


def party1_main():
    """Основная функция для Party 1"""
    print("Party 1: Начало генерации троек Бивера")

    # Генерируем ключи Paillier
    print(f"Party 1: Генерация ключей Paillier (размер: {config.PAILLIER_KEY_SIZE})")
    public_key, private_key = paillier.generate_paillier_keypair(n_length=config.PAILLIER_KEY_SIZE)

    # Отправляем публичный ключ Party 2
    print("Party 1: Отправка публичного ключа Party 2")
    send_object(public_key, dst=1)

    # Генерируем тройки
    triples = []
    for i in range(NUM_TRIPLES):
        print(f"Party 1: Генерация тройки {i + 1}/{NUM_TRIPLES}")
        triple = generate_beaver_triple_party1(public_key, private_key)
        triples.append(triple)

    # Сохраняем результаты в CSV
    os.makedirs('/app/output', exist_ok=True)
    output_path = '/app/output/p1.csv'

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['a', 'b', 'c'])
        for triple in triples:
            writer.writerow(triple)

    print(f"Party 1: Тройки сохранены в {output_path}")
    print("Party 1: Завершено")


def party2_main():
    """Основная функция для Party 2"""
    print("Party 2: Начало генерации троек Бивера")

    # Получаем публичный ключ от Party 1
    print("Party 2: Получение публичного ключа от Party 1")
    public_key = recv_object(src=0)

    # Генерируем тройки
    triples = []
    for i in range(NUM_TRIPLES):
        print(f"Party 2: Генерация тройки {i + 1}/{NUM_TRIPLES}")
        triple = generate_beaver_triple_party2(public_key)
        triples.append(triple)

    # Сохраняем результаты в CSV
    os.makedirs('/app/output', exist_ok=True)
    output_path = '/app/output/p2.csv'

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['a', 'b', 'c'])
        for triple in triples:
            writer.writerow(triple)

    print(f"Party 2: Тройки сохранены в {output_path}")
    print("Party 2: Завершено")


if __name__ == '__main__':
    import torch

    # Инициализируем распределенную среду
    rank, world_size = init_distributed()

    print(f"Запущена сторона с rank={rank}, world_size={world_size}")

    try:
        if rank == 0:
            party1_main()
        elif rank == 1:
            party2_main()
        else:
            raise ValueError(f"Неожиданный rank: {rank}")
    finally:
        dist.destroy_process_group()

    print(f"Сторона {rank} завершила работу")
