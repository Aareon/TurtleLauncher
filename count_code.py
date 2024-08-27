from pathlib import Path

def count_lines(file_path):
    with file_path.open('r', encoding='utf-8') as file:
        lines = file.readlines()
        
    total_lines = len(lines)
    non_empty_lines = sum(1 for line in lines if line.strip())
    non_comment_lines = sum(1 for line in lines if not line.strip().startswith('#'))
    non_empty_non_comment_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    
    return total_lines, non_empty_lines, non_comment_lines, non_empty_non_comment_lines

def process_directory(directory):
    total_loc = 0
    total_loc_no_whitespace = 0
    total_loc_no_comments = 0
    total_loc_no_whitespace_no_comments = 0
    
    for file_path in Path(directory).rglob('*.py'):
        loc, loc_no_whitespace, loc_no_comments, loc_no_whitespace_no_comments = count_lines(file_path)
        
        total_loc += loc
        total_loc_no_whitespace += loc_no_whitespace
        total_loc_no_comments += loc_no_comments
        total_loc_no_whitespace_no_comments += loc_no_whitespace_no_comments
        
        print(f"File: {file_path}")
        print(f"  LOC: {loc}")
        print(f"  LOC (no whitespace): {loc_no_whitespace}")
        print(f"  LOC (no comments): {loc_no_comments}")
        print(f"  LOC (no whitespace, no comments): {loc_no_whitespace_no_comments}")
        print()
    
    print("Total LOC:")
    print(f"  With whitespace and comments: {total_loc}")
    print(f"  Without whitespace: {total_loc_no_whitespace}")
    print(f"  Without comments: {total_loc_no_comments}")
    print(f"  Without whitespace and comments: {total_loc_no_whitespace_no_comments}")

def main():
    directory = Path(input("Enter the directory path to analyze: "))
    
    if not directory.is_dir():
        print("Error: The specified path is not a valid directory.")
        return
    
    process_directory(directory)

if __name__ == "__main__":
    main()