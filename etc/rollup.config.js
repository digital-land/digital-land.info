// get the config object from the package file
import { config } from "../package.json";
const { assets } = config;

module.exports = [
  {
    input: `${assets.sourceDir}/javascripts/application.js`,
    output: {
      file: `${assets.distDir}/javascripts/application.js`,
      format: "iife",
    }
  },
  {
    input: `${assets.sourceDir}/javascripts/filter-checkbox-extension.js`,
    output: {
      file: `${assets.distDir}/javascripts/filter-checkbox-extension.js`,
      format: "iife",
    }
  }
];
