# NPC-Dialogue-Generator
Generates dialogue for a customizable NPC from any game.

The user inputs dialogue of their choosing and the NPC responds to their inputs. 

This runs in a terminal setting. 

This code was written in Python 3.11.

It requires modules imported from tranformers, json, warnings, and openai.


There is a function called "generate_ai_response" which uses an openai model to generate responses. However, an api key is required to use ths function. The function is disbaled by default be can be turned on by setting use_local_model=False when initializing the NPCGeneratorDialogue class in main.py. However the program may not work as intended. 

"generate_local_response" is the main dialogue generator where most of dialogue comes from. It is here that the npc creates responses to the player's input. It sets a max token value to limit the AI from rambling, and it uses temperature and top_p variables to control variability in the responses. There is also a penalty variable to avoid the AI repeating it's dialogues. It is also in this function where the AI is given prompts to learn its role in the dialogue. It is in these prompts, the AI is given the conversation log. 

At the beginning of the NPCDialogueGenerator: multiple variables are initialized and the model used for the program is set. The current model is lodrick-the-lafted/Hermes-Instruct-7B-217K, from Huggingface.co

"save_memory", "load_memory", "update_memory", "retrieve_memory" are functions to save memory into data/memory.json for continuation in later sessions. This is experimental and still in develpment. 

The NPC is set to "Elara, a wise and kind sorceress from Skyrim" by default. These can be changed to a preffered name or personality of the user's choosing. This can be done by modifying the main.py file where the NPCGeneratorDialogue class is initialized. 

As coversations continue, the AI gets a better idea of how to conversate as it keeps a running log of the conversation.  

This program was run in Visual Studio 2022 with python in a single solution
