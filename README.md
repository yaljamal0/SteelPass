# SteelPass

### Current Limitations
- No way to read modifier keys (Ctrl, Shift, etc.) to allow pasting or proper tab key navigation.
- No way to read or write to the clipboard or do auto-entering without using external libraries or calling installed system programs (like xsel for Linux, pbcopy for macOS, etc.), which means there is no way to move passwords out.
- No way to tell where the mouse press happened relative to written characters (for selecting text or inserting between characters).