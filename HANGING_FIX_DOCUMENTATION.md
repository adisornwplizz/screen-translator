# Fix for Issue #24: ใช้ไปสักแปบระบบจะค้าง (System hangs after short usage)

## Problem Description

The system experienced hanging/crashing symptoms during AI Vision text detection. The issue occurred specifically when the AI Vision was performing text box detection, causing the entire application to become unresponsive.

## Root Cause Analysis

The hanging was caused by several factors:

1. **Synchronous Operations**: OCR processing was running on the main UI thread, blocking the interface
2. **Long Timeouts**: HTTP requests to Ollama Vision API had 60-second timeouts
3. **No Cancellation**: Once OCR started, there was no way to cancel long-running operations
4. **Resource Intensive Processing**: Image processing and large images could consume excessive resources
5. **High Frequency Captures**: Too frequent OCR calls could overwhelm the system

## Solution Implemented

### 1. Threading Solution (`src/gui/window.py`)

Added `OCRWorker` class that inherits from `QThread` to move OCR operations to background:

```python
class OCRWorker(QThread):
    """Worker thread สำหรับ OCR เพื่อป้องกานการค้างของ UI"""
    finished = pyqtSignal(str, float)  # text, confidence
    error = pyqtSignal(str)  # error message
```

### 2. Timeout Reduction (`src/translation/ocr.py`)

- Reduced HTTP timeout from 60 seconds to 15 seconds
- Added connection timeout (5 seconds) separate from read timeout (15 seconds)
- Enhanced error handling for different timeout scenarios

```python
# Before: timeout=60
# After: timeout=(5, 15)  # (connect_timeout, read_timeout)
response = requests.post(url, json=payload, timeout=(5, 15))
```

### 3. Resource Management

- Added image size limits (1920x1080) to prevent memory exhaustion
- Optimized image processing to be less resource-intensive
- Added proper thread cancellation and cleanup

### 4. Configuration Improvements (`src/config.py`)

- Increased capture interval from 3 seconds to 5 seconds
- Raised minimum interval from 1 second to 2 seconds
- Increased maximum interval from 10 seconds to 15 seconds

### 5. Error Handling Enhancement

Added specific error handling for:
- Connection timeouts
- Read timeouts
- Network errors
- OCR processing errors

## Benefits

1. **No More UI Hangs**: OCR operations run in background threads
2. **Better Responsiveness**: UI remains interactive during processing
3. **Graceful Error Handling**: Network issues don't crash the application
4. **Resource Efficiency**: Reduced frequency and resource usage
5. **Proper Cleanup**: Threads are properly managed and cleaned up

## Backward Compatibility

All existing functionality is preserved:
- All OCR methods maintain the same interface
- All GUI methods work exactly as before
- All configuration options remain available
- Existing workflows continue to work

## Testing

Created comprehensive tests to validate:
- Syntax correctness of all modified files
- Interface preservation
- Configuration backward compatibility
- Threading component functionality

## Usage

The fix is transparent to users - the application will simply be more responsive and stable during AI Vision text detection operations.

## Files Modified

1. `src/gui/window.py` - Added OCRWorker threading and async processing
2. `src/translation/ocr.py` - Reduced timeouts and enhanced error handling  
3. `src/config.py` - Adjusted capture intervals for better stability

## Technical Details

### Threading Implementation

The `capture_and_process` method now:
1. Checks if OCR is already running (prevents overlapping operations)
2. Creates a new `OCRWorker` instance for each OCR operation
3. Connects signals for completion and error handling
4. Starts processing in background while keeping UI responsive

### Timeout Strategy

- **Connection timeout**: 5 seconds (quick failure if Ollama not available)
- **Read timeout**: 15 seconds (reasonable time for AI processing)
- **Total maximum**: 20 seconds instead of previous 60 seconds

This significantly reduces the maximum time the system can hang while still allowing sufficient time for normal AI Vision processing.

## Future Considerations

- Consider adding a progress indicator during OCR processing
- Implement OCR request queuing for very frequent captures
- Add user-configurable timeout settings
- Consider implementing OCR result caching for repeated text detection