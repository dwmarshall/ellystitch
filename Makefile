.DEFAULT_GOAL := temp

GENERIC ?= rainbow/top.generic.yaml
OUTPUT ?= embroidery_mesh.png

.PHONY: temp mesh
temp:
	@test -f "$(GENERIC)" || (echo "Generic file not found: $(GENERIC)" >&2; exit 1)
	@tmp_file="$$(mktemp -t "$$(basename "$(GENERIC)" .generic.yaml)")"; \
	perl -pe 's/__COLOR(\d+)__/exists $$ENV{"COLOR$$1"} ? $$ENV{"COLOR$$1"} : "__COLOR$$1__"/ge' "$(GENERIC)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$(grep -oE '__COLOR[0-9]+__' "$$tmp_file" | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(GENERIC): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	echo "$$tmp_file"

mesh:
	@test -f "$(GENERIC)" || (echo "Generic file not found: $(GENERIC)" >&2; exit 1)
	@tmp_file="$$(mktemp -t "$$(basename "$(GENERIC)" .generic.yaml)")"; \
	perl -pe 's/__COLOR(\d+)__/exists $$ENV{"COLOR$$1"} ? $$ENV{"COLOR$$1"} : "__COLOR$$1__"/ge' "$(GENERIC)" > "$$tmp_file" || { rm -f "$$tmp_file"; exit 1; }; \
	missing="$$(grep -oE '__COLOR[0-9]+__' "$$tmp_file" | sort -u | tr '\n' ' ')"; \
	if [ -n "$$missing" ]; then \
	  echo "Unresolved placeholders in $(GENERIC): $$missing" >&2; \
	  echo "Provide matching vars, e.g. make COLOR1=... COLOR2=..." >&2; \
	  rm -f "$$tmp_file"; \
	  exit 1; \
	fi; \
	python3 create_mesh.py --threads "$$tmp_file" --output "$(OUTPUT)"; \
	echo "threads_yaml=$$tmp_file"; \
	echo "mesh_png=$(OUTPUT)"
