# Model Selection Fix - OpenAI/Gemini Switching Issue

## Problem Description
When users selected OpenAI as the preferred model and asked database questions, the system was automatically switching back to Google Gemini, even though OpenAI was explicitly chosen. This happened because:

1. **OpenAI Client had built-in Gemini fallback**: The OpenAI client was configured to automatically fall back to Gemini whenever it encountered any error (timeout, rate limit, API error, etc.)
2. **Lack of model preference tracking**: The system was swapping clients at the view level but not properly tracking which model the user wanted to use
3. **Nested fallback logic**: Both the service layer and individual clients had fallback mechanisms, causing confusion about which model was actually being used

## Root Cause
The main issue was in three places:

### 1. `views.py` (Lines 116-120)
```python
# Old approach - swapping clients
if selected_model == 'openai':
    temp = chatbot.gemini_client
    chatbot.gemini_client = chatbot.openai_client
    chatbot.openai_client = temp
```
This approach was confusing because it didn't actually tell the service which model to prefer.

### 2. `chatbot_service.py` (Line 237)
```python
# Always used gemini_client first
response = self.gemini_client.get_chatbot_response(...)
```
This always tried the Gemini client first, regardless of user preference.

### 3. `openai_client.py` (Lines 77-137)
```python
# Automatic fallback to Gemini on any error
except Exception as e:
    return self._use_gemini_fallback(...)
```
The OpenAI client had its own Gemini fallback built-in, which couldn't be disabled.

## Solution Implemented

### 1. Updated `views.py`
- **Change**: Pass the selected model as a parameter instead of swapping clients
```python
response = chatbot.get_response(
    message, 
    context, 
    history, 
    use_cache=not refresh_data,
    preferred_model=selected_model  # Now explicitly passes user's choice
)
```

### 2. Updated `chatbot_service.py`
- **Change**: Accept `preferred_model` parameter and select the appropriate client
```python
def get_response(self, prompt, context=None, history=None, use_cache=True, 
                 sheet_name=None, preferred_model='gemini'):
    # Select appropriate client based on user preference
    if preferred_model == 'openai':
        primary_client = self.openai_client
        fallback_client = self.gemini_client
        primary_model_name = 'openai'
        fallback_model_name = 'gemini'
    else:
        primary_client = self.gemini_client
        fallback_client = self.openai_client
        primary_model_name = 'gemini'
        fallback_model_name = 'openai'
    
    # Use the selected model WITHOUT its built-in fallback
    response = primary_client.get_chatbot_response(
        enhanced_prompt, 
        database_data, 
        history, 
        context_text,
        use_fallback=False  # Disable built-in fallback
    )
```

### 3. Updated `openai_client.py`
- **Change**: Added `use_fallback` parameter to control whether Gemini fallback should be used
```python
def get_chatbot_response(self, prompt, database_data=None, history=None, 
                         context=None, use_fallback=True):
    # ... error handling ...
    
    except openai.RateLimitError:
        # Only use fallback if enabled
        if use_fallback:
            return self._use_gemini_fallback(...)
        else:
            raise Exception("OpenAI rate limit exceeded")
```

### 4. Updated `gemini_client.py`
- **Change**: Added `use_fallback` parameter for consistency (not used, but keeps API consistent)

### 5. Updated `_try_fallback_model` in `chatbot_service.py`
- **Change**: Accept specific fallback client and model name as parameters
```python
def _try_fallback_model(self, prompt, database_data, history, context_text, 
                        error_message, fallback_client, fallback_model_name):
    # Use the provided fallback client instead of hardcoded self.openai_client
    fallback_response = fallback_client.get_chatbot_response(
        prompt, database_data, history, context_text,
        use_fallback=False  # Prevent nested fallback
    )
```

## Key Improvements

### 1. **Clear Model Selection**
- Users can now explicitly choose which model to use
- The system respects this choice and doesn't automatically switch

### 2. **Controlled Fallback**
- Fallback only happens when explicitly needed (rate limits, errors)
- No automatic fallback within individual clients when `use_fallback=False`
- Prevents nested fallback loops

### 3. **Better Error Handling**
- API key issues are caught and reported clearly
- Rate limits trigger controlled retry with exponential backoff
- Only falls back to alternative model after exhausting retries on primary model

### 4. **Proper Attribution**
- Response source is correctly labeled as 'openai' or 'gemini'
- Users can see which model actually answered their question
- Analytics correctly track which model was used

## Testing Recommendations

### Test Case 1: Normal Operation
1. Select OpenAI model
2. Ask a database question
3. Verify response comes from OpenAI (check source label)
4. Verify analytics show OpenAI usage

### Test Case 2: Rate Limit Handling
1. Select OpenAI model
2. Trigger rate limit (many rapid requests)
3. Verify system retries with exponential backoff
4. After max retries, verify it falls back to Gemini
5. Verify fallback is clearly communicated to user

### Test Case 3: Model Switching
1. Ask question with OpenAI selected
2. Switch to Gemini
3. Ask another question
4. Verify second response uses Gemini
5. Check analytics show both models were used

### Test Case 4: API Key Issues
1. Test with invalid/missing API key
2. Verify clear error message
3. Verify system doesn't fall back for authentication errors

## Files Modified
1. `chatbot/views.py` - Updated chat endpoint to pass preferred_model parameter
2. `chatbot/utils/chatbot_service.py` - Updated get_response() and _try_fallback_model() methods
3. `chatbot/utils/openai_client.py` - Added use_fallback parameter to control fallback behavior
4. `chatbot/utils/gemini_client.py` - Added use_fallback parameter for API consistency

## Expected Behavior After Fix
- When OpenAI is selected, queries are sent to OpenAI first
- Only falls back to Gemini after OpenAI retries are exhausted
- Proper model attribution in responses
- Clear communication when fallback occurs
- No automatic switching without user awareness

## Additional Notes
- The fix maintains backward compatibility
- Default behavior (when no model specified) is still Gemini
- All existing fallback mechanisms still work, but are now controllable
- Better separation of concerns between view layer and service layer
