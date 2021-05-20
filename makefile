help:
	@echo "This are the available commands:"
	@echo "build-executable-windows: Build an executable of the project in the output folder."
	@echo "run-windows: Run the project on windows. A folder called venv with the virtual environment to use is needed."
	@echo "run-test-windows: Run the tests of the project. A folder "

run-windows:
	.\venv\Scripts\activate && \
	set PYTHONPATH=. && \
	python .\src\main.py

run-test-windows:
	.\venv\Scripts\activate && \
	set PYTHONPATH=. && \
	python -m unittest discover .\test

build-executable-windows:
	.\venv\Scripts\activate && \
	auto-py-to-exe
