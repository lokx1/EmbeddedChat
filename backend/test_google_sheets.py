"""
Test Google Sheets access without authentication
Using public CSV export method
"""
import requests
import pandas as pd
import json


def get_google_sheets_as_csv(spreadsheet_id: str, gid: str = "0"):
    """
    Get Google Sheets data as CSV (works for public sheets)
    """
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse CSV data
        from io import StringIO
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        return {
            'success': True,
            'data': data,
            'rows': len(data),
            'columns': list(df.columns) if not df.empty else []
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


def test_spreadsheet(spreadsheet_id: str):
    """Test accessing the specific spreadsheet"""
    print(f"Testing spreadsheet: {spreadsheet_id}")
    
    result = get_google_sheets_as_csv(spreadsheet_id)
    
    if result['success']:
        print(f"✅ Success! Found {result['rows']} rows")
        print(f"📊 Columns: {result['columns']}")
        
        # Show first few rows
        if result['data']:
            print("\n📋 First 3 rows:")
            for i, row in enumerate(result['data'][:3]):
                print(f"  Row {i+1}: {row}")
        
    else:
        print(f"❌ Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Test the specific spreadsheet
    spreadsheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    result = test_spreadsheet(spreadsheet_id)
