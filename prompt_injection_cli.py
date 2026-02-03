#!/usr/bin/env python3
"""
Prompt Injection Library CLI

A command-line tool for managing and exploring prompt injection techniques.
For educational and defensive security purposes only.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def get_data_file_path():
    """Get the path to the injections.json file."""
    return Path(__file__).parent / "injections.json"


def load_data():
    """Load the injections data from the JSON file."""
    data_file = get_data_file_path()
    if not data_file.exists():
        return {
            "injections": [],
            "categories": [],
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_injections": 0,
                "disclaimer": "This library is for educational and defensive security purposes only."
            }
        }

    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    """Save the injections data to the JSON file."""
    data_file = get_data_file_path()
    data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    data['metadata']['total_injections'] = len(data['injections'])

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_id(data):
    """Get the next available ID for a new injection."""
    if not data['injections']:
        return 1
    return max(inj['id'] for inj in data['injections']) + 1


def print_header(text):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def print_injection_brief(injection):
    """Print a brief summary of an injection."""
    print(f"  {Colors.BOLD}[{injection['id']:3d}]{Colors.ENDC} {Colors.GREEN}{injection['name']}{Colors.ENDC}")
    print(f"       {Colors.DIM}Category: {injection['category']}{Colors.ENDC}")
    print(f"       {Colors.DIM}Tags: {', '.join(injection.get('tags', []))}{Colors.ENDC}")
    print()


def print_injection_detail(injection):
    """Print detailed information about an injection."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'─'*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}ID:{Colors.ENDC} {injection['id']}")
    print(f"{Colors.BOLD}Name:{Colors.ENDC} {Colors.GREEN}{injection['name']}{Colors.ENDC}")
    print(f"{Colors.BOLD}Category:{Colors.ENDC} {Colors.YELLOW}{injection['category']}{Colors.ENDC}")
    print(f"{Colors.BOLD}Tags:{Colors.ENDC} {Colors.CYAN}{', '.join(injection.get('tags', []))}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Description:{Colors.ENDC}")
    print(f"  {injection['description']}")
    print(f"\n{Colors.BOLD}Payload:{Colors.ENDC}")
    print(f"  {Colors.RED}{injection['payload']}{Colors.ENDC}")

    if injection.get('variants'):
        print(f"\n{Colors.BOLD}Variants:{Colors.ENDC}")
        for i, variant in enumerate(injection['variants'], 1):
            print(f"  {i}. {Colors.DIM}{variant}{Colors.ENDC}")

    print(f"{Colors.BOLD}{Colors.GREEN}{'─'*60}{Colors.ENDC}\n")


def cmd_list(args):
    """List all prompt injections."""
    data = load_data()
    injections = data['injections']

    # Filter by category if specified
    if args.category:
        injections = [i for i in injections if i['category'].lower() == args.category.lower()]

    # Filter by tag if specified
    if args.tag:
        injections = [i for i in injections if args.tag.lower() in [t.lower() for t in i.get('tags', [])]]

    if not injections:
        print(f"{Colors.YELLOW}No injections found matching the criteria.{Colors.ENDC}")
        return

    print_header("Prompt Injection Library")
    print(f"{Colors.DIM}Total: {len(injections)} injection(s){Colors.ENDC}\n")

    for injection in injections:
        print_injection_brief(injection)


def cmd_show(args):
    """Show detailed information about a specific injection."""
    data = load_data()

    injection = next((i for i in data['injections'] if i['id'] == args.id), None)

    if not injection:
        print(f"{Colors.RED}Error: Injection with ID {args.id} not found.{Colors.ENDC}")
        sys.exit(1)

    print_injection_detail(injection)


def cmd_search(args):
    """Search injections by keyword."""
    data = load_data()
    query = args.query.lower()

    results = []
    for injection in data['injections']:
        # Search in name, description, payload, and tags
        searchable = ' '.join([
            injection['name'],
            injection['description'],
            injection['payload'],
            ' '.join(injection.get('tags', [])),
            injection['category']
        ]).lower()

        if query in searchable:
            results.append(injection)

    if not results:
        print(f"{Colors.YELLOW}No injections found matching '{args.query}'.{Colors.ENDC}")
        return

    print_header(f"Search Results for '{args.query}'")
    print(f"{Colors.DIM}Found: {len(results)} injection(s){Colors.ENDC}\n")

    for injection in results:
        print_injection_brief(injection)


