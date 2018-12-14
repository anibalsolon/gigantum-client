const parse = require('parse-gitignore');
const fs = require('fs');

const updateGitIgnore = function(resolve, reject) {

  fs.readdir(__dirname + '/../../../', function(err, items) {
    console.log(items);

    for (var i=0; i<items.length; i++) {
        console.log(items[i]);
    }
});
console.log('asdasad')
fs.readdir(__dirname + '/../../', function(err, items) {
    console.log(items);

    for (var i=0; i<items.length; i++) {
        console.log(items[i]);
    }
});

resolve(true);
return;
  console.log(__dirname)
  let filepath = __dirname.indexOf('opt') > -1 ? __dirname + '/../../../packages/gtmcore/gtmcore/labbook/gitignore.default' : __dirname + '/../../../packages/gtmcore/gtmcore/labbook/gitignore.default'
  let ignoreFiles = parse(fs.readFileSync(filepath));
  let filePath = './src/js/data/gitignore.json'
  let fileContent = JSON.stringify({ gitIgnore: ignoreFiles });

  fs.exists(filePath, function(exists) {
    console.log('updating src/js/data/gitignore.json ...')
    if (exists) {
      //open existing file
      fs.open(filePath, 'w', (err, fd) => {

        if(err){
          console.log(err)
          reject(false);
          console.log('failed to open file', err)
          throw err;
        }
        // write to the file
        fs.write(fd, fileContent, 0, fileContent.length, function(err) {
            if(err){
              reject(false);
              console.log('failed to write file', err)
              throw 'error writing file: ' + err;
            }
            // close file
            fs.close(fd, function() {
                console.log(`${fd} updated`);
                resolve(true)
            })
        });
      });
    } else {

      // create new files
      fs.writeFile(filePath, fileContent, { flag: 'wx' }, (err) => {
        if(err){
          reject(false);
          console.log('failed to create and write file', err)
          if (err) throw err;
        }else{
          resolve(true)
        }
      })
    }
  });
}

module.exports = {
  updateGitIgnore: updateGitIgnore,
};
