"""
Sentiment Analysis Module
Uses DistilBERT Multilingual model with VADER fallback
"""

import pandas as pd
import streamlit as st

# Try to load VADER as backup
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as _SIA
    _vader = _SIA()
except Exception:
    _vader = None

# Try to load AI model
_ai_sentiment_available = False
sentiment_pipeline = None

try:
    from transformers import pipeline
    
    model_name = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"

    @st.cache_resource(show_spinner="Loading Sentiment AI Model...")
    def load_sentiment_model():
        return pipeline("sentiment-analysis", model=model_name, return_all_scores=False)

    sentiment_pipeline = load_sentiment_model()
    _ai_sentiment_available = True

except Exception:
    pass


def _analyze_with_ai(text: str) -> tuple:
    """Analyze sentiment using AI model."""
    result = sentiment_pipeline(text)[0]
    label = result['label']
    score = result['score']
    scaled_score = int(score * 100)

    # Low confidence = Neutral
    if score < 0.60:
        return "Neutral", scaled_score

    if label == 'positive':
        if score > 0.90:
            return "Very Positive", scaled_score
        return "Positive", scaled_score
    
    elif label == 'negative':
        if score > 0.90:
            return "Very Negative", scaled_score
        return "Negative", scaled_score
    
    else:
        return "Neutral", scaled_score


def _analyze_with_keywords(text: str) -> tuple:
    """Fallback: Simple keyword-based sentiment analysis."""
    low = text.lower()
    
    pos_words = [
        "good", "great", "excellent", "clear", "helpful", "amazing",
        "perfect", "professional", "ممتاز", "رائع", "مفيد", "واضح",
        "شكرا", "احسن", "جيد"
    ]
    neg_words = [
        "bad", "poor", "weak", "late", "unclear", "boring",
        "problem", "issue", "سيء", "ضعيف", "مشكلة", "متأخر",
        "صعب", "غير مفيد"
    ]
    
    pos = sum(w in low for w in pos_words)
    neg = sum(w in low for w in neg_words)
    
    if pos > neg:
        return "Positive", min(90, 55 + pos * 8)
    if neg > pos:
        return "Negative", max(10, 45 - neg * 8)
    return "Neutral", 50


def analyze_sentiment_label(text) -> tuple:
    """
    Analyze sentiment of text.
    
    Returns:
        tuple: (label, score) where label is one of:
               "Very Positive", "Positive", "Neutral", "Negative", "Very Negative"
               and score is 0-100
    """
    if pd.isna(text):
        return "Neutral", 50
    
    s = str(text).strip()
    if not s:
        return "Neutral", 50

    # Strategy 1: AI Model
    if _ai_sentiment_available and sentiment_pipeline:
        try:
            return _analyze_with_ai(s)
        except Exception:
            pass

    # Strategy 2: Keyword Fallback
    return _analyze_with_keywords(s)