def cmd_categories(args):
    """List all available categories."""
    data = load_data()

    print_header("Categories")

    # Count injections per category
    category_counts = {}
    for injection in data['injections']:
        cat = injection['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for category in sorted(data['categories']):
        count = category_counts.get(category, 0)
        print(f"  {Colors.YELLOW}{category}{Colors.ENDC} ({count} injection(s))")

    print()


def cmd_tags(args):
    """List all available tags."""
    data = load_data()

    print_header("Tags")

    # Collect all unique tags
    all_tags = {}
    for injection in data['injections']:
        for tag in injection.get('tags', []):
            all_tags[tag] = all_tags.get(tag, 0) + 1

    for tag in sorted(all_tags.keys()):
        print(f"  {Colors.CYAN}{tag}{Colors.ENDC} ({all_tags[tag]} injection(s))")

    print()


def cmd_add(args):
    """Add a new prompt injection."""
    data = load_data()

    print_header("Add New Prompt Injection")

    # Interactive input
    name = input(f"{Colors.BOLD}Name:{Colors.ENDC} ").strip()
    if not name:
        print(f"{Colors.RED}Error: Name is required.{Colors.ENDC}")
        sys.exit(1)

    print(f"\n{Colors.DIM}Available categories: {', '.join(data['categories'])}{Colors.ENDC}")
    category = input(f"{Colors.BOLD}Category:{Colors.ENDC} ").strip()
    if not category:
        print(f"{Colors.RED}Error: Category is required.{Colors.ENDC}")
        sys.exit(1)

    # Add new category if it doesn't exist
    if category not in data['categories']:
        add_cat = input(f"{Colors.YELLOW}Category '{category}' is new. Add it? (y/n):{Colors.ENDC} ").strip().lower()
        if add_cat == 'y':
            data['categories'].append(category)
        else:
            print(f"{Colors.RED}Aborted.{Colors.ENDC}")
            sys.exit(1)

    description = input(f"{Colors.BOLD}Description:{Colors.ENDC} ").strip()
    if not description:
        print(f"{Colors.RED}Error: Description is required.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.DIM}(Use {{placeholder}} for variable parts){Colors.ENDC}")
    payload = input(f"{Colors.BOLD}Payload:{Colors.ENDC} ").strip()
    if not payload:
        print(f"{Colors.RED}Error: Payload is required.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.DIM}(Enter variants one per line, empty line to finish){Colors.ENDC}")
    print(f"{Colors.BOLD}Variants:{Colors.ENDC}")
    variants = []
    while True:
        variant = input("  > ").strip()
        if not variant:
            break
        variants.append(variant)

    print(f"{Colors.DIM}(Comma-separated, e.g., jailbreak, bypass, social){Colors.ENDC}")
    tags_input = input(f"{Colors.BOLD}Tags:{Colors.ENDC} ").strip()
    tags = [t.strip() for t in tags_input.split(',') if t.strip()]

    # Create new injection
    new_injection = {
        "id": get_next_id(data),
        "name": name,
        "category": category,
        "description": description,
        "payload": payload,
        "variants": variants,
        "tags": tags
    }

    data['injections'].append(new_injection)
    save_data(data)

    print(f"\n{Colors.GREEN}Successfully added injection with ID {new_injection['id']}.{Colors.ENDC}")
    print_injection_detail(new_injection)


def cmd_edit(args):
    """Edit an existing prompt injection."""
    data = load_data()

    injection = next((i for i in data['injections'] if i['id'] == args.id), None)

    if not injection:
        print(f"{Colors.RED}Error: Injection with ID {args.id} not found.{Colors.ENDC}")
        sys.exit(1)

    print_header(f"Edit Injection #{args.id}")
    print(f"{Colors.DIM}(Press Enter to keep current value){Colors.ENDC}\n")

    # Edit name
    print(f"{Colors.BOLD}Current name:{Colors.ENDC} {injection['name']}")
    new_name = input(f"{Colors.BOLD}New name:{Colors.ENDC} ").strip()
    if new_name:
        injection['name'] = new_name

    # Edit category
    print(f"\n{Colors.BOLD}Current category:{Colors.ENDC} {injection['category']}")
    print(f"{Colors.DIM}Available: {', '.join(data['categories'])}{Colors.ENDC}")
    new_category = input(f"{Colors.BOLD}New category:{Colors.ENDC} ").strip()
    if new_category:
        if new_category not in data['categories']:
            add_cat = input(f"{Colors.YELLOW}Add new category '{new_category}'? (y/n):{Colors.ENDC} ").strip().lower()
            if add_cat == 'y':
                data['categories'].append(new_category)
        injection['category'] = new_category

    # Edit description
    print(f"\n{Colors.BOLD}Current description:{Colors.ENDC} {injection['description']}")
    new_description = input(f"{Colors.BOLD}New description:{Colors.ENDC} ").strip()
    if new_description:
        injection['description'] = new_description

    # Edit payload
    print(f"\n{Colors.BOLD}Current payload:{Colors.ENDC} {injection['payload']}")
    new_payload = input(f"{Colors.BOLD}New payload:{Colors.ENDC} ").strip()
    if new_payload:
        injection['payload'] = new_payload

    # Edit variants
    print(f"\n{Colors.BOLD}Current variants:{Colors.ENDC}")
    for i, v in enumerate(injection.get('variants', []), 1):
        print(f"  {i}. {v}")

    edit_variants = input(f"{Colors.BOLD}Replace variants? (y/n):{Colors.ENDC} ").strip().lower()
    if edit_variants == 'y':
        print(f"{Colors.DIM}(Enter new variants one per line, empty line to finish){Colors.ENDC}")
        variants = []
        while True:
            variant = input("  > ").strip()
            if not variant:
                break
            variants.append(variant)
        injection['variants'] = variants

    # Edit tags
    print(f"\n{Colors.BOLD}Current tags:{Colors.ENDC} {', '.join(injection.get('tags', []))}")
    new_tags = input(f"{Colors.BOLD}New tags (comma-separated):{Colors.ENDC} ").strip()
    if new_tags:
        injection['tags'] = [t.strip() for t in new_tags.split(',') if t.strip()]

    save_data(data)

    print(f"\n{Colors.GREEN}Successfully updated injection #{args.id}.{Colors.ENDC}")
    print_injection_detail(injection)


def cmd_delete(args):
    """Delete a prompt injection."""
    data = load_data()

    injection = next((i for i in data['injections'] if i['id'] == args.id), None)

    if not injection:
        print(f"{Colors.RED}Error: Injection with ID {args.id} not found.{Colors.ENDC}")
        sys.exit(1)

    print_injection_detail(injection)

    if not args.force:
        confirm = input(f"{Colors.YELLOW}Are you sure you want to delete this injection? (y/n):{Colors.ENDC} ").strip().lower()
        if confirm != 'y':
            print(f"{Colors.DIM}Deletion cancelled.{Colors.ENDC}")
            return

    data['injections'] = [i for i in data['injections'] if i['id'] != args.id]
    save_data(data)

    print(f"{Colors.GREEN}Successfully deleted injection #{args.id}.{Colors.ENDC}")


def cmd_export(args):
    """Export injections to a file."""
    data = load_data()

    # Filter if needed
    injections = data['injections']
    if args.category:
        injections = [i for i in injections if i['category'].lower() == args.category.lower()]

    output = {
        "injections": injections,
        "metadata": data['metadata']
    }

    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        if args.format == 'json':
            json.dump(output, f, indent=2, ensure_ascii=False)
        elif args.format == 'txt':
            for injection in injections:
                f.write(f"[{injection['id']}] {injection['name']}\n")
                f.write(f"Category: {injection['category']}\n")
                f.write(f"Description: {injection['description']}\n")
                f.write(f"Payload: {injection['payload']}\n")
                if injection.get('variants'):
                    f.write("Variants:\n")
                    for v in injection['variants']:
                        f.write(f"  - {v}\n")
                f.write(f"Tags: {', '.join(injection.get('tags', []))}\n")
                f.write("-" * 50 + "\n\n")

    print(f"{Colors.GREEN}Successfully exported {len(injections)} injection(s) to {output_path}.{Colors.ENDC}")


def cmd_import_data(args):
    """Import injections from a JSON file."""
    data = load_data()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"{Colors.RED}Error: File {input_path} not found.{Colors.ENDC}")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        import_data = json.load(f)

    imported = 0
    for injection in import_data.get('injections', []):
        # Assign new ID
        injection['id'] = get_next_id(data)
        data['injections'].append(injection)

        # Add category if new
        if injection['category'] not in data['categories']:
            data['categories'].append(injection['category'])

        imported += 1

    save_data(data)
    print(f"{Colors.GREEN}Successfully imported {imported} injection(s).{Colors.ENDC}")


