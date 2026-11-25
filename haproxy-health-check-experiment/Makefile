.PHONY: test validate smoke pilot all core fast-pilot fast flap-sweep isolation clean

test:
	python3 -m unittest discover -s tests -v

validate: test
	docker compose config --quiet

smoke:
	python3 orchestrate.py smoke

pilot:
	python3 orchestrate.py pilot

all:
	python3 orchestrate.py all

core:
	python3 orchestrate.py core

fast-pilot:
	python3 orchestrate.py fast-pilot

fast:
	python3 orchestrate.py fast

flap-sweep:
	python3 orchestrate.py flap-sweep

isolation:
	python3 orchestrate.py isolation

clean:
	docker compose down -v --remove-orphans

