import psutil
from file_search import build_index, search_file, get_recent_files, suggest_files
from system_utils import get_system_info, open_path

try:
    import nltk
    from nltk import ne_chunk, pos_tag, word_tokenize
    NLTK_AVAILABLE = True
except Exception:
    nltk = None
    NLTK_AVAILABLE = False


NLP_READY = False
NLP_ERROR = ""


def initialize_nlp():
    global NLP_READY, NLP_ERROR

    if NLP_READY:
        return True, ""

    if not NLTK_AVAILABLE:
        NLP_ERROR = "NLTK is not installed. Install it using: pip install nltk"
        return False, NLP_ERROR

    packages = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "maxent_ne_chunker",
        "maxent_ne_chunker_tab",
        "words",
    ]

    try:
        for package in packages:
            nltk.download(package, quiet=True)

        # Quick validation that tokenizer, POS tagger, and chunker are ready.
        tokens = word_tokenize("NLP check")
        tagged = pos_tag(tokens)
        ne_chunk(tagged)

        NLP_READY = True
        NLP_ERROR = ""
        return True, ""
    except Exception as e:
        NLP_ERROR = f"Could not initialize NLP resources: {e}"
        return False, NLP_ERROR


def extract_analysis_text(user_input, triggers):
    lowered = user_input.lower()
    for trigger in triggers:
        index = lowered.find(trigger)
        if index != -1:
            extracted = user_input[index + len(trigger):].strip(" :")
            if extracted:
                return extracted
    return ""


def analyze_pos(text):
    tokens = word_tokenize(text)
    return pos_tag(tokens)


