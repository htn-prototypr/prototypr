all: clean build
clean:
	rm -rf reactify/output/test
build:
	sh run.sh
