import re
import json
import shutil
from pathlib import Path

regex_list = [
    re.compile(r'.*?\\begin{document}', re.DOTALL),                     # document
    re.compile(r'\\begin{figure}.*?\\end{figure}', re.DOTALL),          # figures
    re.compile(r'\\begin{equation}.*?\\end{equation}', re.DOTALL),      # equations
    re.compile(r'\\begin{align}.*?\\end{align}', re.DOTALL),            # equations
    re.compile(r'\\begin{equation\*}.*?\\end{equation\*}', re.DOTALL),  # equations
    re.compile(r'\\begin{table}.*?\\end{table}', re.DOTALL),            # tables
    re.compile(r'\\begin{tabular}.*?\\end{tabular}', re.DOTALL),        # tables
    re.compile(r'\\begin{float}.*?\\end{float}', re.DOTALL),            # floats
    re.compile(r'\\begin{tikz}.*?\\end{tikz}', re.DOTALL),              # tiks
    re.compile(r'\\\(.*?\\\)'),                                         # inline equations with \(\)
    re.compile(r'\$.*?\$'),                                             # inline equations with $$
    re.compile(r'\\[a-zA-Z]*?{.*?}'),                                   # commands in the form of \cmd{}
    re.compile(r'\\[a-zA-Z]*?\n'),                                      # commands in the form of \cmd
    re.compile(r'\\begin{.*}', re.DOTALL),                              # begin environments
    re.compile(r'\\end{.*}', re.DOTALL),                                # end environments
    # re.compile(r'\\[a-z]*\s*\[.*\]', re.DOTALL),
    re.compile(r'\\[a-z]*', re.DOTALL),                                 # extra commands
    re.compile(r'[{}]', re.DOTALL),                                     # { and }
]

TRANSLATED_TEMPLATE_FILENAME  : str = '{filebase}.TRANSLATED.tex'
CODED_TEMPLATE_FILENAME       : str = '{filebase}.CODED.tex'
PLACEHOLDERS_TEMPLATE_FILENAME: str = '{filebase}_placeholders.json'

# Remove LaTeX comments from the content
def remove_latex_comments(line):
    return re.sub(r'(?<!\\)%.*', '', line)

def preprocess_line(line):
    line = remove_latex_comments(line)
    return line

def preprocess_file(preprocess_fn, content):
    """
    this script will apply line by line, the preprocessing function passed
    """
    cleaned_content = []
    for line in content:
        # Remove anything after '%' (including % itself)        
        cleaned_line = preprocess_fn(line)
        cleaned_content.append(cleaned_line)
    new_content = '\n'.join(cleaned_content)  # Join lines back into a single string

    # remove trailing newlines
    new_content = new_content.rstrip()
    return new_content


# Step 1: Read the file content
def read_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content

def replace_with_numbering(match, number, content):    
    placeholder = f'#{number}#'

    # Save the placeholder and original substring
    hash_dict = {
        'placeholder': placeholder,
        'substring': match
    }

    content = content.replace(match, placeholder, 1)

    return content, hash_dict

#Step 3: Process each regex and replace matches with numbered placeholders
def replace_with_numbered_placeholders(content, regex_list):
    hash_dict = []

    # Use an infinite counter starting from 1
    counter = 0
    
    for i, compiled_regex in enumerate(regex_list):
        print(f'Using regex {i}')
        for match in re.finditer(compiled_regex, content):
            content, _hash_dict = replace_with_numbering(match.group(), counter, content)
            hash_dict.append(_hash_dict)
            counter += 1

    print(f'The total number of replaced strings is {counter}')

    return content, hash_dict


# Step 4: Save the placeholder dictionary in JSON format
def save_placeholders_json(hash_dict, placeholder_filepath):
    with open(placeholder_filepath, 'w') as file:
        json.dump(hash_dict, file, indent=4)

# Step 5: Write the content with placeholders
def write_file(content, filepath):
    with open(filepath, 'w') as file:
        file.write(content)

