# SunBot Robotics Official Website

Official website for SunBot Robotics Programming STEAM Education, a STEAM education program in southwest Edmonton, Alberta, serving children ages 6–10 and 9–14.

🌐 **Live Site**: [sunbotcanada.github.io](https://sunbotcanada.github.io)

## ChatGPT / AI search referral note

If Google Analytics (or similar) is added later, ChatGPT Search referrals may appear with `utm_source=chatgpt.com`. No analytics platform is currently configured in this repository.

## Search engine and AI crawler setup

### Crawler policy

`robots.txt` explicitly allows `OAI-SearchBot` (ChatGPT Search), `Googlebot`, `Bingbot`,
`Applebot` (Apple Search / Siri / Spotlight) and all other agents, and points to
`sitemap.xml`. No `GPTBot` rule is defined, so model-training crawling follows the
default `User-agent: *` rule. Change this only as a deliberate policy decision.

### Structured data

The canonical SunBot entity is defined once, on the homepage, as
`https://sunbotcanada.github.io/#organization`. Every other page adds a `WebPage` and
`BreadcrumbList` node that references that same `@id` instead of redefining the
organization. When editing entity facts, edit the homepage `@graph` only.

`faq.html` builds its `FAQPage` JSON-LD from the visible FAQ markup at runtime
(`assets/js/faq-schema.js`), so the schema cannot drift from the visible questions.

### Search Console and Bing Webmaster verification

Verification tokens are intentionally absent. Placeholders are marked with `TODO`
comments in the `<head>` of `index.html`:

- Google: `<meta name="google-site-verification" content="...">`
- Bing: `<meta name="msvalidate.01" content="...">` or a `BingSiteAuth.xml` file at the site root

Insert the real value from each tool, then commit.

### IndexNow

IndexNow tells Bing, Yandex, Seznam and Naver that URLs changed.

- Public key file: `2755c0b1c44be636c12e0ef6010a75e0.txt` at the site root
- Submission script: `.github/scripts/indexnow_submit.py`
- Workflow: `.github/workflows/indexnow.yml`, triggered on pushes to `main` that touch
  `*.html` or `sitemap.xml`, and available via manual dispatch

The key is public by design because IndexNow requires it to be readable at the site root,
so it is not stored in GitHub Secrets.

Preview the payload without submitting:

```bash
python3 .github/scripts/indexnow_submit.py --dry-run
```

Manual submission alternative, if the workflow is disabled:

```bash
curl -X POST https://api.indexnow.org/IndexNow \
  -H "Content-Type: application/json" \
  -d '{"host":"sunbotcanada.github.io","key":"2755c0b1c44be636c12e0ef6010a75e0","keyLocation":"https://sunbotcanada.github.io/2755c0b1c44be636c12e0ef6010a75e0.txt","urlList":["https://sunbotcanada.github.io/"]}'
```

### llms.txt

`llms.txt` is an experimental, optional summary of public pages. It is not required by
OpenAI, Google or any other provider, and it does not affect rankings. The authoritative
sources remain the HTML pages, `robots.txt` and `sitemap.xml`.

### Moving to a custom domain later

Canonical URLs are currently hard-coded as `https://sunbotcanada.github.io/...` because
GitHub Pages serves plain static HTML with no templating layer. To migrate to a custom
domain such as `sunbot.ca`:

1. Add a `CNAME` file at the repository root containing only the new domain.
2. Configure DNS with the domain provider and set the custom domain in
   **Settings → Pages**, then enable HTTPS.
3. Replace `https://sunbotcanada.github.io/` with the new origin in:
   - `<link rel="canonical">` and `og:url` / `twitter:*` URLs in all `*.html`
   - the `@id`, `url`, `logo` and `image` values in the homepage JSON-LD `@graph`
   - the per-page `WebPage` / `BreadcrumbList` `@id` and `item` values
   - `sitemap.xml`
   - the `Sitemap:` line in `robots.txt`
   - `SITE_HOST` in `.github/scripts/indexnow_submit.py`
   - the URLs in `llms.txt`
4. Keep the GitHub Pages URL reachable so it redirects to the custom domain, then
   re-verify the new property in Google Search Console and Bing Webmaster Tools and
   resubmit the sitemap.

A repository-wide find and replace of the origin string covers steps 3, since the string
is identical everywhere.

## 📋 Project Overview

This is a static website built with HTML5, CSS3, and JavaScript, designed to showcase SunBot Robotics' courses, student activities, FLL competition preparation, and contact information. The site features bilingual support (English/Chinese) and is fully responsive for desktop and mobile devices.

## 🎯 Features

- **Home Page**: Hero banner, course preview, gallery, and social media links
- **About Page**: Mission, vision, and founder information
- **Courses Page**: Detailed information about three main programs
- **Gallery Page**: Photo gallery with lightbox functionality
- **FLL Page**: FIRST® LEGO® League competition journey and timeline
- **Contact Page**: Contact form, map, and social links
- **Bilingual Support**: English/Chinese language toggle
- **Responsive Design**: Mobile-friendly layout
- **Modern UI**: Clean, child-friendly design with brand colors

## 🛠️ Technology Stack

- **HTML5** / **CSS3** / **JavaScript** (Vanilla)
- **Bootstrap 5** - Responsive layout framework
- **Font Awesome** - Icon library
- **Google Fonts** - Typography (Poppins, Nunito Sans, Roboto)
- **GitHub Pages** - Static website hosting

## 📁 File Structure

```
sunbotrobotics.github.io/
│
├── index.html              # Home page
├── about.html              # About page
├── courses.html            # Courses page
├── gallery.html            # Gallery page
├── fll.html                # FLL Challenge page
├── contact.html            # Contact page
│
├── assets/
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── js/
│   │   └── main.js         # Main JavaScript
│   ├── images/
│   │   ├── courses/        # Course images
│   │   └── gallery/        # Gallery images
│   └── icons/              # Custom icons
│
├── LICENSE                 # Dual licensing information
└── README.md               # This file
```

## 🚀 Deployment Instructions

### Step 1: Prepare the Repository

1. **Create a GitHub repository** named `sunbotcanada.github.io`
   - Repository name must match exactly: `sunbotcanada.github.io`
   - Make it public (required for GitHub Pages)
   - Or rename existing repository to `sunbotcanada.github.io`

2. **Initialize and push code**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SunBot Robotics website"
   git branch -M main
   git remote add origin https://github.com/sunbotcanada/sunbotcanada.github.io.git
   git push -u origin main
   ```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
4. Click **Save**

### Step 3: Access Your Website

- Your site will be live at: `https://sunbotcanada.github.io`
- It may take a few minutes for changes to propagate

### Step 4: (Optional) Custom Domain

If you want to use a custom domain (e.g., `sunbot.ca`):

1. Add a `CNAME` file in the root directory:
   ```
   sunbot.ca
   ```
   Or add both:
   ```
   sunbot.ca
   www.sunbot.ca
   ```

2. Configure DNS settings with your domain provider:
   - Type: `CNAME`
   - Name: `@` (or `www`)
   - Value: `sunbotcanada.github.io`

3. In GitHub repository Settings → Pages, add your custom domain

## 🎨 Design System

### Color Palette
- **Primary Yellow**: `#ffcc00`
- **Primary Blue**: `#0b3954`
- **Background Gray**: `#f5f5f5`
- **Accent Red**: `#e63946`

### Typography
- **Primary Font**: Poppins, Nunito Sans, Roboto
- **Headings**: Poppins (600 weight)
- **Body**: Nunito Sans, Roboto (400 weight)

## 📝 Adding Content

### Adding Images

1. **Gallery Images**: Place images in `assets/images/gallery/`
2. **Course Images**: Place images in `assets/images/courses/`
3. Update HTML image `src` attributes to point to the new images

### Updating Course Information

Edit `courses.html` and modify the course card sections with new details.

### Updating Contact Information

Edit the contact section in `contact.html` to update email, address, or social links.

## 🔧 Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sunbotrobotics/sunbotrobotics.github.io.git
   cd sunbotrobotics.github.io
   ```

2. **Open in browser**:
   - Simply open `index.html` in a web browser
   - Or use a local server:
     ```bash
     # Using Python 3
     python3 -m http.server 8000
     
     # Using Node.js (http-server)
     npx http-server
     ```

3. **Access locally**: `http://localhost:8000`

## 📧 Contact Information

- **Email**: sunbotcanada@gmail.com
- **Location**: Edmonton, Alberta, Canada
- **Founder**: Adam Sun

## 📄 License

This project uses a dual licensing strategy:

- **Code (HTML/CSS/JS)**: Licensed under [MIT License](https://opensource.org/licenses/MIT)
- **Content (Images, Text, Graphics)**: Licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)

See the [LICENSE](LICENSE) file for full details.

### Quick License Summary

**MIT License** (Code):
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

**CC BY-NC 4.0** (Content):
- ✅ Share and adapt
- ✅ Attribution required
- ❌ Commercial use

## 🔄 Future Enhancements

Planned features for future phases:

- [ ] SEO optimization improvements
- [ ] Enhanced multi-language support
- [ ] Dynamic content management (Flask/Google Sheets API)
- [ ] Online enrollment form integration
- [ ] Analytics and visitor statistics
- [ ] Blog/news section

## 🤝 Contributing

This is a private project for SunBot Robotics. For inquiries or suggestions, please contact sunbotcanada@gmail.com.

## 📚 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [FIRST LEGO League](https://www.firstlegoleague.org/)

---

**Maintained by**: Adam Sun  
**Last Updated**: January 2025
