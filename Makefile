.PHONY: all lint test test-cov install dev clean distclean

PYTHON ?= python
PIP ?= pip

all: ;

lint:
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_motus

install:
	if ! command -v motu-profiler &> /dev/null; \
	then \
		$(PIP) install motu-profiler; \
	else \
		echo "motu-profiler is already installed"; \
	fi

	if ! command -v bwa &> /dev/null; \
	then \
		git clone https://github.com/lh3/bwa.git && cd bwa && make && ln -s $(PWD)/bwa/bwa $(CONDA_PREFIX)/bin; \
	else \
		echo "bwa is already installed"; \
	fi

	motus downloadDB
	$(PIP) install .

dev: all
	$(PIP) install -e .

clean: distclean

distclean: ;