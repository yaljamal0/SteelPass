# SteelPass

### Todos
- [ ] Cryptography
- [ ] Time-based security measures
- [ ] 2FA
- [x] Add icons for buttons instead of letters
- [x] Search box to search for entries
- [x] Button hover effect
- [x] Password length adjustment
- [x] Hide password fields content by default

### Challenges
- ~~No way to read modifier keys (Ctrl, Shift, etc.) to allow pasting or proper tab key navigation.~~

**Solution:** Use the 'modifiers' argument in onKeyPress.

- ~~No way to read or write to the clipboard or do auto-entering without using external libraries or calling installed system programs (like xsel for Linux, pbcopy for macOS, etc.), which means there is no way to move passwords out.~~
**Solution:** Use the os library temporarily to execute clipboard shell commands.

- ~~No way to tell where the mouse press happened relative to written characters (for selecting text or inserting between characters).~~
**Solution:** Use monospace.

- ~~How do I name constants in camelCase?~~
**Solution:** Don't capitalize all letters (use normal camelCase).

- Text zigzags after writing or removing a space character at the end