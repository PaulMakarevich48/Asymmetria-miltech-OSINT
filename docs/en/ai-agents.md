[Русский](../ai-agents.md)

# Working with AI agents

The product was written by one person together with Claude Code agents: hundreds of sessions over four months, some of them from a phone. Speed is not the point. The point is being able to trust an agent with work on a live system that has subscribers, money and keys.

## 1. A boundary, not a rule

An agent can forget an instruction or break it by mistake. So the important things rest on boundaries that do not depend on its memory:

- **An OS sandbox around every agent command.** The agent cannot see keys, Telegram sessions or the subscriber database, cannot write to the production copy or the operations scripts, and can reach only the model APIs over the network.
- **A separate user for production.** The bot, the scheduled runs and the portal run from a clone the agent cannot see. Code gets there only through deployment.
- **Deployment is a button in the owner's bot**, executed by a runner that checks the commit itself: import check of every module, an access-control test for the bot, the lab gate, run windows, one-command rollback.
- **Only the operations folder runs outside the sandbox**, and it never imports code from the working copy: otherwise an agent's edit would execute as a user with administrator rights.

## 2. A lab instead of "seems to work"

Any change to the digest path is first run in the lab: the same day, the same code and prompts, a full assembly — without publishing, with its own daily spending cap and a comparison with what was actually published. A green run leaves a mark on the commit; without it the deployment gate will not let the change through. A run that cannot afford the whole cycle does not start at all: two runs that stopped halfway are money spent with no result.

## 3. A lessons log

Every incident is recorded: what broke, why, and what follows. The conclusion becomes code or a test, not a note. An example chain: an image caption in the PDF turned out to describe the wrong picture six times. Five fixes closed one specific path each; the sixth introduced a rule ("the caption is what is recognised in the image"), validated by running it over the whole archive rather than one case.

## 4. Money

- The cost of every model call is recorded by purpose, so the unit cost of the digest, the bot and the graph is visible day by day.
- Spending kill-switches: a run that would exceed the threshold does not start.
- Models are chosen by measurement on our own tasks: moving post parsing to a newer model cut its cost 3–5× with the same number of extracted entities — checked on the same posts, not taken from marketing.
- Large one-off jobs (graph cleaning, OCR of scanned catalogues, company dossiers) ran as waves of agents on a subscription rather than through the paid API — planned around the five-hour usage window, with automatic resumption after the window resets.

## 5. AI checking AI

- **The digest checker**: every claim is compared with its source post and the graph's reference data; a model fixes it, then the fix is checked again.
- **Forecast backtesting on the archive**: different models build projections from a past window, and a blind judge scores them against what happened. That is how we learned that the most expensive model pairing adds no accuracy — and the cost decision was made on data.
- **An independent provider**: a second model vendor serves as a fallback and as a critic — it makes different mistakes.

## 6. Documents the agent reads

| Document | Role |
|---|---|
| project map | where things are, what is forbidden, how to deploy |
| plan | the single task list: number, summary, status, next step |
| backlog | rationale and measurements under the same numbers |
| journal | what was done, by day |
| lessons | incidents and conclusions |
| agent registry | what each agent may do and what it must not do |

There is no second task list: when there were five, they contradicted each other. When the plan grew to 190 KB and could no longer be read in full, it was cut down to the essentials and the history was moved to the backlog.