# Step 6: Restore the substrings from placeholders
def restore_substrings(content, hash_dict):
    for entry in hash_dict:
        content = content.replace(entry['placeholder'], entry['substring'])
    return content




def encode(output_dir: Path, input_filename: Path):

    # first we copy the file to the output dir
    tmp_input_filename: Path = output_dir/input_filename.name
    shutil.copy(input_filename, tmp_input_filename)
    input_filename = tmp_input_filename
    
    content: str = read_file(input_filename)
    content: str = preprocess_file(preprocess_line, content.split('\n'))

    # Replace substrings with numbered placeholders using multiple regexes
    numbered_content, hash_dict = replace_with_numbered_placeholders(content, regex_list)

    # Save the placeholder dictionary to JSON
    save_placeholders_json(hash_dict, output_dir/PLACEHOLDERS_TEMPLATE_FILENAME.format(filebase=input_filename.stem))

    # Write the content with placeholders
    write_file(numbered_content, output_dir/CODED_TEMPLATE_FILENAME.format(filebase=input_filename.stem))
    
    return


def translate(output_dir: Path, input_filename: Path, dry_run: bool, full_run: bool = False):
    from translate_utils import initialize_translator
    from translate_utils import translate as translate_fn
    
    # retrieve coded tex
    coded_file: Path = output_dir/CODED_TEMPLATE_FILENAME.format(filebase=input_filename.stem)

    with open(coded_file, 'r') as file:
        coded_content = file.read()

    translator = None
    if not dry_run:
        translator = initialize_translator()

    translated_content: str = translate_fn(translator, coded_content, dry_run=dry_run, do_full=full_run)

    write_file(translated_content, output_dir/TRANSLATED_TEMPLATE_FILENAME.format(filebase=input_filename.stem))

    return



def decode(output_dir: Path, input_filename: Path, output_filename: Path):
    
    # Restore the original content using the saved placeholders
    with open(output_dir/PLACEHOLDERS_TEMPLATE_FILENAME.format(filebase=input_filename.stem), 'r') as file:
        saved_hash_dict = json.load(file)
    
    with open(output_dir/TRANSLATED_TEMPLATE_FILENAME.format(filebase=input_filename.stem), 'r') as file:
        coded_content = file.read()
    
    restored_content = restore_substrings(coded_content, saved_hash_dict)

    # Write the restored content back to a file if needed
    with open(output_filename.with_suffix('.tex'), 'w') as file:
        file.write(restored_content)
    
    return



def main(filename: str, output: str, do_encode: bool, do_decode: bool, do_trans: bool, dry_run: bool = False, full_run: bool = False):
    
    input_filename : Path = Path(filename)
    print(f'Input  Filename = {input_filename}')
    
    
    output_dir: Path = Path(input_filename.stem)
    output_dir.mkdir(exist_ok=True)
    print(f'Input/output directory: {output_dir}')
    

    new_input_filename: Path = output_dir/input_filename.stem
    
    if output:
        output_filename: Path = Path(output)
        print(f'Output Filename = {output_filename}')
    else:
        output_filename: Path = new_input_filename.parent / (new_input_filename.stem + '_translated')
        print(f'Output Filename = {output_filename}')



    if do_encode:
        print('Encoding')
        encode(output_dir, input_filename)
    elif do_trans:
        print('Translating')
        translate(output_dir, new_input_filename, dry_run, full_run)
    elif do_decode:
        print('Decoding')
        decode(output_dir, input_filename, output_dir/output_filename)

    return


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-e", "--encode"   , action="store_true")
    parser.add_argument("-d", "--decode"   , action="store_true")
    parser.add_argument("-t", "--translate", action="store_true")
    parser.add_argument("-o", "--output"   , type=str)
    parser.add_argument("-f", "--file"     , help="code FILE")
    parser.add_argument("-n", "--dry_run"  , action="store_true", help="Dry run for translating")
    parser.add_argument("-R", "--full_run" , action="store_true", help="Run over all the latex file")

    args = parser.parse_args()    
    main(args.file, args.output, args.encode, args.decode, args.translate, args.dry_run, args.full_run)
