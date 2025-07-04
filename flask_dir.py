#!/usr/bin/env python3
"""
Script to create the proper directory structure for Flask templates
Run this script to set up the templates directory with the HTML file
"""

import os

def create_templates_directory():
    """Create templates directory and index.html file"""
    
    # Create templates directory
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"Created {templates_dir} directory")
    
    # HTML content for index.html
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice-Bot</title>
    <style>
        /* Copy the CSS from the HTML artifact above */
    </style>
</head>
<body>
    <!-- Copy the HTML body content from the HTML artifact above -->
</body>
</html>'''
    
    # Write index.html
    index_path = os.path.join(templates_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created {index_path}")
    print("Please copy the complete HTML content from the HTML artifact to this file")

if __name__ == "__main__":
    create_templates_directory()