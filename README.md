# Buckeling Automation

A Python automation tool for streamlining buckeling calculations by automating input of multiple depth and surface weight combinations and collecting FOE (Force on Element) results.

## Features

- **Table-Based Input**: Enter multiple depth and surface weight combinations in a spreadsheet-like interface
- **Paste from Excel**: Copy data directly from Excel or other spreadsheet applications and paste into the input table
- **Batch Processing**: Automatically process multiple input rows in sequence
- **Real-time Progress**: Visual feedback during automation with row-by-row status updates
- **Results Table**: View all results in an organized table format
- **Export Results**: Copy results to clipboard for pasting into Excel or other applications
- **Error Handling**: Robust error handling with user-friendly messages

## Requirements

- Python 3.8 or higher
- Windows OS
- Orpheus application installed and running

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Running from Source

1. Ensure Orpheus application is running
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Run the automation GUI:
   ```powershell
   python main.py
   ```
4. **Add input rows** using one of these methods:
   - Click "Add Row" to manually add rows one at a time
   - Copy data from Excel (Depth and Surface Weight columns) and click "Paste Rows"
   - Double-click any cell to edit values
5. Click "Run Automation" to process all rows
6. Results will appear in the right pane as they are calculated
7. Click "Copy Results" to copy the results table to your clipboard

### Pasting from Excel

You can copy multiple rows directly from Excel:

1. In Excel, select columns with Depth and Surface Weight data (with or without headers)
2. Copy the selection (Ctrl+C)
3. In the Buckeling Automation app, click "Paste Rows"
4. The data will be automatically inserted into the input table

### Building Executable

To create a standalone executable:

```powershell
pyinstaller --onefile --windowed --name "BuckelingAutomation" main.py
```

The executable will be created in the `dist/` folder.

## Project Structure

- `main.py` - Application entry point
- `Automation.py` - Main GUI application with table-based input and batch processing
- `Button_Repository.py` - Low-level UI automation functions for Orpheus
- `requirements.txt` - Python package dependencies
- `version.py` - Version tracking
- `.gitignore` - Git ignore rules

## Components

### Button_Repository Class

Provides methods to interact with Orpheus UI elements:
- `Surface_Weight_Button()` - Click surface weight option
- `Surface_Weight_Button_Value(value)` - Set surface weight value
- `Depth_Value(value)` - Set depth value
- `Refresh()` - Refresh calculations
- `Bypass_Warning_Button()` - Handle warning dialogs
- `FOE_Value()` - Retrieve FOE result

### Automation GUI

**Input Features:**
- Spreadsheet-like table for entering multiple depth/weight combinations
- Add/Remove rows
- Edit cells with double-click
- Paste multiple rows from clipboard
- Delete selected rows with Delete key

**Automation Features:**
- Run/Stop buttons for batch processing
- Progress status display
- Background threading to keep UI responsive

**Results Features:**
- Results table showing all processed data
- Copy results to clipboard for Excel
- Columns: Depth, Surface Weight, FOE Value

## Version History

### v1.0.0
- Initial release
- Table-based GUI for multiple inputs
- Batch processing with progress tracking
- Paste from Excel support
- Results table with copy to clipboard

## Author

Brad Smith

## License

Proprietary - Internal Use Only
