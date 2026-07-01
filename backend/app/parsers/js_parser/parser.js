/**
 * JavaScript/TypeScript AST Parser
 * Extracts structure from JS/TS code using Babel parser
 */

const parser = require("@babel/parser");
const fs = require("fs");
const path = require("path");

/**
 * Parse a JavaScript/TypeScript file and extract structure
 */
function parseFile(filePath) {
  try {
    const code = fs.readFileSync(filePath, "utf-8");

    const ast = parser.parse(code, {
      sourceType: "module",
      allowImportExportEverywhere: true,
      allowReturnOutsideFunction: true,
      plugins: [
        "jsx",
        "typescript",
        "decorators-legacy",
        "classProperties",
        "classPrivateProperties",
        "classPrivateMethods",
        "exportDefaultFrom",
        "partialApplication",
        "recordAndTuple",
        "asyncGenerators",
        ["pipelineOperator", { proposal: "minimal" }],
        "throwExpressions",
      ],
    });

    return {
      success: true,
      ast: ast,
      error: null,
    };
  } catch (error) {
    return {
      success: false,
      ast: null,
      error: error.message,
    };
  }
}

/**
 * Extract imports from AST
 */
function extractImports(ast) {
  const imports = [];

  ast.program.body.forEach((node) => {
    if (node.type === "ImportDeclaration") {
      imports.push({
        type: "import",
        source: node.source.value,
        specifiers: node.specifiers.map((spec) => ({
          type: spec.type,
          local: spec.local.name,
          imported:
            spec.type === "ImportDefaultSpecifier"
              ? "default"
              : spec.imported.name,
        })),
        line: node.loc.start.line,
      });
    }
  });

  return imports;
}

/**
 * Extract exports from AST
 */
function extractExports(ast) {
  const exports = [];

  ast.program.body.forEach((node) => {
    if (node.type === "ExportNamedDeclaration") {
      if (node.declaration) {
        if (node.declaration.type === "ClassDeclaration") {
          exports.push({
            type: "class",
            name: node.declaration.id.name,
            line: node.loc.start.line,
          });
        } else if (node.declaration.type === "FunctionDeclaration") {
          exports.push({
            type: "function",
            name: node.declaration.id.name,
            line: node.loc.start.line,
          });
        } else if (node.declaration.type === "VariableDeclaration") {
          node.declaration.declarations.forEach((decl) => {
            exports.push({
              type: "variable",
              name: decl.id.name,
              line: node.loc.start.line,
            });
          });
        }
      }
      if (node.specifiers) {
        node.specifiers.forEach((spec) => {
          exports.push({
            type: "re-export",
            exported: spec.exported.name,
            local: spec.local.name,
            line: node.loc.start.line,
          });
        });
      }
    } else if (node.type === "ExportDefaultDeclaration") {
      let name = "default";
      if (node.declaration.type === "ClassDeclaration") {
        name = node.declaration.id?.name || "default";
      } else if (node.declaration.type === "FunctionDeclaration") {
        name = node.declaration.id?.name || "default";
      }

      exports.push({
        type: "default",
        name: name,
        line: node.loc.start.line,
      });
    }
  });

  return exports;
}

/**
 * Extract class declarations
 */
function extractClasses(ast) {
  const classes = [];

  ast.program.body.forEach((node) => {
    let classNode = null;

    if (node.type === "ClassDeclaration") {
      classNode = node;
    } else if (
      node.type === "ExportNamedDeclaration" &&
      node.declaration &&
      node.declaration.type === "ClassDeclaration"
    ) {
      classNode = node.declaration;
    }

    if (classNode) {
      classes.push({
        name: classNode.id.name,
        methods: classNode.body.body
          .filter((m) => m.type === "MethodDefinition")
          .map((m) => ({
            name: m.key.name,
            kind: m.kind,
          })),
        superClass: classNode.superClass
          ? classNode.superClass.name
          : null,
        line: classNode.loc.start.line,
      });
    }
  });

  return classes;
}

/**
 * Extract function declarations
 */
function extractFunctions(ast) {
  const functions = [];

  ast.program.body.forEach((node) => {
    if (node.type === "FunctionDeclaration") {
      functions.push({
        name: node.id.name,
        async: node.async,
        generator: node.generator,
        params: node.params.map((p) => p.name),
        line: node.loc.start.line,
      });
    }
  });

  return functions;
}

/**
 * Main extraction function
 */
function extractStructure(filePath) {
  const parseResult = parseFile(filePath);

  if (!parseResult.success) {
    return {
      success: false,
      error: parseResult.error,
      data: null,
    };
  }

  const ast = parseResult.ast;

  return {
    success: true,
    error: null,
    data: {
      file: filePath,
      imports: extractImports(ast),
      exports: extractExports(ast),
      classes: extractClasses(ast),
      functions: extractFunctions(ast),
    },
  };
}

// CLI usage
if (require.main === module) {
  const filePath = process.argv[2];

  if (!filePath) {
    console.error("Usage: node parser.js <file-path>");
    process.exit(1);
  }

  const result = extractStructure(filePath);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { extractStructure };