[Русский](forecast_backtest.md)

# Backtesting forecasts on the archive

How to choose a model for analytical forecasts when "which one is smarter" by public rankings does not answer "whose forecasts come true on my data".

## Setup

1. **Windows in the past.** Material for the 30 days before the window date; the forecast is made from that point. A window one month back is checked against the next 30 days, a window three months back against the next 90.
2. **One input for everyone.** The material is assembled once and given to every participant byte for byte.
3. **Isolation.** A participant model sees only its window's material: no internet, no files after the window date. Each participant lists what it read.
4. **A checkable forecast format.** Each item has a confidence level ("high / medium / low"), the projection, and "Check by:" — an observable sign that will confirm or refute it within the horizon.
5. **A blind judge.** All participants' forecasts are shuffled and labelled with random numbers; authorship is stored separately and is not visible to the judge. The judge's material is what happened during the check period.

## The judge's scale

| Field | Values |
|---|---|
| verdict | came true · partly · did not come true · cannot be checked (no evidence either way) |
| specificity | 0 — vague · 1 — direction with a sign · 2 — a sign with a threshold or event |
| non-obviousness | 0 — continuation of the main news · 1 — an expected step · 2 — an inference from several signals combined |

Points: came true — 1, partly — 0.5. Separately — points among forecasts that are both specific and non-obvious: a vague "will keep developing" almost always comes true and must not win.

## What the run showed

Five participants (a strong model, the strongest model, two models from another vendor, and a pairing "draft → critique by a second model → final"), six forecasts each:

- accuracy was the same for everyone except one participant, which fell behind;
- the strongest model and the pairing write multi-part forecasts with caveats, so all of theirs were "partly"; the simpler model writes boldly — half came true, half did not;
- the pairing was slightly better on "specific and non-obvious" — at three times the cost;
- the judge was stable: on unchanged forecasts, a second run agreed in 12 cases out of 12.

Conclusion: do not enable the pairing by default; collect statistics from live issues, where the forecast scorecard is kept every month. The sample is small, and that is stated plainly.

## Pitfalls we hit

- **The judge breaks JSON** with straight quotes inside citations — require typographic quotes or validate by parsing.
- **The second model's answer was cut off** at the per-request output limit — without long decoding the critique covered 4 points out of 9. See [long_decode.py](long_decode.py).
- **The model's training cutoff** may be later than the window: then the "forecast" is memory. Treat the most recent window as the main one.
