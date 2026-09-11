.PHONY: all

VERSION ?= us.v11
N64_RECOMP_CLI = lib/N64Recomp/build/N64Recomp

default: all

all: $(N64_RECOMP_CLI) lib/blastcorps/init/build/init.$(VERSION).elf
	mkdir -p syms/init
	$(N64_RECOMP_CLI) init.$(VERSION).toml --dump-context
	mv dump.toml syms/init/init.us.v11.toml
	mv data_dump.toml syms/init/data_init.us.v11.toml
	mkdir -p syms/game
	$(N64_RECOMP_CLI) game.$(VERSION).toml --dump-context
	mv dump.toml syms/game/game.us.v11.toml
	mv data_dump.toml syms/game/data_game.us.v11.toml
	python3 tools/combine_syms.py

$(N64_RECOMP_CLI):
	cmake -S lib/N64Recomp -B lib/N64Recomp/build -DCMAKE_BUILD_TYPE=Release
	cmake --build lib/N64Recomp/build --target N64RecompCLI -j

lib/blastcorps/init/build/init.$(VERSION).elf: lib/blastcorps/baserom.$(VERSION).z64
	make -C lib/blastcorps full

lib/blastcorps/baserom.$(VERSION).z64: baserom.$(VERSION).z64
	cp baserom.$(VERSION).z64 lib/blastcorps/baserom.$(VERSION).z64

clean:
	make -C lib/blastcorps clean
	rm -rf lib/N64Recomp/build
	rm -rf syms