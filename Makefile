.DEFAULT_GOAL := help
.EXPORT_ALL_VARIABLES:

SETTINGS ?=
GENERIC ?= rainbow/top.generic.yaml
OUTPUT ?= embroidery_mesh.png

ifneq ($(strip $(SETTINGS)),)
-include $(SETTINGS)
endif

.PHONY: help temp mesh

help:
	@echo "Usage: make <target> [SETTINGS=path] [GENERIC=path] [OUTPUT=file] COLOR1=... [COLOR2=...]"
	@echo "Targets:"
	@echo "  temp  - print path to generated threads temp YAML"
	@echo "  mesh  - generate mesh image using create_mesh.py"
	@echo "Example:"
	@echo "  make mesh GENERIC=rainbow/top.generic.yaml OUTPUT=embroidery_mesh.png COLOR1=310 COLOR2=321"

temp:
	@test -f "$(GENERIC)" || (echo "Generic file not found: $(GENERIC)" >&2; exit 1)
	@set -e; \
	tmp_file="$$(mktemp -t "$$(basename "$(GENERIC)" .generic.yaml)")"; \
	perl -pe 's{__COLOR(\d+)__}{exists $$ENV{"COLOR$$1"} ? do { my $$v = $$ENV{"COLOR$$1"}; $$v =~ s/\\/\\\\/g; $$v =~ s/"/\\"/g; "\"$$v\"" } : "__COLOR$$1__"}ge' "$(GENERIC)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$( (grep -oE '__COLOR[0-9]+__' "$$tmp_file" || true) | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(GENERIC): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	echo "$$tmp_file"

mesh:
	@test -f "$(GENERIC)" || (echo "Generic file not found: $(GENERIC)" >&2; exit 1)
	@set -e; \
	tmp_file="$$(mktemp -t "$$(basename "$(GENERIC)" .generic.yaml)")"; \
	perl -pe 's{__COLOR(\d+)__}{exists $$ENV{"COLOR$$1"} ? do { my $$v = $$ENV{"COLOR$$1"}; $$v =~ s/\\/\\\\/g; $$v =~ s/"/\\"/g; "\"$$v\"" } : "__COLOR$$1__"}ge' "$(GENERIC)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$( (grep -oE '__COLOR[0-9]+__' "$$tmp_file" || true) | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(GENERIC): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	python3 create_mesh.py --threads "$$tmp_file" --output "$(OUTPUT)"; \
	echo "threads_yaml=$$tmp_file"; \
	echo "mesh_png=$(OUTPUT)"
