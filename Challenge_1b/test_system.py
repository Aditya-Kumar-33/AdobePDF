#!/usr/bin/env python3
"""
Test script for Challenge 1b PDF Analysis System

This script validates the system functionality and output quality.
"""

import os
import json
import sys
from datetime import datetime
from src.pdf_analyzer import PDFAnalyzer


def test_system():
    """Run comprehensive system tests."""
    print("=" * 60)
    print("Challenge 1b System Test")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analyzer = PDFAnalyzer()
    
    # Test 1: Check if all collections exist
    print("Test 1: Collection Availability")
    print("-" * 30)
    collections = ['Collection 1', 'Collection 2', 'Collection 3']
    
    for collection in collections:
        if os.path.exists(collection):
            print(f"✅ {collection}: Found")
        else:
            print(f"❌ {collection}: Missing")
    print()
    
    # Test 2: Validate input files
    print("Test 2: Input File Validation")
    print("-" * 30)
    
    for collection in collections:
        input_file = os.path.join(collection, 'challenge1b_input.json')
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check required fields
                required_fields = ['challenge_info', 'documents', 'persona', 'job_to_be_done']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"✅ {collection}: Input file valid")
                else:
                    print(f"❌ {collection}: Missing fields - {missing_fields}")
                    
            except Exception as e:
                print(f"❌ {collection}: Error reading input - {str(e)}")
        else:
            print(f"❌ {collection}: Input file not found")
    print()
    
    # Test 3: Check PDF files
    print("Test 3: PDF File Availability")
    print("-" * 30)
    
    for collection in collections:
        pdf_dir = os.path.join(collection, 'PDFs')
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
            print(f"✅ {collection}: {len(pdf_files)} PDF files found")
        else:
            print(f"❌ {collection}: PDF directory not found")
    print()
    
    # Test 4: Process each collection
    print("Test 4: Collection Processing")
    print("-" * 30)
    
    for collection in collections:
        collection_path = os.path.join('.', collection)
        if os.path.exists(collection_path):
            try:
                print(f"Processing {collection}...")
                output_data = analyzer.analyze_collection(collection_path)
                
                # Validate output
                if analyzer.validate_output(output_data):
                    print(f"✅ {collection}: Processed and validated successfully")
                else:
                    print(f"❌ {collection}: Processing failed validation")
                    
            except Exception as e:
                print(f"❌ {collection}: Processing error - {str(e)}")
        else:
            print(f"❌ {collection}: Collection not found")
    print()
    
    # Test 5: Output file validation
    print("Test 5: Output File Validation")
    print("-" * 30)
    
    for collection in collections:
        output_file = os.path.join(collection, 'challenge1b_output.json')
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                
                # Check structure
                if 'metadata' in output_data and 'extracted_sections' in output_data and 'subsection_analysis' in output_data:
                    print(f"✅ {collection}: Output structure valid")
                    
                    # Check content
                    sections_count = len(output_data.get('extracted_sections', []))
                    subsections_count = len(output_data.get('subsection_analysis', []))
                    
                    print(f"   - Extracted sections: {sections_count}")
                    print(f"   - Subsection analysis: {subsections_count}")
                    
                else:
                    print(f"❌ {collection}: Invalid output structure")
                    
            except Exception as e:
                print(f"❌ {collection}: Error reading output - {str(e)}")
        else:
            print(f"❌ {collection}: Output file not found")
    print()
    
    # Test 6: Content quality assessment
    print("Test 6: Content Quality Assessment")
    print("-" * 30)
    
    for collection in collections:
        output_file = os.path.join(collection, 'challenge1b_output.json')
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                
                # Check metadata
                metadata = output_data.get('metadata', {})
                persona = metadata.get('persona', '')
                task = metadata.get('job_to_be_done', '')
                
                print(f"✅ {collection}:")
                print(f"   - Persona: {persona}")
                print(f"   - Task: {task[:50]}...")
                
                # Check section quality
                sections = output_data.get('extracted_sections', [])
                if sections:
                    avg_title_length = sum(len(s.get('section_title', '')) for s in sections) / len(sections)
                    print(f"   - Average section title length: {avg_title_length:.1f} characters")
                
                # Check subsection quality
                subsections = output_data.get('subsection_analysis', [])
                if subsections:
                    avg_text_length = sum(len(s.get('refined_text', '')) for s in subsections) / len(subsections)
                    print(f"   - Average refined text length: {avg_text_length:.1f} characters")
                
            except Exception as e:
                print(f"❌ {collection}: Quality assessment error - {str(e)}")
    print()
    
    # Test 7: Performance metrics
    print("Test 7: Performance Metrics")
    print("-" * 30)
    
    for collection in collections:
        collection_path = os.path.join('.', collection)
        if os.path.exists(collection_path):
            summary = analyzer.get_analysis_summary(collection_path)
            
            if 'error' not in summary:
                print(f"✅ {collection}:")
                print(f"   - Documents: {summary.get('total_documents', 0)}")
                print(f"   - Pages: {summary.get('total_pages', 0)}")
                print(f"   - Sections: {summary.get('total_sections', 0)}")
            else:
                print(f"❌ {collection}: {summary['error']}")
    print()
    
    # Final summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    # Count successful tests
    successful_collections = 0
    for collection in collections:
        output_file = os.path.join(collection, 'challenge1b_output.json')
        if os.path.exists(output_file):
            successful_collections += 1
    
    print(f"Successfully processed: {successful_collections}/{len(collections)} collections")
    
    if successful_collections == len(collections):
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def test_single_collection(collection_name: str):
    """Test a single collection."""
    print(f"Testing collection: {collection_name}")
    
    analyzer = PDFAnalyzer()
    collection_path = os.path.join('.', collection_name)
    
    if not os.path.exists(collection_path):
        print(f"Error: Collection '{collection_name}' not found")
        return
    
    try:
        # Process collection
        output_data = analyzer.analyze_collection(collection_path)
        
        # Validate output
        if analyzer.validate_output(output_data):
            print(f"✅ {collection_name}: Processing successful")
            
            # Show summary
            summary = analyzer.get_analysis_summary(collection_path)
            if 'error' not in summary:
                print(f"   - Documents: {summary.get('total_documents', 0)}")
                print(f"   - Pages: {summary.get('total_pages', 0)}")
                print(f"   - Sections: {summary.get('total_sections', 0)}")
                print(f"   - Persona: {summary.get('persona', '')}")
                print(f"   - Task: {summary.get('task', '')}")
        else:
            print(f"❌ {collection_name}: Validation failed")
            
    except Exception as e:
        print(f"❌ {collection_name}: Error - {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        collection_name = sys.argv[1]
        test_single_collection(collection_name)
    else:
        test_system() 