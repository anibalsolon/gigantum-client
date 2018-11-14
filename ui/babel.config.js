module.exports = {
 "presets": [
   "@babel/preset-react",
   "@babel/preset-flow",
   ["@babel/preset-env", {
      "targets": {
          "esmodules": true
       }
    }
  ],
   "react-app"
 ],
 "plugins": [
   "relay",
   "@babel/plugin-proposal-class-properties",
   "@babel/plugin-syntax-dynamic-import",
   ["@babel/plugin-proposal-decorators", {
    "legacy": true
   }],
   ["@babel/plugin-proposal-object-rest-spread", { "loose": true, "useBuiltIns": true }],
   [
     "module-resolver",
     {
       "root": [
         "./src",
         "./submodules"
       ],
       "alias": {
         "Mutations": "./src/js/mutations",
         "JS": "./src/js",
         "Components": "./src/js/components",
         "Submodules": "./submodules"
       }
     }
   ]
 ],
 "env": {
  "test": {
    "presets": [
      '@babel/preset-env',
      '@babel/preset-react',
    ],
    "plugins": [
      '@babel/plugin-proposal-class-properties',
      '@babel/plugin-transform-modules-commonjs',
      'babel-plugin-dynamic-import-node-babel-7',
    ],
  },
},
}
