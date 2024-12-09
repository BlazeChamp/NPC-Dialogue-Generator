import warnings
from dialogueEngine import NPCDialogueGenerator


# Example usage
if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    npc = NPCDialogueGenerator(npc_name="Elara", personality="a wise and kind sorceress from Skyrim.", use_local_model=True)
    
    print(f"{npc.npc_name}: Greetings. Ask your questions or share your opinions.")

    while True:
        player_input = input("You: ")
        if player_input.lower() in ["exit", "quit", "goodbye", "farewell", "later", "adios"]:
            print (f"{npc.npc_name}: Farewell, traveler.")
            break

        if "my name is" in player_input.lower():
            user_name = player_input.split("is")[-1].strip()
            npc.update_memory("facts", {"Your name": user_name})
            print("Elara: Ah, I see. I will remember your name.")
            continue

        elif "I like" in player_input.lower():
            user_preference = player_input.split("I like")[-1].strip()
            npc.update_memory("user_preferences", {user_preference: "liked"})
            print("Elara: Interesting, I will keep that in mind.")
            continue

        elif "remember" in player_input.lower():
            memory_content = npc.retrieve_memory("facts")
            if memory_content:
                print(f"Elara: I recall this: {memory_content}")
            else:
                print("Elara: I'm afraid I don't recall anything specific yet.")
            continue
        npc_response = npc.get_response(player_input)
        print(f"{npc.npc_name}: {npc_response}")



