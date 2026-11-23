"""Клиент «долгого декодирования» Gemini 4 по REST: ответ, который не влезает в один запрос.

Проблема: у части моделей один запрос без стриминга отдаёт ограниченное число токенов вывода, и
размышления модели идут в тот же счёт. На большом входе с глубоким размышлением модель тратит весь
лимит на мысли и возвращает пустой текст с причиной CONTINUATION и токеном продолжения. Если токен не
передать, ответ теряется — а деньги за размышления уже списаны.

Правила (по документации Google, проверено на практике):
  * повторять ТОТ ЖЕ запрос, добавив continuationToken; частичный ответ в contents не добавлять;
  * передавать только последний токен — он несёт всё состояние;
  * maxOutputTokens — общий лимит на все шаги, а не на один;
  * любая причина остановки, кроме CONTINUATION, — конец; не STOP — предупреждение, а не тишина;
  * каждый шаг оплачивается отдельно — и учитывать расход надо по шагам.
"""
import time

import httpx

MAX_HOPS = 8


def generate(url: str, token: str, system: str, prompt: str, *, level: str = "high",
             budget: int = 131072, on_usage=None, http=httpx) -> dict:
    """-> {'text', 'hops', 'finish', 'input_tokens', 'output_tokens'}."""
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": budget, "thinkingConfig": {"thinkingLevel": level}}}
    parts, cont, reason, tin, tout = [], None, None, 0, 0
    for hop in range(MAX_HOPS):
        req = dict(body, continuationToken=cont) if cont else body
        for attempt in range(4):
            r = http.post(url, headers={"Authorization": f"Bearer {token}"}, json=req, timeout=1800)
            if r.status_code == 200:
                break
            if r.status_code in (429, 500, 503) and attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {r.status_code} на шаге {hop + 1}: {r.text[:300]}")
        j = r.json()
        um = j.get("usageMetadata", {})
        used_in = um.get("promptTokenCount", 0)
        used_out = um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)
        if on_usage:
            on_usage(used_in, used_out)           # учёт — по каждому шагу
        tin, tout = tin + used_in, tout + used_out
        cand = (j.get("candidates") or [{}])[0]
        parts += (cand.get("content") or {}).get("parts", [])
        reason, cont = cand.get("finishReason"), cand.get("continuationToken")
        if reason != "CONTINUATION" or not cont:
            break
    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    if not text:
        raise RuntimeError(f"пустой ответ: причина {reason}, вывод {tout} токенов, шагов {hop + 1}")
    return {"text": text, "hops": hop + 1, "finish": reason, "input_tokens": tin, "output_tokens": tout}
