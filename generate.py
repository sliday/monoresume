import yaml
from markdown import markdown as md
from jinja2 import Template, Environment
from colorama import init, Fore, Style
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import argparse
import PyPDF2
import os
import ell
import fitz
import re
import requests
from urllib.parse import urlparse
from datetime import datetime
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import emoji
import shutil
import colorama
import random
from spinners import Spinners
from halo import Halo

# Initialize colorama
colorama.init()

def read_and_encode_file(file_path):
    parsed_url = urlparse(file_path)
    if parsed_url.scheme in ['http', 'https']:
        # It's a URL, use requests to fetch content
        response = requests.get(file_path)
        content = response.content
    else:
        # It's a local file, read as before
        with open(file_path, 'rb') as file:
            content = file.read()
    return base64.b64encode(content).decode('utf-8')

def generate_favicon_base64(name, theme_name):
    initials = ''.join([word[0].upper() for word in name.split()[:2]])
    
    theme_colors = {
        'default': {'bg': '#1a1a1a', 'fg': '#e0e0e0'},
        'solarized': {'bg': '#002b36', 'fg': '#839496'},
        'terminal': {'bg': '#2e3436', 'fg': '#d3d7cf'},
        'surprise': {'bg': '#3a3a3a', 'fg': '#f0f0f0'}  # Default colors for surprise theme
    }
    
    # If it's a surprise theme, read colors from the generated CSS file
    if theme_name == 'surprise':
        try:
            with open('theme_surprise_light.css', 'r') as f:
                css_content = f.read()
                bg_color = re.search(r'--background-color:\s*(#[A-Fa-f0-9]{6})', css_content)
                fg_color = re.search(r'--text-color:\s*(#[A-Fa-f0-9]{6})', css_content)
                if bg_color and fg_color:
                    theme_colors['surprise']['bg'] = bg_color.group(1)
                    theme_colors['surprise']['fg'] = fg_color.group(1)
        except FileNotFoundError:
            print("Surprise theme CSS file not found. Using default colors.")
    
    bg_color = theme_colors[theme_name]['bg']
    fg_color = theme_colors[theme_name]['fg']
    
    img = Image.new("RGB", (32, 32), bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((8, 8), initials, font=font, fill=fg_color)
    buffer = BytesIO()
    img.save(buffer, format="ICO")
    return base64.b64encode(buffer.getvalue()).decode('ascii')

def choose_theme():
    while True:
        print(f"\n{Fore.CYAN}Choose an option:{Style.RESET_ALL}")
        print(f"1. {Fore.MAGENTA}🎨  Surprise me! (Default){Style.RESET_ALL}")
        print(f"2. {Fore.WHITE}🖥️  Black & white{Style.RESET_ALL}")
        print(f"3. {Fore.YELLOW}☀️  Solarized{Style.RESET_ALL}")
        print(f"4. {Fore.GREEN}💻  Terminal{Style.RESET_ALL}")
        choice = input(f"{Fore.MAGENTA}Enter 1, 2, 3, or 4 (default is 1): {Style.RESET_ALL}")
        if choice == '':
            choice = '1'  # Set default to 'Surprise me!'
        if choice in ['1', '2', '3', '4']:
            theme_name = {
                '1': 'surprise',
                '2': 'default',
                '3': 'solarized',
                '4': 'terminal'
            }[choice]
            theme_files = {
                'surprise': ['theme_surprise_light.css', 'theme_surprise_dark.css'],
                'default': ['theme_light.css', 'theme_dark.css'],
                'solarized': ['theme_solarized_light.css', 'theme_solarized_dark.css'],
                'terminal': ['theme_terminal_light.css', 'theme_terminal_dark.css']
            }[theme_name]
            if theme_name == 'surprise':
                generate_surprise_themes()
            return theme_name, theme_files
        print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")

@ell.simple(model="claude-3-5-sonnet-20240620", max_tokens=1000)
def generate_surprise_light_theme():
    """Generate a retro computing inspired CSS color scheme for a light theme."""
    prompt = """Create a CSS color scheme inspired by retro computing for a light theme. 
    The scheme should include colors for: text, text-alt, background, background-alt, border, link, button-hover, placeholder, selection-background, and selection-color.
    Return the results as CSS root variable declarations in the following format:

    :root {
      --text-color: #XXXXXX;
      --text-color-alt: #XXXXXX;
      --background-color: #XXXXXX;
      --background-color-alt: #XXXXXX;
      --border-color: #XXXXXX;
      --link-color: #XXXXXX;
      --button-hover-color: #XXXXXX;
      --placeholder-color: #XXXXXX;
      --selection-background: #XXXXXX;
      --selection-color: #XXXXXX;
    }

    ::selection {
        background: var(--selection-background);
        color: var(--selection-color);
    }

    Ensure the colors are appropriate for a light theme (i.e., light background, dark text) and maintain good contrast for readability.
    Use color names that reflect the retro computing inspiration (e.g., 'commodore-blue', 'apple-beige', etc.).
    No \`\`\` or ``` or ```yaml or ```json or ```json5 or ``` or --- or any other formatting. Just clean css.
    """
    return prompt

@ell.simple(model="claude-3-5-sonnet-20240620", max_tokens=1000)
def generate_surprise_dark_theme(light_theme):
    """Generate a retro computing inspired CSS color scheme for a dark theme based on the light theme."""
    prompt = f"""Given the following light theme CSS variables:

    {light_theme}

    Create a corresponding dark theme version inspired by retro computing. 
    The scheme should include colors for: text, text-alt, background, background-alt, border, link, button-hover, placeholder, selection-background, and selection-color.
    Return the results as CSS root variable declarations in the following format:

    :root {{
      --text-color: #XXXXXX;
      --text-color-alt: #XXXXXX;
      --background-color: #XXXXXX;
      --background-color-alt: #XXXXXX;
      --border-color: #XXXXXX;
      --link-color: #XXXXXX;
      --button-hover-color: #XXXXXX;
      --placeholder-color: #XXXXXX;
      --selection-background: #XXXXXX;
      --selection-color: #XXXXXX;
    }}

    ::selection {{
        background: var(--selection-background);
        color: var(--selection-color);
    }}

    Ensure the colors are appropriate for a dark theme (i.e., dark background, light text) and maintain good contrast for readability.
    Use color names that reflect the retro computing inspiration and correspond to the light theme names.
    Aim for a cohesive look between the light and dark themes while ensuring they are distinct and suitable for their respective purposes.
    No \`\`\` or ``` or ```yaml or ```json or ```json5 or ``` or --- or any other formatting. Just clean css.
    """
    return prompt

def generate_surprise_themes():
    """Generate retro computing inspired CSS color schemes for light and dark themes."""
    light_theme = generate_surprise_light_theme()
    dark_theme = generate_surprise_dark_theme(light_theme)
    
    # Save the themes to files
    with open('theme_surprise_light.css', 'w') as f:
        f.write(light_theme)
    with open('theme_surprise_dark.css', 'w') as f:
        f.write(dark_theme)
    
    return ['theme_surprise_light.css', 'theme_surprise_dark.css']

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

@ell.simple(model="claude-3-5-sonnet-20240620", max_tokens=8192)
def unify_format(extracted_data: str) -> str:
    """You are a resume parser that converts raw text into a clean, structured markdown format."""
    prompt = """
    Given the following raw text extracted from a resume, convert it into a unified format following these guidelines:

    Resume Object Model Definition (Markdown):
    ===
    # Full legal name as it appears on official documents or as preferred professionally.        | First and last name; include middle name or initial if commonly used. | Use your professional or legal name.     |
    ## Specific position or role aimed for, aligned with the job you're applying for to showcase career focus. | Concise title, typically 2-5 words. | Be specific to highlight your career goals. |

    Format: Email / Phone / Country / City
    | Field      | Description                                                        | Expected Length                | Guidelines                                         |
    |------------|--------------------------------------------------------------------|--------------------------------|----------------------------------------------------|
    | **Email**  | Professional email address (e.g., name@example.com).               | Standard email format          | Use a professional email; avoid unprofessional addresses. |
    | **Phone**  | Primary contact number, including country code if applicable.      | Include country code if applicable | Provide a reliable contact number.                  |
    | **Country**| Full country name of current residence.                            | Full country name              | Specify for relocation considerations.             |
    | **City**   | Full city name of current residence if available.                          | Full city name                 | Indicates proximity to job location.               |

    MUST omit if any of the fields are not provided.

    ## Summary

    Format: plain text

    | Field      | Description                                                                                                                | Expected Length                | Guidelines                           |
    |------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------------------------|
    | **Summary**| Brief overview of qualifications and career goals, highlighting key skills, experiences, and achievements aligned with the desired job. | Mention quantifiable data. STAR format, approximately 5-6 sentences or bullet points | Keep it concise and impactful.       |

    Format: _skill, skill, skill_   

    | Field      | Description                                                                                                                | Expected Length                | Guidelines                           |
    |------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------------------------|
    | **Skills**| List of skills (1-2 words each), separated by commas. | Mention technical skills, programming languages, frameworks, tools, and any other relevant skills. SCan the original data and find the skills. | 1-2 words each, 6-12 skills      |


    ## Employment History

    **Description**: Chronological list of past employment experiences (**one or more** entries).
    Format: Company / Job Title / Location

    Start - End Date

    Responsibilities (list or description)

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Company**      | Name of employer; include brief descriptor if not well-known.         | Full official name     | Provide context for lesser-known companies.          |
    | **Job Title**    | Official title held; accurately reflects roles and responsibilities.  | Standard job title     | Use accurate and professional titles.                |
    | **Location**     | City, State/Province, Country.                                        | Full location          | Provides context about work environment.             |
    | **Start - End Date** | Employment period (e.g., June 2015 - Present).                       | Format as 'Month Year' | Ensure accuracy and consistency in formatting.       |
    | **Responsibilities** | Key duties, achievements, contributions (**one or more** bullet points). | ~3-6 bullet points     | Start with action verbs; quantify achievements when possible. |

    ## Education

    **Description**: Academic qualifications and degrees obtained (**one or more** entries).
    Format: Institution / Degree / Location

    Start - End Date

    Description (if any)

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Institution**  | Name of educational institution; add location if not widely known.    | Full official name     | Provide context for lesser-known institutions.       |
    | **Degree**       | Degree or certification earned; specify field of study.               | Full degree title      | Highlight relevance to desired job.                  |
    | **Location**     | City, State/Province, Country.                                        | Full location          | Provides context about institution's setting.        |
    | **Start - End Date** | Education period (e.g., August 2004 - May 2008).                     | Format as 'Month Year' | Use consistent formatting.                           |
    | **Description**    | Additional information about the education (if any).                  | ~1-2 sentences         | Include if relevant; keep it concise.               |

    ## Courses (Optional)

    **Description**: Relevant courses, certifications, or training programs completed (**one or more** entries).
    Format: Course / Platform

    Start - End Date

    Description (if any)    

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Platform**     | Provider or platform name (e.g., Coursera, Udemy).                    | Organization name      | List reputable providers.                            |
    | **Title**        | Official course or certification name.                                | Full title             | Use exact title for verification.                    |
    | **Start - End Date** | Course period; can omit if not available.                           | Format as 'Month Year' | Include for context if possible.                     |
    | **Description**  | Additional information about the course (if any).                    | ~1-2 sentences         | Include if relevant; keep it concise.               |

    ## Languages

    **Description**: Languages known and proficiency levels (**one or more** entries).
    Format: Language / Proficiency

    | Field            | Description                                | Expected Length    | Guidelines                                   |
    |------------------|--------------------------------------------|--------------------|----------------------------------------------|
    | **Language**     | Name of the language (e.g., Spanish).      | Full language name | List languages enhancing your profile.       |
    | **Proficiency**  | Level of proficiency (e.g., Native, Fluent). | Standard levels    | Use recognized scales like CEFR.             |

    ## Links (Optional)

    **Description**: Online profiles, portfolios, or relevant links (**one or more** entries).
    Format: list of links

    - [Title](URL)

    | Field      | Description                                          | Expected Length | Guidelines                                     |
    |------------|------------------------------------------------------|-----------------|------------------------------------------------|
    | **Title**  | Descriptive title (e.g., "My GitHub Profile").       | Short phrase    | Make it clear and professional.                |
    | **URL**    | Direct hyperlink to the resource.                    | Full URL        | Ensure links are active and professional.      |

    ## Hobbies (Optional)
    Format: list of hobbies

    | Field      | Description                          | Expected Length     | Guidelines                                       |
    |------------|--------------------------------------|---------------------|--------------------------------------------------|
    | **Hobbies**| Personal interests or activities.    | List of 3-5 hobbies | Showcase positive traits; avoid controversial topics. |

    ## Misc (Optional)
    Format: list of misc

    | Field      | Description                          | Expected Length     | Guidelines                                       |
    |------------|--------------------------------------|---------------------|--------------------------------------------------|
    | **Misc**| Any other information.    | List of any other information | Showcase positive traits; avoid controversial topics. |

    ===

    # General Guidelines:

    - **Repeatable Sections**: Employment History, Education, Courses, Languages, and Links can contain **one or more** entries.
    - **Optional Sections**: Courses, Links, and Hobbies are **optional**. Omit sections not present in the original resume. **Do not add or invent information**.
    - **No Invented Information**: The parser must strictly use only the information provided in the original resume. Do not create, infer, or embellish any details.

    # Parser Rules:

    To convert an original resume into the defined object model, a parser should follow these rules:

    1. **Information Extraction**: Extract information exactly as it appears in the original document. Pay attention to details such as names, dates, job titles, and descriptions.

    2. **Section Mapping**: Map the content of the resume to the corresponding sections in the object model:
       - **Name**: Extract from the top of the resume or personal details section.
       - **Desired Job Title**: Look for a stated objective or title near the beginning.
       - **Personal Details**: Extract email, phone, country, and city from the contact information.
       - **Summary**: Use the professional summary or objective section.
       - **Employment History**: Identify past job experiences, including company names, job titles, locations, dates, and responsibilities.
       - **Education**: Extract academic qualifications with institution names, degrees, locations, and dates.
       - **Courses**: Include any additional training or certifications listed.
       - **Languages**: Note any languages and proficiency levels mentioned.
       - **Links**: Extract URLs to professional profiles or portfolios.
       - **Hobbies**: Include personal interests if provided.
       - **Misc**: Include any other information if provided.

    3. **Consistency and Formatting**:
       - Ensure dates are formatted consistently throughout (e.g., 'Month Year').
       - Use bullet points for lists where applicable.
       - Maintain the order of entries as they appear in the original resume unless a different order enhances clarity.

    4. **Accuracy**:
       - Double-check all extracted information for correctness.
       - Preserve the original wording, especially in descriptions and responsibilities, unless minor adjustments are needed for clarity.

    5. **Exclusion of Unavailable Information**:
       - If a section or specific detail is not present in the original resume, omit that section or field in the output.
       - Do not fill in default or placeholder values for missing information.

    6. **Avoiding Invention or Assumption**:
       - Do not add any information that is not explicitly stated in the original document.
       - Do not infer skills, responsibilities, or qualifications from context or general knowledge.

    7. **Enhancements**:
       - Minor rephrasing for grammar or clarity is acceptable but should not alter the original meaning.
       - Do NOT fix typos or grammar mistakes.
       - Quantify achievements where numbers are provided; do not estimate or create figures.

    8. **Professional Language**:
       - Ensure all language used is professional and appropriate for a resume.
       - Remove any informal language or slang that may have been present.

    9. **Confidentiality**:
       - Handle all personal data with confidentiality.
       - Do not expose sensitive information in the output that was not intended for inclusion.

    10. **Validation**:
        - Validate all URLs to ensure they are correctly formatted.
        - Verify that contact information follows standard formats.

    11. **Omit Empty Sections**:
        - Omit sections that contain no information from the original resume.

    Raw Resume Text:
    ~~~
    {resume_text}
    ~~~

    Please structure the resume information according to the provided format. Only include sections and details that are present in the original text. Do not invent or assume any information. No more then 4000 tokens.
    No intro, no explanations, no comments. 
    Use telegraphic english with no fluff. Keep all the information, do NOT invent data.
    No ```` or ```yaml or ```json or ```json5 or ``` or --- or any other formatting. Just clean text.
    You can only speak in clean, concise, Markdown format.     
    """
    return prompt.format(resume_text=extracted_data)

def extract_image_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        image_list = page.get_images(full=True)
        if image_list:
            xref = image_list[0][0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Open the image with Pillow
            image = Image.open(BytesIO(image_bytes))
            
            # Create a white background
            white_bg = Image.new("RGB", image.size, (255, 255, 255))
            
            # Paste the image onto the white background
            if image.mode == 'RGBA':
                white_bg.paste(image, (0, 0), image)
            else:
                white_bg.paste(image, (0, 0))
            
            # Save as JPEG with 60% quality
            white_bg.save("photo.jpg", "JPEG", quality=60)
            return "photo.jpg"
    return None

def clean_markdown_links(markdown_content):
    def fix_link(match):
        text = match.group(1)
        url = match.group(2)
        # Remove any nested markdown links from the URL
        clean_url = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', url)
        
        # Check if it's an email link
        if clean_url.startswith('mailto:'):
            email = clean_url.replace('mailto:', '')
            return f'[{text}](mailto:{email})'
        else:
            return f'[{text}]({clean_url})'

    # Fix markdown links (including email links)
    markdown_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', fix_link, markdown_content)
    
    # Additionally, convert plain emails to markdown links
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    markdown_content = re.sub(email_pattern, lambda m: f'[{m.group(0)}](mailto:{m.group(0)})', markdown_content)
    
    return markdown_content

@ell.simple(model="claude-3-5-sonnet-20240620", max_tokens=8192)
def enhance_resume(resume_content: str, components_content: str, photo_path: str = None) -> str:
    prompt = """
    You are an expert resume designer. Your task is to improve the structure and presentation of the given resume using appropriate components from the <available components> list. Aim for clarity and visual appeal, follow best typography practices, German, Scandinavian style. Clean markdown links. DO NOT change <resume content>, stay factual, follow best practices.
    
    Follow these guidelines:

    Add extra line breaks for better readability.
    0. Mark important parts with **bold** and *italic*. Do not overuse it.
    1. Analyze the <resume content> and the <available components>
    2. Select appropriate components that can enhance the <resume content> and readability.
    3. Apply the chosen components to the <resume content>, maintaining the original information and order.
    4. Ensure the enhanced resume remains in valid Markdown format.
    5. Do not add or remove any information from the original resume.
    6. Focus on improving the visual structure and organization of the resume.
    7. Use horizontal rules (---) to separate sections.
    8. If a photo path is provided, include it in metadata. No images in md content.
    9. Use bullet-points for for clarity.
    10. Use unorthodox Unicode characters for better typography effect readability.
    11. Use tables and div class=grid for better structure. Refer to <available components> for available components.
    12. Make sure you set this metadata in .md:
---
updated: Today's date
author: Full Name
---

    <resume content>
    ~~~
    {resume_content}
    ~~~

    <available components>
    ~~~
    {components_content}
    ~~~

    <photo path>
    {photo_path}
    ~~~

    Do NOT add classless divs.

    No \`\`\` or \`\`\`yaml or \`\`\`json or \`\`\`json5 or \`\`\` or any other formatting. No comments, no explanations, no intro. Just clean Markdown in output.
    """
    enhanced_content = prompt.format(resume_content=resume_content, components_content=components_content, photo_path=photo_path)
    return clean_markdown_links(enhanced_content)

def process_and_encode_photo(photo_path):
    with Image.open(photo_path) as img:
        # Resize image if it's too large
        max_size = (300, 300)  # Max dimensions
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Create white background
        bg = Image.new("RGB", img.size, (255, 255, 255))
        
        # Paste image onto background
        bg.paste(img, (0, 0), img if img.mode == 'RGBA' else None)
        
        buffer = BytesIO()
        bg.save(buffer, format="JPEG", quality=60)
        
        # Encode to base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def convert_markdown_formatting(text):
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text

def format_date(date_value):
    if isinstance(date_value, str):
        try:
            # Try parsing with different formats
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y", "%Y"):
                try:
                    return datetime.strptime(date_value, fmt).strftime("%B %d, %Y")
                except ValueError:
                    continue
            return date_value  # Return original string if all parsing attempts fail
        except Exception:
            return date_value
    elif isinstance(date_value, datetime):
        return date_value.strftime("%B %d, %Y")
    else:
        return str(date_value)  # Convert to string for any other type

def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(format)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def enhance_resume_with_retry(unified_resume, components_content, photo_path):
    try:
        return enhance_resume(unified_resume, components_content, photo_path)
    except httpx.ReadError as e:
        print(f"Network error occurred: {e}. Retrying...")
        raise  # This will trigger a retry

def date_filter(value, format='%B %d, %Y'):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').strftime(format)
        except ValueError:
            return value
    return value

def convert_to_links(html_content):
    # Convert emails to links, but only if they're not already in a link
    email_pattern = r'(?<!href="mailto:)(?<!>)\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    html_content = re.sub(email_pattern, lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', html_content)
    
    # Convert URLs to links, ensuring they start with http:// or https://, but only if they're not already in a link
    url_pattern = r'(?<!href=")(?<!>)\b(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/\S*)?)\b'
    
    def url_replace(match):
        url = match.group(0)
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return f'<a href="{url}">{match.group(0)}</a>'
    
    html_content = re.sub(url_pattern, url_replace, html_content)
    
    return html_content

# Custom extension to handle markdown inside divs
class DivMarkdownExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(DivMarkdownProcessor(r'<div.*?>(.*?)</div>', md), 'div_markdown', 175)

class DivMarkdownProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        div_content = m.group(1)
        div_html = md(div_content, extensions=['extra'])
        return f'<div>{div_html}</div>', m.start(0), m.end(0)

def process_nested_divs(html_content):
    def replace_div_content(match):
        div_content = match.group(1)
        processed_content = md(div_content, extensions=['extra'])
        return f'<div>{processed_content}</div>'

    pattern = r'<div.*?>(.*?)</div>'
    previous_content = ""
    iteration_count = 0
    max_iterations = 10  # Set a maximum number of iterations

    while html_content != previous_content and iteration_count < max_iterations:
        previous_content = html_content
        html_content = re.sub(pattern, replace_div_content, html_content, flags=re.DOTALL)
        iteration_count += 1

    if iteration_count == max_iterations:
        print("Warning: Maximum iterations reached in process_nested_divs. Some nested content may not be fully processed.")

    return html_content

def enhanced_markdown_render(content):
    # Process markdown with 'extra' and 'pymdownx.emoji' extensions
    html_content = md(content, extensions=['extra', 'pymdownx.emoji'])
    return html_content

def select_random_google_font():
    print(f"{Fore.CYAN}📚 Reading Google Fonts list...{Style.RESET_ALL}")
    with open('google-fonts.txt', 'r') as f:
        fonts = f.read().splitlines()
    print(f"{Fore.GREEN}✅ Font list read successfully{Style.RESET_ALL}")
    
    random_font = random.choice(fonts)
    random_font = random_font.replace('+', ' ')  # Replace '+' with spaces
    print(f"{Fore.YELLOW}🎲 Randomly selected font: {random_font}{Style.RESET_ALL}")
    
    return random_font

def main():
    parser = argparse.ArgumentParser(description="Generate a website and optionally process a PDF resume.")
    parser.add_argument("--pdf", help="Path to the PDF resume file")
    args = parser.parse_args()

    # Initialize variables
    photo_path = None
    resume_content = ""
    metadata = {}
    author = "John Doe"  # Default author name

    if args.pdf:
        with Halo(text='Reading PDF...', spinner=Spinners.dots.value) as spinner:
            pdf_content = read_pdf(args.pdf)
            time.sleep(1)  # Simulate longer process
            spinner.succeed('PDF read successfully')

        with Halo(text='Unifying format...', spinner=Spinners.dots.value) as spinner:
            unified_resume = unify_format(pdf_content)
            time.sleep(1)  # Simulate longer process
            spinner.succeed('Format unified')
        
        # Extract name from the unified resume
        name_match = re.search(r'^# (.+)$', unified_resume, re.MULTILINE)
        if name_match:
            parsed_name = name_match.group(1).strip()
        else:
            parsed_name = "Unknown"

        # Check if resume.md exists and contains a different name
        if os.path.exists("resume.md"):
            with open("resume.md", "r") as f:
                existing_content = f.read()
                existing_name_match = re.search(r'^# (.+)$', existing_content, re.MULTILINE)
                if existing_name_match:
                    existing_name = existing_name_match.group(1).strip()
                    if existing_name != parsed_name:
                        print(f"{Fore.YELLOW}⚠️  Warning: The existing resume.md contains a different name.{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Existing name: {existing_name}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Parsed name: {parsed_name}{Style.RESET_ALL}")
                        overwrite = input(f"{Fore.MAGENTA}Do you want to overwrite the existing resume.md? (y/n): {Style.RESET_ALL}").lower()
                        if overwrite != 'y':
                            print(f"{Fore.RED}❌ Keeping the existing resume.md. Exiting.{Style.RESET_ALL}")
                            return

        # Write the new resume content
        with open("resume.md", "w") as f:
            f.write(unified_resume)
        print(f"{Fore.GREEN}✅ Resume has been processed and saved as resume.md{Style.RESET_ALL}")

        with Halo(text='Extracting photo from PDF...', spinner=Spinners.dots.value) as spinner:
            photo_path = extract_image_from_pdf(args.pdf)
            time.sleep(1)  # Simulate longer process
            if photo_path:
                spinner.succeed(f'Photo extracted and saved as {photo_path}')
            else:
                spinner.warn('No photo found in the PDF')

        # Prompt user for AI-enhanced resume design
        enhance_design = input(f"{Fore.MAGENTA}🤖 Would you like AI to improve the resume layout? (y/n): {Style.RESET_ALL}").lower()
        
        if enhance_design == 'y':
            with Halo(text='Reading components...', spinner=Spinners.dots.value) as spinner:
                with open("components.md", "r") as f:
                    components_content = f.read()
                time.sleep(1)  # Simulate longer process
                spinner.succeed('Components read successfully')

            with Halo(text='Enhancing resume...', spinner=Spinners.dots.value) as spinner:
                try:
                    enhanced_resume = enhance_resume_with_retry(unified_resume, components_content, photo_path)
                    spinner.succeed('Resume enhancement completed successfully')
                except Exception as e:
                    spinner.fail(f'Failed to enhance resume after multiple attempts. Error: {e}')
                    print(f"{Fore.YELLOW}⚠️  Proceeding with the original resume content{Style.RESET_ALL}")
                    enhanced_resume = unified_resume

            with open("resume-enhanced.md", "w") as f:
                f.write(enhanced_resume)
            print(f"{Fore.GREEN}✅ Enhanced resume has been saved as resume-enhanced.md{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}📋 Skipping AI enhancement. Copying resume.md to resume-enhanced.md{Style.RESET_ALL}")
            shutil.copy("resume.md", "resume-enhanced.md")
            print(f"{Fore.GREEN}✅ resume.md copied to resume-enhanced.md{Style.RESET_ALL}")

    # Read resume-enhanced.md
    if os.path.exists('resume-enhanced.md'):
        print(f"{Fore.CYAN}📖 Reading resume-enhanced.md...{Style.RESET_ALL}")
        with open('resume-enhanced.md', 'r') as resume_file:
            resume_content = resume_file.read()
        print(f"{Fore.GREEN}✅ resume-enhanced.md read successfully{Style.RESET_ALL}")

    # Split front matter and markdown content
    parts = resume_content.split('---', 2)
    metadata = {}
    if len(parts) == 3:
        try:
            front_matter, markdown_content = parts[1:]
            metadata = yaml.safe_load(front_matter)
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML front matter. Error: {e}")
            print("Proceeding with the entire content as markdown.")
            markdown_content = resume_content
    else:
        markdown_content = resume_content

    author = metadata.get('author', "John Doe")  # Default author name
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Process photo after metadata extraction
    photo_html = ''
    if photo_path and os.path.exists(photo_path):
        photo_base64 = process_and_encode_photo(photo_path)
        photo_html = f'<img alt="{author}" src="data:image/jpeg;base64,{photo_base64}">'

    # Remove image tag from markdown content
    markdown_content = re.sub(r'!\[.*?\]\(.*?\)', '', markdown_content)

    # Convert markdown to HTML
    html_content = enhanced_markdown_render(markdown_content)
    
    # Process all metadata values
    if metadata:
        for key, value in metadata.items():
            metadata[key] = format_date(value)

    chosen_theme, theme_files = choose_theme()
    theme_files.append('index.css')  # Add this line

    if chosen_theme == 'process_resume':
        print("Resume processing completed. Exiting.")
        return

    print(f"Debug: Chosen theme is {chosen_theme}")

    favicon_base64 = generate_favicon_base64(author, chosen_theme)

    with open('template.html', 'r') as file:
        template_string = file.read()

    # Remove the CSS embedding code entirely
    # The template.html file should already have the correct links to CSS files

    # Embed JavaScript files
    js_files = re.findall(r'<script src="(.+?)"></script>', template_string)
    for js_file in js_files:
        try:
            js_content = read_and_encode_file(js_file)
            template_string = template_string.replace(
                f'<script src="{js_file}"></script>',
                f'<script>{js_content}</script>'
            )
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch {js_file}. Error: {e}")

    # Embed images
    img_tags = re.findall(r'<img src="(.+?)"', template_string)
    for img_src in img_tags:
        img_content = read_and_encode_file(img_src)
        img_ext = os.path.splitext(img_src)[1][1:]
        template_string = template_string.replace(
            f'src="{img_src}"',
            f'src="data:image/{img_ext};base64,{img_content}"'
        )

    # Create a Jinja2 environment and add the custom date filter
    env = Environment()
    env.filters['date'] = date_filter

    # Use the environment to create the template
    template = env.from_string(template_string)

    # Get current date and time
    now = datetime.now()

    google_font = select_random_google_font()

    try:
        rendered_html = template.render(
            metadata=metadata,
            title=metadata.get('title', 'My Resume'),
            author=author,
            content=html_content,
            favicon=f"data:image/x-icon;base64,{favicon_base64}",
            theme_files=theme_files,
            photo=photo_html,
            format_date=format_date,
            now=now,
            format_datetime=format_datetime,
            google_font=google_font,
            current_date=current_date  # Add this line
        )
        print("HTML rendering completed successfully.")
    except Exception as e:
        print(f"Error occurred during HTML rendering: {e}")
        print("Falling back to a simple HTML template.")
        rendered_html = f"<html><body><h1>{metadata.get('title', 'My Resume')}</h1>{html_content}</body></html>"

    with open('index.html', 'w') as file:
        file.write(rendered_html)

    print(f"Debug: index.html has been generated with embedded resources")

    print(f"{Fore.GREEN}🎉 Process completed! index.html has been generated with embedded resources{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
