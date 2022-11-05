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
	which motus  || pip install motu-profiler
	which bwa || git clone https://github.com/lh3/bwa.git || cd bwa || make || cd .. || rm -rf bwa
	motus downloadDB
	$(PYTHON) setup.py install

dev: all
	pip install -e .

clean: distclean

distclean: ;