from results import BuildTableSuccess, BuildTableChunksSuccess


def _determine_col_width(headers, rows):
    all_rows = (headers,) + rows
    columns = list(zip(*all_rows))
    return [max(len(str(item)) for item in column) for column in columns]

class BuildTableUseCase:
    def build_ascii_table(self, headers, rows, default_col_width=None):
        col_width = _determine_col_width(headers, rows) if default_col_width is None else default_col_width

        all_rows = (headers,) + rows
        lines = []
        for row in all_rows:
            padded_row = [
                str(item).ljust(col_width[i]) for i, item in enumerate(row)
            ]
            lines.append("| " + " | ".join(padded_row) + " |")

        border = "+-" + "-+-".join("-" * width for width in col_width) + "-+"

        # Add border above and below:
        table = [border] + [lines[0], border] + lines[1:] + [border]

        return BuildTableSuccess(table="\n".join(table))

    def build_ascii_table_chunks(self, headers, rows, max_rows=None):
        if max_rows is None:
            return BuildTableChunksSuccess(table_chunks=[self.build_ascii_table(headers, rows)])

        else:
            # Determine col_width once for longest value in whole table, this makes the chunks a consistent width:
            col_width = _determine_col_width(headers, rows)

            table_chunks = []
            for i in range(0, len(rows), max_rows):
                chunk = rows[i:i + max_rows]
                build_table_result = self.build_ascii_table(headers, chunk, col_width)
                table_chunks.append(build_table_result.table)

            return BuildTableChunksSuccess(table_chunks=table_chunks)