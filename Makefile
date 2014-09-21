OBJ	= tests.py

.PHONY: clean

all: clean
	python $(OBJ)
graphs:
	dot -Tpng structure.dot -o structure.png
clean:
	rm -f *.pyc

