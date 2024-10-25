# Mono Resume

Simple resume template built with monospace fonts. Pretty. Geeky.

![CleanShot 2024-10-26 at 00 18 14@2x](https://github.com/user-attachments/assets/044195b8-e8fa-4a03-93e7-e7c77330ac86)

Monospace fonts are dear to many of us. Some find them more readable, consistent, and beautiful, than their proportional alternatives. Maybe we're just brainwashed from spending years in terminals? Or are we hopelessly nostalgic? I'm not sure. But I like them, and that's why I started experimenting with all-monospace Web.

Monospace fonts:
- https://owickstrom.github.io/the-monospace-web
- https://monaspace.githubnext.com
- https://github.com/gabrielelana/awesome-terminal-fonts

## Build

```
python generate.py [--pdf path/to/resume.pdf]
```

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

Run the script with:

```bash
python generate.py [--pdf path/to/resume.pdf]
```

This will create the website file based on your chosen theme and the content in `resume-enhanced.md` (or the processed PDF if provided).

## License

[MIT](LICENSE.md)
