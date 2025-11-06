# Генерация троек Бивера с использованием Paillier

Реализация алгоритма генерации мультипликативных троек (тройки Бивера) для двух сторон без участия третьей доверенной стороны (TTP), используя частично гомоморфное шифрование Paillier.

## Протокол генерации троек

Протокол использует частично гомоморфное шифрование Paillier для безопасной генерации троек (a, b, c), где c = a * b mod MPC_MODULO.
Шаги протокола:

1. Party 1 генерирует пару ключей Paillier и отправляет публичный ключ Party 2 
2. Party 1 генерирует случайные значения a₁, b₁ и вычисляет c₁_local = a₁ * b₁ 
3. Party 1 шифрует a₁ и b₁ и отправляет зашифрованные значения Party 2 
4. Party 2 генерирует случайные значения a₂, b₂ и вычисляет c₂_local = a₂ * b₂ 
5. Party 2 использует гомоморфные свойства для вычисления:

    ```
    E(a₁ * b₂) = E(a₁)^b₂
    E(a₂ * b₁) = E(b₁)^a₂
    E(a₁b₂ + a₂b₁) = E(a₁b₂) + E(a₂b₁)
    ```

6. Party 2 генерирует случайную маску r₂ и вычисляет E(cross_term - r₂)
7. Party 2 отправляет зашифрованное значение Party 1 и устанавливает c₂ = c₂_local + r₂
8. Party 1 расшифровывает cross_term и вычисляет c₁ = c₁_local + cross_term

Результат:

- Party 1 получает долю: (a₁, b₁, c₁)
- Party 2 получает долю: (a₂, b₂, c₂)
- Выполняется свойство: c₁ + c₂ ≡ (a₁ + a₂) * (b₁ + b₂) (mod MPC_MODULO)

## Zapusk

...

## Example

```bash
 ✔ homework-party1               Built                                                                                          0.0s 
 ✔ homework-party2               Built                                                                                          0.0s 
 ✔ Network homework_mpc_network  Created                                                                                        0.7s 
 ✔ Container party1              Created                                                                                        0.8s 
 ✔ Container party2              Created                                                                                        0.1s 
Attaching to party1, party2
party2  | [Gloo] Rank 1 is connected to 1 peer ranks. Expected number of connected peer ranks is : 1
party2  | Запущена сторона с rank=1, world_size=2
party1  | [Gloo] Rank 0 is connected to 1 peer ranks. Expected number of connected peer ranks is : 1
party1  | Запущена сторона с rank=0, world_size=2
party1  | Party 1: Начало генерации троек Бивера
party1  | Party 1: Генерация ключей Paillier (размер: 2048)
party2  | Party 2: Начало генерации троек Бивера
party2  | Party 2: Получение публичного ключа от Party 1
party1  | Party 1: Отправка публичного ключа Party 2
party1  | Party 1: Генерация тройки 1/10
party2  | Party 2: Генерация тройки 1/10
party2  | Party 2: Генерация тройки 2/10
party1  | Party 1: Генерация тройки 2/10
party2  | Party 2: Генерация тройки 3/10
party1  | Party 1: Генерация тройки 3/10
party2  | Party 2: Генерация тройки 4/10
party1  | Party 1: Генерация тройки 4/10
party2  | Party 2: Генерация тройки 5/10
party1  | Party 1: Генерация тройки 5/10
party2  | Party 2: Генерация тройки 6/10
party1  | Party 1: Генерация тройки 6/10
party2  | Party 2: Генерация тройки 7/10
party1  | Party 1: Генерация тройки 7/10
party2  | Party 2: Генерация тройки 8/10
party1  | Party 1: Генерация тройки 8/10
party2  | Party 2: Генерация тройки 9/10
party1  | Party 1: Генерация тройки 9/10
party2  | Party 2: Генерация тройки 10/10
party1  | Party 1: Генерация тройки 10/10
party2  | Party 2: Тройки сохранены в /app/output/p2.csv
party2  | Party 2: Завершено
party2  | Сторона 1 завершила работу
party1  | Party 1: Тройки сохранены в /app/output/p1.csv
party1  | Party 1: Завершено
party1  | Сторона 0 завершила работу
party1 exited with code 0
party2 exited with code 0
```

```
python3 mul.py 
All triples are correct
```