def cmd_stats(args):
    """Show statistics about the library."""
    data = load_data()

    print_header("Library Statistics")

    print(f"{Colors.BOLD}Total Injections:{Colors.ENDC} {len(data['injections'])}")
    print(f"{Colors.BOLD}Total Categories:{Colors.ENDC} {len(data['categories'])}")

    # Count by category
    category_counts = {}
    for injection in data['injections']:
        cat = injection['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"\n{Colors.BOLD}Injections by Category:{Colors.ENDC}")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        bar = '█' * count
        print(f"  {cat:25} {Colors.GREEN}{bar}{Colors.ENDC} {count}")

    # Count unique tags
    all_tags = set()
    for injection in data['injections']:
        all_tags.update(injection.get('tags', []))

    print(f"\n{Colors.BOLD}Unique Tags:{Colors.ENDC} {len(all_tags)}")
    print(f"{Colors.BOLD}Version:{Colors.ENDC} {data['metadata']['version']}")
    print(f"{Colors.BOLD}Last Updated:{Colors.ENDC} {data['metadata']['last_updated']}")
    print()


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Prompt Injection Library CLI - Manage and explore prompt injection techniques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    List all injections
  %(prog)s list -c Jailbreak       List injections in the Jailbreak category
  %(prog)s list -t bypass          List injections with the 'bypass' tag
  %(prog)s show 5                  Show details for injection #5
  %(prog)s search "ignore"         Search for injections containing "ignore"
  %(prog)s add                     Add a new injection interactively
  %(prog)s edit 3                  Edit injection #3
  %(prog)s delete 7                Delete injection #7
  %(prog)s categories              List all categories
  %(prog)s tags                    List all tags
  %(prog)s stats                   Show library statistics
  %(prog)s export -o backup.json   Export to JSON file
  %(prog)s import -i new.json      Import from JSON file

For educational and defensive security purposes only.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='List all prompt injections')
    list_parser.add_argument('-c', '--category', help='Filter by category')
    list_parser.add_argument('-t', '--tag', help='Filter by tag')
    list_parser.set_defaults(func=cmd_list)

    # Show command
    show_parser = subparsers.add_parser('show', aliases=['get'], help='Show details of a specific injection')
    show_parser.add_argument('id', type=int, help='Injection ID')
    show_parser.set_defaults(func=cmd_show)

    # Search command
    search_parser = subparsers.add_parser('search', aliases=['find'], help='Search injections by keyword')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=cmd_search)

    # Categories command
    cat_parser = subparsers.add_parser('categories', aliases=['cats'], help='List all categories')
    cat_parser.set_defaults(func=cmd_categories)

    # Tags command
    tags_parser = subparsers.add_parser('tags', help='List all tags')
    tags_parser.set_defaults(func=cmd_tags)

    # Add command
    add_parser = subparsers.add_parser('add', aliases=['new'], help='Add a new prompt injection')
    add_parser.set_defaults(func=cmd_add)

    # Edit command
    edit_parser = subparsers.add_parser('edit', aliases=['update'], help='Edit an existing injection')
    edit_parser.add_argument('id', type=int, help='Injection ID')
    edit_parser.set_defaults(func=cmd_edit)

    # Delete command
    delete_parser = subparsers.add_parser('delete', aliases=['rm', 'remove'], help='Delete an injection')
    delete_parser.add_argument('id', type=int, help='Injection ID')
    delete_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=cmd_delete)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export injections to a file')
    export_parser.add_argument('-o', '--output', default='exported_injections.json', help='Output file path')
    export_parser.add_argument('-f', '--format', choices=['json', 'txt'], default='json', help='Output format')
    export_parser.add_argument('-c', '--category', help='Export only this category')
    export_parser.set_defaults(func=cmd_export)

    # Import command
    import_parser = subparsers.add_parser('import', help='Import injections from a JSON file')
    import_parser.add_argument('-i', '--input', required=True, help='Input file path')
    import_parser.set_defaults(func=cmd_import_data)

    # Stats command
    stats_parser = subparsers.add_parser('stats', aliases=['info'], help='Show library statistics')
    stats_parser.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
