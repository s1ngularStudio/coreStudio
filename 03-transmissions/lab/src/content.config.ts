import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const pieces = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/pieces" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()),
    builtWith: z.array(z.string()).optional(),
    summary: z.string(),
    link: z.string().url().optional(),
    // Path under public/, e.g. "/work/my-piece/hero.mp4" -- see README for where to put
    // the actual file. Rendered as <img> or <video> automatically based on the extension,
    // and used as the piece's thumbnail everywhere it's listed (cards, featured, etc).
    media: z.string().optional(),
    // Additional images/videos shown on the detail page only, below the write-up -- same
    // public/ path convention and auto img/video detection as `media`.
    gallery: z.array(z.string()).optional(),
  }),
});

export const collections = { pieces };