def analyze_ner(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    chunk_tree = ne_chunk(tagged)

    entities = []
    for chunk in chunk_tree:
        if hasattr(chunk, "label"):
            entity_text = " ".join(token for token, _ in chunk)
            entities.append((entity_text, chunk.label()))

    return entities


# -------------------------------
# Intent Detection
# -------------------------------
def get_intent(text):
    text = text.lower()

    if "pos tag" in text or "part of speech" in text or text.startswith("pos "):
        return "POS_TAG"

    elif "named entity" in text or " ner " in f" {text} " or text.startswith("ner "):
        return "NER"

    if "open" in text:
        return "OPEN_FILE"

    elif "find" in text or "where" in text or "search" in text:
        return "SEARCH_FILE"

    elif "recent" in text:
        return "RECENT_FILES"

    # 🔋 Battery TIME (must come before battery)
    elif "how long" in text or "time left" in text:
        return "BATTERY_TIME"

    elif "last charged" in text or "when charged" in text:
        return "BATTERY_HISTORY"

    elif "battery" in text or "charg" in text:
        return "BATTERY"

    elif "system" in text or "config" in text:
        return "SYSTEM_INFO"

    elif text.strip() == "exit":
        return "EXIT"

    else:
        return "SEARCH_FILE"


# -------------------------------
# Clean Query
# -------------------------------
def clean_query(text):
    stopwords = {
        "find", "open", "search", "where", "is", "my", "file",
        "all", "files", "the", "a", "an", "show", "me", "please",
        "can", "you", "i", "need", "want"
    }

    words = text.lower().split()
    filtered = [w for w in words if w not in stopwords and len(w) > 2]

    return " ".join(filtered)


# -------------------------------
# Battery Helpers
# -------------------------------
def get_battery_status():
    battery = psutil.sensors_battery()

    if battery is None:
        return "Battery info not available."

    status = "charging" if battery.power_plugged else "not charging"
    return f"{battery.percent}% | {status}"


def get_battery_time():
    battery = psutil.sensors_battery()

    if battery is None:
        return "Battery info not available."

    if battery.power_plugged:
        return "Laptop is charging, so battery will not drain right now."

    if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
        return "Unable to estimate battery time."

    mins = battery.secsleft // 60
    hours = mins // 60
    minutes = mins % 60

    return f"Estimated battery time left: {hours}h {minutes}m"


# -------------------------------
# Main Assistant
# -------------------------------
def main():
    print("Zynni: Starting up...")
    print("Zynni: Indexing your files, please wait...\n")

    build_index()

    print("Zynni: Ready! You can now ask me things 😄")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        intent = get_intent(user_input)

        # EXIT
        if intent == "EXIT":
            print("Zynni: Goodbye!")
            break

        # -------------------------------
        # SEARCH FILE (with suggestions)
        # -------------------------------
        elif intent == "SEARCH_FILE":
            query = clean_query(user_input)

            if not query:
                print("Zynni: Please specify what to search.\n")
                continue

            results = search_file(query)

            if results:
                print("\nZynni: I found these matching files:")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r}")

                print("\nTip: You can type 'open <name>' to open the file.\n")

            else:
                print("Zynni: No exact match found.")

                suggestions = suggest_files(query)

                if suggestions:
                    print("Zynni: Did you mean:")
                    for s in suggestions:
                        print("-", s)
                    print()
                else:
                    print("Zynni: No similar files found.\n")

        # -------------------------------
        # OPEN FILE
        # -------------------------------
        elif intent == "OPEN_FILE":
            query = clean_query(user_input)

            if not query:
                print("Zynni: Please specify a file to open.\n")
                continue

            results = search_file(query)

            if results:
                try:
                    opened, error = open_path(results[0])
                    if opened:
                        print(f"Zynni: Opening → {results[0]}\n")
                    else:
                        print("Zynni: Error opening file:", error, "\n")
                except Exception as e:
                    print("Zynni: Error opening file:", e, "\n")
            else:
                print("Zynni: File not found.\n")

        # -------------------------------
        # RECENT FILES
        # -------------------------------
        elif intent == "RECENT_FILES":
            results = get_recent_files()

            if results:
                print("\nZynni: Here are your most recent files:")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r}")
                print()
            else:
                print("Zynni: No recent files found.\n")

        # -------------------------------
        # BATTERY STATUS
        # -------------------------------
        elif intent == "BATTERY":
            print("Zynni:", get_battery_status(), "\n")

        # -------------------------------
        # BATTERY TIME
        # -------------------------------
        elif intent == "BATTERY_TIME":
            print("Zynni:", get_battery_time(), "\n")

        # -------------------------------
        # BATTERY HISTORY
        # -------------------------------
        elif intent == "BATTERY_HISTORY":
            print("Zynni: I currently provide real-time battery info.")
            print("Tracking last charge time requires background logging (future upgrade).\n")

        # -------------------------------
        # POS TAGGING
        # -------------------------------
        elif intent == "POS_TAG":
            ready, error = initialize_nlp()
            if not ready:
                print(f"Zynni: {error}\n")
                continue

            sentence = extract_analysis_text(
                user_input,
                ["pos tag", "part of speech", "pos", "tag"],
            )

            if not sentence:
                sentence = input("Zynni: Enter a sentence for POS tagging: ").strip()

            if not sentence:
                print("Zynni: Please provide a non-empty sentence.\n")
                continue

            tags = analyze_pos(sentence)
            print("\nZynni: POS tags:")
            for token, tag in tags:
                print(f"{token} -> {tag}")
            print()

        # -------------------------------
        # NAMED ENTITY RECOGNITION
        # -------------------------------
        elif intent == "NER":
            ready, error = initialize_nlp()
            if not ready:
                print(f"Zynni: {error}\n")
                continue

            sentence = extract_analysis_text(
                user_input,
                ["named entity", "ner", "entities in", "extract entities"],
            )

            if not sentence:
                sentence = input("Zynni: Enter a sentence for NER: ").strip()

            if not sentence:
                print("Zynni: Please provide a non-empty sentence.\n")
                continue

            entities = analyze_ner(sentence)
            if entities:
                print("\nZynni: Named entities found:")
                for entity_text, label in entities:
                    print(f"{entity_text} -> {label}")
                print()
            else:
                print("Zynni: No named entities found in that sentence.\n")

        # -------------------------------
        # SYSTEM INFO
        # -------------------------------
        elif intent == "SYSTEM_INFO":
            print("Zynni:", get_system_info(), "\n")


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()