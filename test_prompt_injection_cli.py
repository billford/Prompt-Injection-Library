#!/usr/bin/env python3
"""
Unit tests for the Prompt Injection Library CLI.
"""
# pylint: disable=redefined-outer-name,unused-argument,too-few-public-methods

import json
import os
import sys
import tempfile
from argparse import Namespace
from pathlib import Path
from unittest import mock

import pytest

# Import the module under test
import prompt_injection_cli as cli


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_data():
    """Return sample test data."""
    return {
        "injections": [
            {
                "id": 1,
                "name": "Test Injection 1",
                "category": "Test Category",
                "description": "Test description 1",
                "payload": "Test payload 1",
                "variants": ["variant 1a", "variant 1b"],
                "tags": ["test", "sample"]
            },
            {
                "id": 2,
                "name": "Test Injection 2",
                "category": "Another Category",
                "description": "Test description 2",
                "payload": "Test payload 2",
                "variants": [],
                "tags": ["test", "demo"]
            },
            {
                "id": 5,
                "name": "Test Injection 5",
                "category": "Test Category",
                "description": "Test description 5",
                "payload": "Test payload 5",
                "variants": ["variant 5a"],
                "tags": ["advanced"]
            }
        ],
        "categories": ["Test Category", "Another Category"],
        "metadata": {
            "version": "1.0.0",
            "last_updated": "2024-01-01",
            "total_injections": 3,
            "disclaimer": "Test disclaimer"
        }
    }


@pytest.fixture
def temp_data_file(sample_data):
    """Create a temporary data file with sample data."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False, encoding='utf-8'
    ) as f:
        json.dump(sample_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_data_file(temp_data_file, monkeypatch):
    """Mock the get_data_file_path to use temporary file."""
    monkeypatch.setattr(cli, 'get_data_file_path', lambda: Path(temp_data_file))
    return temp_data_file


# =============================================================================
# Test Helper Functions
# =============================================================================

class TestGetDataFilePath:
    """Tests for get_data_file_path function."""

    def test_returns_path_object(self):
        """Should return a Path object."""
        result = cli.get_data_file_path()
        assert isinstance(result, Path)

    def test_path_ends_with_injections_json(self):
        """Should return path ending with injections.json."""
        result = cli.get_data_file_path()
        assert result.name == "injections.json"


class TestLoadData:
    """Tests for load_data function."""

    def test_loads_existing_file(self, mock_data_file, sample_data):
        """Should load data from existing file."""
        result = cli.load_data()
        assert result['injections'] == sample_data['injections']
        assert result['categories'] == sample_data['categories']

    def test_returns_default_when_file_missing(self, monkeypatch, tmp_path):
        """Should return default data when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.json"
        monkeypatch.setattr(cli, 'get_data_file_path', lambda: nonexistent)

        result = cli.load_data()

        assert result['injections'] == []
        assert result['categories'] == []
        assert 'metadata' in result


class TestSaveData:
    """Tests for save_data function."""

    def test_saves_data_to_file(self, mock_data_file, sample_data):
        """Should save data to file."""
        sample_data['injections'].append({
            "id": 10,
            "name": "New Injection",
            "category": "Test",
            "description": "desc",
            "payload": "payload",
            "variants": [],
            "tags": []
        })

        cli.save_data(sample_data)

        # Reload and verify
        with open(mock_data_file, 'r', encoding='utf-8') as f:
            saved = json.load(f)

        assert len(saved['injections']) == 4
        assert saved['metadata']['total_injections'] == 4

    def test_updates_metadata_on_save(self, mock_data_file, sample_data):
        """Should update last_updated and total_injections on save."""
        cli.save_data(sample_data)

        with open(mock_data_file, 'r', encoding='utf-8') as f:
            saved = json.load(f)

        assert saved['metadata']['total_injections'] == 3
        assert saved['metadata']['last_updated'] is not None


class TestGetNextId:
    """Tests for get_next_id function."""

    def test_returns_one_for_empty_list(self):
        """Should return 1 when injections list is empty."""
        data = {"injections": []}
        assert cli.get_next_id(data) == 1

    def test_returns_max_plus_one(self, sample_data):
        """Should return max ID + 1."""
        # Sample data has IDs 1, 2, 5
        assert cli.get_next_id(sample_data) == 6

    def test_handles_non_sequential_ids(self):
        """Should handle non-sequential IDs."""
        data = {"injections": [{"id": 10}, {"id": 3}, {"id": 7}]}
        assert cli.get_next_id(data) == 11


