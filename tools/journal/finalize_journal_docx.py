from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile


SOURCE = Path("revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi2.docx")
OUTPUT = Path("/private/tmp/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-final.docx")


REPLACEMENTS = {
    "Christianto Elvern Haryanto1*, [Nama Dosen Pembimbing]2":
        "Christianto Elvern Haryanto1*, Dr. Ir. Agustinus Bimo Gumelar, ST, MT2",
    "E-mail: 1*[email penulis 1], 2[email pembimbing]  (* : corresponding author)":
        "E-mail: 1*Chriselvern890@gmail.com, 2 bimo.gumelar@ciputra.ac.id  (* : corresponding author)",
    "memenuhi standar":
        "laik-layan",
    "tercatat memuncak pada 57%, sedangkan":
        "sepanjang pengujian tetap berada di bawah ambang 80%, sedangkan",
    "puncak penggunaan CPU ":
        "penggunaan CPU ",
    " 57% berada di bawah ambang 80%, sehingga ":
        " yang tidak melampaui ambang 80% memastikan ",
}


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Source journal not found: {SOURCE}")

    with ZipFile(SOURCE, "r") as source_zip:
        document_xml = source_zip.read("word/document.xml").decode("utf-8")

        for old, new in REPLACEMENTS.items():
            count = document_xml.count(old)
            if count != 1:
                raise SystemExit(
                    f"Expected exactly one occurrence of {old!r}, found {count}"
                )
            document_xml = document_xml.replace(old, new, 1)

        pilot_match = re.search(
            r"<w:p(?: [^>]*)?>(?:(?!</w:p>).)*?"
            r"Seluruh kriteria gerbang validasi terpenuhi\.(?:(?!</w:p>).)*?"
            r"Ringkasan hasil (?:(?!</w:p>).)*?disajikan pada Tabel 3\."
            r"(?:(?!</w:p>).)*?</w:p>",
            document_xml,
            flags=re.DOTALL,
        )
        if pilot_match is None:
            raise SystemExit("Pilot-study result paragraph not found")
        pilot_xml = pilot_match.group(0)
        if pilot_xml.count(" tidak menjadi ") != 1:
            raise SystemExit("Expected one 'tidak menjadi' phrase in pilot paragraph")
        revised_pilot_xml = pilot_xml.replace(
            " tidak menjadi ", " bukan menjadi ", 1
        )
        document_xml = (
            document_xml[: pilot_match.start()]
            + revised_pilot_xml
            + document_xml[pilot_match.end() :]
        )

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as output_zip:
            for item in source_zip.infolist():
                payload = (
                    document_xml.encode("utf-8")
                    if item.filename == "word/document.xml"
                    else source_zip.read(item.filename)
                )
                output_zip.writestr(item, payload)

    print(OUTPUT)


if __name__ == "__main__":
    main()
