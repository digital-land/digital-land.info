SOURCE_URL=https://raw.githubusercontent.com/digital-land/

# deduce the repository
ifeq ($(REPOSITORY),)
REPOSITORY=$(shell basename -s .git `git config --get remote.origin.url`)
endif

define dataset_url
'https://collection-dataset.s3.eu-west-2.amazonaws.com/$(2)-collection/dataset/$(1).sqlite3'
endef

.PHONY: \
	makerules\
	specification\
	init\
	first-pass\
	second-pass\
	clobber\
	clean\
	commit-makerules\
	prune

# keep intermediate files
.SECONDARY:

# don't keep targets build with an error
.DELETE_ON_ERROR:

# work in UTF-8
LANGUAGE := en_GB.UTF-8
LANG := C.UTF-8

# for consistent collation on different machines
LC_COLLATE := C.UTF-8

# current git branch
BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

all:: first-pass second-pass

first-pass::
	@:

# restart the make process to pick-up collected files
second-pass::
	@:

# initialise
init::
	pip install --upgrade pip
ifneq (,$(wildcard requirements.txt))
	pip3 install --upgrade -r requirements.txt
endif
ifneq (,$(wildcard setup.py))
	pip install -e .
endif

submodules::
	git submodule update --init --recursive --remote

# remove targets, force relink
clobber::
	@:

# remove intermediate files
clean::
	@:

# prune back to source code
prune::
	rm -rf ./var $(VALIDATION_DIR)

# update makerules from source
makerules::
	curl -qfsL '$(SOURCE_URL)/makerules/main/makerules.mk' > makerules/makerules.mk

ifeq (,$(wildcard ./makerules/specification.mk))
# update local copies of specification files
specification::
	@mkdir -p specification/
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/collection.csv' > specification/collection.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/dataset.csv' > specification/dataset.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/dataset-schema.csv' > specification/dataset-schema.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/schema.csv' > specification/schema.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/schema-field.csv' > specification/schema-field.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/field.csv' > specification/field.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/datatype.csv' > specification/datatype.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/typology.csv' > specification/typology.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/pipeline.csv' > specification/pipeline.csv

init::	specification
endif

commit-makerules::
	git add makerules
	git diff --quiet && git diff --staged --quiet || (git commit -m "Updated makerules $(shell date +%F)"; git push origin $(BRANCH))

commit-collection::
	@:
