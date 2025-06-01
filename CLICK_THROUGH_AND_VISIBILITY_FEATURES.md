# Click-Through and Visibility Toggle Features

## Overview

This document describes the new features added to the SelectionWidget to fix issues #5:

1. **Click-Through Functionality**: Allows clicking on background applications when not clicking directly on the selection box
2. **Visibility Toggle**: Allows hiding/showing the selection box while maintaining text detection functionality

## Features Added

### 1. Click-Through Functionality

**Problem Solved**: Previously, the SelectionWidget captured all mouse events across the entire screen, preventing users from clicking on background applications.

**Solution**: 
- Modified mouse event handling to only capture events within the selection rectangle and resize handles
- Removed fullscreen background painting that was blocking clicks
- Added `get_interactive_region()` method to define clickable areas
- Added `should_handle_mouse_event()` to check if mouse events should be handled

**Usage**:
- Click and drag within the selection rectangle to move it
- Click and drag on the edges/corners to resize
- Click anywhere outside the selection area and the click will pass through to background applications

### 2. Visibility Toggle

**Problem Solved**: No way to hide the selection box overlay while keeping text detection active.

**Solution**:
- Added `visible_mode` state variable to track visibility
- Added methods: `toggle_visibility()`, `set_visible_mode()`, `is_visible_mode()`
- Modified `paintEvent()` to skip drawing when invisible
- Added keyboard shortcuts and UI controls

**Usage**:
- Press `V` key when selection widget is focused to toggle visibility
- Press `Ctrl+V` in the main window to toggle visibility
- Click the "👁️ ซ่อน/แสดง" button in the main UI
- When hidden, the selection box is invisible but text detection continues working

## API Reference

### SelectionWidget New Methods

#### `toggle_visibility()`
Toggles the visibility state of the selection widget.

#### `set_visible_mode(visible: bool)`
Sets the visibility state explicitly.
- `visible`: True to show, False to hide

#### `is_visible_mode() -> bool`
Returns the current visibility state.

#### `get_interactive_region() -> QRect`
Returns the area where mouse events should be handled (selection rect + resize handles).

#### `should_handle_mouse_event(pos: QPoint) -> bool`
Determines if a mouse event at the given position should be handled.

### Window Class New Methods

#### `toggle_selection_visibility()`
Toggles the visibility of the selection widget from the main window.

#### `set_selection_visible(visible: bool)`
Sets the selection widget visibility from the main window.

## Keyboard Shortcuts

- `V` - Toggle visibility (when selection widget is focused)
- `Ctrl+V` - Toggle visibility (when main window is focused)
- `ESC` - Hide selection widget completely

## Implementation Details

### Click-Through Mechanism

1. **Interactive Region Detection**: The `get_interactive_region()` method calculates the area that should respond to mouse events
2. **Event Filtering**: `should_handle_mouse_event()` checks if mouse events should be processed
3. **Event Ignoring**: Mouse events outside the interactive region are ignored, allowing them to pass through to applications below

### Visibility Toggle Mechanism

1. **State Management**: `visible_mode` boolean tracks whether the widget should be visible
2. **Paint Override**: `paintEvent()` checks `visible_mode` and skips drawing when false
3. **Cursor Management**: Cursor changes are disabled when widget is invisible
4. **Event Handling**: Mouse events are still processed for position tracking even when invisible

## Testing

### Manual Testing Steps

1. **Click-Through Testing**:
   - Open the application and show the selection widget
   - Try clicking on areas outside the selection rectangle
   - Verify that clicks pass through to background applications
   - Verify that dragging/resizing still works within the selection area

2. **Visibility Toggle Testing**:
   - Press `V` key to hide the selection widget
   - Verify the widget disappears but position tracking continues
   - Press `V` again to show the widget
   - Test the UI button and Ctrl+V shortcut

### Test Files

- `test_click_through.py` - Comprehensive test with interactive elements
- `demo_selection.py` - Updated demo showcasing new features
- `mock_test.py` - Syntax and structure validation

## Compatibility

- All existing functionality is preserved
- No breaking changes to the public API
- Backward compatible with existing code

## Performance Impact

- Minimal performance impact
- Event filtering is lightweight
- No additional background processing

## Future Enhancements

Potential improvements for future versions:

1. **Customizable Shortcuts**: Allow users to configure keyboard shortcuts
2. **Visual Indicators**: Add visual feedback when widget is in invisible mode
3. **Multi-Monitor Support**: Enhanced handling for multi-monitor setups
4. **Opacity Control**: Allow adjusting widget opacity instead of full hide/show