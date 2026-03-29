class InputProcessorAgent:
    def run(self, state: dict):
        # Use .get() to prevent crashes if raw_input is missing
        raw = state.get("raw_input", "")

        # Update the dictionary
        state["cleaned_input"] = raw.strip()

        print("--- Input Processed and Cleaned ---")
        return state  # LangGraph needs this return to update the global state
