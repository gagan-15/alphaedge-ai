import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
    build: {
        emptyOutDir: false,
        lib: {
            entry: resolve(__dirname, "legacy_score_entry.ts"),
            formats: ["es"],
            fileName: () => "legacy-score-audit.mjs",
        },
        outDir: resolve(__dirname, "../../tmp/trade7e"),
        minify: false,
    },
});
