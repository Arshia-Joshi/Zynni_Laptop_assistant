import os
from difflib import get_close_matches

INDEX_PATHS = [
    "C:\\Users\\arshi\\Documents",
    "C:\\Users\\arshi\\Desktop",
    "C:\\Users\\arshi\\Downloads"
]

file_index = []


def _detect_extension_filters(query_words):
    filters = set()

    for word in query_words:
        token = word.strip().lower()

        if token in {"pdf", ".pdf"}:
            filters.add(".pdf")
        elif token in {"csv", ".csv"}:
            filters.add(".csv")
        elif token in {"excel", "xls", ".xls", "xlsx", ".xlsx"}:
            filters.update({".xls", ".xlsx", ".xlsm", ".xlsb"})
        elif token in {"word", "doc", ".doc", "docx", ".docx"}:
            filters.update({".doc", ".docx", ".docm"})
        elif token in {"powerpoint", "ppt", ".ppt", "pptx", ".pptx", "slides", "presentation"}:
            filters.update({".ppt", ".pptx", ".pptm"})

    return filters


def _is_type_token(word):
    return word in {
        "pdf", ".pdf",
        "csv", ".csv",
        "excel", "xls", ".xls", "xlsx", ".xlsx",
        "word", "doc", ".doc", "docx", ".docx",
        "powerpoint", "ppt", ".ppt", "pptx", ".pptx", "slides", "presentation",
        "file", "files",
    }

def build_index():
    global file_index
    for path in INDEX_PATHS:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                file_index.append((file.lower(), full_path))
                #print(f"Scanning folder: {path}")
                #print(f"Total files indexed: {len(file_index)}")


def search_file(query):
    query_words = query.lower().split()
    results = []
    extension_filters = _detect_extension_filters(query_words)
    content_words = [word for word in query_words if not _is_type_token(word)]

    for name, path in file_index:
        name_lower = name.lower()

        if extension_filters and not any(name_lower.endswith(ext) for ext in extension_filters):
            continue
        
        # match if ALL words are present in filename
        if all(word in name_lower for word in content_words):
            results.append(path)

    return results[:200]


def get_recent_files(n=5):
    files = []

    for name, path in file_index:
        try:
            modified_time = os.path.getmtime(path)
            files.append((modified_time, path))
        except:
            continue  # skip inaccessible files

    # sort by most recent
    files.sort(reverse=True)

    return [f[1] for f in files[:n]]

def suggest_files(query, n=3):
    names = [name for name, _ in file_index]

    matches = get_close_matches(query, names, n=n, cutoff=0.5)

    # return full paths of matched names
    results = []
    for match in matches:
        for name, path in file_index:
            if name == match:
                results.append(path)
                break

    return results