VENV ?= venv
PYTHON = $(VENV)/bin/python
BOOTSTRAP_PYTHON ?= python3
FAMILY = Goist

.DEFAULT_GOAL := help
.PHONY: help build baseline test proof qa venv package

help:
	@echo "Goist: make build | make baseline | make test | make proof | make qa | make package"
	@echo "Fonts: fonts/$(FAMILY)/; editable sources: build/$(FAMILY)/sources/; proofs and QA: out/$(FAMILY)/."
	@echo "Offline rebuilds use the vendored sources and an already installed venv."

venv: $(VENV)/touchfile

$(VENV)/touchfile: requirements.txt requirements.in
	test -d "$(VENV)" || $(BOOTSTRAP_PYTHON) -m venv "$(VENV)"
	"$(PYTHON)" -m pip install -r requirements.txt
	touch "$@"

# Always run the content-hash driver: every file inside either glyphspackage,
# configuration, scripts and compiler versions participates in cache invalidation.
# This also restores a deleted or modified artifact instead of trusting a stamp.
build: venv
	"$(PYTHON)" scripts/build.py

baseline: venv
	"$(PYTHON)" scripts/build.py --baseline

test: build baseline
	"$(PYTHON)" scripts/verify.py --fonts fonts/$(FAMILY) --reference sources/$(FAMILY)/upstream/reference \
		--source-baseline build/$(FAMILY)/baseline --output out/$(FAMILY)/verification.json
	"$(PYTHON)" -m unittest discover -s tests -v

proof: build
	"$(PYTHON)" scripts/proof.py --fonts fonts/$(FAMILY) --reference sources/$(FAMILY)/upstream/reference \
		--output out/$(FAMILY)/proof

# Optional external QA; failures are never suppressed.
qa: build
	command -v fontspector
	mkdir -p out/$(FAMILY)/fontspector
	fontspector --profile googlefonts -l warn --full-lists --succinct \
		--html out/$(FAMILY)/fontspector/report.html --ghmarkdown out/$(FAMILY)/fontspector/report.md \
		fonts/$(FAMILY)/variable/*.ttf

# Stage webfonts into packages/goist and produce an inspectable npm tarball.
package: build
	cd packages/goist && npm pack
