OBJ		:= tests.py
VENV_DIR	:= .venv

.PHONY: clean

install:
	python3 -m venv $(VENV_DIR) && \
		. $(VENV_DIR)/bin/activate && \
		pip3 install -r requirements.txt && \
		deactivate
run:
	$(VENV_DIR)/bin/python3 bandeventnotifier.py
graphs:
	dot -Tpng structure.dot -o structure.png
clean:
	rm -rf *.pyc $(VENV_DIR)

