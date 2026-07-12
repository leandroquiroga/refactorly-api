from __future__ import annotations

class RefactorlyError(Exception):
    """Base exception for all domain errors
    
    All Custom exceptions inherit from here, allowing callers to 
    catch any domain error with a single except RefactorlyError
    """
    
class InvalidCodeError(RefactorlyError):
    """Raised when the submitted code fails validation
    
    Example: empty code, code exceeding maximum length, etc
    """
    
class ReviewNotFoundError(RefactorlyError):
    """Raised when a review is not found in the repository"""
    
    
class LLMProviderError(RefactorlyError):
    """Raised when an error occurs with the LLM provider
    
    Wraps underlying provider exceptions (rate limits, auth errors, etc)
    into a single domain exception
    """