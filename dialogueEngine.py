import openai
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

class NPCDialogueGenerator:
    def __init__(self, npc_name, personality, use_local_model=True):
        self.npc_name = npc_name
        self.personality = personality
        self.dialogue_history = []
        self.use_local_model = use_local_model 
        self.long_term_memory = {"user_preferences": {}, "facts": {}, "previous_topics": []}
        self.load_memory()


        if self.use_local_model:
            modelName = "lodrick-the-lafted/Hermes-Instruct-7B-217K"
            self.local_tokenizer = AutoTokenizer.from_pretrained(modelName)
            self.local_model = AutoModelForCausalLM.from_pretrained(modelName)

    def save_memory(self, file_path="data/memory.json"):
        with open(file_path, "w") as file:
            json.dump(self.long_term_memory, file)

    def load_memory(self, file_path="data/memory.json"):
        try:
            with open(file_path, "r") as file:
                self.long_term_memory = json.load(file)
        except FileNotFoundError:
            self.long_term_memory = {"user_preferences": {}, "facts": {}, "previous_topics": []}

    def update_memory(self, key, value):
        if key in self.long_term_memory:
            if isinstance(self.long_term_memory[key], list):
                self.long_term_memory[key].append(value)
            elif isinstance(self.long_term_memory[key], dict):
                self.long_term_memory[key].update(value)
        else:
            self.long_term_memory[key] = value
        self.save_memory()

    def retrieve_memory(self, key):
        return self.long_term_memory.get(key, None)

    def load_predefined_dialogue(self, file_path):
        """Load predefined dialogues from a JSON file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def generate_local_response(self, player_input):
        relevant_memory = self.retrieve_memory("facts")
        memory_context = ""
        if relevant_memory:
            memory_context = "\n".join([f"{k}: {v}" for k, v in relevant_memory.items()])
        
        try:
            if self.local_tokenizer.pad_token is None:
                self.local_tokenizer.pad_token = self.local_tokenizer.eos_token
            
            if not hasattr(self, "cached_tokenizer_config"):
                self.cached_tokenizer_config = self.local_tokenizer.pad_token or self.local_tokenizer.eos_token
            self.local_tokenizer.pad_token = self.cached_tokenizer_config
            
            trimmed_history = self.dialogue_history[-5:]

            conversation_history = "\n".join([
            f"Player: {turn['content']}" if turn["role"] == "user" else f"{self.npc_name}: {turn['content']}"
            for turn in trimmed_history
        ])

            conversation_history = ""
            for turn in trimmed_history:
                if turn["role"] == "user":
                    conversation_history += f"Player: {turn['content']}\n"
                elif turn["role"] == "assistant":
                    conversation_history += f"{self.npc_name}: {turn['content']}\n"

            prompt = (
                f"{self.npc_name} is {self.personality} She is grounded and avoids discussing any other games,"
                f"or irrelevant topics. Her responses are never unfinshed, concise, relevant to the player's questions, and she never repeats or includes the player's dialogue in her response.\n"
                f"She never includes narrative descriptions like '(player asks)' or anything similar in her answers."
                f"{memory_context}\n"
                f"Conversation:\n"
                f"{conversation_history}"
                f"Player: {player_input}\n"
                f"{self.npc_name}:"
            )

            bad_words = ["Player:", "(player", "(asks", "(says", "(replies", "player"]
            bad_words_ids = self.local_tokenizer(bad_words, add_special_tokens=False)["input_ids"]

            inputs = self.local_tokenizer(
                prompt, 
                return_tensors='pt', 
                padding=True,
                truncation=True,
                max_length=1024,
            )
            outputs = self.local_model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=60,
                num_return_sequences=1,
                temperature=0.1,
                top_p=0.9,
                repetition_penalty=1.7,
                pad_token_id=self.local_tokenizer.eos_token_id,
                do_sample=True,
                bad_words_ids=bad_words_ids
            )
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the NPC's response
            if f"{self.npc_name}:" in response:
                response = response.split(f"{self.npc_name}:")[-1].strip()

            if "Player:" in response:
                response = response.split("Player:")[0].strip()

            #if not response.endswith((".", "!", "?")):
               # response = response.rsplit(maxsplit=1)[0] + "."

            #response = response.replace("Elanna", "Elara").replace("Etta-san", "Elara").strip()

            if response in [turn["content"] for turn in self.dialogue_history[-5:] if turn["role"] == "assistant"]:
                response = "I'm not sure how to respond to that."

            #if len(response.split()) < 3 or not response.endswith((".", "!", "?")):
                #response = "I'm not sure how to respond to that, but let's focus on our journey."

            # Update the dialogue history
            self.dialogue_history.append({"role": "user", "content": player_input})
            self.dialogue_history.append({"role": "assistant", "content": response})

            return response
        except Exception as e:
            print(f"Error generating local response: {e}")
            return "I cannot respond right now."

    def get_response(self, player_input):
        response = self.generate_local_response(player_input)
        self.update_memory("previous_topics", player_input)
        return response


    def generate_ai_response(self, player_input):
        """Generate a dynamic response using OpenAI."""
        try:
            prompt = self.build_prompt(player_input)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=prompt,
                max_tokens=150,
                temperature=0.7
            )
            ai_message = response['choices'][0]['message']['content']
            return ai_message
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Sorry, I cannot think of anything to say right now."

    def build_prompt(self, player_input):
        """Build the prompt for AI based on context and personality."""
        base_prompt = [
            {"role": "system", "content": f"You are {self.npc_name}, {self.personality}."},
            {"role": "system", "content": "Maintain a consistent personality and give concise answers."},
            {"role": "user", "content": player_input}
        ]
        
        # Include dialogue history for context
        for turn in self.dialogue_history:
            base_prompt.append(turn)

        # Add the player's latest input
        base_prompt.append({"role": "user", "content": player_input})
        return base_prompt

    def add_to_history(self, user_message, npc_response):
        """Update conversation history."""
        self.dialogue_history.append({"role": "user", "content": user_message})
        self.dialogue_history.append({"role": "assistant", "content": npc_response})

    def get_response(self, player_input):
        """Get response for player input."""
        predefined_responses = self.load_predefined_dialogue("data/templates.json")
        
        # Check if input matches a predefined response
        if player_input in predefined_responses:
            response = predefined_responses[player_input]
        else:
            if self.use_local_model:
                response = self.generate_local_response(player_input)
            else:
                # Generate AI response if no predefined response exists
                response = self.generate_ai_response(player_input)

        # Update dialogue history
        self.add_to_history(player_input, response)
        return response