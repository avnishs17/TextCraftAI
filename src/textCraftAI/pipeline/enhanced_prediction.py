from textCraftAI.config.configuration import ConfigurationManager
from transformers import AutoTokenizer, pipeline
import os
import PyPDF2
import docx
import io
from typing import Union


class EnhancedPredictionPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_evaluation_config()
        self.max_file_size = 5 * 1024 * 1024  # 5MB limit
        self.max_text_length = 10000  # Character limit for processing
        
        # Cache for models to avoid reloading
        self._summarization_pipeline = None
        self._paraphrase_pipeline = None

    def _get_model_and_tokenizer(self):
        """Get model and tokenizer with fallback logic and caching"""
        if os.path.exists(self.config.model_path) and os.path.exists(self.config.tokenizer_path):
            # Use trained model
            tokenizer = AutoTokenizer.from_pretrained(
                self.config.tokenizer_path,
                cache_dir=os.environ.get('TRANSFORMERS_CACHE', '/root/.cache/huggingface/transformers')
            )
            model_path = self.config.model_path
            print("Using trained model for prediction...")
        else:
            # Fallback to base model
            model_path = "google/pegasus-cnn_dailymail"
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=os.environ.get('TRANSFORMERS_CACHE', '/root/.cache/huggingface/transformers')
            )
            print("Trained model not found. Using base model for prediction...")
        
        return model_path, tokenizer

    def _get_summarization_pipeline(self):
        """Get cached summarization pipeline"""
        if self._summarization_pipeline is None:
            model_path, tokenizer = self._get_model_and_tokenizer()
            self._summarization_pipeline = pipeline(
                "summarization", 
                model=model_path, 
                tokenizer=tokenizer,
                model_kwargs={
                    "cache_dir": os.environ.get('TRANSFORMERS_CACHE', '/root/.cache/huggingface/transformers')
                }
            )
        return self._summarization_pipeline

    def _get_paraphrase_pipeline(self):
        """Get cached paraphrase pipeline"""
        if self._paraphrase_pipeline is None:
            self._paraphrase_pipeline = pipeline(
                "text2text-generation", 
                model="t5-base",
                tokenizer="t5-base",
                model_kwargs={
                    "cache_dir": os.environ.get('TRANSFORMERS_CACHE', '/root/.cache/huggingface/transformers')
                }            )
        return self._paraphrase_pipeline

    def summarize_text(self, text: str) -> str:
        """Summarize input text using cached pipeline"""
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length] + "..."
        
        gen_kwargs = {
            "length_penalty": 0.8, 
            "num_beams": 8, 
            "max_length": 128,
            "no_repeat_ngram_size": 3,
            "do_sample": False,
            "early_stopping": True
        }

        pipe = self._get_summarization_pipeline()
        output = pipe(text, **gen_kwargs)[0]["summary_text"]
        
        return self._clean_text(output)

    def paraphrase_text(self, text: str, length_factor: float = 1.0) -> str:
        """Paraphrase input text using T5 model with configurable length using cached pipeline
        
        Args:
            text: Input text to paraphrase
            length_factor: Length multiplier (0.5 = shorter, 1.0 = same, 1.5 = longer)
        """
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length] + "..."
        
        # Get cached pipeline
        paraphrase_pipe = self._get_paraphrase_pipeline()
        
        # Format input for T5 paraphrasing
        input_text = f"paraphrase: {text}"
        
        # Calculate dynamic max_length based on input and user preference
        input_word_count = len(text.split())
        target_length = max(10, int(input_word_count * length_factor))
        
        # Ensure reasonable bounds
        min_length = max(5, int(input_word_count * 0.3))
        max_length = min(512, int(input_word_count * 2.0))
        target_length = max(min_length, min(target_length, max_length))
        
        result = paraphrase_pipe(
            input_text,
            max_length=target_length,
            min_length=min_length,
            num_beams=4,
            early_stopping=True,
            do_sample=True,
            temperature=0.7
        )[0]["generated_text"]
        
        return self._clean_text(result)

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds {self.max_file_size // (1024*1024)}MB limit")
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            max_pages = 10  # Limit to first 10 pages
            
            for page_num in range(min(len(pdf_reader.pages), max_pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds {self.max_file_size // (1024*1024)}MB limit")
        
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise ValueError(f"Error processing DOCX: {str(e)}")

    def process_file(self, file_content: bytes, filename: str, operation: str, length_factor: float = 1.0) -> str:
        """Process uploaded file and perform operation"""
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            text = self.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            text = file_content.decode('utf-8')
        else:
            raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT files.")
        
        if not text.strip():
            raise ValueError("No readable text found in the uploaded file.")
        
        # Perform requested operation
        if operation == "summarize":
            return self.summarize_text(text)
        elif operation == "paraphrase":
            return self.paraphrase_text(text, length_factor)
        else:
            raise ValueError("Invalid operation. Choose 'summarize' or 'paraphrase'.")

    def _clean_text(self, text: str) -> str:
        """Clean the generated text by removing special tokens and formatting issues"""
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
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
        
        # Remove leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
        
        # Remove leading/trailing punctuation that might be artifacts
        cleaned_text = re.sub(r'^[^\w\'"]*', '', cleaned_text)
        cleaned_text = re.sub(r'[^\w\'".,!?;:]*$', '', cleaned_text)
        
        # Fix common spacing issues around punctuation
        cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)
        cleaned_text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', cleaned_text)
        
        # Ensure proper sentence capitalization
        if cleaned_text and not cleaned_text[0].isupper():
            cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]
        
        # Handle multiple consecutive punctuation
        cleaned_text = re.sub(r'[.]{2,}', '.', cleaned_text)
        cleaned_text = re.sub(r'[!]{2,}', '!', cleaned_text)
        cleaned_text = re.sub(r'[?]{2,}', '?', cleaned_text)
        
        return cleaned_text


# Backward compatibility - keep the original class for existing code
class PredictionPipeline(EnhancedPredictionPipeline):
    def predict(self, text: str) -> str:
        """Legacy method for backward compatibility"""
        return self.summarize_text(text)
