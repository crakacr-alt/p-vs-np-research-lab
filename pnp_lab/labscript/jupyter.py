from .runtime import LabRuntime


def load_ipython_extension(ipython):
    """Registers %lab and %%lab. Runtime state persists between notebook cells."""

    runtime = LabRuntime(output=_IPythonWriter())

    def lab_magic(line, cell=None):
        source = cell if cell is not None else line
        runtime.execute(source, filename="<jupyter-cell>")
        return None

    ipython.register_magic_function(lab_magic, "line_cell", "lab")


class _IPythonWriter:
    def write(self, text):
        if text:
            print(text, end="")

    def flush(self):
        return None
