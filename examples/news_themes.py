"""Темы по векторам: новости за период → группы по смыслу → какие темы растут.

Задача: за 30 дней — около двух тысяч новостей. Нужно увидеть не отдельные заголовки, а темы и их
динамику: «вертолёты против дронов: 3 → 15 → 17 → 7 новостей по неделям». Счёт делает код, модель
получает уже готовые числа — и не может их выдумать.

Три решения, которые оказались важны на практике:
  1. Вектор — на новость, а не на фрагмент фиксированной длины. Фрагменты по ~1500 знаков смешивают
     заголовок раздела с двумя-тремя новостями, и группы собираются по разделам, а не по темам.
  2. Групп — около одной на 30 новостей. Крупные группы сглаживают динамику до неразличимости.
  3. Рост — по доле темы среди всех новостей половины периода, а не по сырому счёту: если во второй
     половине новостей просто меньше, по сырому счёту «спадает» всё.

Без numpy: сферический k-means на чистом Python — для ~2 тыс. векторов размерности 512 это пара минут.
"""
import math
import operator
import random
from datetime import date


def unit(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def dot(a, b):
    return sum(map(operator.mul, a, b))


def kmeans(X, k, iters=20, restarts=2, seed=7):
    """Сферический k-means по косинусу. X — единичные векторы. -> (метки, центры)."""
    rnd = random.Random(seed)
    best = None
    for _ in range(restarts):
        C = [X[i] for i in rnd.sample(range(len(X)), k)]
        lab = None
        for _ in range(iters):
            new = [max(range(k), key=lambda j: dot(x, C[j])) for x in X]
            if new == lab:
                break
            lab = new
            for j in range(k):
                members = [X[i] for i in range(len(X)) if lab[i] == j]
                if members:
                    C[j] = unit([sum(col) for col in zip(*members)])
        score = sum(dot(X[i], C[lab[i]]) for i in range(len(X)))
        if best is None or score > best[0]:
            best = (score, lab, C)
    return best[1], best[2]


def themes(items, vectors, days, k=None, reps=6):
    """items: [{'day': 'ГГГГ-ММ-ДД', 'head': str, 'text': str}], vectors — по одному на новость.
    -> темы, крупные первыми: размер, счёт по неделям и половинам, характерные новости."""
    X = [unit(v) for v in vectors]
    k = k or max(16, min(60, len(items) // 30))
    lab, C = kmeans(X, k)
    start, half = days[0], len(days) // 2
    nweeks = (len(days) + 6) // 7
    out = []
    for j in range(len(C)):
        idx = sorted((i for i in range(len(items)) if lab[i] == j), key=lambda i: -dot(X[i], C[j]))
        if not idx:
            continue
        weeks, halves = [0] * nweeks, [0, 0]
        for i in idx:
            off = (date.fromisoformat(items[i]["day"]) - start).days
            weeks[min(off // 7, nweeks - 1)] += 1
            halves[off >= half] += 1
        # характерные: ближние к центру, по одной на неделю, без повторов одного сюжета
        pick = []
        for i in idx:
            if len(pick) >= reps:
                break
            if all(dot(X[i], X[p]) < 0.95 for p in pick):
                pick.append(i)
        out.append({"size": len(idx), "weeks": weeks, "halves": halves,
                    "examples": [items[i] for i in sorted(pick, key=lambda i: items[i]["day"])]})
    total = [sum(t["halves"][0] for t in out), sum(t["halves"][1] for t in out)]
    for t in out:
        t["trend"] = trend(t["halves"], total)
    return sorted(out, key=lambda t: -t["size"])


def trend(halves, total):
    """'рост' / 'спад' / '' — по доле темы в своей половине, только при заметной разнице:
    в полтора раза и не меньше четырёх новостей сверх ожидаемого."""
    a, b = halves
    ta, tb = total
    expected_b = a * tb / ta if ta else a
    if b >= 5 and b >= 1.5 * expected_b and b - expected_b >= 4:
        return "рост"
    if a >= 5 and expected_b >= 1.5 * b and expected_b - b >= 4:
        return "спад"
    return ""
