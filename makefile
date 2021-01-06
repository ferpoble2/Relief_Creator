help:
	@echo "This are the available commands:"
	@echo "build-executable: Build an executable of the project in the dist folder."

build-executable:
	pyinstaller --clean ReliefeCreator.spec