# =============================================================================
# Test Print Functions
# =============================================================================

class TestPrintHeader:
    """Tests for print_header function."""

    def test_prints_formatted_header(self, capsys):
        """Should print a formatted header."""
        cli.print_header("Test Header")
        captured = capsys.readouterr()

        assert "Test Header" in captured.out
        assert "=" in captured.out


class TestPrintInjectionBrief:
    """Tests for print_injection_brief function."""

    def test_prints_injection_summary(self, capsys, sample_data):
        """Should print injection summary."""
        injection = sample_data['injections'][0]
        cli.print_injection_brief(injection)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "Test Category" in captured.out
        assert "test" in captured.out

    def test_handles_missing_tags(self, capsys):
        """Should handle injection without tags."""
        injection = {
            "id": 1,
            "name": "No Tags",
            "category": "Test"
        }
        cli.print_injection_brief(injection)
        captured = capsys.readouterr()

        assert "No Tags" in captured.out


class TestPrintInjectionDetail:
    """Tests for print_injection_detail function."""

    def test_prints_full_details(self, capsys, sample_data):
        """Should print all injection details."""
        injection = sample_data['injections'][0]
        cli.print_injection_detail(injection)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "Test Category" in captured.out
        assert "Test description 1" in captured.out
        assert "Test payload 1" in captured.out
        assert "variant 1a" in captured.out

    def test_handles_no_variants(self, capsys, sample_data):
        """Should handle injection without variants."""
        injection = sample_data['injections'][1]  # Has empty variants
        cli.print_injection_detail(injection)
        captured = capsys.readouterr()

        assert "Test Injection 2" in captured.out


# =============================================================================
# Test Command Functions
# =============================================================================

class TestCmdList:
    """Tests for cmd_list command."""

    def test_lists_all_injections(self, mock_data_file, capsys):
        """Should list all injections."""
        args = Namespace(category=None, tag=None)
        cli.cmd_list(args)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "Test Injection 2" in captured.out
        assert "Test Injection 5" in captured.out
        assert "3 injection(s)" in captured.out

    def test_filters_by_category(self, mock_data_file, capsys):
        """Should filter by category."""
        args = Namespace(category="Test Category", tag=None)
        cli.cmd_list(args)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "Test Injection 5" in captured.out
        assert "Test Injection 2" not in captured.out
        assert "2 injection(s)" in captured.out

    def test_filters_by_tag(self, mock_data_file, capsys):
        """Should filter by tag."""
        args = Namespace(category=None, tag="demo")
        cli.cmd_list(args)
        captured = capsys.readouterr()

        assert "Test Injection 2" in captured.out
        assert "Test Injection 1" not in captured.out

    def test_case_insensitive_category_filter(self, mock_data_file, capsys):
        """Should filter category case-insensitively."""
        args = Namespace(category="test category", tag=None)
        cli.cmd_list(args)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out

    def test_no_matches_message(self, mock_data_file, capsys):
        """Should show message when no matches found."""
        args = Namespace(category="Nonexistent", tag=None)
        cli.cmd_list(args)
        captured = capsys.readouterr()

        assert "No injections found" in captured.out


