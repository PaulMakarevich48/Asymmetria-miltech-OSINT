[Русский](../lessons.md)

# Selected lessons

From the incident log — the ones that changed not one line but the way of working. Format: what happened → why → what follows.

### The deployment gate could let an unverified change through
**Happened.** The bash check "does this commit range touch the digest path" used `git diff --name-only | grep -q` under `set -o pipefail`.
**Why.** `grep -q` exits on the first match, `git` gets SIGPIPE on a long list, the pipeline returns 141 — and that was read as "no changes". It never fired on short deployments because the output fit in the pipe buffer.
**Follows.** Capture the output in a variable first, then search it. A tool error is treated as "there is a change": a safety mechanism errs only on the strict side. The test uses 12,000 files in the range.

### An empty model response is a failure, not "nothing found"
**Happened.** Extraction of named systems returned zero names — and the zero was cached. The digest went out without illustrations or links, and the quality watchdog suggested the wrong fix.
**Why.** An empty response with HTTP 200 is the normal shape of a safety-classifier refusal; the code read it as a result. The same investigation found a 600-token answer cap (exactly the archive record) and a numbering strip that ate the start of designations such as "9M723".
**Follows.** An empty answer to a non-empty input means: log the stop reason and try a fallback model; never cache emptiness. A watchdog must tell "the measurement broke" from "the data got thinner".

### A background thread could have crashed the digest
**Happened.** The audio version is synthesised in the background inside the digest run. With the key missing, helper code raised `SystemExit`; `ThreadPoolExecutor` stores any `BaseException` in the `Future`, `result()` re-raises it, and the handler caught only `Exception`.
**Follows.** The "background → main process" boundary catches `BaseException` (except Ctrl+C); helper code never exits the process. Test the "no key" path, not only "synthesis failed".

### The model provider blocked the organisation — the whole pipeline stopped
**Happened.** One morning the API refused at the organisation level: not the key, not credits, not a spending limit. The digest did not go out; the graph, the feeds and the bot stopped.
**Follows.** A fallback: on refusal the pipeline switches by itself to the same models through another cloud, then to another vendor's models, and switches back by itself. Manual mode is a bot command. Failed runs are restarted in dependency order.

### Two sessions, one file
**Happened.** An agent was editing a shared page generator without committing, waiting for a decision. A parallel session committed the whole file, including the other agent's insertion, which imported a module that had not been committed yet. The morning build was hours away from failing.
**Why.** `git add <file>` takes every change in the file, not "my lines"; the working copy is shared by all sessions.
**Follows.** An edit to a shared file does not stay uncommitted longer than one turn — either commit it behind a switch or work in a copy. Before deployment the checks are repeated on a clean `git archive` of the commit.

### The model did not know whose channel it was
**Happened.** The digest said one side "uses" a system that was in fact used by the other side: the model read a slang nickname in the post the wrong way round.
**Follows.** A registry of channel sides — a label in the inputs of the digest, the graph and the checker; a rule about nicknames in the prompt; the checker knows this class of error; a fix in one block is propagated to repeats further down.

### The sixth time about an image caption
**Happened.** In the PDF, a photo of an uncrewed boat carried a caption about a ground robot. Five earlier fixes had each closed one path: the caption was taken from text near the image — a heading, a sentence subject, a checker's answer.
**Follows.** A rule instead of a patch: the caption is what is recognised in the image, or text that names it. A new rule is first run over the entire archive (829 images, 27 captions changed — all for the better), not just today's case.

### A long model answer was silently cut off
**Happened.** A second model's critique in the forecast backtest stopped after 4 points out of 9, and a section draft came back empty twice.
**Why.** The model has an output limit per request, and its reasoning counts against the same limit; when it runs out, the API returns a continuation token that must be passed in a follow-up request. The code did not pass it.
**Follows.** The client walks the steps with the token until the real end, and any stop reason other than the normal one is a warning, not silence. Example: [examples/long_decode.py](../../examples/long_decode.py).
