from deepl import Translator
import re
import os



def initialize_translator():
    api_key = os.getenv('DEEPL_API_KEY')
    print(f'Initializing DeepL translator...')
    translator = Translator(api_key)
    return translator


def translate_text(translator, text: str, source_lang: str = 'EN', target_lang: str = 'ES') -> str:
    # Translate text using DeepL API
    result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    return result.text


def translate(translator, latex_content: str, source_lang: str = 'EN', target_lang: str = 'ES', dry_run: bool = False, do_full: bool = False) -> str:
    translated_content: list[str] = []
    # Split the content using regex that captures paragraphs and newlines
    parts: list[str] = re.split(r'(\n{2,})', latex_content)
    
    for i, part in enumerate(parts):
        
        if part.strip() and not part.startswith('\n'):
            # If it's a paragraph (not just newlines), ask if it should be translated
            print('-'*100)
            print('-'*100)
            print('-'*100)
            print(f"\n\nInput paragraph  {source_lang} -> {target_lang}:")
            print('-'*100)
            print(part)
            print('-'*100)
            
            if do_full:
                do_translate = True
            else:
                do_translate = (input("\nDo you want to translate this paragraph? (y/n): ").strip().lower() == 'y')
            
            
            if do_translate:
                print(f'\n\nOutput paragraph:')
                if dry_run:
                    print(part)
                    translated_content.append(part)  # Keep the original text
                else:
                    translated_text = translate_text(translator, part, source_lang, target_lang)
                    print(translated_text)
                    translated_content.append(translated_text)
            else:
                translated_content.append(part)  # Keep the original text
            
            print('-'*100)
            print('-'*100)
            print('-'*100)
        else:
            # If it's newlines, just append them without translation
            translated_content.append(part)
    

    translated_content: str = ''.join(translated_content)

    print(f'Output translated contet:')
    print('-'*100)
    print(translated_content)
    print('-'*100)
    
    return translated_content
