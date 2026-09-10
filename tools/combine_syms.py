import os
import re
from pathlib import Path

import tomlkit
from elftools.elf.elffile import ELFFile

VERSION = os.environ.get("VERSION") or "us.v11"
SYMS = Path("syms")
INIT = SYMS / "init"
GAME = SYMS / "game"
GAME_ELF = Path(f"lib/blastcorps/game/build/game.{VERSION}.elf")


def shift_rom(path, delta):
    text = re.sub(
        r"^rom = 0x([0-9A-Fa-f]+)$",
        lambda m: f"rom = 0x{int(m.group(1), 16) + delta:08X}",
        path.read_text(),
        flags=re.M,
    )
    path.write_text(text)


def section_size(path, name):
    m = re.search(
        rf'name = "{re.escape(name)}"\n(?:.*\n)*?size = 0x([0-9A-Fa-f]+)',
        path.read_text(),
    )
    return int(m.group(1), 16)


def elf_symbol_size(path, name):
    with path.open("rb") as f:
        return ELFFile(f).get_section_by_name(".symtab").get_symbol_by_name(name)[0]["st_size"]


def rename_entrypoint(path, size):
    text = re.sub(
        r'name = "recomp_entrypoint"(, vram = 0x[0-9A-Fa-f]+, )size = 0x[0-9A-Fa-f]+',
        rf'name = "MainJump"\g<1>size = 0x{size:X}',
        path.read_text(),
    )
    path.write_text(text)


def combine(init_path, game_path, out_path, key):
    doc = tomlkit.document()
    doc["section"] = tomlkit.aot()
    for path, prefixed in ((init_path, True), (game_path, False)):
        for section in tomlkit.parse(path.read_text())["section"]:
            if section["name"] == "":
                continue
            if prefixed:
                for item in section.get(key, []):
                    if item["name"] != "recomp_entrypoint":
                        item["name"] = "_" + item["name"]
            doc["section"].append(section)
    out_path.write_text(tomlkit.dumps(doc))


def main():
    init_size = section_size(INIT / f"init.{VERSION}.toml", ".init")
    for name in (f"init.{VERSION}.toml", f"data_init.{VERSION}.toml"):
        shift_rom(INIT / name, 0x1000)

    entry_size = elf_symbol_size(GAME_ELF, "MainJump")
    for name in (f"game.{VERSION}.toml", f"data_game.{VERSION}.toml"):
        shift_rom(GAME / name, 0x1000 + init_size)
        rename_entrypoint(GAME / name, entry_size)

    combine(
        INIT / f"init.{VERSION}.toml",
        GAME / f"game.{VERSION}.toml",
        SYMS / f"blastcorps.{VERSION}.toml",
        "functions",
    )
    combine(
        INIT / f"data_init.{VERSION}.toml",
        GAME / f"data_game.{VERSION}.toml",
        SYMS / f"data_blastcorps.{VERSION}.toml",
        "symbols",
    )


if __name__ == "__main__":
    main()
