#!/usr/bin/env python3
"""
Model Pre-download Script for TextCraftAI
Downloads required models during Docker build to cache them.
"""

from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM, 
    T5Tokenizer, 
    T5ForConditionalGeneration,
    pipeline
)
import os
import sys

def download_models():
    """Download and cache all required models"""
    
    print("=" * 60)
    print("TextCraftAI Model Pre-download Script")
    print("=" * 60)
    
    # Model configurations
    models_to_download = [
        {
            "name": "PEGASUS (Summarization)",
            "model_id": "google/pegasus-cnn_dailymail",
            "tokenizer_class": AutoTokenizer,
            "model_class": AutoModelForSeq2SeqLM
        },
        {
            "name": "T5-Base (Paraphrasing)",
            "model_id": "t5-base", 
            "tokenizer_class": T5Tokenizer,
            "model_class": T5ForConditionalGeneration
        }
    ]
    
    success_count = 0
    total_models = len(models_to_download)
    
    for model_config in models_to_download:
        print(f"\nDownloading {model_config['name']}...")
        print(f"Model ID: {model_config['model_id']}")
        
        try:
            # Download tokenizer
            print("  - Downloading tokenizer...")
            tokenizer = model_config['tokenizer_class'].from_pretrained(
                model_config['model_id'],
                cache_dir="/root/.cache/huggingface/transformers"
            )
            
            # Download model
            print("  - Downloading model...")
            model = model_config['model_class'].from_pretrained(
                model_config['model_id'],
                cache_dir="/root/.cache/huggingface/transformers"
            )
            
            # Test pipeline creation
            print("  - Testing pipeline...")
            if "pegasus" in model_config['model_id'].lower():
                test_pipeline = pipeline(
                    "summarization", 
                    model=model, 
                    tokenizer=tokenizer
                )
            else:
                test_pipeline = pipeline(
                    "text2text-generation",
                    model=model,
                    tokenizer=tokenizer
                )
            
            print(f"  ✅ {model_config['name']} downloaded and cached successfully!")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to download {model_config['name']}: {str(e)}")
            # Don't exit on individual model failure, continue with others
            continue
    
    print("\n" + "=" * 60)
    print(f"Model Download Summary: {success_count}/{total_models} successful")
    
    if success_count == total_models:
        print("🎉 All models downloaded successfully!")
        print("Models are cached and ready for use.")
    elif success_count > 0:
        print("⚠️  Some models downloaded successfully.")
        print("Application will download missing models at runtime.")
    else:
        print("❌ No models were downloaded successfully.")
        print("All models will be downloaded at first use.")
    
    print("=" * 60)
    
    # Cache info
    cache_dir = "/root/.cache/huggingface/transformers"
    if os.path.exists(cache_dir):
        cache_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(cache_dir)
            for filename in filenames
        )
        cache_size_mb = cache_size / (1024 * 1024)
        print(f"Cache size: {cache_size_mb:.1f} MB")
    
    return success_count == total_models

if __name__ == "__main__":
    try:
        success = download_models()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)
