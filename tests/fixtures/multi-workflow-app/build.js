const fs = require("fs");
const path = require("path");

function parseFrontMatter(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) throw new Error("Missing front matter");
  const [, frontMatterRaw, body] = match;
  const frontMatter = {};
  for (const line of frontMatterRaw.split("\n")) {
    const [key, ...rest] = line.split(":");
    frontMatter[key.trim()] = rest.join(":").trim();
  }
  return { frontMatter, body };
}

function build() {
  const postsDir = path.join(__dirname, "posts");
  const distDir = path.join(__dirname, "dist");
  fs.mkdirSync(distDir, { recursive: true });

  const files = fs.readdirSync(postsDir).filter((f) => f.endsWith(".md"));
  for (const file of files) {
    const raw = fs.readFileSync(path.join(postsDir, file), "utf8");
    const { frontMatter, body } = parseFrontMatter(raw);
    if (frontMatter.draft === "true") continue;

    const html = `<article><h1>${frontMatter.title}</h1>${body}</article>`;
    fs.writeFileSync(path.join(distDir, file.replace(".md", ".html")), html);
  }
}

build();
