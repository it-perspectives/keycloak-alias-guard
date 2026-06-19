#!/usr/bin/env python3
"""Sync error-mailbox-not-unique translations from Keycloak base theme locales."""

from __future__ import annotations

import pathlib
import re
import urllib.request

KEYCLOAK_VERSION = "26.5.7"
BASE_URL = (
    f"https://raw.githubusercontent.com/keycloak/keycloak/{KEYCLOAK_VERSION}"
    "/themes/src/main/resources-community/theme/base/login/messages"
)
ROOT = pathlib.Path(__file__).resolve().parents[1] / "src/main/resources/theme-resources/messages"
MESSAGE_KEY = "error-mailbox-not-unique"
ENGLISH = "This email address is already registered."

LOCALE_FILES = [
    "messages_en.properties",
    "messages_ar.properties",
    "messages_az.properties",
    "messages_ca.properties",
    "messages_cs.properties",
    "messages_da.properties",
    "messages_de.properties",
    "messages_el.properties",
    "messages_es.properties",
    "messages_eu.properties",
    "messages_fa.properties",
    "messages_fi.properties",
    "messages_fr.properties",
    "messages_hr.properties",
    "messages_hu.properties",
    "messages_it.properties",
    "messages_ja.properties",
    "messages_ka.properties",
    "messages_kk.properties",
    "messages_ko.properties",
    "messages_ky.properties",
    "messages_lt.properties",
    "messages_lv.properties",
    "messages_nl.properties",
    "messages_no.properties",
    "messages_pl.properties",
    "messages_pt.properties",
    "messages_pt_BR.properties",
    "messages_ro.properties",
    "messages_ru.properties",
    "messages_sk.properties",
    "messages_sl.properties",
    "messages_sv.properties",
    "messages_th.properties",
    "messages_tr.properties",
    "messages_uk.properties",
    "messages_zh_Hans.properties",
    "messages_zh_Hant.properties",
    "messages_zh_CN.properties",
    "messages_zh_TW.properties",
]

ALIASES = {
    "messages_en.properties": ENGLISH,
    "messages_zh_CN.properties": "messages_zh_Hans.properties",
    "messages_zh_TW.properties": "messages_zh_Hant.properties",
}


def needs_utf8_header(text: str) -> bool:
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def fetch_keycloak_message(filename: str) -> str:
    if filename in ALIASES and not filename.startswith("messages_zh"):
        return ALIASES[filename]

    source = ALIASES.get(filename, filename)
    url = f"{BASE_URL}/{source}"
    text = urllib.request.urlopen(url, timeout=20).read().decode("utf-8")
    match = re.search(r"^emailExistsMessage=(.*)$", text, re.M)
    if not match:
        raise RuntimeError(f"emailExistsMessage missing in {source}")
    return match.group(1).strip()


def write_bundle(filename: str, message: str) -> None:
    lines: list[str] = []
    if needs_utf8_header(message):
        lines.extend(["# encoding: UTF-8", ""])
    lines.append(f"{MESSAGE_KEY}={message}")
    lines.append("")
    (ROOT / filename).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for filename in LOCALE_FILES:
        write_bundle(filename, fetch_keycloak_message(filename))
        print(f"wrote {filename}")


if __name__ == "__main__":
    main()
