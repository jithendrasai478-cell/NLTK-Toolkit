import ast
import re
from typing import Any, Dict, List, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from backend.utils.error_handlers import APIException

def check_nltk_tokenizer_resources() -> None:
    """Ensure required NLTK tokenizer resources (punkt / punkt_tab) are available."""
    missing = []
    for res in ["punkt", "punkt_tab"]:
        found = False
        for prefix in [
            f"tokenizers/{res}",
            f"tokenizers/{res}.zip",
            f"tokenizers/{res}_tab",
            f"tokenizers/{res}_tab.zip"
        ]:
            try:
                nltk.data.find(prefix)
                found = True
                break
            except LookupError:
                continue
        if not found:
            try:
                nltk.download(res, quiet=True)
                nltk.data.find(f"tokenizers/{res}")
                found = True
            except Exception:
                missing.append(res)
    
    if "punkt" in missing and "punkt_tab" in missing:
        raise APIException(
            "MISSING_NLTK_RESOURCE",
            "Required NLTK tokenizer resources ('punkt' / 'punkt_tab') are missing. "
            "Please run 'python -m nltk.downloader punkt punkt_tab' on the server.",
            status_code=500
        )

def get_call_name(node: ast.AST) -> Optional[str]:
    """Recursively resolves function/attribute call name, e.g. nltk.word_tokenize -> 'nltk.word_tokenize'."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parent = get_call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None

def parse_nlp_input(raw: str) -> Dict[str, Any]:
    """
    Safely parses user input for NLP tokenization.
    Supports:
    1. Normal text: "Let's tokenize this sentence!"
    2. Function-style: word_tokenize("Let's tokenize this sentence!")
    3. Function-style: sent_tokenize("Sentence 1. Sentence 2.")
    4. Qualified calls: nltk.word_tokenize("..."), nltk.tokenize.sent_tokenize("...")
    
    Security: Uses ast.parse(mode='eval') safely without eval/exec.
    Rejects unsupported functions, invalid syntax, and invalid arguments.
    """
    text = raw.strip()
    if not text:
        raise APIException(
            "EMPTY_INPUT",
            "Input text cannot be empty. Please enter text or a supported function call like word_tokenize(\"...\").",
            status_code=400
        )

    # Check if text looks like a function call: e.g. identifier(...) or module.func(...)
    call_candidate = re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*\s*\(', text)
    if call_candidate:
        prefix = call_candidate.group(0).rstrip('(').strip()
        base_func = prefix.split('.')[-1]
        
        # 1. Try parsing as a Python expression
        try:
            tree = ast.parse(text, mode='eval')
            if isinstance(tree.body, ast.Call):
                call = tree.body
                call_name = get_call_name(call.func) or base_func
                
                # Check if it resolves to word_tokenize or sent_tokenize
                normalized_func = call_name.split('.')[-1]
                if normalized_func in {'word_tokenize', 'sent_tokenize'}:
                    if not call.args:
                        raise APIException(
                            "INVALID_ARGUMENT",
                            f"Invalid argument: {normalized_func}(...) requires a text string argument.",
                            status_code=400
                        )
                    if len(call.args) > 1:
                        raise APIException(
                            "INVALID_ARGUMENT",
                            f"Invalid argument: {normalized_func}(...) takes only 1 text argument.",
                            status_code=400
                        )
                    
                    arg0 = call.args[0]
                    if not (isinstance(arg0, ast.Constant) and isinstance(arg0.value, str)):
                        raise APIException(
                            "INVALID_ARGUMENT",
                            f"Invalid argument: the argument to {normalized_func}(...) must be a string literal, e.g. {normalized_func}(\"your text\").",
                            status_code=400
                        )
                    
                    return {
                        "text": arg0.value,
                        "is_function_call": True,
                        "function_name": normalized_func,
                        "processing_method": f"NLTK {normalized_func}",
                        "library_used": "NLTK",
                        "raw_input": raw
                    }
                else:
                    # Explicit Python call to an unsupported function (security rejection)
                    raise APIException(
                        "UNSUPPORTED_FUNCTION",
                        f"Unsupported NLP function '{call_name}'. Supported functions are 'word_tokenize' and 'sent_tokenize'.",
                        status_code=400
                    )
        except SyntaxError as e:
            # If the user specifically attempted to call a known tokenizer but has a syntax error
            if base_func in {'word_tokenize', 'sent_tokenize'}:
                raise APIException(
                    "INVALID_SYNTAX",
                    f"Invalid function syntax in {base_func}: {e.msg}. Expected format: {base_func}(\"your text here\")",
                    status_code=400
                )
            # Otherwise, it might just be natural text like "Note (important): ..."
            pass

    # Normal natural-language text input
    return {
        "text": text,
        "is_function_call": False,
        "function_name": "word_tokenize",
        "processing_method": "NLTK word_tokenize",
        "library_used": "NLTK",
        "raw_input": raw
    }

def tokenize_text(text: str, language: str = "english") -> Dict[str, Any]:
    """
    Safely parses input (normal text or function-style syntax) and executes REAL NLTK tokenization.
    Calculates token counts, sentence counts, and character counts dynamically without hardcoding.
    """
    check_nltk_tokenizer_resources()
    
    parsed = parse_nlp_input(text)
    extracted_text = parsed["text"]
    func_name = parsed["function_name"]
    processing_method = parsed["processing_method"]
    library_used = parsed["library_used"]

    # Real NLTK sentence tokenization
    try:
        sentences = sent_tokenize(extracted_text, language=language)
    except Exception:
        # Fallback regex sentence splitter for non-standard or unsupported language codes
        sentences = [s.strip() for s in re.split(r'(?<=[.!?।॥])\s+', extracted_text) if s.strip()]
        if not sentences and extracted_text.strip():
            sentences = [extracted_text.strip()]

    # Real NLTK word tokenization
    try:
        tokens = word_tokenize(extracted_text, language=language)
    except Exception:
        # Unicode word tokenizer fallback: keeps words and punctuation tokens
        tokens = re.findall(r'\w+|[^\w\s]', extracted_text, re.UNICODE)

    # Sentence-by-sentence word breakdown
    sentence_breakdown: List[Dict[str, Any]] = []
    for idx, sent in enumerate(sentences, start=1):
        try:
            sent_words = word_tokenize(sent, language=language)
        except Exception:
            sent_words = re.findall(r'\w+|[^\w\s]', sent, re.UNICODE)
        sentence_breakdown.append({
            "sentence_index": idx,
            "text": sent,
            "token_count": len(sent_words),
            "tokens": sent_words
        })

    token_count = len(tokens)
    sentence_count = len(sentences)
    character_count = len(extracted_text)

    return {
        "input_text": extracted_text,
        "raw_input": parsed["raw_input"],
        "is_function_call": parsed["is_function_call"],
        "function_name": func_name,
        "processing_method": processing_method,
        "library_used": library_used,
        "token_count": token_count,
        "sentence_count": sentence_count,
        "character_count": character_count,
        "character_count_no_spaces": len(extracted_text.replace(" ", "")),
        "tokens": tokens,
        "sentences": sentences,
        "sentence_breakdown": sentence_breakdown,
        "language_used": language,
    }

