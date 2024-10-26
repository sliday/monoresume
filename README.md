# Mono Resume

Simple resume template built with monospace fonts. Pretty. Geeky.

Monospace fonts are dear to many of us. Some find them more readable, consistent, and beautiful, than their proportional alternatives. Maybe we're just brainwashed from spending years in terminals? Or are we hopelessly nostalgic? I'm not sure. But I like them, and that's why I started experimenting with all-monospace Web.

![CleanShot 2024-10-26 at 09 42 01@2x](https://github.com/user-attachments/assets/ef176c87-89f5-4479-8c40-b3e6d0dd0b8e)

| Mobile | Desktop |
|------------|-----------|
| ![CleanShot 2024-10-26 at 00 18 14@2x](https://github.com/user-attachments/assets/044195b8-e8fa-4a03-93e7-e7c77330ac86) | ![CleanShot 2024-10-26 at 09 43 32@2x](https://github.com/user-attachments/assets/0d6aeff8-a429-4c72-8101-5a6acc48e625) |


## Build

```
python generate.py --pdf path/to/resume.pdf
```

Will convert PDF resume into a cool website. It will output a single `index.html` in the current directory.

## How it works

The `generate.py` script creates a customized static website:

1. Processes a PDF resume (optional):
   - Extracts text and photo from the PDF
   - Converts the content to a unified markdown format
   - Enhances the resume structure and presentation
2. Prompts user to choose a theme (Default, Solarized, Terminal, or Surprise)
3. Reads content from `resume-enhanced.md` (YAML front matter + Markdown)
4. Processes content: parses YAML, converts Markdown to HTML
5. Applies chosen theme to HTML/CSS templates
6. Generates a simple favicon based on the author's initials
7. Embeds all resources (CSS, JS, images) into a single HTML file
8. Outputs the final `index.html` file

### Additional Features:
- Supports custom themes, including a "Surprise" option that generates random retro-inspired themes
- Processes nested divs and maintains markdown formatting within them
- Converts URLs and email addresses to clickable links
- Resizes and optimizes the extracted photo
- Implements responsive design for various screen sizes
- Includes a theme toggle for light/dark mode
- Randomly selects a Google Font for the resume
- Provides AI-enhanced resume layout option

The script creates the website file based on your chosen theme and the content in `resume-enhanced.md` (or the processed PDF if provided).

- `resume.md` - ordered snapshot of your resume
- `resume-enhanced.md` - your resume 're-designed' by AI, same content

## Features

- Choose from a variety of themes, including a fun "Surprise" option for unique, retro-inspired looks
- Preserve your resume's structure and formatting, ensuring it looks great in digital form
- Automatically create clickable links for websites and email addresses
- Optimize your profile photo for web display
- Enjoy a responsive design that looks good on any device
- Switch between light and dark modes with a simple toggle
- Experience a fresh look with randomly selected modern fonts
- Optional AI-powered layout enhancement for a polished, professional appearance

## Project Structure

- `generate.py` - Main script to generate the resume website
- `templates.html` - Main HTML template for the resume
- `index.css` - Base CSS styles for the resume
- `theme_...css` - Pre-built CSS themes for the resume
- `resume.md` - your resume in clean .md format.
- `resume-enhanced.md` - your resume 're-designed' by AI, same content

Simply run the script, and Mono Resume will create a sleek, customized website based on your resume content and chosen theme. It's that easy to make your CV stand out in the digital world!

## Monospace fonts

- https://owickstrom.github.io/the-monospace-web
- https://monaspace.githubnext.com
- https://github.com/gabrielelana/awesome-terminal-fonts
- https://en.wikipedia.org/wiki/List_of_monospaced_typefaces

## License

[MIT](LICENSE.md)