class TestCmdShow:
    """Tests for cmd_show command."""

    def test_shows_existing_injection(self, mock_data_file, capsys):
        """Should show details of existing injection."""
        args = Namespace(id=1)
        cli.cmd_show(args)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "Test description 1" in captured.out

    def test_exits_on_missing_id(self, mock_data_file, capsys):
        """Should exit with error for missing ID."""
        args = Namespace(id=999)

        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_show(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestCmdSearch:
    """Tests for cmd_search command."""

    def test_searches_by_name(self, mock_data_file, capsys):
        """Should find injection by name."""
        args = Namespace(query="Injection 1")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        assert "Test Injection 1" in captured.out
        assert "1 injection(s)" in captured.out

    def test_searches_by_description(self, mock_data_file, capsys):
        """Should find injection by description."""
        args = Namespace(query="description 2")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        assert "Test Injection 2" in captured.out

    def test_searches_by_tag(self, mock_data_file, capsys):
        """Should find injection by tag."""
        args = Namespace(query="advanced")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        assert "Test Injection 5" in captured.out

    def test_searches_by_payload(self, mock_data_file, capsys):
        """Should find injection by payload content."""
        args = Namespace(query="payload 5")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        assert "Test Injection 5" in captured.out

    def test_case_insensitive_search(self, mock_data_file, capsys):
        """Should search case-insensitively."""
        args = Namespace(query="TEST")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        # All injections have "test" in them
        assert "Test Injection 1" in captured.out

    def test_no_results_message(self, mock_data_file, capsys):
        """Should show message when no results found."""
        args = Namespace(query="nonexistent_xyz")
        cli.cmd_search(args)
        captured = capsys.readouterr()

        assert "No injections found" in captured.out


class TestCmdCategories:
    """Tests for cmd_categories command."""

    def test_lists_all_categories(self, mock_data_file, capsys):
        """Should list all categories with counts."""
        args = Namespace()
        cli.cmd_categories(args)
        captured = capsys.readouterr()

        assert "Test Category" in captured.out
        assert "Another Category" in captured.out
        assert "2 injection(s)" in captured.out  # Test Category has 2
        assert "1 injection(s)" in captured.out  # Another Category has 1


class TestCmdTags:
    """Tests for cmd_tags command."""

    def test_lists_all_tags(self, mock_data_file, capsys):
        """Should list all unique tags with counts."""
        args = Namespace()
        cli.cmd_tags(args)
        captured = capsys.readouterr()

        assert "test" in captured.out
        assert "sample" in captured.out
        assert "demo" in captured.out
        assert "advanced" in captured.out


class TestCmdStats:
    """Tests for cmd_stats command."""

    def test_shows_statistics(self, mock_data_file, capsys):
        """Should show library statistics."""
        args = Namespace()
        cli.cmd_stats(args)
        captured = capsys.readouterr()

        assert "Total Injections:" in captured.out
        assert "3" in captured.out  # 3 injections
        assert "Total Categories:" in captured.out
        assert "2" in captured.out  # 2 categories
        assert "Unique Tags:" in captured.out


class TestCmdAdd:
    """Tests for cmd_add command."""

    def test_adds_new_injection(self, mock_data_file, capsys):
        """Should add a new injection interactively."""
        inputs = [
            "New Test Injection",  # name
            "Test Category",  # category (existing)
            "A new description",  # description
            "New payload here",  # payload
            "variant A",  # variant 1
            "variant B",  # variant 2
            "",  # end variants
            "new, tags",  # tags
        ]

        with mock.patch('builtins.input', side_effect=inputs):
            args = Namespace()
            cli.cmd_add(args)

        # Verify it was added
        data = cli.load_data()
        new_inj = next(
            (i for i in data['injections'] if i['name'] == "New Test Injection"),
            None
        )
        assert new_inj is not None
        assert new_inj['description'] == "A new description"
        assert new_inj['payload'] == "New payload here"
        assert "variant A" in new_inj['variants']
        assert "new" in new_inj['tags']

    def test_exits_on_empty_name(self, mock_data_file, capsys):
        """Should exit if name is empty."""
        with mock.patch('builtins.input', return_value=""):
            args = Namespace()

            with pytest.raises(SystemExit) as exc_info:
                cli.cmd_add(args)

            assert exc_info.value.code == 1

    def test_adds_new_category_when_confirmed(self, mock_data_file, capsys):
        """Should add new category when user confirms."""
        inputs = [
            "New Injection",
            "Brand New Category",  # New category
            "y",  # Confirm new category
            "description",
            "payload",
            "",  # No variants
            "tag1",
        ]

        with mock.patch('builtins.input', side_effect=inputs):
            args = Namespace()
            cli.cmd_add(args)

        data = cli.load_data()
        assert "Brand New Category" in data['categories']


class TestCmdEdit:
    """Tests for cmd_edit command."""

    def test_edits_existing_injection(self, mock_data_file, capsys):
        """Should edit an existing injection."""
        inputs = [
            "Updated Name",  # New name
            "",  # Keep category
            "Updated description",  # New description
            "",  # Keep payload
            "n",  # Don't replace variants
            "newtag1, newtag2",  # New tags
        ]

        with mock.patch('builtins.input', side_effect=inputs):
            args = Namespace(id=1)
            cli.cmd_edit(args)

        data = cli.load_data()
        edited = next(i for i in data['injections'] if i['id'] == 1)
        assert edited['name'] == "Updated Name"
        assert edited['description'] == "Updated description"
        assert "newtag1" in edited['tags']

    def test_keeps_values_on_empty_input(self, mock_data_file, capsys):
        """Should keep original values when input is empty."""
        inputs = ["", "", "", "", "n", ""]  # All empty except variants question

        with mock.patch('builtins.input', side_effect=inputs):
            args = Namespace(id=1)
            cli.cmd_edit(args)

        data = cli.load_data()
        edited = next(i for i in data['injections'] if i['id'] == 1)
        assert edited['name'] == "Test Injection 1"  # Unchanged

    def test_exits_on_missing_id(self, mock_data_file, capsys):
        """Should exit with error for missing ID."""
        args = Namespace(id=999)

        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_edit(args)

        assert exc_info.value.code == 1


class TestCmdDelete:
    """Tests for cmd_delete command."""

    def test_deletes_with_force(self, mock_data_file, capsys):
        """Should delete without confirmation when force is True."""
        args = Namespace(id=1, force=True)
        cli.cmd_delete(args)

        data = cli.load_data()
        assert not any(i['id'] == 1 for i in data['injections'])
        assert len(data['injections']) == 2

    def test_deletes_with_confirmation(self, mock_data_file, capsys):
        """Should delete after user confirms."""
        with mock.patch('builtins.input', return_value="y"):
            args = Namespace(id=1, force=False)
            cli.cmd_delete(args)

        data = cli.load_data()
        assert not any(i['id'] == 1 for i in data['injections'])

    def test_cancels_on_no_confirmation(self, mock_data_file, capsys):
        """Should cancel deletion when user says no."""
        with mock.patch('builtins.input', return_value="n"):
            args = Namespace(id=1, force=False)
            cli.cmd_delete(args)

        data = cli.load_data()
        assert any(i['id'] == 1 for i in data['injections'])
        captured = capsys.readouterr()
        assert "cancelled" in captured.out

    def test_exits_on_missing_id(self, mock_data_file, capsys):
        """Should exit with error for missing ID."""
        args = Namespace(id=999, force=True)

        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_delete(args)

        assert exc_info.value.code == 1


class TestCmdExport:
    """Tests for cmd_export command."""

    def test_exports_to_json(self, mock_data_file, tmp_path):
        """Should export all injections to JSON file."""
        output_file = tmp_path / "export.json"
        args = Namespace(output=str(output_file), format='json', category=None)

        cli.cmd_export(args)

        assert output_file.exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert len(exported['injections']) == 3

    def test_exports_to_txt(self, mock_data_file, tmp_path):
        """Should export all injections to TXT file."""
        output_file = tmp_path / "export.txt"
        args = Namespace(output=str(output_file), format='txt', category=None)

        cli.cmd_export(args)

        assert output_file.exists()
        content = output_file.read_text()
        assert "Test Injection 1" in content
        assert "Test payload 1" in content

    def test_exports_filtered_by_category(self, mock_data_file, tmp_path):
        """Should export only specified category."""
        output_file = tmp_path / "export.json"
        args = Namespace(
            output=str(output_file), format='json', category='Test Category'
        )

        cli.cmd_export(args)

        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert len(exported['injections']) == 2  # Only Test Category


class TestCmdImport:
    """Tests for cmd_import_data command."""

    def test_imports_from_json(self, mock_data_file, tmp_path):
        """Should import injections from JSON file."""
        import_file = tmp_path / "import.json"
        import_data = {
            "injections": [
                {
                    "name": "Imported Injection",
                    "category": "Import Category",
                    "description": "Imported desc",
                    "payload": "Imported payload",
                    "variants": [],
                    "tags": ["imported"]
                }
            ]
        }
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump(import_data, f)

        args = Namespace(input=str(import_file))
        cli.cmd_import_data(args)

        data = cli.load_data()
        assert len(data['injections']) == 4  # 3 + 1 imported
        imported = next(
            (i for i in data['injections'] if i['name'] == "Imported Injection"),
            None
        )
        assert imported is not None
        assert "Import Category" in data['categories']

    def test_exits_on_missing_file(self, mock_data_file, capsys):
        """Should exit with error for missing import file."""
        args = Namespace(input="/nonexistent/file.json")

        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_import_data(args)

        assert exc_info.value.code == 1


# =============================================================================
# Test Main Function and Argument Parsing
# =============================================================================

class TestMain:
    """Tests for main function."""

    def test_shows_help_with_no_command(self, capsys, monkeypatch):
        """Should show help when no command provided."""
        monkeypatch.setattr(sys, 'argv', ['prompt_injection_cli.py'])

        with pytest.raises(SystemExit) as exc_info:
            cli.main()

        assert exc_info.value.code == 0

    def test_list_command_alias(self, mock_data_file, capsys, monkeypatch):
        """Should accept 'ls' as alias for 'list'."""
        monkeypatch.setattr(sys, 'argv', ['prompt_injection_cli.py', 'ls'])
        cli.main()
        captured = capsys.readouterr()
        assert "Prompt Injection Library" in captured.out

    def test_show_command_alias(self, mock_data_file, capsys, monkeypatch):
        """Should accept 'get' as alias for 'show'."""
        monkeypatch.setattr(sys, 'argv', ['prompt_injection_cli.py', 'get', '1'])
        cli.main()
        captured = capsys.readouterr()
        assert "Test Injection 1" in captured.out


# =============================================================================
# Test Colors Class
# =============================================================================

class TestColors:
    """Tests for Colors class."""

    def test_color_codes_are_strings(self):
        """Should have string color codes."""
        assert isinstance(cli.Colors.RED, str)
        assert isinstance(cli.Colors.GREEN, str)
        assert isinstance(cli.Colors.BOLD, str)

    def test_color_codes_are_ansi_sequences(self):
        """Should have valid ANSI escape sequences."""
        assert cli.Colors.RED.startswith('\033[')
        assert cli.Colors.ENDC == '\033[0m'


# =============================================================================
# Test Edge Cases and Security
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and security concerns."""

    def test_handles_unicode_content(self, mock_data_file, capsys):
        """Should handle unicode characters in content."""
        data = cli.load_data()
        data['injections'].append({
            "id": 100,
            "name": "Unicode Test \u00e9\u00e0\u00fc",
            "category": "Test Category",
            "description": "Description with \u4e2d\u6587",
            "payload": "\u0418\u0433\u043d\u043e\u0440\u0435 instructions",
            "variants": [],
            "tags": ["\u65e5\u672c\u8a9e"]
        })
        cli.save_data(data)

        # Should be able to load and display
        args = Namespace(id=100)
        cli.cmd_show(args)
        captured = capsys.readouterr()
        assert "Unicode Test" in captured.out

    def test_handles_empty_data_file(self, monkeypatch, tmp_path, capsys):
        """Should handle empty/new data gracefully."""
        empty_file = tmp_path / "empty.json"
        monkeypatch.setattr(cli, 'get_data_file_path', lambda: empty_file)

        args = Namespace(category=None, tag=None)
        cli.cmd_list(args)
        captured = capsys.readouterr()
        assert "No injections found" in captured.out

    def test_handles_special_chars_in_search(self, mock_data_file, capsys):
        """Should handle special regex characters in search."""
        args = Namespace(query="test.*")
        cli.cmd_search(args)
        # Should not crash, may or may not find results

    def test_large_id_numbers(self, mock_data_file):
        """Should handle large ID numbers."""
        data = cli.load_data()
        data['injections'].append({
            "id": 999999,
            "name": "Large ID",
            "category": "Test",
            "description": "desc",
            "payload": "payload",
            "variants": [],
            "tags": []
        })
        cli.save_data(data)

        assert cli.get_next_id(cli.load_data()) == 1000000


class TestFileOperationsSecurity:
    """Tests for secure file operations."""

    def test_uses_utf8_encoding(self, mock_data_file):
        """Should use UTF-8 encoding for file operations."""
        data = cli.load_data()
        data['injections'][0]['name'] = "Test \u00e9\u00e0\u00fc\u00f1"
        cli.save_data(data)

        with open(mock_data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "\u00e9\u00e0\u00fc\u00f1" in content

    def test_json_pretty_printed(self, mock_data_file):
        """Should save JSON with indentation for readability."""
        data = cli.load_data()
        cli.save_data(data)

        with open(mock_data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Pretty printed JSON has newlines
        assert '\n' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
