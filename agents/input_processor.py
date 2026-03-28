class InputProcessorAgent:
    def run(self, state):
        state.cleaned_input = state.raw_input.strip()
        return state
