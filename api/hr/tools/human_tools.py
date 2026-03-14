from crewai.tools import tool

@tool("AskHiringManager")
def ask_hiring_manager(candidate_name: str, score: int, justification: str):
    """Asks the hiring manager if the candidate is Selected or Not Selected. If Selected, asks for CTC."""
    print(f"\n--- HIRING MANAGER REVIEW ---\nCandidate: {candidate_name}\nScore: {score}\nJustification: {justification}\n")
    
    # In a real deployment, this would be an API call or a callback.
    # For this CLI implementation, we use input().
    decision = input("Is the candidate SELECTED? (yes/no): ").strip().lower()
    
    if decision == 'yes':
        ctc = input("Enter CTC offered (e.g. 50 LPA): ").strip()
        return f"Selected|{ctc}"
    else:
        return "Not Selected"
