all: clean build
clean:
	rm reactify/output/test
build:
	sh run.sh
