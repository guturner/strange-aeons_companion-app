def _determine_col_widths(headers, rows):
    all_rows = (headers,) + rows
    columns = list(zip(*all_rows))
    return [max(len(str(item)) for item in column) for column in columns]

class BuildTableUseCase:
    def build_ascii_table(self, headers, rows, default_col_widths=None):
        """
        Builds an ascii table from the given headers and rows.

        :param headers: A tuple of header names: ("Header 1", "Header 2", "Header 3", etc.)
        :param rows: A nested tuple of row data: (("Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"), ("Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"))
        :param default_col_widths: An array of default column widths for each column: [20, 40, 20]
        :return:
        """
        col_width = _determine_col_widths(headers, rows) if default_col_widths is None else default_col_widths

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

        return "\n".join(table)

    def build_ascii_tables(self, headers, rows, max_rows=None):
        """
        Builds multiple ascii tables from the given headers and rows.
        This is typically used to account for the max message size limit.

        :param headers: A tuple of header names: ("Header 1", "Header 2", "Header 3", etc.)
        :param rows: A nested tuple of row data: (("Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"), ("Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"))
        :param max_rows: An integer for limiting the size of a table.
        :return:
        """
        if max_rows is None:
            return [self.build_ascii_table(headers, rows)]

        else:
            # Determine col_width once for longest value in whole table, this makes the chunks a consistent width:
            col_width = _determine_col_widths(headers, rows)

            tables = []
            for i in range(0, len(rows), max_rows):
                chunk = rows[i:i + max_rows]
                table = self.build_ascii_table(headers, chunk, col_width)
                tables.append(table)

            return tables