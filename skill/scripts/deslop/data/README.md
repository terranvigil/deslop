# Config layers

Merged at runtime in this order, later wins: `rules.py` (curated), then
`fingerprint.json`, then `personal.json` (pet peeves). `fingerprint.json`
holds a word list measured from current Claude output. Both JSON layers are
optional. Each has `words` and `phrases` objects mapping the term to its fix
hint.
