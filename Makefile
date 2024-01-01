PYTHON = python3
PYTHON_VERSION_MIN=3.11
PYTHON_VERSION=$(shell $(PYTHON) -c 'import sys; print("%d.%d"% sys.version_info[0:2])' )
PYTHON_VERSION_OK=$(shell $(PYTHON) -c 'import sys;\
  print(int(float("%d.%d"% sys.version_info[0:2]) >= $(PYTHON_VERSION_MIN)))' )

ifeq ($(PYTHON_VERSION_OK),0)
  $(error "detected Python $(PYTHON_VERSION) need Python >= $(PYTHON_VERSION_MIN)")
endif

prepare_venv:
	test -d venv || python3 -m venv ./venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

clean:
	rm -rf venv

run:
	./venv/bin/python3 main.py


