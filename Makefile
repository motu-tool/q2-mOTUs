.PHONY: all lint test test-cov install dev clean distclean

PYTHON ?= python

all: ;

lint:
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_motus

install:
	if ! which motus > /dev/null; then pip install motu-profiler; fi
	if ! which bwa > /dev/null; then git clone https://github.com/lh3/bwa.git && cd bwa && make && ln -s $(PWD)/bwa/bwa $(CONDA_PREFIX)/bin; fi

	motus downloadDB
	$(PYTHON) setup.py install --user

dev: all
	pip install -e .

clean: distclean

distclean: ;