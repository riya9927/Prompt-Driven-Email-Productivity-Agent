class PromptService:
    def __init__(self, database):
        self.db = database
    
    def get_all_prompts(self):
        rows = self.db.execute_query('SELECT * FROM prompts')
        prompts = {}
        for row in rows:
            row_dict = self.db.row_to_dict(row)
            prompts[row_dict['prompt_type']] = row_dict['prompt_text']
        return prompts
    
    def get_prompt(self, prompt_type):
        rows = self.db.execute_query(
            'SELECT prompt_text FROM prompts WHERE prompt_type = ?',
            (prompt_type,)
        )
        if rows:
            return rows[0]['prompt_text']
        return None
    
    def update_prompts(self, prompts_dict):
        for prompt_type, prompt_text in prompts_dict.items():
            self.db.execute_query(
                '''UPDATE prompts 
                   SET prompt_text = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE prompt_type = ?''',
                (prompt_text, prompt_type)
            )
    
    def update_prompt(self, prompt_type, prompt_text):
        self.db.execute_query(
            '''UPDATE prompts 
               SET prompt_text = ?, updated_at = CURRENT_TIMESTAMP
               WHERE prompt_type = ?''',
            (prompt_text, prompt_type)
        )
    
    def create_prompt(self, prompt_type, prompt_text):
        self.db.execute_insert(
            '''INSERT INTO prompts (prompt_type, prompt_text)
               VALUES (?, ?)''',
            (prompt_type, prompt_text)
        )