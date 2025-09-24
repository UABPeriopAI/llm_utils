"""
Light-weight, object-oriented helper that collects artifacts
(DataFrames, matplotlib figures, bytes, existing files …),
writes them to a temporary directory and finally zips everything
into a BytesIO object for easy download (e.g. from Streamlit).

Usage
-----
from CreditScore.report_builder import ReportBuilder

with ReportBuilder() as rb:
    rb.add_dataframe(coef_df,     "coefficients.csv")
    rb.add_dataframe(power_df,    "power_analysis.csv")
    rb.add_figure(fig,            "power_curve.png")
    rb.add_file("some/path/note.txt")         # existing file
    rb.add_bytes(pdf_bytes,       "report.pdf")

zip_bytes = rb.build_zip()  # ready for st.download_button
"""

import tempfile
import zipfile
from contextlib import AbstractContextManager
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from aiweb_common.file_operations.docx_creator import StreamlitDocxCreator


class SafeStreamlitDocxCreator(StreamlitDocxCreator):
    def __init__(self, summary, results, figures):
        super().__init__(summary, results, figures)
        self.summary = summary  # manually assign the third value
        self.results = results  # reassign to guard against reassignment
        self.figures = figures


def compile_report_bytes(summary: str, results: dict, figures: dict):
    # ------------------------------------------------------------------ #
    # 💡  VERBOSE DEBUGGING  
    # ------------------------------------------------------------------ #
    import textwrap, pandas as pd, numbers

    def _describe(obj, indent=0):
        pad = " " * indent
        if isinstance(obj, pd.DataFrame):
            print(f"{pad}↳ DataFrame shape={obj.shape}")
        elif isinstance(obj, pd.Series):
            print(f"{pad}↳ Series   len={len(obj)}  name={obj.name!r}")
        elif isinstance(obj, (list, tuple)):
            print(f"{pad}↳ {type(obj).__name__}  len={len(obj)}")
        elif isinstance(obj, dict):
            print(f"{pad}↳ dict keys={list(obj.keys())}")
        elif isinstance(obj, (str, bytes, numbers.Number)):
            preview = textwrap.shorten(str(obj), width=60, placeholder=" …")
            print(f"{pad}↳ {type(obj).__name__}  value={preview!r}")
        else:
            print(f"{pad}↳ {type(obj)}")

    print("\n" + "=" * 60 + "\nDEBUG :: compile_report_bytes\n" + "=" * 60)

    print("• summary :", end=" ")
    _describe(summary)

    print("• results :", end=" ")
    _describe(results)
    if isinstance(results, dict):
        for meth, sections in results.items():
            print(f"  └─ method {meth!r} :", end=" ")
            _describe(sections, indent=4)
            if isinstance(sections, dict):
                for sec, data in sections.items():
                    print(f"      └─ section {sec!r} :", end=" ")
                    _describe(data, indent=8)

    print("• figures :", end=" ")
    _describe(figures)
    if isinstance(figures, dict):
        for name, fig in figures.items():
            print(f"  └─ figure {name!r} :", end=" ")
            _describe(fig, indent=4)

    print("=" * 60 + "\n")

    creator = SafeStreamlitDocxCreator(summary, results, figures)
    doc = creator.create_docx_report()
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    return docx_buffer


class ReportBuilder(AbstractContextManager):
    """Collect artifacts → produce in-memory ZIP."""

    _FIG_EXTS = {"png", "jpg", "jpeg", "svg", "gif", "tif", "tiff", "bmp", "webp"}
    _CSV_EXTS = {"csv"}  # easy to extend later

    def __init__(self, tmp_prefix: str = "report_", auto_cleanup: bool = True):
        self._tmpdir_ctx = tempfile.TemporaryDirectory(prefix=tmp_prefix)
        self.tmp_path = Path(self._tmpdir_ctx.name)  # Real Path
        self.auto_cleanup = auto_cleanup
        self._closed = False

    # ------------------------------------------------------------------ helpers
    def _check_closed(self):
        if self._closed:
            raise RuntimeError("ReportBuilder is already closed.")

    def _add_readme(self):
        """Copy config/Report_README.md into temp dir root if present."""
        readme_path = Path("config/Report_README.md")
        if readme_path.exists():
            dest = self.tmp_path / "Report_README.md"
            dest.write_bytes(readme_path.read_bytes())

    def _safe_path(self, filename: str) -> Path:
        """
        Decide where a file should live (figures/, data/, or root) and return a
        full path *inside* the temp directory.  The needed sub-folders are
        created on the fly.
        """
        name = Path(filename).name  # strip any upstream path
        ext = name.split(".")[-1].lower()

        if ext in self._CSV_EXTS:
            subdir = "data"
        elif ext in self._FIG_EXTS:
            subdir = "figures"
        else:
            subdir = ""  # everything else in root

        target = self.tmp_path / subdir / name if subdir else self.tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    # ------------------------------------------------------------------ adders
    def add_dataframe(self, df: pd.DataFrame, filename: str):
        """Save DataFrame as CSV inside the bundle."""
        self._check_closed()
        df.to_csv(self._safe_path(filename), index=False, float_format="%.4f")

    def add_figure(self, fig, filename: str, dpi: int = 300):
        print("adding (only matplotlib, for now) figure to report")
        """Save figure for matplotlib, altair, or plotly."""
        self._check_closed()
        path = self._safe_path(filename)
        # This only works for Matplotlib
        # TODO add more checks and additional functionality.
        try:
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
        except:
            raise TypeError(f"Unsupported figure type: {type(fig)}")

    def add_bytes(self, data: Union[bytes, BytesIO], filename: str):
        self._check_closed()
        with open(self._safe_path(filename), "wb") as f:
            if isinstance(data, BytesIO):  # already a stream
                print("adding BytesIO stream to report")
                data.seek(0)
                f.write(data.read())
            elif isinstance(data, bytes):  # raw bytes
                print("adding bytes to report")
                f.write(data)
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")

    def add_file(self, file_path: Union[str, Path], filename: Optional[str] = None):
        """Copy an existing file into the bundle."""
        self._check_closed()
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(src)
        dest_name = filename or src.name
        dest = self._safe_path(dest_name)
        dest.write_bytes(src.read_bytes())

    # ------------------------------------------------------------------ build
    def build_zip(self, zip_name: str = "report.zip") -> BytesIO:
        """Create an in-memory ZIP and return it as BytesIO."""
        self._check_closed()
        self._add_readme()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in self.tmp_path.rglob("*"):
                if file.is_file():
                    # keep relative path so folders appear in the archive
                    zf.write(file, arcname=file.relative_to(self.tmp_path))
        zip_buffer.seek(0)
        return zip_buffer

    # ------------------------------------------------------------------ context
    def close(self):
        if not self._closed and self.auto_cleanup:
            self._tmpdir_ctx.cleanup()
        self._closed = True

    def __exit__(self, exc_type, exc, tb):
        self.close()
        # propagate exception (if any)
        return False
