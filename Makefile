all: clean build
clean:
	rm -r reactify/output/test
build:
	sh run.sh
