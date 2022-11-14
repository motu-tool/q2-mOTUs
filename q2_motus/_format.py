from qiime2.plugin import model, ValidationError, TextFileFormat


class MotusMergedAbundanceFormat(TextFileFormat):
    def _equal_number_of_columns(self, n_lines):
        call_params = {}
        with self.open() as fh:
            header_line = fh.readline()
            param_line = header_line.split("#")[-1]
            name, info = param_line.split()[0], param_line
            call_params[name] = info
            while header_line.startswith('# '):
                header_line = fh.readline()
                param_line = header_line.split("#")[-1]
                name, info = param_line.split()[0], param_line
                call_params[name] = info
            if not "merge" in call_params["call:"]:
                raise ValidationError("This is not a merged abundance file. Please, merge abundance files first.")
            n_header_fields = len(header_line.split('\t'))
            if n_header_fields < 3:
                raise ValidationError(
                    'No sample columns appear to be present.')
            for idx, line in enumerate(fh, 2):
                if n_lines is not None and idx > n_lines + 1:
                    break
                fields = line.strip().split('\t')
                n_fields = len(fields)
                if n_fields != n_header_fields:
                    raise ValidationError(
                        f'Number of columns on line {line} is inconsistent with '
                        'the header line.')
                for value in fields[2:]:
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValidationError(
                            f'Values in table must be int-able. Found: {value}'
                        )

    def _validate_(self, level):
        level_to_n_lines = {'min': 5, 'max': None}
        self._equal_number_of_columns(level_to_n_lines[level])

MotusMergedAbundanceDirectoryFormat = model.SingleFileDirectoryFormat(
    'MotusMergedAbundanceDirectoryFormat', 'table.tsv',
    MotusMergedAbundanceFormat)

