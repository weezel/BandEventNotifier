VENV_DIR	:= venv


install:
	python3 -m venv $(VENV_DIR) && \
		$(VENV_DIR)/bin/pip3 install -r requirements.txt

.PHONY: clean
clean:
	rm -rf *.pyc $(VENV_DIR)

