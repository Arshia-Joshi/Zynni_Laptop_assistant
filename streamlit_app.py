import streamlit as st

from file_search import build_index, search_file, get_recent_files, suggest_files
from main import (
    analyze_ner,
    analyze_pos,
    clean_query,
    get_battery_status,
    get_battery_time,
    initialize_nlp,
)
from system_utils import get_system_info, open_path


st.set_page_config(
    page_title="Zynni Laptop Assistant",
    page_icon="Z",
    layout="wide",
)


st.markdown(
    """
    <style>
        .stApp {
                background:
                    radial-gradient(circle at top left, rgba(124, 58, 237, 0.10), transparent 26%),
                    radial-gradient(circle at top right, rgba(167, 139, 250, 0.09), transparent 24%),
                    linear-gradient(180deg, #faf7ff 0%, #ffffff 58%);
            color: #1f2937;
        }
        .hero {
            padding: 1.5rem 1.75rem;
                border: 1px solid rgba(109, 40, 217, 0.18);
            border-radius: 24px;
                background: rgba(255, 255, 255, 0.96);
                box-shadow: 0 18px 50px rgba(109, 40, 217, 0.08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.25rem;
            line-height: 1.1;
            color: #5b21b6;
        }
        .hero p {
            margin-top: 0.65rem;
            color: #4b5563;
            font-size: 1rem;
        }
        .panel {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            border: 1px solid rgba(109, 40, 217, 0.14);
            background: rgba(255, 255, 255, 0.97);
            box-shadow: 0 12px 30px rgba(109, 40, 217, 0.05);
            margin-bottom: 0.75rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.75rem;
        }
        .stTabs [data-baseweb="tab"] {
            color: #6b7280;
            border-radius: 999px;
            padding: 0.4rem 1rem;
            background: rgba(255, 255, 255, 0.82);
        }
        .stTabs [aria-selected="true"] {
            color: #5b21b6;
            background: rgba(124, 58, 237, 0.10);
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: rgba(255, 255, 255, 0.98);
            border-color: rgba(109, 40, 217, 0.18);
        }
        .stTextInput label,
        .stTextArea label,
        .stRadio label,
        .stSelectbox label {
            color: #4b5563;
        }
        .stButton button {
            background: linear-gradient(135deg, #7c3aed, #6d28d9);
            color: white;
            border: none;
            border-radius: 999px;
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #6d28d9, #5b21b6);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def prepare_index():
    build_index()
    return True


def render_path_list(paths, empty_message, key_prefix):
    if not paths:
        st.info(empty_message)
        return

    for index, path in enumerate(paths, 1):
        left, right = st.columns([5, 1])
        with left:
            st.markdown(f"**{index}.** {path}")
        with right:
            if st.button("Open", key=f"{key_prefix}_{index}"):
                opened, error = open_path(path)
                if opened:
                    st.success(f"Opened {path}")
                else:
                    st.error(error)


st.markdown(
    """
    <div class="hero">
        <h1>Zynni Laptop Assistant</h1>
        <p>Search local files, inspect recent items, check system status, and run NLP tools from one interface.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

prepare_index()

with st.sidebar:
    st.header("Controls")
    if st.button("Refresh file index", use_container_width=True):
        build_index()
        st.success("File index refreshed")

    st.caption("Indexed folders")
    st.write(r"C:\Users\arshi\Documents")
    st.write(r"C:\Users\arshi\Desktop")
    st.write(r"C:\Users\arshi\Downloads")


search_tab, recent_tab, system_tab, nlp_tab = st.tabs(["Search", "Recent", "System", "NLP"])

with search_tab:
    search_text = st.text_input("Search for a file", placeholder="e.g. budget pdf, project notes, resume")
    search_col_1, search_col_2 = st.columns([1, 1])
    with search_col_1:
        run_search = st.button("Find files", use_container_width=True)
    with search_col_2:
        run_clear = st.button("Clear results", use_container_width=True)

    if run_clear:
        st.session_state.pop("search_results", None)
        st.session_state.pop("search_suggestions", None)
        st.session_state.pop("search_query", None)

    if run_search:
        query = clean_query(search_text)
        if not query:
            st.warning("Please enter a search term.")
        else:
            results = search_file(query)
            suggestions = [] if results else suggest_files(query)
            st.session_state["search_query"] = query
            st.session_state["search_results"] = results
            st.session_state["search_suggestions"] = suggestions
            st.session_state["search_has_run"] = True

    if st.session_state.get("search_query"):
        st.caption(f"Query: {st.session_state['search_query']}")

    render_path_list(
        st.session_state.get("search_results", []),
        "No exact matches yet.",
        "search_results",
    )

    suggestions = st.session_state.get("search_suggestions", [])
    if suggestions:
        st.subheader("Suggestions")
        render_path_list(suggestions, "No suggestions available.", "search_suggestions")
    elif st.session_state.get("search_has_run"):
        st.info("No similar files were found.")

with recent_tab:
    recent_files = get_recent_files()
    render_path_list(recent_files, "No recent files were found in the indexed folders.", "recent_files")

with system_tab:
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("System info")
        st.text(get_system_info())

    with right_col:
        st.subheader("Battery")
        st.write(get_battery_status())
        st.write(get_battery_time())

with nlp_tab:
    task = st.radio("Task", ["POS tagging", "Named entity recognition"], horizontal=True)
    sentence = st.text_area("Sentence", placeholder="Type a sentence to analyze")
    analyze_button = st.button("Analyze text", use_container_width=True)

    if analyze_button:
        ready, error = initialize_nlp()
        if not ready:
            st.error(error)
        elif not sentence.strip():
            st.warning("Please enter a non-empty sentence.")
        elif task == "POS tagging":
            tags = analyze_pos(sentence)
            st.subheader("POS tags")
            st.table([[token, tag] for token, tag in tags])
        else:
            entities = analyze_ner(sentence)
            st.subheader("Named entities")
            if entities:
                st.table([[entity, label] for entity, label in entities])
            else:
                st.info("No named entities found.")