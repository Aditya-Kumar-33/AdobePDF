#!/usr/bin/env python3
"""
Main execution script for Challenge 1b: Multi-Collection PDF Analysis

This script processes all collections and generates the required output files.
"""

import os
import sys
import json
from datetime import datetime
from src.pdf_analyzer import PDFAnalyzer


def main():
    """Main execution function."""
    print("=" * 60)
    print("Challenge 1b: Multi-Collection PDF Analysis")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the analyzer
    analyzer = PDFAnalyzer()
    
    # Check if we're in the correct directory
    collections = ['Collection 1', 'Collection 2', 'Collection 3']
    missing_collections = []
    
    for collection in collections:
        if not os.path.exists(collection):
            missing_collections.append(collection)
    
    if missing_collections:
        print(f"Warning: Missing collections: {', '.join(missing_collections)}")
        print("Make sure you're running this script from the Challenge_1b directory.")
        print()
    
    # Process all collections
    print("Processing all collections...")
    analyzer.process_all_collections()
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    
    # Generate summary for each collection
    print("\nCollection Summaries:")
    print("-" * 40)
    
    for collection_name in collections:
        collection_path = os.path.join('.', collection_name)
        if os.path.exists(collection_path):
            summary = analyzer.get_analysis_summary(collection_path)
            
            if 'error' in summary:
                print(f"{collection_name}: ERROR - {summary['error']}")
            else:
                print(f"{collection_name}:")
                print(f"  Persona: {summary['persona']}")
                print(f"  Task: {summary['task']}")
                print(f"  Documents: {summary['total_documents']}")
                print(f"  Pages: {summary['total_pages']}")
                print(f"  Sections: {summary['total_sections']}")
                print()
    
    # Validate outputs
    print("Validating outputs...")
    validation_results = []
    
    for collection_name in collections:
        output_file = os.path.join(collection_name, 'challenge1b_output.json')
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                
                is_valid = analyzer.validate_output(output_data)
                validation_results.append((collection_name, is_valid))
                
                if is_valid:
                    print(f"✓ {collection_name}: Output validation passed")
                else:
                    print(f"✗ {collection_name}: Output validation failed")
                    
            except Exception as e:
                print(f"✗ {collection_name}: Error reading output file - {str(e)}")
                validation_results.append((collection_name, False))
        else:
            print(f"✗ {collection_name}: Output file not found")
            validation_results.append((collection_name, False))
    
    # Final summary
    print("\n" + "=" * 60)
    print("Final Summary:")
    print("=" * 60)
    
    successful = sum(1 for _, is_valid in validation_results if is_valid)
    total = len(validation_results)
    
    print(f"Successfully processed: {successful}/{total} collections")
    
    if successful == total:
        print("🎉 All collections processed successfully!")
    else:
        print("⚠️  Some collections had issues. Check the output above for details.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def process_single_collection(collection_name: str):
    """Process a single collection."""
    print(f"Processing single collection: {collection_name}")
    
    analyzer = PDFAnalyzer()
    collection_path = os.path.join('.', collection_name)
    
    if not os.path.exists(collection_path):
        print(f"Error: Collection '{collection_name}' not found")
        return
    
    try:
        output_data = analyzer.analyze_collection(collection_path)
        
        # Save output
        output_file = os.path.join(collection_path, 'challenge1b_output.json')
        analyzer.json_handler.save_output_json(output_data, output_file)
        
        # Validate output
        if analyzer.validate_output(output_data):
            print(f"✓ {collection_name} processed and validated successfully")
        else:
            print(f"✗ {collection_name} processed but validation failed")
            
    except Exception as e:
        print(f"Error processing {collection_name}: {str(e)}")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        collection_name = sys.argv[1]
        process_single_collection(collection_name)
    else:
        main() 