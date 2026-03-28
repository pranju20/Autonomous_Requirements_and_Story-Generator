class HumanApprovalAgent:
    def run(self, state):
        print("\n=== REQUIREMENTS ===")
        for r in state.requirements:
            print(r)

        approval = input("Approve? (yes/no): ")

        if approval.lower() != "yes":
            raise Exception("Approval Denied")

        state.approved = True
        return state
