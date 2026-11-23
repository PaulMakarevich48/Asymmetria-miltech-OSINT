[Русский](../decisions.md)

# Key decisions

Each is a short record: what we decided, why, and what it cost.

### SQLite instead of a separate DBMS and vector database
One machine, one scheduled writer, reads from the bot and the portal. FTS5 and sqlite-vec cover full-text and vector search in a single file; a backup is one command. The cost is discipline around locking: runs are spread out in time, and service copies of the database are made only with `.backup`.

### A static portal instead of a web application
Cards, maps and reviews are generated once a day and after each deployment. Serving static files is cheap and reliable; dynamic parts exist only where needed (login, payments, a graph editor for the administrator). The cost is that changes appear with the next build, not instantly.

### Independent sources instead of link counts
The storefront figure of "911 sources" turned out to be inflated threefold: posts from one channel and fragments of one document were counted as separate sources. The honest count goes by documents and channels. The number got smaller, but every specification now shows how many **independent** sources support it — and that is the product's main differentiator.

### Model inferences kept separate
The graph distinguishes three levels: from a source, an expert edit, inferred by a model. Inferred values are marked and do not count as facts: the reader must see where the source ends and the guess begins.

### Checking before publishing
At first the digest was published and checked afterwards — and the owner noticed errors after subscribers had already read them. Now checking, fixing and re-checking happen before sending; whatever could not be fixed goes to the owner with the text of the block.

### One model where a pairing has not proven its value
Pairing the two strongest models for forecasts would have tripled the cost. Backtesting on the archive showed equal accuracy, so the pairing is built in behind a switch, and turning it on is deferred until live issues provide statistics.

### The agent does not deploy by itself
Deployment could have been handed to the agent — faster. Instead, a person presses a button in the bot, and automatic gates do the checking: the cost of a mistake on a live channel is higher than one minute of the owner's time.

### Neutral language
The product writes about a war, and one side's vocabulary in our own voice turns analysis into a position. The sides are named directly; nicknames for weapons and judgemental words are not used. This is a prompt rule, and code backs it up.
