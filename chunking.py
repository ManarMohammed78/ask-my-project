from load_data import read_word, read_excel, DATA_DIR


def clean(line):
    """Remove empty trailing cells like ' |  | ' from the end of a line."""
    return line.rstrip(" |")


def chunk_word(lines, max_chars=800):
    """Group Word lines into chunks of roughly max_chars characters."""
    chunks = []
    current = ""
    for line in lines:
        line = clean(line)
        if current and len(current) + len(line) + 1 > max_chars:
            chunks.append(current)
            current = ""
        current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return [{"source": "Word report", "text": c} for c in chunks]


def chunk_excel(lines, rows_per_chunk=12):
    """Group Excel rows by sheet; repeat the sheet's first 3 rows in every chunk."""
    sheets = {}
    for line in lines:
        head, _, rest = line.partition("] ")
        sheet_name = head.lstrip("[")
        sheets.setdefault(sheet_name, []).append(clean(rest))

    chunks = []
    for sheet_name, rows in sheets.items():
        header = rows[:3]
        body = rows[3:]
        if not body:
            text = f"Sheet: {sheet_name}\n" + "\n".join(rows)
            chunks.append({"source": f"Excel - {sheet_name}", "text": text})
            continue
        for i in range(0, len(body), rows_per_chunk):
            part = body[i:i + rows_per_chunk]
            text = (
                f"Sheet: {sheet_name}\n"
                + "\n".join(header)
                + "\n...\n"
                + "\n".join(part)
            )
            chunks.append({"source": f"Excel - {sheet_name}", "text": text})
    return chunks


def build_chunks():
    word_lines = read_word(DATA_DIR / "apple_valuation_report.docx")
    excel_lines = read_excel(DATA_DIR / "apple_financial_statements.xlsx")
    return chunk_word(word_lines) + chunk_excel(excel_lines)


if __name__ == "__main__":
    chunks = build_chunks()
    print("Total chunks:", len(chunks))
    print("Longest chunk (characters):", max(len(c["text"]) for c in chunks))
    print("--- Sample Excel chunk ---")
    sample = next(c for c in chunks if c["source"].startswith("Excel"))
    print(sample["source"])
    print(sample["text"])