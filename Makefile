VENV ?= venv
PYTHON = $(VENV)/bin/python
BOOTSTRAP_PYTHON ?= python3
# Every family in scripts/families.py; override to build one, e.g. FAMILIES=GoistMono.
FAMILIES ?= Goist GoistMono

.DEFAULT_GOAL := help
.PHONY: help build baseline test proof qa venv package

help:
	@echo "Goist: make build | make baseline | make test | make proof | make qa | make package"
	@echo "Families: $(FAMILIES). Override with FAMILIES=GoistMono."
	@echo "Fonts: fonts/<family>/; editable sources: build/<family>/sources/; proofs and QA: out/<family>/."

venv: $(VENV)/touchfile

$(VENV)/touchfile: requirements.txt requirements.in
	test -d "$(VENV)" || $(BOOTSTRAP_PYTHON) -m venv "$(VENV)"
	"$(PYTHON)" -m pip install -r requirements.txt
	touch "$@"

# Always run the content-hash driver: every file inside each glyphspackage,
# configuration, scripts and compiler versions participates in cache invalidation.
# This also restores a deleted or modified artifact instead of trusting a stamp.
build: venv
	set -e; for family in $(FAMILIES); do "$(PYTHON)" scripts/build.py --family $$family; done

baseline: venv
	set -e; for family in $(FAMILIES); do "$(PYTHON)" scripts/build.py --family $$family --baseline; done

test: build baseline
	set -e; for family in $(FAMILIES); do "$(PYTHON)" scripts/verify.py --family $$family; done
	"$(PYTHON)" -m unittest discover -s tests -v

proof: build
	set -e; for family in $(FAMILIES); do "$(PYTHON)" scripts/proof.py --family $$family; done

# Optional external QA; failures are never suppressed.
qa: build
	command -v fontspector
	set -e; for family in $(FAMILIES); do \
		mkdir -p out/$$family/fontspector; \
		fontspector --profile googlefonts -l warn --full-lists --succinct \
			--html out/$$family/fontspector/report.html --ghmarkdown out/$$family/fontspector/report.md \
			fonts/$$family/variable/*.ttf; \
	done

# Stage webfonts into packages/goeist and produce an inspectable npm tarball.
package: build
	cd packages/goeist && npm pack
