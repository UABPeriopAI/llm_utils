import logging
import types
from pathlib import Path
from typing import Any, List, Optional, Tuple

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


class _ContainerProxy(types.SimpleNamespace):
    """
    Very thin façade that passes every attribute access straight through
    to the wrapped Streamlit container (st, st.sidebar, st.container …).

    Example
    -------
    sb = _ContainerProxy(st.sidebar)
    sb.checkbox(...)   # == st.sidebar.checkbox(...)
    sb.columns(2)      # == st.sidebar.columns(2)
    """

    def __init__(self, container):
        super().__init__()
        object.__setattr__(self, "_c", container)

    def __getattr__(self, name):
        return getattr(self._c, name)

    def __setattr__(self, name, value):
        setattr(self._c, name, value)


class StreamlitUIHelper:
    """
    A thin wrapper around Streamlit calls so the core logic isn’t tied directly to st.xxx calls.
    """

    def __init__(self):
        self.session_state = st.session_state
        self.sidebar = _ContainerProxy(st.sidebar)

    def _target(self, sidebar: bool = False):
        return st.sidebar if sidebar else st

    def hide_streamlit_branding(self):
        hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    def apply_uab_font(self):
        streamlit_style = """
                <style>
                html, body, [class*="css"]  {
                font-family: proxima-nova, sans-serif;
                }
                </style>
                """
        st.markdown(streamlit_style, unsafe_allow_html=True)

    @staticmethod
    def setup_page(page_title: str, page_icon: str = "🤖", hide_branding: bool = True):
        """
        Setup Streamlit page configuration.

        Args:
            page_title: Title for the page
            page_icon: Icon for the page
            hide_branding: Whether to hide Streamlit branding
        """
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            # layout="wide",
            initial_sidebar_state="collapsed",
        )

        if hide_branding:
            try:
                from aiweb_common.streamlit.streamlit_common import (
                    hide_streamlit_branding,
                )

                hide_streamlit_branding()
            except ImportError:
                logger.warning("Could not import hide_streamlit_branding")

    @staticmethod
    def file_uploader_with_info(
        label: str, file_types: List[str] = ["xlsx", "csv"], help_text: Optional[str] = None
    ) -> Tuple[Any, Optional[str]]:
        """
        Create file uploader with file type detection.

        Args:
            label: Label for the uploader
            file_types: Allowed file types
            help_text: Help text for the uploader

        Returns:
            Tuple of (uploaded_file, file_extension)
        """
        uploaded_file = st.file_uploader(label, type=file_types, help=help_text)

        if uploaded_file is not None:
            extension = Path(uploaded_file.name).suffix.lower()
            return uploaded_file, extension

        return None, None

    def select_columns(
        self,
        data: pd.DataFrame,
        select_type: str = "features",
        default_columns: list[str] | None = None,
        exclude_column: str | None = None,
        key: str | None = None,
        help_text: str = "Select one or more columns.",
    ) -> list[str]:
        """
        Show a multi-select widget that lets the user choose columns from the
        provided DataFrame.

        Parameters
        ----------
        data : pd.DataFrame
            The DataFrame whose column names will be offered.
        select_type : str, default `"features"`
            Appears in the widget label – e.g. “Select the *feature* columns”.
        default_columns : list[str] | None
            Columns that should be pre-selected if present in *data*.
        exclude_column : str | None
            Single column that must **not** appear in the options list
            (useful for excluding the chosen target variable).
        key : str | None
            Optional Streamlit widget key.
        help_text : str
            Tooltip shown when the user hovers over the widget.

        Returns
        -------
        list[str]
            The list of selected column names (may be empty).
        """
        options = [c for c in data.columns if c != exclude_column]
        defaults = [c for c in (default_columns or []) if c in options]

        return self.multiselect(
            f"3️⃣ Select the {select_type} columns to include",
            options=options,
            default=defaults,
            key=key,
            help=help_text,
        )

    def balloons(self):
        st.balloons()

    def button(self, label, key=None, sidebar: bool = False, **kwargs):
        kwargs.pop("sidebar", None)  # remove the sidebar marker
        return self._target(sidebar).button(label, key=key, **kwargs)

    def checkbox(self, label, help, key=None, **kwargs):
        return st.checkbox(label=label, help=help, key=key, **kwargs)

    def columns(self, spec, **kwargs):
        return st.columns(spec, **kwargs)

    def dataframe(self, data, **kwargs):
        return st.dataframe(data=data, **kwargs)

    def download_button(self, label, data, file_name, mime, **kwargs):
        return st.download_button(label, data, file_name, mime, **kwargs)

    def error(self, text, **kwargs):
        st.error(text, **kwargs)

    def expander(self, label, expanded=True, **kwargs):
        return st.expander(label, expanded=expanded, **kwargs)

    def file_uploader(self, label, type, key, **kwargs):
        return st.file_uploader(label, type=type, key=key, **kwargs)

    def header(self, text, **kwargs):
        return st.header(text, **kwargs)

    def info(self, text, **kwargs):
        st.info(text, **kwargs)

    def markdown(self, text, **kwargs):
        st.markdown(text, **kwargs)

    def metric(self, label, value, **kwargs):
        return st.metric(label, value, **kwargs)

    def multiselect(self, label, options, **kwargs):
        return st.multiselect(label, options, **kwargs)

    def number_input(self, label, **kwargs):
        return st.number_input(label, **kwargs)

    def pyplot(self, figure, **kwargs):
        st.pyplot(figure, **kwargs)

    def radio(self, label, options, **kwargs):
        return st.radio(label, options, **kwargs)

    def rerun(self):
        st.rerun(scope="app")

    def selectbox(self, label, options, **kwargs):
        return st.selectbox(label, options, **kwargs)

    def slider(self, label, min_value, max_value, value, step, key, **kwargs):
        return st.slider(label, min_value, max_value, value, step, key, **kwargs)

    def spinner(self, text, **kwargs):
        return st.spinner(text, **kwargs)

    def stop(self):
        st.stop()

    def subheader(self, text, **kwargs):
        return st.subheader(text, **kwargs)

    def success(self, text, **kwargs):
        st.success(text, **kwargs)

    def tabs(self, tabs, **kwargs):
        return st.tabs(tabs, **kwargs)

    def text(self, body, **kwargs):
        st.text(body, **kwargs)

    def text_input(self, label, value="", key=None, **kwargs):
        return st.text_input(label, value=value, key=key, **kwargs)

    def title(self, label, **kwargs):
        st.title(label, **kwargs)

    def warning(self, text, **kwargs):
        st.warning(text, icon="🚨", **kwargs)

    def write(self, *args, **kwargs):
        """
        Proxy for ``st.write`` that accepts any number of positional
        arguments, mirroring the behaviour of the original Streamlit
        function.

        Nothing else in existing code changes, so this modification is
        completely backwards-compatible.
        """
        import streamlit as st

        return st.write(*args, **kwargs)
