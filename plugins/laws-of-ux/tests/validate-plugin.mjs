import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pluginRoot = path.resolve(__dirname, "..");

const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(pluginRoot, rel), "utf8"));
const readText = (rel) => fs.readFileSync(path.join(pluginRoot, rel), "utf8");
const exists = (rel) => fs.existsSync(path.join(pluginRoot, rel));
const frontmatter = (body) => {
  const m = body.match(/^---\n([\s\S]*?)\n---/);
  return m ? m[1] : "";
};

describe("laws-of-ux — dual-platform Claude Code + Codex plugin", () => {
  it("declares a valid Claude Code manifest (lean, no Codex keys)", () => {
    const m = readJson(".claude-plugin/plugin.json");
    assert.equal(m.name, "laws-of-ux");
    assert.match(m.version, /^\d+\.\d+\.\d+$/);
    assert.ok(m.description, "manifest needs a description");
    assert.equal(m.license, "MIT");
    assert.ok(Array.isArray(m.keywords) && m.keywords.includes("ux") && m.keywords.includes("laws-of-ux"));
    for (const forbidden of ["interface", "skills", "agents", "mcpServers"]) {
      assert.ok(!(forbidden in m), `Claude manifest must not carry the Codex-style "${forbidden}" key`);
    }
  });

  it("ships a Codex manifest with an interface block (this plugin IS dual-platform)", () => {
    assert.ok(exists(".codex-plugin/plugin.json"), ".codex-plugin/plugin.json must exist");
    const c = readJson(".codex-plugin/plugin.json");
    assert.equal(c.name, "laws-of-ux");
    assert.match(c.version, /^\d+\.\d+\.\d+$/);
    assert.equal(c.skills, "./skills/");
    assert.ok(c.interface && c.interface.displayName, "Codex manifest needs interface.displayName");
    assert.ok(!("includes" in c.interface), "Codex manifest must avoid unsupported interface.includes metadata");
    // Claude and Codex versions must stay in lockstep.
    assert.equal(c.version, readJson(".claude-plugin/plugin.json").version);
  });

  it("has a well-formed core skill whose references all resolve", () => {
    const skillPath = "skills/laws-of-ux/SKILL.md";
    const skill = readText(skillPath);
    const fm = frontmatter(skill);
    assert.match(skill, /^---/, "SKILL.md must start with frontmatter");
    assert.match(fm, /name:\s*laws-of-ux/, "skill name must match its directory");
    assert.match(fm, /This skill should be used when/, "description must follow the Claude Code trigger pattern");
    assert.ok(!/user-invocable:/.test(fm), "Codex-only user-invocable field must not appear");
    assert.ok(!/^allowed-tools:/m.test(fm), "Codex-only allowed-tools skill field must not appear");

    const expected = [
      "skills/laws-of-ux/references/scoring-rubric.md",
      "skills/laws-of-ux/references/concern-areas.md",
      "skills/laws-of-ux/references/stack-detection.md",
      "skills/laws-of-ux/references/live-audit.md",
      "skills/laws-of-ux/references/laws/README.md",
      "skills/laws-of-ux/templates/report-template.md",
      "skills/laws-of-ux/templates/scorecard/scorecard.html",
      "skills/laws-of-ux/templates/scorecard/scorecard.css",
    ];
    for (const rel of expected) {
      assert.ok(exists(rel), `${rel} should exist`);
    }

    // No dangling top-level references/… paths cited in SKILL.md.
    for (const ref of skill.match(/references\/[\w-]+\.md/g) ?? []) {
      assert.ok(exists(`skills/laws-of-ux/${ref}`), `SKILL.md cites ${ref} which does not exist`);
    }
  });

  it("documents all 30 laws as individual files under references/laws/", () => {
    const dir = path.join(pluginRoot, "skills/laws-of-ux/references/laws");
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md") && f !== "README.md");
    assert.equal(files.length, 30, "there must be exactly 30 per-law files");
    const corpus = files.map((f) => fs.readFileSync(path.join(dir, f), "utf8")).join("\n");
    const laws = [
      "Aesthetic-Usability", "Fitts", "Goal-Gradient", "Hick", "Jakob", "Miller", "Parkinson",
      "Common Region", "Proximity", "Prägnanz", "Similarity", "Uniform Connectedness",
      "Peak-End", "Serial Position", "Von Restorff", "Zeigarnik",
      "Doherty", "Occam", "Pareto", "Postel", "Tesler",
      "Choice Overload", "Chunking", "Cognitive Bias", "Cognitive Load", "Flow",
      "Mental Model", "Paradox of the Active User", "Selective Attention", "Working Memory",
    ];
    for (const law of laws) {
      assert.ok(corpus.includes(law), `per-law corpus should document "${law}"`);
    }
    // concern-areas.md must point at real per-law files (no dangling references/laws/… paths).
    const concern = readText("skills/laws-of-ux/references/concern-areas.md");
    for (const ref of concern.match(/references\/laws\/[\w-]+\.md/g) ?? []) {
      assert.ok(exists(`skills/laws-of-ux/${ref}`), `concern-areas.md cites ${ref} which does not exist`);
    }
  });

  it("locks the scoring rubric so the formula can't silently drift", () => {
    const r = readText("skills/laws-of-ux/references/scoring-rubric.md");
    for (const band of ["90", "80", "70", "60"]) {
      assert.ok(r.includes(band), `rubric must state the ${band} letter-grade threshold`);
    }
    assert.match(r, /NOT_APPLICABLE|N\/A/, "rubric must define the N/A exclusion");
    assert.match(r, /confidence/i, "rubric must define confidence weighting");
    assert.match(r, /NOT_ASSESSED/, "rubric must define the NOT_ASSESSED state");
    assert.match(r, /file:line/, "rubric must require file:line evidence");
  });

  it("ships the three slash commands with the right frontmatter", () => {
    for (const cmd of ["ux-audit", "ux-fix", "ux-explain"]) {
      const fm = frontmatter(readText(`commands/${cmd}.md`));
      assert.ok(fm, `${cmd}.md must have frontmatter`);
      assert.match(fm, /description:/, `${cmd}.md needs a description`);
      assert.match(fm, /argument-hint:/, `${cmd}.md needs an argument-hint`);
    }
    for (const cmd of ["ux-audit", "ux-fix"]) {
      assert.match(frontmatter(readText(`commands/${cmd}.md`)), /allowed-tools:/, `${cmd}.md needs allowed-tools`);
    }
  });

  it("ships the ux-auditor and ux-synthesizer subagents", () => {
    for (const agent of ["ux-auditor", "ux-synthesizer"]) {
      const body = readText(`agents/${agent}.md`);
      const fm = frontmatter(body);
      assert.match(fm, new RegExp(`name:\\s*${agent}`), `${agent} name must match`);
      assert.match(fm, /model:/, `${agent} needs a model`);
      assert.match(fm, /color:/, `${agent} needs a color`);
      assert.match(fm, /tools:/, `${agent} needs tools`);
      assert.match(body, /<example>/, `${agent} should include at least one <example> block`);
    }
    // The auditor is read-only; the synthesizer is the only agent allowed to write.
    assert.doesNotMatch(frontmatter(readText("agents/ux-auditor.md")), /tools:.*Write/);
    assert.match(frontmatter(readText("agents/ux-synthesizer.md")), /tools:.*Write/);
  });

  it("ships a self-contained HTML scorecard in the shadcn/Geist style", () => {
    const html = readText("skills/laws-of-ux/templates/scorecard/scorecard.html");
    const css = readText("skills/laws-of-ux/templates/scorecard/scorecard.css");
    assert.match(html, /<svg/, "scorecard needs the SVG grade dial");
    assert.match(html, /grade-dial/, "scorecard needs the grade-dial component");
    assert.match(html, /scorecard\.css/, "scorecard must link its stylesheet");
    assert.match(css, /Geist/, "scorecard.css must load Geist");
    assert.match(css, /JetBrains Mono/, "scorecard.css must load JetBrains Mono");
  });

  it("ships policy docs, an icon, and README with the install line", () => {
    assert.match(readText("README.md"), /\/plugin install laws-of-ux/);
    assert.match(readText("README.md"), /lawsofux\.com/);
    assert.match(readText("LICENSE"), /MIT License/);
    assert.ok(exists("PRIVACY.md"));
    assert.ok(exists("TERMS.md"));
    assert.match(readText("assets/app-icon.svg"), /<svg/);
  });

  it("ships the verification fixtures", () => {
    for (const fx of ["known-bad", "known-good", "no-frontend"]) {
      assert.ok(exists(`tests/fixtures/${fx}`), `fixture ${fx} should exist`);
    }
  });
});
