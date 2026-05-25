.DEFAULT_GOAL := help
.EXPORT_ALL_VARIABLES:

SETTINGS ?=
TEMPLATE ?=
GENERIC ?=
OUTPUT ?= embroidery_mesh.png

ifeq ($(strip $(TEMPLATE)),)
ifneq ($(strip $(GENERIC)),)
TEMPLATE := $(GENERIC)
else
TEMPLATE := rainbow/top.generic.yaml
endif
endif

ifneq ($(strip $(SETTINGS)),)
-include $(SETTINGS)
endif

.PHONY: help temp mesh

help:
	@echo "Usage: make <target> [SETTINGS=path] [TEMPLATE=path] [OUTPUT=file] COLOR1=... [COLOR2=...]"
	@echo "Targets:"
	@echo "  temp  - print path to generated threads temp YAML"
	@echo "  mesh  - generate mesh image using create_mesh.py"
	@echo "Example:"
	@echo "  make mesh TEMPLATE=rainbow/top.generic.yaml OUTPUT=embroidery_mesh.png COLOR1=310 COLOR2=321"

temp:
	@test -f "$(TEMPLATE)" || (echo "Template file not found: $(TEMPLATE)" >&2; exit 1)
	@set -e; \
	tmp_file="$$(mktemp -t "$$(basename "$(TEMPLATE)" .generic.yaml)")"; \
	perl -pe 's{__COLOR(\d+)__}{exists $$ENV{"COLOR$$1"} ? do { my $$v = $$ENV{"COLOR$$1"}; $$v =~ s/\\/\\\\/g; $$v =~ s/"/\\"/g; "\"$$v\"" } : "__COLOR$$1__"}ge' "$(TEMPLATE)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$( (grep -oE '__COLOR[0-9]+__' "$$tmp_file" || true) | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(TEMPLATE): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	echo "$$tmp_file"

mesh:
	@test -f "$(TEMPLATE)" || (echo "Template file not found: $(TEMPLATE)" >&2; exit 1)
	@set -e; \
	tmp_file="$$(mktemp -t "$$(basename "$(TEMPLATE)" .generic.yaml)")"; \
	perl -pe 's{__COLOR(\d+)__}{exists $$ENV{"COLOR$$1"} ? do { my $$v = $$ENV{"COLOR$$1"}; $$v =~ s/\\/\\\\/g; $$v =~ s/"/\\"/g; "\"$$v\"" } : "__COLOR$$1__"}ge' "$(TEMPLATE)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$( (grep -oE '__COLOR[0-9]+__' "$$tmp_file" || true) | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(TEMPLATE): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	python3 create_mesh.py --template "$$tmp_file" --output "$(OUTPUT)"; \
	echo "threads_yaml=$$tmp_file"; \
	echo "mesh_png=$(OUTPUT)"
