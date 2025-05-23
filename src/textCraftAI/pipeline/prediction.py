from textCraftAI.config.configuration import ConfigurationManager
from transformers import AutoTokenizer
from transformers import pipeline
import os


class PredictionPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_evaluation_config()

    def predict(self, text):
        if os.path.exists(self.config.model_path) and os.path.exists(self.config.tokenizer_path):
            # Use trained model
            tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer_path)
            model_path = self.config.model_path
            print("Using trained model for prediction...")
        else:
            # Fallback to base model
            model_path = "google/pegasus-cnn_dailymail"
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            print("Trained model not found. Using base model for prediction...")

        gen_kwargs = {
            "length_penalty": 0.8, 
            "num_beams": 8, 
            "max_length": 128,
            "no_repeat_ngram_size": 3,
            "do_sample": False,
            "early_stopping": True
        }

        pipe = pipeline("summarization", model=model_path, tokenizer=tokenizer)

        print("Dialogue:")
        print(text)

        output = pipe(text, **gen_kwargs)[0]["summary_text"]
        
        # Clean the output by removing special tokens
        cleaned_output = self._clean_text(output)
        
        print("\nModel Summary:")
        print(cleaned_output)        
        return cleaned_output
    
    def _clean_text(self, text):
        # Clean the generated text by removing special tokens and formatting issues.
        import re
        
        # Remove common special tokens and artifacts
        special_tokens = [
            '<n>', '</s>', '<pad>', '<unk>', '<s>', '<mask>',
            '<|endoftext|>', '<|startoftext|>', '<bos>', '<eos>',
            '[UNK]', '[PAD]', '[CLS]', '[SEP]', '[MASK]',
            '<extra_id_0>', '<extra_id_1>', '<extra_id_2>',
            '<<UNK>>', '##', '<|im_start|>', '<|im_end|>'
        ]
        
        cleaned_text = text
        
        # Remove special tokens (case insensitive)
        for token in special_tokens:
            cleaned_text = re.sub(re.escape(token), '', cleaned_text, flags=re.IGNORECASE)
        
        # Remove HTML/XML-like tags
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
        
        # Remove unusual whitespace characters and normalize
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_text)  # Remove control characters
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
        cleaned_text = re.sub(r'\n+', ' ', cleaned_text)  # Replace newlines with spaces
        
        # Remove leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
        
        # Remove leading/trailing punctuation that might be artifacts
        cleaned_text = re.sub(r'^[^\w\'"]*', '', cleaned_text)
        cleaned_text = re.sub(r'[^\w\'".,!?;:]*$', '', cleaned_text)
        
        # Fix common spacing issues around punctuation
        cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)  # Remove space before punctuation
        cleaned_text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', cleaned_text)  # Add space after punctuation
        
        # Ensure proper sentence capitalization
        if cleaned_text and not cleaned_text[0].isupper():
            cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]
        
        # Handle multiple consecutive punctuation
        cleaned_text = re.sub(r'[.]{2,}', '.', cleaned_text)
        cleaned_text = re.sub(r'[!]{2,}', '!', cleaned_text)
        cleaned_text = re.sub(r'[?]{2,}', '?', cleaned_text)
        
        return cleaned_text