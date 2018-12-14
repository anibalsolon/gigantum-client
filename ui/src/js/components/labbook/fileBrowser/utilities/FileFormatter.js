export default class FileFormatter {
    constructor(worker) {
        const code = worker.toString();
        const blob = new Blob([`(${code})()`]);
        return new Worker(URL.createObjectURL(blob));
    }
}
/**
*  @param {}
*  Worker that handles the formating and grouping of files
*  @return {}
*/
export const fileHandler = () => {
    /* eslint-disable */
    self.addEventListener('message', (evt) => {
    /* eslint-enable */
        let edges = evt.data.files;
        let edgesToSort = JSON.parse(JSON.stringify(edges));
        let fileObject = {};
        const { search } = evt.data;
        const searchLowerCase = search.toLowerCase();

        if (search !== '') {
          let edgesSearchMatch = edgesToSort.filter((edge) => {
            const lowerCaseKey = edge.node.key.toLowerCase();
            return (lowerCaseKey.indexOf(searchLowerCase) > -1);
          });

          edgesToSort = edgesToSort.filter((edge) => {
            let keyMatch = false;
            edgesSearchMatch.forEach((matchEdge) => {
              if (matchEdge.node.key.indexOf(edge.node.key) > -1) {
                keyMatch = true;
              }
            });
            return keyMatch;
          });
        }

        edgesToSort.forEach((edge, index) => {
            let key = edge.node.key.toLowerCase();
            let searchLowerCase = search.toLowerCase();

            if (edge.node) {
              let currentObject = fileObject;
              let splitKey = edge.node.key.split('/').filter(key => key.length);

              splitKey.forEach((key, index) => {
                  if (currentObject && (index === (splitKey.length - 1))) {
                      if (!currentObject[key]) {
                        currentObject[key] = {
                          edge,
                          index,
                        };
                      } else {
                        currentObject[key].edge = edge;
                      }
                  } else if (currentObject && !currentObject[key]) {
                      currentObject[key] = {
                        children: {
                        },
                        edge: {
                          node: {
                            key: `${splitKey.slice(0, index + 1).join('/')}/`,
                            isDir: true,
                            modifiedAt: Math.floor(Date.now() / 1000),
                          },
                        },
                        index,
                      };
                      currentObject = currentObject[key].children;
                  } else if (currentObject && currentObject[key] && !currentObject[key].children) {
                      currentObject[key].children = {};
                      currentObject = currentObject[key].children;
                  } else {
                    currentObject = currentObject[key].children;
                  }
              });
           }
        });
        const hash = btoa(JSON.stringify(fileObject) + search);
        postMessage({ files: fileObject, hash });
    });
};
