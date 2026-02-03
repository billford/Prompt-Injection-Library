# Prompt Injection Library

A command-line tool for managing and exploring prompt injection techniques. For educational and defensive security purposes only.

## Installation

```bash
# No dependencies required - uses Python 3.6+ standard library
chmod +x prompt_injection_cli.py
```

## Usage

```bash
# List all injections
python prompt_injection_cli.py list

# Filter by category
python prompt_injection_cli.py list -c Jailbreak

# Filter by tag
python prompt_injection_cli.py list -t bypass

# Show details of a specific injection
python prompt_injection_cli.py show 5

# Search for injections
python prompt_injection_cli.py search "ignore instructions"

# List categories
python prompt_injection_cli.py categories

# List tags
python prompt_injection_cli.py tags

# Show statistics
python prompt_injection_cli.py stats

# Add a new injection (interactive)
python prompt_injection_cli.py add

# Edit an existing injection
python prompt_injection_cli.py edit 3

# Delete an injection
python prompt_injection_cli.py delete 7
python prompt_injection_cli.py delete 7 -f  # Skip confirmation

# Export to file
python prompt_injection_cli.py export -o backup.json
python prompt_injection_cli.py export -o backup.txt -f txt

# Import from file
python prompt_injection_cli.py import -i new_injections.json
```

## Categories

The library includes the following categories of prompt injections:

- **Instruction Override** - Techniques to override system instructions
- **Jailbreak** - Methods to bypass safety guidelines
- **Information Extraction** - Extracting system prompts or sensitive info
- **Indirect Injection** - Injections via external data sources
- **Context Exploitation** - Manipulating context windows
- **Obfuscation** - Encoding/hiding malicious content
- **Social Engineering** - Psychological manipulation techniques
- **Completion Exploitation** - Exploiting completion behavior
- **Conversation Exploitation** - Multi-turn manipulation
- **Format Exploitation** - Using output formats to bypass filters
- **Logic Exploitation** - Logical paradoxes and recursion

## Disclaimer

This library is intended for:
- Security researchers studying AI vulnerabilities
- Developers building robust AI systems
- Educational purposes

Do not use these techniques maliciously. Always follow responsible disclosure practices.
