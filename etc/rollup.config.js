// get the config object from the package file
import { config } from "../package.json";
const { nodeResolve } = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");
const { assets } = config;

module.exports = [
  {
    input: `${assets.sourceDir}/javascripts/application.js`,
    output: {
      file: `${assets.distDir}/javascripts/application.js`,
      format: "iife",
    },
    plugins: [nodeResolve(), commonjs()],
  },
  {
    input: "node_modules/govuk-frontend/govuk/all.js",
    output: {
      file: `${assets.distDir}/javascripts/govuk/govuk-frontend.min.js`,
    },
    context: "window",
  },
];
