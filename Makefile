.PHONY: test gate

# per-rule dirty/clean examples (skill/scripts/tests/rule_examples.py)
test:
	. skill/scripts/find_python.sh && "$$PY" -m unittest discover -s skill/scripts/tests

# the full eval gate; runs the tests too, as gate 5
gate:
	scripts/gate.sh
